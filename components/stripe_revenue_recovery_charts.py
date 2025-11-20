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

def failed_volume_by_decline_reason_stacked_bar_chart(data: pd.DataFrame) -> go.Figure:
    df = data.copy()

    # -------------------------------------------------
    # 1. Preparación de datos
    # -------------------------------------------------
    df['initial_payment_failed_at'] = pd.to_datetime(df['initial_payment_failed_at'])
    df['Mes'] = df['initial_payment_failed_at'].dt.strftime('%Y-%m')

    # Total histórico por motivo para seleccionar top 5
    total_por_motivo = (
        df.groupby('initial_payment_decline_reason')['initial_failed_amount']
        .sum()
        .sort_values(ascending=False)
    )

    top_5_motivos = total_por_motivo.head(5).index.tolist()
    
    # Nueva columna: top 5 o "Others"
    df['motivo_grafico'] = df['initial_payment_decline_reason'].where(
        df['initial_payment_decline_reason'].isin(top_5_motivos), 
        'Others'
    )

    # Agrupación final
    df_grouped = (
        df.groupby(['Mes', 'motivo_grafico'], as_index=False)
        .agg(total_amount=('initial_failed_amount', 'sum'))
    )

    # Total por mes
    total_mes = df_grouped.groupby('Mes')['total_amount'].transform('sum')
    df_grouped['percentage'] = 100 * df_grouped['total_amount'] / total_mes

    # Orden de meses
    meses_ordenados = sorted(df_grouped['Mes'].unique())
    df_grouped['Mes'] = pd.Categorical(df_grouped['Mes'], categories=meses_ordenados, ordered=True)

    # Orden de leyenda: top 5 + Others al final
    orden_leyenda = top_5_motivos + ['Others']
    df_grouped['motivo_grafico'] = pd.Categorical(
        df_grouped['motivo_grafico'],
        categories=orden_leyenda,
        ordered=True
    )

    # Ordenamos para que Plotly respete el orden
    df_grouped = df_grouped.sort_values(['Mes', 'motivo_grafico'])

    # -------------------------------------------------
    # 2. Gráfico con Graph Objects (más control que px.bar)
    # -------------------------------------------------
    fig = go.Figure()

    for motivo in orden_leyenda:
        df_motivo = df_grouped[df_grouped['motivo_grafico'] == motivo]
        
        fig.add_trace(go.Bar(
            x=df_motivo['Mes'],
            y=df_motivo['total_amount'],
            name=motivo,
            text=df_motivo['total_amount'].apply(lambda x: f'${x:,.0f}'),
            textposition='none',
            hovertemplate=
                '<b>%{x}</b><br>' +
                f'Motivo: <b>{motivo}</b><br>' +
                'Monto: <b>$%{y:,.0f}</b><br>' +
                'Porcentaje: <b>%{customdata:.1f}%</b>' +
                '<extra></extra>',
            customdata=df_motivo['percentage']
        ))

    # Layout
    fig.update_layout(
        title='Monto fallido por mes y motivo (Top 5 + Others)',
        xaxis_title='Mes',
        yaxis_title='Monto total fallido ($)',
        yaxis=dict(tickformat=',.0f'),
        barmode='stack',
        hovermode='closest',
        template='simple_white',
        bargap=0.15,
        legend_title='Motivo de fallo',
        legend=dict(traceorder='normal')
    )

    return fig

def failed_reasons_detail_table(df: pd.DataFrame, selected_month: str = None):
    """
    Tabla de detalle que muestra todas las razones de fallo para un mes seleccionado.
    Si no se selecciona mes, muestra el total histórico.
    
    Ideal para usar como callback con el click/hover del gráfico de barras.
    """
    df = df.copy()
    df['initial_payment_failed_at'] = pd.to_datetime(df['initial_payment_failed_at'])
    df['Mes'] = df['initial_payment_failed_at'].dt.strftime('%Y-%m')

    # Filtrar por mes seleccionado (o todo si no hay selección)
    if selected_month:
        df_filtered = df[df['Mes'] == selected_month]
        title = f"Detalles de motivos - {selected_month}"
    else:
        df_filtered = df
        title = "Detalles de motivos - Total histórico"

    if df_filtered.empty:
        # Tabla vacía con mensaje
        data = []
        columns = [
            {"name": "Motivo", "id": "motivo"},
            {"name": "Monto fallido ($)", "id": "monto"},
            {"name": "% del mes (%)", "id": "porcentaje"}
        ]
    else:
        # Agrupamos por motivo
        summary = (
            df_filtered.groupby('initial_payment_decline_reason', as_index=False)
            .agg(monto=('initial_failed_amount', 'sum'))
        )

        total_mes = summary['monto'].sum()
        summary['porcentaje'] = (summary['monto'] / total_mes * 100).round(2)
        summary = summary.sort_values('monto', ascending=False).reset_index(drop=True)

        # Renombramos para mostrar bonito
        summary['motivo'] = summary['initial_payment_decline_reason']
        summary['Monto fallido ($)'] = summary['monto']
        summary['% del mes'] = summary['porcentaje'] + "%"

        # Formateo final
        data = summary[['motivo', 'Monto fallido ($)', '% del mes']].to_dict('records')

        columns = [
            {"name": "Motivo", "id": "motivo"},
            {"name": "Monto fallido ($)", "id": "Monto fallido ($)", 
             "type": "numeric", "format": {"specifier": ",.0f"}},
            {"name": "% del mes", "id": "% del mes", 
             "type": "numeric", "format": {"specifier": ".2f"}}
        ]

    # Creamos la tabla Dash
    table = dash_table.DataTable(
        data=data,
        columns=columns,
        id='failed-reasons-detail-table',
        
        style_header={
            'backgroundColor': '#2c3e50',
            'color': 'white',
            'fontWeight': 'bold',
            'textAlign': 'center',
            'fontFamily': 'Arial, sans-serif'
        },
        style_cell={
            'textAlign': 'left',
            'padding': '12px',
            'fontFamily': 'Arial, sans-serif',
            'fontSize': '14px'
        },
        style_data={
            'backgroundColor': 'white',
            'border': '1px solid #ecf0f1'
        },
        style_data_conditional=[
            {'if': {'row_index': 'odd'}, 'backgroundColor': '#f8f9fa'},
            {'if': {'column_id': 'Monto fallido ($)'}, 'textAlign': 'right'},
            {'if': {'column_id': '% del mes'}, 'textAlign': 'right', 'fontWeight': 'bold'},
        ],
        style_table={'overflowX': 'auto'},
        page_size=12,
        sort_action="native",
        filter_action="native",
        export_format="csv",
        export_headers="display",
    )

    return table

def recovery_subs_funnel_chart(recoverable_subs: pd.DataFrame) -> go.Figure:
    """
    Crea un gráfico que muestra el status de suscripciones en recovery
    """
    
    recovery_dict = {
        "Entered Recovery": len(recoverable_subs), 
        "Unpaid": len(recoverable_subs[recoverable_subs['subscription_status']=='unpaid']),
        "Past Due": len(recoverable_subs[recoverable_subs['subscription_status']=='past_due']),
        "Active": len(recoverable_subs[recoverable_subs['subscription_status']=='active']),
        "Canceled": len(recoverable_subs[recoverable_subs['subscription_status']=='canceled']), 
        "Incomplete": len(recoverable_subs[recoverable_subs['subscription_status']=='incomplete'])
    }

    labels = list(recovery_dict.keys())
    source = [0]*len(labels[1:])
    target = list(range(1, len(labels)))
    value  = list(recovery_dict.values())[1:]
    fig = go.Figure(go.Sankey(
        node=dict(pad=30, thickness=40, label=labels,
                  color=["#37474F", "#FF9800", "#636EFA", "#4CAF50"]),
        link=dict(source=source, target=target, value=value,
                  color=["#FF9800", "#636EFA", "#4CAF50"])
    ))

    fig.update_layout(title=f"Estado actual de suscripciones ({len(recoverable_subs)} totales)", height=500)
    return fig
