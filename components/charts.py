# components/charts.py
import plotly.graph_objs as go
import plotly.express as px
from style.styles import colors
import pandas as pd

def create_bar_chart(data, title, x_label, y_label, color):
    fig = go.Figure(data=[go.Bar(
        x=list(data.keys()), 
        y=list(data.values()),
        marker_color=color
    )])
    fig.update_layout(
        title_text=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        plot_bgcolor=colors['light_gray'],
        paper_bgcolor=colors['card_bg'],
        font=dict(color=colors['text']),
        margin=dict(l=40, r=40, t=50, b=40),
    )
    return fig

def create_mp_type_charts(mp_types_data):
    # Ordenar por cantidad de mayor a menor
    sorted_data = sorted(mp_types_data, key=lambda x: x['cantidad'], reverse=True)
    
    # Separar los 3 mayores y el resto
    top_three = sorted_data[:3]
    others = sorted_data[3:]
    
    # Colores para los gráficos
    top_colors = ['#009EE3', '#00C2FF', '#36D4FF']
    other_colors = px.colors.qualitative.Pastel1[:len(others)]
    
    # Gráfico para los 3 mayores
    fig_top = go.Figure()
    for i, item in enumerate(top_three):
        fig_top.add_trace(go.Bar(
            x=['Top 3'],
            y=[item['cantidad']],
            name=item['tipo'],
            marker_color=top_colors[i],
            text=item['cantidad'],
            textposition='auto',
        ))
    
    fig_top.update_layout(
        title_text="Top 3 Suscripciones MercadoPago por Tipo",
        yaxis_title="Cantidad",
        plot_bgcolor=colors['light_gray'],
        paper_bgcolor=colors['card_bg'],
        font=dict(color=colors['text']),
        margin=dict(l=40, r=40, t=50, b=40),
        barmode='stack',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        ),
    )
    
    # Gráfico para el resto
    fig_others = go.Figure()
    for i, item in enumerate(others):
        fig_others.add_trace(go.Bar(
            x=['Otros Tipos'],
            y=[item['cantidad']],
            name=item['tipo'],
            marker_color=other_colors[i % len(other_colors)],
            text=item['cantidad'],
            textposition='auto',
        ))
    
    fig_others.update_layout(
        title_text="Otras Suscripciones MercadoPago por Tipo",
        yaxis_title="Cantidad",
        plot_bgcolor=colors['light_gray'],
        paper_bgcolor=colors['card_bg'],
        font=dict(color=colors['text']),
        margin=dict(l=40, r=40, t=50, b=40),
        barmode='stack',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.5,  # Ajustar según la cantidad de elementos
            xanchor="center",
            x=0.5
        ),
    )
    
    return fig_top, fig_others


def create_stacked_bar_chart(data_df, stack_column, title, x_label, y_label, x = "date", y = "count", bar_width_days=None):
    """
    Crea un gráfico de barras apiladas donde el ancho de las barras es dinámico.
    
    Args:
        data_df: DataFrame con columnas 'date', 'count' y la columna para apilar
        stack_column: Nombre de la columna que se utilizará para dividir las barras apiladas
        title: Título del gráfico
        x_label: Etiqueta del eje X
        y_label: Etiqueta del eje Y
        bar_width_days: Ancho de las barras en días (opcional). Si no se proporciona, se calcula automáticamente.
        
    Returns:
        Figura de Plotly
    """    
    # Asegurarse de que la columna date sea de tipo datetime
    data_df = data_df.copy()
    if 'date' in data_df.columns:  # Verificar si la columna 'date' existe
        data_df['date'] = pd.to_datetime(data_df['date'])

    # Balance total por fecha
    df_total = data_df.groupby(x)[y].sum().reset_index()
    
    # Calcular el ancho de barra de forma dinámica si no se proporciona
    if bar_width_days is None:
        # Si hay suficientes fechas, calcular el ancho basado en la diferencia promedio entre fechas
        if len(data_df['date'].unique()) > 1:
            dates_sorted = sorted(data_df['date'].unique())
            date_diffs = [(dates_sorted[i+1] - dates_sorted[i]).total_seconds() / (24*60*60) 
                         for i in range(len(dates_sorted)-1)]
            # Usar el promedio de diferencias como ancho, pero no menos de 0.5 días
            bar_width_days = max(0.5, sum(date_diffs) / len(date_diffs) * 0.8)  # 80% del intervalo promedio
        else:
            # Valor predeterminado si solo hay una fecha
            bar_width_days = 1
        # Convertir el ancho de días a milisegundos para Plotly
        bar_width_ms = bar_width_days * 24 * 60 * 60 * 1000
    else:
        bar_width_ms = bar_width_days
        
    # Crear el gráfico de barras apiladas
    fig = px.bar(
        data_df,
        x=x,
        y=y,
        color=stack_column,
        title=title,
        labels={y: y_label, x: x_label},
        barmode='stack'
    )
    
    fig.add_trace(go.Scatter(
    x=df_total[x],
    y=df_total[y],
    mode='lines+markers+text',
    name='Total',
    line=dict(color='blue', width=2),
    text=df_total[y],            
    textposition='top center',   
    textfont=dict(size=12)       
    ))

    # Aplicar el ancho de barra calculado
    fig.update_traces(width=bar_width_ms, selector=dict(type="bar"))
    
    # Configurar el layout para barras apiladas
    fig.update_layout(
        barmode='stack',
        xaxis_title=x_label,
        yaxis_title=y_label,
        margin=dict(l=40, r=40, t=50, b=40),
        legend_title_text=stack_column.capitalize(),
    )
    
    # Opcional: agregar colores personalizados si se desea
    # Si deseas mantener los colores definidos en tu código original:
    try:
        colors = {
            'light_gray': '#f9f9f9',
            'card_bg': '#ffffff',
            'text': '#333333'
        }
        fig.update_layout(
            plot_bgcolor=colors['light_gray'],
            paper_bgcolor=colors['card_bg'],
            font=dict(color=colors['text']),
        )
    except:
        # Si los colores no están definidos, usar los valores predeterminados de Plotly
        pass
        
    return fig

def plot_subscription_balance(df, title):
    """
    Genera un gráfico de barras apiladas por país y una línea del balance total por fecha.

    Parámetros:
    df (DataFrame): debe contener las columnas 'date', 'country' y 'balance'

    Retorna:
    Una figura de Plotly
    """

    # Balance total por fecha
    df_total = df.groupby('date')['balance'].sum().reset_index()

    # Crear figura con barras apiladas
    fig = go.Figure()

    # Añadir barras por país
    for country in df['country'].unique():
        df_country = df[df['country'] == country]
        fig.add_trace(go.Bar(
            x=df_country['date'],
            y=df_country['balance'],
            name=country
        ))

    # Añadir línea del balance total
    fig.add_trace(go.Scatter(
        x=df_total['date'],
        y=df_total['balance'],
        mode='lines+markers',
        name='Balance total',
        line=dict(color='blue', width=2)
    ))

    # Layout
    fig.update_layout(
        barmode='relative',
        title=title,
        xaxis_title='Fecha',
        yaxis_title='Balance',
        xaxis_tickangle=-45
    )
    return fig

def plot_monthly_creations_cancellations(df):
    """
    Creates a bar chart of monthly creations and cancellations using Plotly.
    
    Parameters:
    df (pandas.DataFrame): DataFrame with 'localdate', 'creations_count', and 'cancelations_count' columns
    
    Returns:
    plotly.graph_objects.Figure: Plotly figure with grouped bars for creations and cancellations
    """
    # Validate input columns
    if not {'localdate', 'creations_count', 'cancelations_count'}.issubset(df.columns):
        raise ValueError("DataFrame must contain 'localdate', 'creations_count', and 'cancelations_count' columns")
    
    # Create a copy to avoid modifying input
    df = df.copy()
    
    # Ensure localdate is datetime and extract year-month
    df['localdate'] = pd.to_datetime(df['localdate'])
    df['year_month'] = df['localdate'].dt.strftime('%Y-%m')
    
    # Group by year-month and sum creations and cancellations
    monthly_data = df.groupby('year_month').agg({
        'creations_count': 'sum',
        'cancelations_count': 'sum'
    }).reset_index()
    
    # Create Plotly figure
    fig = go.Figure()
    
    # Add bars for creations (light blue)
    fig.add_trace(go.Bar(
        x=monthly_data['year_month'],
        y=monthly_data['creations_count'],
        name='Creations',
        marker_color='lightblue',  # Light blue color
        text=monthly_data['creations_count'],
        textposition='auto'
    ))
    
    # Add bars for cancellations (light red)
    fig.add_trace(go.Bar(
        x=monthly_data['year_month'],
        y=monthly_data['cancelations_count'],
        name='Cancellations',
        marker_color='lightcoral',  # Light red color
        text=monthly_data['cancelations_count'],
        textposition='auto'
    ))
    
    # Customize layout
    fig.update_layout(
        title='Monthly Creations and Cancellations',
        xaxis_title='Month (YYYY-MM)',
        yaxis_title='Count',
        barmode='group',  # Group bars side by side
        legend_title='Category',
        xaxis=dict(
            tickangle=45,
            tickmode='array',
            tickvals=monthly_data['year_month']
        ),
        showlegend=True,
        width=1000,
        height=600,
        template='plotly_white',
        margin=dict(b=150)  # Extra margin for rotated labels
    )
    
    # Add grid
    fig.update_xaxes(showgrid=True, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridcolor='lightgray')
    
    return fig


def stripe_tme_subscriptions_chart(mongo_subs_per_month, canceladas_mongo_per_month, 
                                   incomplete_mongo_per_month, title):
    fig = go.Figure()
    # Created Stripe Subscriptions
    fig.add_scatter(x=mongo_subs_per_month.index, y=mongo_subs_per_month["count"], mode='lines+markers+text', 
                line_shape='spline', name='Created', 
                text=mongo_subs_per_month["count"],  # Display the count values as labels
                textposition='top center',  # Position the labels above the markers
                line=dict(color="#2AA834"),marker=dict(size=4, symbol='circle'))
    # Canceled Mongo Subscriptions
    fig.add_scatter(x=canceladas_mongo_per_month.index, y=canceladas_mongo_per_month["count"], mode='lines+markers+text', 
                line_shape='spline', name='Canceled', 
                text=canceladas_mongo_per_month["count"],  # Display the count values as labels
                textposition='top center',  # Position the labels above the markers
                line=dict(color="#B8100A"),marker=dict(size=4, symbol='circle'))

    # Incomplete Mongo Subscriptions
    fig.add_scatter(x=incomplete_mongo_per_month.index, y=incomplete_mongo_per_month["count"], mode='lines+markers+text', 
                line_shape='spline', name='Incomplete', 
                text=incomplete_mongo_per_month["count"],  # Display the count values as labels
                textposition='top center',  # Position the labels above the markers
                line=dict(color="#FFA500"),marker=dict(size=4, symbol='circle'))

    fig.update_layout(title=title, yaxis_title="Subscriptions", xaxis_title="Month",
                        yaxis_tickformat=',', title_x=0.5)
    return fig


def net_stripe_tme_subs_chart(neto_series, title):
    fig = go.Figure()
    # Net Stripe Subscriptions
    fig.add_scatter(x=neto_series.index, y=neto_series, mode='lines+markers+text', 
                line_shape='spline', name='Net', 
                text=neto_series,  # Display the count values as labels
                textposition='top center',  # Position the labels above the markers
                line=dict(color="#3330CE"),marker=dict(size=4, symbol='circle'))


    fig.update_layout(title=title, yaxis_title="Subscriptions", xaxis_title="Month",
                        yaxis_tickformat=',', title_x=0.5)
    return fig

def plot_mp_planes(df):
    df_sorted = df.sort_values(by="count", ascending=True)
    fig = px.bar(
        df_sorted,
        x='count', 
        y="reason",
        text="count",
        orientation="h",  # horizontal
        title="Cantidad de suscriptores activos por plan",
        labels={"reason": "Plan", "count": "Cantidad"},
    )
    
    # Opciones estéticas
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(
        yaxis=dict(categoryorder="total ascending"),
        uniformtext_minsize=8,
        # uniformtext_mode="hide",
        template="plotly_white"
    )
    return fig

def mp_monthly_subscriptions_chart(df):
    """Chart for Mercado Pago monthly subscriptions data."""
    fig = go.Figure()
       
    # Suscripciones creadas
    fig.add_scatter(x=df["month"], y=df["creations_count"], mode='lines+markers+text', line_shape='spline',
                    name='Creadas', #fill='tozeroy',
                    text=df["creations_count"],  # Display the count values as labels
                    textposition='top center',  # Position the labels above the markers
                    line=dict(color="#5BC75B"), marker=dict(size=4, symbol='circle'))

    # Suscripciones Canceladas
    fig.add_scatter(x=df["month"], y=df["cancelations_count"],mode='lines+markers+text', line_shape='spline',
                    name='Canceladas', #fill='tozeroy',
                    text=df["cancelations_count"],  # Display the count values as labels
                    textposition='top center',  # Position the labels above the markers
                    line=dict(color="#E06D6D"), marker=dict(size=4, symbol='circle'))

    # Estética general
    fig.update_layout(title=f"Suscripciones creadas y canceladas", yaxis_title="Cantidad", xaxis_title="Mes",
                        yaxis_tickformat=',', title_x=0.5)
    return fig

def mp_net_subscriptions_chart(df):
    """Chart for Mercado Pago net monthly subscriptions."""
    fig = go.Figure()
    # Suscripciones netas
    fig.add_scatter(x=df["month"], y=df["net_subscriptions"], mode='lines+markers+text', line_shape='spline', 
                    name='Neto', #fill='tozeroy',
                    text=df["net_subscriptions"],  # Display the count values as labels
                    textposition='top center',  # Position the labels above the markers
                    line=dict(color="#180779"),marker=dict(size=4, symbol='circle'))
    
    # Estética general
    fig.update_layout(title=f"Suscripciones Netas", yaxis_title="Cantidad", xaxis_title="Mes",
                        yaxis_tickformat=',', title_x=0.5)
    return fig

def mp_unique_payments_per_month(df):
    pagos_total = df.copy()
    pagos_total['date_approved'] = pd.to_datetime(df['date_approved'])
    mp_discount = pagos_total[pagos_total['description'] == 'single_payment_discount'].copy()
    recargas_tokens = pagos_total[pagos_total['description'] == 'single_payment_C'].copy()
    recargas_min = pagos_total[pagos_total['description'] == 'single_payment_T'].copy()

    mp_discount_per_month = (
        mp_discount
        .groupby(mp_discount['date_approved'].dt.to_period('M').dt.to_timestamp())
        .agg(count=('date_approved', 'size'))
        .reset_index()
    )

    recargas_tokens_per_month = (
        recargas_tokens
        .groupby(recargas_tokens['date_approved'].dt.to_period('M').dt.to_timestamp())
        .agg(count=('date_approved', 'size'))
        .reset_index()
    )

    recargas_min_per_month = (
        recargas_min
        .groupby(recargas_min['date_approved'].dt.to_period('M').dt.to_timestamp())
        .agg(count=('date_approved', 'size'))
        .reset_index()
    )

    fig = go.Figure()
    # Suscripciones de 3 meses
    fig.add_scatter(x=mp_discount_per_month["date_approved"], y=mp_discount_per_month["count"], mode='lines+markers+text', 
                line_shape='spline', name='mp-3-meses', 
                text=mp_discount_per_month["count"],  # Display the count values as labels
                textposition='top center',  # Position the labels above the markers
                line=dict(color="#2AA834"),marker=dict(size=4, symbol='circle'))

    # Recargas de tokens
    fig.add_scatter(x=recargas_tokens_per_month["date_approved"], y=recargas_tokens_per_month["count"], mode='lines+markers+text', 
                line_shape='spline', name='Recargas de tokens', 
                text=recargas_tokens_per_month["count"],  # Display the count values as labels
                textposition='top center',  # Position the labels above the markers
                line=dict(color="#3116AA"),marker=dict(size=4, symbol='circle'))

    # Recargas de minutos
    fig.add_scatter(x=recargas_min_per_month["date_approved"], y=recargas_min_per_month["count"], mode='lines+markers+text', 
                line_shape='spline', name='Recargas de minutos', 
                text=recargas_min_per_month["count"],  # Display the count values as labels
                textposition='top center',  # Position the labels above the markers
                line=dict(color="#23979B"),marker=dict(size=4, symbol='circle'))


    fig.update_layout(title=f"Pagos únicos Mercado Pago", yaxis_title="Pagos", xaxis_title="Month",
                        yaxis_tickformat=',', title_x=0.5)
    return fig

def mp_subscription_payments_per_month(df):
    pagos_total = df.copy()
    pagos_total['date_approved'] = pd.to_datetime(df['date_approved'])
    suscripciones = pagos_total[pagos_total['description'].str.contains('TranscribeMe')].copy()

    suscripciones_per_month = (
        suscripciones
        .groupby(suscripciones['date_approved'].dt.to_period('M').dt.to_timestamp())
        .agg(count=('date_approved', 'size'))
        .reset_index()
    )

    fig = go.Figure()
    # Suscripciones
    fig.add_scatter(x=suscripciones_per_month["date_approved"], y=suscripciones_per_month["count"], mode='lines+markers+text', 
                line_shape='spline', name='Suscripciones', 
                text=suscripciones_per_month["count"],  # Display the count values as labels
                textposition='top center',  # Position the labels above the markers
                line=dict(color="#23979B"),marker=dict(size=4, symbol='circle'))


    fig.update_layout(title=f"Pagos por suscripciones en Mercado Pago", yaxis_title="Suscripciones", xaxis_title="Month",
                        yaxis_tickformat=',', title_x=0.5)
    return fig

def income_mp_per_month(df, selector = 'Total'):
    pagos_total = df.copy()

    pagos_total['date_approved'] = pd.to_datetime(df['date_approved'])

    # Unificar los valores de description según el tipo
    def unify_description(desc):
        if desc.startswith('TranscribeMe'):
            return 'Suscripciones'
        elif desc == 'single_payment_discount':
            return 'Plan de 3 meses'
        elif desc == 'single_payment_C':
            return 'Recargas de tokens'
        elif desc == 'single_payment_T':
            return 'Recargas de minutos'
        return desc  # Mantener el valor original si no coincide con ninguna regla

    pagos_total['description'] = pagos_total['description'].apply(unify_description)

    if selector == 'Total':
        income_per_month = (
            pagos_total
            .groupby(pagos_total['date_approved'].dt.to_period('M').dt.to_timestamp())
            .agg(income=('transaction_amount', 'sum'))
            .reset_index()
        )
    else:
        income_per_month = (
            pagos_total[pagos_total['description'] == selector].copy()
            .groupby(pagos_total['date_approved'].dt.to_period('M').dt.to_timestamp())
            .agg(income=('transaction_amount', 'sum'))
            .reset_index()
        )

    income_per_month['income'] = income_per_month['income'].round(2)

    fig = go.Figure()
    # Income
    fig.add_scatter(x=income_per_month["date_approved"], y=income_per_month["income"], mode='lines+markers+text', 
                line_shape='spline', name=f'{selector}', 
                text=income_per_month["income"],  # Display the income values as labels
                textposition='top center',  # Position the labels above the markers
                line=dict(color="#23979B"),marker=dict(size=4, symbol='circle'))

    fig.update_layout(yaxis_title="Income", xaxis_title="Month",
                        yaxis_tickformat=',', title_x=0.5)
    return fig

def total_subscriptions_chart(df):
    fig = go.Figure()
    # Created Stripe Subscriptions
    fig.add_scatter(x=df['month'], y=df["total_creations"], mode='lines+markers+text', 
                line_shape='spline', name='Created', 
                text=df["total_creations"],  # Display the count values as labels
                textposition='top center',  # Position the labels above the markers
                line=dict(color="#2AA834"),marker=dict(size=4, symbol='circle'))
    # Canceled Mongo Subscriptions
    fig.add_scatter(x=df['month'], y=df["total_cancellations"], mode='lines+markers+text', 
                line_shape='spline', name='Canceled', 
                text=df["total_cancellations"],  # Display the count values as labels
                textposition='top center',  # Position the labels above the markers
                line=dict(color="#B8100A"),marker=dict(size=4, symbol='circle'))

    # Incomplete Mongo Subscriptions
    fig.add_scatter(x=df['month'], y=df["total_incomplete"], mode='lines+markers+text', 
                line_shape='spline', name='Incomplete', 
                text=df["total_incomplete"],  # Display the count values as labels
                textposition='top center',  # Position the labels above the markers
                line=dict(color="#FFA500"),marker=dict(size=4, symbol='circle'))

    fig.update_layout(title='Total Subscriptions', yaxis_title="Subscriptions", xaxis_title="Month",
                        yaxis_tickformat=',', title_x=0.5)
    return fig

def net_subscriptions_chart(df):
    fig = go.Figure()
    # Net Subs
    fig.add_scatter(x=df['month'], y=df["net_total"], mode='lines+markers+text', 
                line_shape='spline', name='Created', 
                text=df["net_total"],  # Display the count values as labels
                textposition='top center',  # Position the labels above the markers
                line=dict(color="#2AA834"),marker=dict(size=4, symbol='circle'))

    fig.update_layout(title='Net Subscriptions', yaxis_title="Subscriptions", xaxis_title="Month",
                        yaxis_tickformat=',', title_x=0.5)
    return fig
