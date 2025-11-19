import plotly.graph_objs as go
import plotly.express as px
from style.styles import colors
import pandas as pd
from dash import dash_table

def recovery_status_stacked_bar_chart(data:pd.DataFrame) -> go.Figure:
    """
    Crea un gráfico de barras apiladas que muestra los montos fallidos de revenue recovery
    desglosados por estado de recuperación a lo largo del tiempo.

    Args:
        df (pd.DataFrame): DataFrame que contiene las columnas 'initial_payment_failed_at', 'amount_failed' y 'recovery_status'.
    Returns: 
        go.Figure: Gráfico de barras apiladas.
    """
    df = data.copy()
    
    # Convertimos la columna a datetime
    df['initial_payment_failed_at'] = pd.to_datetime(df['initial_payment_failed_at'])
    
    # Creamos la columna "Mes" en formato "2025-11", "2025-12", etc.
    df['Mes'] = df['initial_payment_failed_at'].dt.strftime('%Y-%m')

    # Agrupamos por mes y recovery_status, sumando el monto fallido
    df_grouped = (
        df.groupby(['Mes', 'recovery_status'], as_index=False)
        .agg(total_amount=('initial_failed_amount', 'sum'))
    )

    # Ordenamos los meses cronológicamente (importante para que el eje X quede bien)
    df_grouped['Mes'] = pd.Categorical(
        df_grouped['Mes'],
        categories=sorted(df_grouped['Mes'].unique()),
        ordered=True
    )
    df_grouped = df_grouped.sort_values('Mes')

    # -------------------------------------------------
    # 2. Creamos el gráfico de barras apiladas
    # -------------------------------------------------
    fig = px.bar(
        df_grouped,
        x='Mes',
        y='total_amount',
        color='recovery_status',
        title='Monto fallido por mes y estado de recuperación',
        labels={
            'total_amount': 'Monto fallido ($)',
            'Mes': 'Mes',
            'recovery_status': 'Estado de recuperación'
        },
        color_discrete_map={
            'In recovery':     "#EEE129",   
            'Recovered':       "#311286",   
            'Not recovered':   "#68C4E0"    
        },
        template='simple_white',
    )

    # Mejoramos un poco el formato
    fig.update_traces(
        text = None,
        hovertemplate='<b>%{x}</b><br>'
                  'Estado: <b>%{fullData.name}</b><br>'
                  'Monto: <b>$%{y:,.2f}</b><extra></extra>'
    )

    fig.update_layout(
        hovermode='x unified',
        legend_title='Estado de recuperación',
        yaxis=dict(title='Monto total fallido ($)', tickformat=',.0f'),
        xaxis=dict(title='Mes'),
        bargap=0.15
    )

    return fig

def recovery_reason_stacked_bar_chart(data: pd.DataFrame) -> go.Figure:
    """
    Crea un gráfico de barras apiladas que muestra el voluman recuperado por mes y motivo de fallo
    """
    # -------------------------------------------------
    # 1. Preparamos los datos
    # -------------------------------------------------
    recovered_df = data[data['recovery_status']=='Recovered'].copy()  

    # Convertimos la columna a datetime
    recovered_df['recovered_at'] = pd.to_datetime(recovered_df['recovered_at'])

    # Creamos la columna "Mes" en formato "2025-11", "2025-12", etc.
    recovered_df['Mes'] = recovered_df['recovered_at'].dt.strftime('%Y-%m')

    # Agrupamos por mes y recovery_status, sumando el monto fallido
    df_grouped = (
        recovered_df.groupby(['Mes', 'recovery_method'], as_index=False)
        .agg(total_amount=('recovered_amount', 'sum'))
    )

    # Ordenamos los meses cronológicamente (importante para que el eje X quede bien)
    df_grouped['Mes'] = pd.Categorical(
        df_grouped['Mes'],
        categories=sorted(df_grouped['Mes'].unique()),
        ordered=True
    )
    df_grouped = df_grouped.sort_values('Mes')
    # -------------------------------------------------
    # 2. Creamos el gráfico de barras apiladas
    # -------------------------------------------------
    fig = px.bar(
        df_grouped,
        x='Mes',
        y='total_amount',
        color='recovery_method',
        title='Volumen recuperado por mes y método de recuperación',
        labels={
            'total_amount': 'Monto recuperado ($)',
            'Mes': 'Mes',
            'recovery_method': 'Método de recuperación'
        },
        color_discrete_map={
            'retry':     "#9566E2",   # naranja claro
            'email':       "#3E12B8",   # verde éxito
            'external':   "#2C1179"    # rojo
        },
        template='simple_white',
    )

    # Mejoramos un poco el formato
    fig.update_traces(
        text = None,
        hovertemplate='<b>%{x}</b><br>'
                  'Método: <b>%{fullData.name}</b><br>'
                  'Monto: <b>$%{y:,.2f}</b><extra></extra>'
    )

    fig.update_layout(
        hovermode='x unified',
        legend_title='Método de recuperación',
        yaxis=dict(title='Monto total recuperado ($)', tickformat=',.0f'),
        xaxis=dict(title='Mes'),
        bargap=0.15
    )

    return fig

def failed_volumne_by_decline_reason_stacked_bar_chart(data: pd.DataFrame) -> go.Figure:
    """
    Crea un gráfico de barras apiladas que muestra el monto de pagos fallidos
    desglosados por motivo de fallo a lo largo del tiempo.
    
    Args:
        df (pd.DataFrame): DataFrame que contiene las columnas 'initial_payment_failed_at', 
                        'initial_failed_amount' y 'initial_payment_decline_reason'.
    Returns: 
        go.Figure: Gráfico de barras apiladas.
    """
    # -------------------------------------------------
    # 1. Preparamos los datos
    # -------------------------------------------------
    df = data.copy()  

    # Convertimos la columna a datetime
    df['initial_payment_failed_at'] = pd.to_datetime(df['initial_payment_failed_at'])

    # Creamos la columna "Mes" en formato "2025-11", "2025-12", etc.
    df['Mes'] = df['initial_payment_failed_at'].dt.strftime('%Y-%m')

    # Agrupamos por mes y initial_payment_decline_reason, sumando el monto fallido
    df_grouped = (
        df.groupby(['Mes', 'initial_payment_decline_reason'], as_index=False)
        .agg(total_amount=('initial_failed_amount', 'sum'))
    )

    # Ordenamos los meses cronológicamente (importante para que el eje X quede bien)
    df_grouped['Mes'] = pd.Categorical(
        df_grouped['Mes'],
        categories=sorted(df_grouped['Mes'].unique()),
        ordered=True
    )
    df_grouped = df_grouped.sort_values('Mes')

    # -------------------------------------------------
    # 2. Creamos el gráfico de barras apiladas
    # -------------------------------------------------
    fig = px.bar(
        df_grouped,
        x='Mes',
        y='total_amount',
        color='initial_payment_decline_reason',
        title='Monto fallido por mes y motivo',
        labels={
            'total_amount': 'Monto fallido ($)',
            'Mes': 'Mes',
            'initial_payment_decline_reason': 'Motivo de fallo'
        },
    
        template='simple_white',
    )

    # Mejoramos un poco el formato
    fig.update_traces(
        text = None,
        hovertemplate='<b>%{x}</b><br>'
                  'Motivo: <b>%{fullData.name}</b><br>'
                  'Monto: <b>$%{y:,.2f}</b><extra></extra>'
    )

    fig.update_layout(
        hovermode='x unified',
        legend_title='Motivo de fallo',
        yaxis=dict(title='Monto total fallido ($)', tickformat=',.0f'),
        xaxis=dict(title='Mes'),
        bargap=0.15
    )

    return fig
