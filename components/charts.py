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

def create_comparison_chart(total_data, stripe_data, mp_data, title, x_label):
    # Asegurar que todas las fechas estén incluidas
    all_dates = set(list(total_data.keys()) + list(stripe_data.keys()) + list(mp_data.keys()))
    all_dates = sorted(list(all_dates))
    
    # Crear listas ordenadas
    x_values = all_dates
    total_values = [total_data.get(date, 0) for date in all_dates]
    stripe_values = [stripe_data.get(date, 0) for date in all_dates]
    mp_values = [mp_data.get(date, 0) for date in all_dates]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=x_values, y=total_values,
        mode='lines+markers',
        name='Total',
        line=dict(color=colors['primary'], width=3),
        marker=dict(size=8)
    ))
    
    fig.add_trace(go.Scatter(
        x=x_values, y=stripe_values,
        mode='lines+markers',
        name='Stripe',
        line=dict(color=colors['stripe'], width=2),
        marker=dict(size=8)
    ))
    
    fig.add_trace(go.Scatter(
        x=x_values, y=mp_values,
        mode='lines+markers',
        name='MercadoPago',
        line=dict(color=colors['mp'], width=2),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title_text=title,
        xaxis_title=x_label,
        yaxis_title="Cantidad",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
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


# Función para crear gráficos de barras apiladas
def create_stacked_bar_chart(data_df, title, x_label, y_label, colors_dict=None):
    """
    Crea un gráfico de barras apiladas por país.
    
    Args:
        data_df: DataFrame con fechas en el índice y países en las columnas
        title: Título del gráfico
        x_label: Etiqueta del eje X
        y_label: Etiqueta del eje Y
        colors_dict: Diccionario opcional que asigna países a colores específicos
    
    Returns:
        Figura de Plotly
    """
    # Si no se proporciona un diccionario de colores, crear uno predeterminado
    if colors_dict is None:
        # Lista de colores predefinidos para los países más comunes
        default_colors = [
            "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
            "#9467bd", "#8c564b", "#e377c2", "#7f7f7f",
            "#bcbd22", "#17becf", "#003f5c", "#58508d",
            "#bc5090", "#ff6361", "#ffa600", "#4c78a8",
            "#f58518", "#54a24b", "#b279a2"
        ]
        # Asignar colores a países
        colors_dict = {}
        for i, country in enumerate(data_df.columns):
            colors_dict[country] = default_colors[i % len(default_colors)]
    
    fig = go.Figure()
    
    # Ordenando en orden descendente según la cantidad
    ordered_columns = data_df.sum().sort_values(ascending=True).index.tolist()

    # Agregar una traza (barra) para cada país
    for country in ordered_columns:
        fig.add_trace(go.Bar(
            x=data_df.index,
            y=data_df[country],
            name=country,
            marker_color=colors_dict.get(country)
        ))
    
    # Configurar el layout para barras apiladas
    fig.update_layout(
        barmode='stack',
        title_text=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        plot_bgcolor=colors['light_gray'],
        paper_bgcolor=colors['card_bg'],
        font=dict(color=colors['text']),
        margin=dict(l=40, r=40, t=50, b=40),
        legend_title_text='Países',
    )
    
    return fig