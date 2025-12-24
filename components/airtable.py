from config import PERSONAL_ACCESS_TOKEN, BASE_ID, TABLE_ID, STRIPE_API_KEY
from pyairtable import Table
import pandas as pd
from get_country import getCountry
import plotly.graph_objs as go
import plotly.express as px
from components.charts import create_stacked_bar_chart
import stripe

# Conexión a Stripe
stripe.api_key = STRIPE_API_KEY

# Conectar a la tabla
table = Table(PERSONAL_ACCESS_TOKEN, BASE_ID, TABLE_ID)

# Obtener todos los registros
records = table.all()
# Convertir a DataFrame (los datos están en 'fields')
df = pd.DataFrame([record['fields'] for record in records])

def determine_country(row):
    if row['client_reference_id'].startswith('u'):
        return "TranscribeGo"
    elif row['client_reference_id'].startswith('t'):
        return "Telegram"
    elif row['client_reference_id'].startswith('w'):
        user_phone = '+' + str(row['client_reference_id'][1:])
        return getCountry(user_phone)

df['country'] = df.apply(determine_country, axis=1)

# ------------------------- FUNNEL CHART ----------------------------------------------------------
# Total Expired Checkout Sessions by Country
total_expired = df['country'].value_counts().reset_index()
total_expired['stage'] = 'Expired Sessions'

# Users emailed (customer email is not NaN)
users_emailed = df[~df['customer email'].isna()].copy()
# TME users emailed
users_emailed = users_emailed[users_emailed['country']!= 'TranscribeGo'].copy()
total_emailed = users_emailed['country'].value_counts().reset_index()
total_emailed['stage'] = 'Emailed'

# Subscribed Users
subs = []
for idx, row in users_emailed.iterrows():
    customer = row['customer ID']
    expired_session_timestamp = row['created']
    subscriptions = stripe.Subscription.list(limit=10, customer=customer, created = {'gt': expired_session_timestamp}, status='active')
    subs.append(subscriptions.data[0].id) if subscriptions.data else subs.append(None)
users_emailed['sub_id'] = subs
subscribed_df = users_emailed[~users_emailed['sub_id'].isna()].copy()
total_subscribed = subscribed_df['country'].value_counts().reset_index()
total_subscribed['stage'] = 'Subscribed'

# Combining all stages
final = pd.concat([total_expired, total_emailed, total_subscribed], axis=0)

# Agrupar y sumar los counts por stage
total = final.groupby('stage')['count'].sum().reset_index()

# Ordena el DataFrame según el orden categorical
total = total.sort_values('count', ascending=False)

# Ahora sí, el funnel respetará el orden
total_funnel_fig = px.funnel(total, 
                x='count', 
                y='stage',
                title='Subscriptions among emailed users with expired checkout sessions',)

# --------------------- Heat Map Users by Country -------------------------------------------------
df_map = df.groupby('country').size().reset_index(name='Users')

def heat_map_users_by_country(total_users_by_country, title = 'Expired Sessions by Country'):
    fig = go.Figure(data=go.Choropleth(
        locations=total_users_by_country['country'],
        locationmode='country names',
        z=total_users_by_country['Users'],
        text=total_users_by_country['country'],
        colorscale=[
            [0.0, 'rgb(220, 255, 220)'],
            [0.02, 'rgb(180, 240, 180)'],
            [0.1, 'rgb(140, 220, 140)'],
            [0.3, 'rgb(100, 200, 100)'],
            [0.6, 'rgb(60, 160, 60)'],
            [1.0, 'rgb(0, 100, 0)']
        ],
        autocolorscale=False,
        marker_line_color='darkgray',
        marker_line_width=0.5,
        #colorbar_title='Users',
        hovertemplate='%{text}: %{z}<extra></extra>'
    ))

    fig.update_layout(
        title_text=title,
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='equirectangular'
        ),
        margin={"r":0, "t":50, "l":0, "b":0},
        title_x=0.5
    )
    
    return fig

map_fig = heat_map_users_by_country(df_map)

# --------------------- Stacked Bar Chart Users by Country Over Time -------------------------
df = df.rename(columns={'Created (date)': 'date'})

df['date'] = pd.to_datetime(df['date'])

# Extraer solo la parte de la fecha (sin hora)
df['date'] = df['date'].dt.date

# Agrupar por fecha y país, y contar las ocurrencias
expired_per_day = df.groupby(['date', 'country']).size().reset_index(name='count')

# Ordenar por fecha y país
expired_per_day = expired_per_day.sort_values(['date', 'country']).reset_index(drop=True)

expired_per_day_fig = create_stacked_bar_chart(
                data_df=expired_per_day, stack_column = "country",
                title="", x_label="Mes", y_label="Cantidad")

