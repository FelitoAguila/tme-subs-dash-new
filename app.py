from dash import Dash, dcc, html, Input, Output, callback_context
import plotly.graph_objs as go
import plotly.express as px
from datetime import date
from subs_metrics import SubscriptionMetrics

# Instanciar la clase
metrics = SubscriptionMetrics()

# Crear la app con hoja de estilos externa
app = Dash(__name__)
app.title = "Dashboard de Suscripciones"
server = app.server  # Esto es importante para Gunicorn

# Definir colores
colors = {
    'background': '#f9f9f9',
    'text': '#333333',
    'primary': '#2c3e50',
    'secondary': '#3498db',
    'accent': '#e74c3c',
    'stripe': '#6772E5',
    'mp': '#009EE3',
    'card_bg': '#ffffff',
    'light_gray': '#ecf0f1'
}

# Estilos
card_style = {
    'backgroundColor': colors['card_bg'],
    'borderRadius': '8px',
    'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
    'padding': '20px',
    'margin': '10px',
}

metric_card_style = {
    **card_style,
    'textAlign': 'center',
    'flex': '1',
    'minWidth': '200px',
}

graph_card_style = {
    **card_style,
    'flex': '1',
    'minWidth': '45%',
}

tab_style = {
    'padding': '10px 15px',
    'borderBottom': '1px solid #d6d6d6',
    'fontWeight': 'bold',
    'backgroundColor': colors['light_gray'],
    'borderRadius': '5px 5px 0 0',
    'margin': '0 2px',
}

tab_selected_style = {
    'padding': '10px 15px',
    'borderBottom': '1px solid #d6d6d6',
    'borderTop': f'3px solid {colors["secondary"]}',
    'backgroundColor': colors['card_bg'],
    'color': colors['secondary'],
    'borderRadius': '5px 5px 0 0',
    'margin': '0 2px',
}

# Layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("Dashboard de Suscripciones", 
                style={"color": colors['primary'], "marginBottom": "10px"}),
        html.Hr(style={"margin": "0 0 20px 0"}),
    ], style={"textAlign": "center", "paddingTop": "20px"}),
    
    # Filtros
    html.Div([
        html.Div([
            html.Label("Rango de Fechas:", style={"fontWeight": "bold", "marginBottom": "10px"}),
            dcc.DatePickerRange(
                id='date-range',
                start_date=date(2024, 1, 1),
                end_date=date.today(),
                display_format='YYYY-MM-DD',
                style={"width": "100%"}
            ),
        ], style={**card_style, "width": "100%"}),
    ], style={"marginBottom": "20px"}),
    
    # Tarjetas de Métricas Resumen
    html.Div([
        html.Div([
            html.H3("Total Suscripciones", style={"color": colors['primary'], "marginBottom": "15px"}),
            html.Div(id='total-subs-summary', style={"fontSize": "16px"})
        ], style={**metric_card_style, "borderTop": f"4px solid {colors['primary']}"}),
        
        html.Div([
            html.H3("Stripe", style={"color": colors['stripe'], "marginBottom": "15px"}),
            html.Div(id='stripe-subs-summary', style={"fontSize": "16px"})
        ], style={**metric_card_style, "borderTop": f"4px solid {colors['stripe']}"}),
        
        html.Div([
            html.H3("MercadoPago", style={"color": colors['mp'], "marginBottom": "15px"}),
            html.Div(id='mp-subs-summary', style={"fontSize": "16px"})
        ], style={**metric_card_style, "borderTop": f"4px solid {colors['mp']}"}),
    ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between", "marginBottom": "20px"}),
    
    # Pestañas para organizar gráficos
    dcc.Tabs(id="tabs", value='tab-overview', children=[
        # Pestaña de Vista General
        dcc.Tab(label='Vista General', value='tab-overview', style=tab_style, selected_style=tab_selected_style),
        # Pestaña de Stripe
        dcc.Tab(label='Stripe', value='tab-stripe', style=tab_style, selected_style=tab_selected_style),
        # Pestaña de MercadoPago
        dcc.Tab(label='MercadoPago', value='tab-mp', style=tab_style, selected_style=tab_selected_style),
        # Pestaña de Comparativas
        dcc.Tab(label='Comparativas', value='tab-compare', style=tab_style, selected_style=tab_selected_style),
    ], style={"marginBottom": "20px"}),
    
    # Contenido de las pestañas
    html.Div(id='tab-content')
    
], style={"padding": "20px", "fontFamily": "Arial, sans-serif", "backgroundColor": colors['background'], "maxWidth": "1400px", "margin": "0 auto"})

@app.callback(
    Output('total-subs-summary', 'children'),
    Output('stripe-subs-summary', 'children'),
    Output('mp-subs-summary', 'children'),
    Input('date-range', 'start_date'),
    Input('date-range', 'end_date')
)
def update_summary_metrics(start_date, end_date):
    total = metrics.total_subs(start_date, end_date)
    avg_daily = metrics.average_daily_subs(start_date, end_date)
    avg_monthly = metrics.average_monthly_subs(start_date, end_date)
    total_stripe = metrics.total_stripe_subs(start_date, end_date)
    avg_daily_stripe = metrics.average_stripe_daily_subs(start_date, end_date)
    avg_monthly_stripe = metrics.average_stripe_monthly_subs(start_date, end_date)
    total_mp = metrics.total_mp_subs(start_date, end_date)
    avg_daily_mp = metrics.average_mp_daily_subs(start_date, end_date)
    avg_monthly_mp = metrics.average_mp_monthly_subs(start_date, end_date)

    return (
        html.Div([
            html.Div([
                html.Span("Total: ", style={"fontWeight": "bold"}),
                html.Span(f"{total}", style={"fontSize": "24px", "color": colors['primary']})
            ], style={"marginBottom": "10px"}),
            html.Div([
                html.Span("Promedio Diario: ", style={"fontWeight": "bold"}),
                html.Span(f"{avg_daily:.2f}")
            ], style={"marginBottom": "5px"}),
            html.Div([
                html.Span("Promedio Mensual: ", style={"fontWeight": "bold"}),
                html.Span(f"{avg_monthly:.2f}")
            ]),
        ]),
        html.Div([
            html.Div([
                html.Span("Total: ", style={"fontWeight": "bold"}),
                html.Span(f"{total_stripe}", style={"fontSize": "24px", "color": colors['stripe']})
            ], style={"marginBottom": "10px"}),
            html.Div([
                html.Span("Promedio Diario: ", style={"fontWeight": "bold"}),
                html.Span(f"{avg_daily_stripe:.2f}")
            ], style={"marginBottom": "5px"}),
            html.Div([
                html.Span("Promedio Mensual: ", style={"fontWeight": "bold"}),
                html.Span(f"{avg_monthly_stripe:.2f}")
            ]),
        ]),
        html.Div([
            html.Div([
                html.Span("Total: ", style={"fontWeight": "bold"}),
                html.Span(f"{total_mp}", style={"fontSize": "24px", "color": colors['mp']})
            ], style={"marginBottom": "10px"}),
            html.Div([
                html.Span("Promedio Diario: ", style={"fontWeight": "bold"}),
                html.Span(f"{avg_daily_mp:.2f}")
            ], style={"marginBottom": "5px"}),
            html.Div([
                html.Span("Promedio Mensual: ", style={"fontWeight": "bold"}),
                html.Span(f"{avg_monthly_mp:.2f}")
            ]),
        ]),
    )

@app.callback(
    Output('tab-content', 'children'),
    Input('tabs', 'value'),
    Input('date-range', 'start_date'),
    Input('date-range', 'end_date')
)
def render_tab_content(tab, start_date, end_date):
    # Obtener datos comunes
    monthly_total = metrics.monthly_subs(start_date, end_date)
    daily_total = metrics.daily_subs(start_date, end_date)
    stripe_monthly = metrics.monthly_stripe_subs(start_date, end_date)
    stripe_daily = metrics.daily_stripe_subs(start_date, end_date)
    mp_monthly = metrics.monthly_mp_subs(start_date, end_date)
    mp_daily = metrics.daily_mp_subs(start_date, end_date)
    stripe_status_data = metrics.status_stripe_subs()
    tme_plus_status_data = metrics.status_tme_plus()
    tme_plus2_status_data = metrics.status_tme_plus2()
    
    # Crear gráficos comunes
    fig_monthly_total = create_bar_chart(
        monthly_total, "Total de Suscripciones por Mes", "Mes", "Cantidad", colors['primary']
    )
    
    fig_daily_total = create_bar_chart(
        daily_total, "Total de Suscripciones por Día", "Fecha", "Cantidad", colors['primary']
    )
    
    fig_stripe_monthly = create_bar_chart(
        stripe_monthly, "Stripe - Suscripciones Mensuales", "Mes", "Cantidad", colors['stripe']
    )
    
    fig_stripe_daily = create_bar_chart(
        stripe_daily, "Stripe - Suscripciones Diarias", "Fecha", "Cantidad", colors['stripe']
    )
    
    fig_mp_monthly = create_bar_chart(
        mp_monthly, "MercadoPago - Suscripciones Mensuales", "Mes", "Cantidad", colors['mp']
    )
    
    fig_mp_daily = create_bar_chart(
        mp_daily, "MercadoPago - Suscripciones Diarias", "Fecha", "Cantidad", colors['mp']
    )
    
    # Gráfico de estados de Stripe
    statuses = [item['_id'] for item in stripe_status_data]
    counts = [item['count'] for item in stripe_status_data]
    fig_stripe_status = go.Figure(data=[go.Bar(
        x=statuses, 
        y=counts,
        marker_color=colors['stripe']
    )])
    fig_stripe_status.update_layout(
        title_text="Estado de Suscripciones de Stripe",
        xaxis_title="Estado",
        yaxis_title="Cantidad",
        plot_bgcolor=colors['light_gray'],
        paper_bgcolor=colors['card_bg'],
        font=dict(color=colors['text']),
        margin=dict(l=40, r=40, t=50, b=40),
    )

    # Gráfico de estados de TME Plus
    statuses = [item['_id'] for item in tme_plus_status_data]
    counts = [item['count'] for item in tme_plus_status_data]
    fig_tme_plus_status = go.Figure(data=[go.Bar(
        x=statuses, 
        y=counts,
        marker_color=colors['mp']
    )])
    fig_tme_plus_status.update_layout(
        title_text="Estado de Suscripciones de TranscribeMe Plus",
        xaxis_title="Estado",
        yaxis_title="Cantidad",
        plot_bgcolor=colors['light_gray'],
        paper_bgcolor=colors['card_bg'],
        font=dict(color=colors['text']),
        margin=dict(l=40, r=40, t=50, b=40),
    )

    # Gráfico de estados de TME Plus 2
    statuses = [item['_id'] for item in tme_plus2_status_data]
    counts = [item['count'] for item in tme_plus2_status_data]
    fig_tme_plus2_status = go.Figure(data=[go.Bar(
        x=statuses, 
        y=counts,
        marker_color=colors['mp']
    )])
    fig_tme_plus2_status.update_layout(
        title_text="Estado de Suscripciones de TranscribeMe Plus 2",
        xaxis_title="Estado",
        yaxis_title="Cantidad",
        plot_bgcolor=colors['light_gray'],
        paper_bgcolor=colors['card_bg'],
        font=dict(color=colors['text']),
        margin=dict(l=40, r=40, t=50, b=40),
    )
    
    # Crear gráfico comparativo
    fig_comparison = create_comparison_chart(
        monthly_total, stripe_monthly, mp_monthly,
        "Comparación de Suscripciones Mensuales",
        "Mes"
    )
    
    # Crear gráfico de proporción
    total_by_platform = {
        'Stripe': sum(stripe_monthly.values()), 
        'MercadoPago': sum(mp_monthly.values())
    }
    fig_proportion = go.Figure(data=[go.Pie(
        labels=list(total_by_platform.keys()),
        values=list(total_by_platform.values()),
        marker=dict(colors=[colors['stripe'], colors['mp']])
    )])
    fig_proportion.update_layout(
        title_text="Proporción de Suscripciones por Plataforma",
        plot_bgcolor=colors['light_gray'],
        paper_bgcolor=colors['card_bg'],
        font=dict(color=colors['text']),
        margin=dict(l=40, r=40, t=50, b=40),
    )
    
    # Contenido para cada pestaña
    if tab == 'tab-overview':
        return html.Div([
            html.Div([
                html.Div([
                    dcc.Graph(figure=fig_monthly_total)
                ], style=graph_card_style),
                html.Div([
                    dcc.Graph(figure=fig_daily_total)
                ], style=graph_card_style),
            ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),
            html.Div([
                html.Div([
                    dcc.Graph(figure=fig_proportion)
                ], style=graph_card_style),
            ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),
        ])
    
    elif tab == 'tab-stripe':
        return html.Div([
            html.Div([
                html.Div([
                    dcc.Graph(figure=fig_stripe_monthly)
                ], style=graph_card_style),
                html.Div([
                    dcc.Graph(figure=fig_stripe_daily)
                ], style=graph_card_style),
            ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),
            html.Div([
                html.Div([
                    dcc.Graph(figure=fig_stripe_status)
                ], style=graph_card_style),
            ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),
        ])
    
    elif tab == 'tab-mp':
        # Obtener datos para los gráficos de tipo de suscripción
        mp_types_data = metrics.contar_suscripciones_mercado_pago()
        fig_mp_top_types, fig_mp_other_types = create_mp_type_charts(mp_types_data)
    
        return html.Div([
            html.Div([
                html.Div([
                    dcc.Graph(figure=fig_mp_monthly)
                ], style=graph_card_style),
                html.Div([
                    dcc.Graph(figure=fig_mp_daily)
                ], style=graph_card_style),
            ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),
        
            # Nueva sección para los gráficos de tipo de suscripción
            html.Div([
                html.Div([
                    dcc.Graph(figure=fig_mp_top_types)
                ], style=graph_card_style),
                html.Div([
                    dcc.Graph(figure=fig_mp_other_types)
                ], style=graph_card_style),
            ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),
            html.Div([
                html.Div([
                    dcc.Graph(figure=fig_tme_plus_status)
                ], style=graph_card_style),
            ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),   
            html.Div([
                html.Div([
                    dcc.Graph(figure=fig_tme_plus2_status)
                ], style=graph_card_style),
            ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),                     
        ])
    
    elif tab == 'tab-compare':
        return html.Div([
            html.Div([
                html.Div([
                    dcc.Graph(figure=fig_comparison)
                ], style=graph_card_style),
                html.Div([
                    dcc.Graph(figure=fig_proportion)
                ], style=graph_card_style),
            ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),
        ])

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

if __name__ == '__main__':
    # Obtener puerto de variable de entorno (para Render) o usar 8050 por defecto (para desarrollo local)
    port = int(os.environ.get("PORT", 8050))
    app.run_server(host="0.0.0.0", port=port, debug=False)
