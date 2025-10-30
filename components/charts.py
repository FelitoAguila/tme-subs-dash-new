# components/charts.py
import plotly.graph_objs as go
import plotly.express as px
from style.styles import colors
import pandas as pd
from dash import dash_table

# ============ CHART FUNCTIONS ============================

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

def mp_unique_payments_per_month(df, selector = 'Total'):
    # Tomo solo los pagos únicos de all_mp_payments
    pagos_unicos = df[df['operation_type']=='regular_payment'].copy()
    # Transformo las fechas al formato que necesito para agrupar
    pagos_unicos['date_created'] = pd.to_datetime(df['date_created'])

    # Selección de pagos
    if selector == 'Aprobados':
        pagos_unicos = pagos_unicos[pagos_unicos['status']=='approved']
    elif selector == 'Rechazados':
        pagos_unicos = pagos_unicos[pagos_unicos['status']=='rejected']
    
    mp_discount = pagos_unicos[pagos_unicos['description'] == 'single_payment_discount'].copy()
    recargas_tokens = pagos_unicos[pagos_unicos['description'] == 'single_payment_C'].copy()
    recargas_min = pagos_unicos[pagos_unicos['description'] == 'single_payment_T'].copy()

    mp_discount_per_month = (
        mp_discount
        .groupby(mp_discount['date_created'].dt.to_period('M').dt.to_timestamp())
        .agg(count=('date_created', 'size'))
        .reset_index()
    )

    recargas_tokens_per_month = (
        recargas_tokens
        .groupby(recargas_tokens['date_created'].dt.to_period('M').dt.to_timestamp())
        .agg(count=('date_created', 'size'))
        .reset_index()
    )

    recargas_min_per_month = (
        recargas_min
        .groupby(recargas_min['date_created'].dt.to_period('M').dt.to_timestamp())
        .agg(count=('date_created', 'size'))
        .reset_index()
    )

    fig = go.Figure()
    # Suscripciones de 3 meses
    fig.add_scatter(x=mp_discount_per_month["date_created"], y=mp_discount_per_month["count"], mode='lines+markers+text', 
                line_shape='spline', name='mp-3-meses', 
                text=mp_discount_per_month["count"],  # Display the count values as labels
                textposition='top center',  # Position the labels above the markers
                line=dict(color="#2AA834"),marker=dict(size=4, symbol='circle'))

    # Recargas de tokens
    fig.add_scatter(x=recargas_tokens_per_month["date_created"], y=recargas_tokens_per_month["count"], mode='lines+markers+text', 
                line_shape='spline', name='Recargas de tokens', 
                text=recargas_tokens_per_month["count"],  # Display the count values as labels
                textposition='top center',  # Position the labels above the markers
                line=dict(color="#3116AA"),marker=dict(size=4, symbol='circle'))

    # Recargas de minutos
    fig.add_scatter(x=recargas_min_per_month["date_created"], y=recargas_min_per_month["count"], mode='lines+markers+text', 
                line_shape='spline', name='Recargas de minutos', 
                text=recargas_min_per_month["count"],  # Display the count values as labels
                textposition='top center',  # Position the labels above the markers
                line=dict(color="#23979B"),marker=dict(size=4, symbol='circle'))


    fig.update_layout(yaxis_title="Pagos", xaxis_title="Month",
                        yaxis_tickformat=',', title_x=0.5)
    return fig

def mp_subscription_payments_per_month(df, selector = 'Total'):
    # Tomo solo las suscripciones de all_mp_payments
    suscripciones = df[df['operation_type']=='recurring_payment'].copy()
    # Transformo las fechas al formato que necesito para agrupar
    suscripciones['date_created'] = pd.to_datetime(df['date_created'])

    # Selección de pagos
    if selector == 'Aprobados':
        suscripciones = suscripciones[suscripciones['status']=='approved']
    elif selector == 'Rechazados':
        suscripciones = suscripciones[suscripciones['status']=='rejected']
    
    suscripciones_per_month = (
        suscripciones
        .groupby(suscripciones['date_created'].dt.to_period('M').dt.to_timestamp())
        .agg(count=('date_created', 'size'))
        .reset_index()
    )

    fig = go.Figure()
    # Suscripciones
    fig.add_scatter(x=suscripciones_per_month["date_created"], y=suscripciones_per_month["count"], mode='lines+markers+text', 
                line_shape='spline', name='Suscripciones', 
                text=suscripciones_per_month["count"],  # Display the count values as labels
                textposition='top center',  # Position the labels above the markers
                line=dict(color="#23979B"),marker=dict(size=4, symbol='circle'))


    fig.update_layout(yaxis_title="Pagos", xaxis_title="Month",
                        yaxis_tickformat=',', title_x=0.5)
    return fig

def income_mp_per_month(df, selector = 'Total'):
    pagos_total = df[df['status']=='approved'].copy()

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

def tgo_income_chart (payments, selector = 'Total'):
    df = payments[payments['statement_descriptor'] == 'TranscribeGo subscript'].copy()
    df['created'] = pd.to_datetime(df['created'])
    if selector == 'Total':
        income_per_month = (
            df
            .groupby(df['created'].dt.to_period('M').dt.to_timestamp())
            .agg(income=('amount', 'sum'))
            .reset_index()
        )
    else:
        income_per_month = (
            df[df['description'] == selector].copy()
            .groupby(df['created'].dt.to_period('M').dt.to_timestamp())
            .agg(income=('amount', 'sum'))
            .reset_index()
        )

    income_per_month['income'] = income_per_month['income'].round(2)
    
    fig = go.Figure()
    # Income
    fig.add_scatter(x=income_per_month["created"], y=income_per_month["income"], mode='lines+markers+text', 
                line_shape='spline', name=f'{selector}', 
                text=income_per_month["income"],  # Display the income values as labels
                textposition='top center',  # Position the labels above the markers
                line=dict(color="#23979B"),marker=dict(size=4, symbol='circle'))

    fig.update_layout(yaxis_title="Income", xaxis_title="Month",
                        yaxis_tickformat=',', title_x=0.5)
    return fig

def tme_subs_income_chart (payments, selector = 'Total'):
    df = payments[payments['statement_descriptor'] != 'Recarga'].copy()
    df['created'] = pd.to_datetime(df['created'])
    if selector == 'Total':
        income_per_month = (
            df
            .groupby(df['created'].dt.to_period('M').dt.to_timestamp())
            .agg(income=('amount', 'sum'))
            .reset_index()
        )
    else:
        income_per_month = (
            df[df['description'] == selector].copy()
            .groupby(df['created'].dt.to_period('M').dt.to_timestamp())
            .agg(income=('amount', 'sum'))
            .reset_index()
        )

    income_per_month['income'] = income_per_month['income'].round(2)
    
    fig = go.Figure()
    # Income
    fig.add_scatter(x=income_per_month["created"], y=income_per_month["income"], mode='lines+markers+text', 
                line_shape='spline', name=f'{selector}', 
                text=income_per_month["income"],  # Display the income values as labels
                textposition='top center',  # Position the labels above the markers
                line=dict(color="#23979B"),marker=dict(size=4, symbol='circle'))

    fig.update_layout(yaxis_title="Income", xaxis_title="Month", yaxis_tickformat=',', title_x=0.5)
    return fig

def total_stripe_recargas_per_month_chart(df):
    fig = go.Figure()
    # Created Stripe Subscriptions
    fig.add_scatter(x=df['created'], y=df["income"], mode='lines+markers+text', 
                line_shape='spline', name='Recargas', 
                text=df["income"],  # Display the count values as labels
                textposition='top center',  # Position the labels above the markers
                line=dict(color="#23979B"),marker=dict(size=4, symbol='circle'))

    fig.update_layout(yaxis_title="Income", xaxis_title="Month", yaxis_tickformat=',', title_x=0.5)
    return fig

def total_income_chart(total_income):
    fig = go.Figure()
    # Created Stripe Subscriptions
    fig.add_scatter(x=total_income['month'], y=total_income['total_income'], mode='lines+markers+text', 
                line_shape='spline', name='Total Income', 
                text=total_income['total_income'],  # Display the count values as labels
                textposition='top center',  # Position the labels above the markers
                line=dict(color="#25C010"),marker=dict(size=4, symbol='circle'))
    fig.add_scatter(x=total_income['month'], y=total_income['stripe_income'], mode='lines+markers+text', 
                line_shape='spline', name='Stripe Income', 
                text=total_income['stripe_income'],  # Display the count values as labels
                textposition='top center',  # Position the labels above the markers
                line=dict(color="#2419B4"),marker=dict(size=4, symbol='circle'))
    fig.add_scatter(x=total_income['month'], y=total_income['mp_income'], mode='lines+markers+text', 
                line_shape='spline', name='Mercado Pago Income', 
                text=total_income['mp_income'],  # Display the count values as labels
                textposition='top center',  # Position the labels above the markers
                line=dict(color="#E9E636"),marker=dict(size=4, symbol='circle'))
    fig.update_layout(title='Income (USD)', yaxis_title="Income", xaxis_title="Month", yaxis_tickformat=',', title_x=0.5)
    return fig


def plot_tgo_onboardings(df, selector='Role', max_categories=7):
    # Mapeo de columnas
    column_map = {
        'Role': 'role',
        'Use Case': 'useCase',
        'First Project': 'firstProject',
        'How Did You Hear': 'howDidYouHear'
    }
    
    if selector not in column_map:
        raise ValueError(f"Selector debe ser uno de: {list(column_map.keys())}")
    
    column = column_map[selector]
    
    # Contar frecuencias
    count_df = df[column].value_counts().reset_index()
    count_df.columns = [column, 'count']
    
    # Calcular porcentaje
    total = count_df['count'].sum()
    count_df['percentage'] = (count_df['count'] / total * 100).round(2)
    
    # === LIMITAR CATEGORÍAS ===
    if len(count_df) > max_categories:
        top_n = count_df.head(max_categories).copy()
        others = count_df.iloc[max_categories:].copy()
        others_row = pd.DataFrame([{
            column: 'Otros',
            'count': others['count'].sum().round(2),
            'percentage': others['percentage'].sum().round(2)
        }])
        count_df = pd.concat([top_n, others_row], ignore_index=True)
    else:
        # Si hay menos o igual, no agrupar
        pass
    
    # Ordenar: "Otros" al final, el resto por conteo ascendente
    others = count_df[count_df[column] == 'Otros']
    main = count_df[count_df[column] != 'Otros'].sort_values(by='count', ascending=True)
    count_df = pd.concat([main, others], ignore_index=True) if not others.empty else main
    
    # Reset index para hover
    count_df = count_df.reset_index(drop=True)
    
    # === TRUCO: Columna dummy para una sola barra ===
    count_df['dummy'] = 'Total Onboardings'
    
    # === PALETA DE AZULES CLAROS (profesional y legible) ===
    # Usamos una escala personalizada: azules claros a medianos
    n_colors = len(count_df)
    blue_palette = [
        # '#E3F2FD', '#BBDEFB', '#90CAF9',
        '#64B5F6', 
        '#42A5F5', '#2196F3', '#1E88E5', '#1976D2', 
        '#1565C0', '#0D47A1'
    ]
    # Repetir o recortar según necesidad
    colors = (blue_palette * (n_colors // len(blue_palette) + 1))[:n_colors]
    
    # Asignar color a "Otros" como gris claro
    color_map = {val: colors[i] for i, val in enumerate(count_df[column])}
    if 'Otros' in color_map:
        color_map['Otros'] = '#B0BEC5'  # Gris azulado claro
    
    
    # === ANTES de px.bar: preparar customdata ===
    count_df['category_name'] = count_df[column]  # nombre real de la categoría
    count_df['customdata'] = count_df[['count', 'category_name']].values.tolist()  # array [count, name]
    
    # === GRÁFICO ===
    fig = px.bar(
        count_df,
        x='percentage',
        y='dummy',
        color=column,
        orientation='h',
        labels={
            'percentage': 'Porcentaje (%)',
            'dummy': '',
            column: selector
        },
        color_discrete_map=color_map,
        custom_data=['customdata']  # ← importante: pasar el array
    )
    
    # Personalizar barras
    fig.update_traces(
        hovertemplate=(
            f'<b>{selector}:</b> %{{customdata[0][1]}}</b><br>'
            'Porcentaje: %{x:.2f}%<br>'
            'Conteo: %{customdata[0][0]}<extra></extra>'
        )
    )
    
    # Layout final
    fig.update_layout(
        barmode='stack',
        showlegend=True,
        xaxis_title="Porcentaje del total (%)",
        yaxis_title="",
        yaxis=dict(
            showticklabels=False,
            fixedrange=True
        ),
        height=300,
        legend_title_text=selector,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02
        ),
        margin=dict(r=180),  # Espacio para leyenda externa
        uniformtext=dict(mode='hide')
    )
    
    # Forzar eje X al 100%
    fig.update_xaxes(range=[0, 100], ticksuffix="%")
    
    return fig

def table_tgo_onboardings(df, selector='Role'):
    column_map = {
        'Role': 'role',
        'Use Case': 'useCase',
        'First Project': 'firstProject',
        'How Did You Hear': 'howDidYouHear'
    }
    column = column_map[selector]
    
    # Conteo y porcentaje
    count_df = df[column].value_counts().reset_index()
    count_df.columns = [selector, 'Conteo']
    total = count_df['Conteo'].sum()
    count_df['Porcentaje (%)'] = (count_df['Conteo'] / total * 100).round(2)
    
    # Ordenar
    count_df = count_df.sort_values(by='Conteo', ascending=False).reset_index(drop=True)
    
    # Formatear para DataTable
    data = count_df.to_dict('records')
    columns = [
        {"name": selector, "id": selector},
        {"name": "Conteo", "id": "Conteo", "type": "numeric", "format": {"specifier": ","}},
        {"name": "Porcentaje (%)", "id": "Porcentaje (%)", "type": "numeric", "format": {"specifier": ".2f"}}
    ]
    
    table = dash_table.DataTable(data=data, columns=columns, id ='tgo-onboardings-table',
                                            style_header={'backgroundColor': '#f5f7fa',
                                                           'fontWeight': 'bold','textAlign': 'center'},
                                            style_cell={'textAlign': 'left','padding': '10px','fontFamily': 'Arial, sans-serif'},
                                            style_data={'backgroundColor': 'white'},
                                            style_data_conditional=[
                                                {'if': {'row_index': 'odd'}, 'backgroundColor': '#f9f9f9'}
                                            ],
                                            page_size=10,
                                            sort_action="native",
                                            filter_action="native",
                                            export_format="csv",
                                            export_headers="display"
                                        )
    return table
