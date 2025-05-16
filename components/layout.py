# components/layout.py

from dash import dcc, html
from datetime import date
from style.styles import (
    colors, card_style, metric_card_style, graph_card_style,
    tab_style, tab_selected_style
)

def serve_layout():
    return html.Div([
        # Header
        html.Div([
            html.H1("Dashboard de Suscripciones - TranscribeMe", 
                    style={"color": colors['primary'], "marginBottom": "10px"}),
            html.Hr(style={"margin": "0 0 20px 0"}),
        ], style={"textAlign": "center", "paddingTop": "20px"}),
        
        # Filtros
        html.Div([
            html.Div([
                html.Label("Rango de Fechas:", style={"fontWeight": "bold", "marginBottom": "10px"}),
                dcc.DatePickerRange(
                    id='date-range',
                    start_date=date(2023, 1, 1),
                    end_date=date.today(),
                    display_format='YYYY-MM-DD',
                    style={"width": "100%"}
                ),
            ], style={**card_style, "width": "100%"}),
        ], style={"marginBottom": "20px"}),

        # Tarjetas de Métricas Resumen
        html.Div([
            html.Div([
                html.H3("Suscripciones Creadas en el Rango de Fechas", style={"color": colors['primary'], "marginBottom": "15px"}),
                html.Div(id='total-subs-summary', style={"fontSize": "16px"})
            ], style={**metric_card_style, "borderTop": f"4px solid {colors['primary']}"}),

            html.Div([
                html.H3("Suscripciones Activas Actualmente", style={"color": colors['stripe'], "marginBottom": "15px"}),
                html.Div(id='stripe-subs-summary', style={"fontSize": "16px"})
            ], style={**metric_card_style, "borderTop": f"4px solid {colors['stripe']}"}),
        ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between", "marginBottom": "20px"}),

        # Pestañas para organizar gráficos
        dcc.Tabs(id="tabs", value='tab-overview', children=[
            dcc.Tab(label='Vista General', value='tab-overview', style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(label='Stripe', value='tab-stripe', style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(label='MercadoPago', value='tab-mp', style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(label='Comparativas', value='tab-compare', style=tab_style, selected_style=tab_selected_style),
        ], style={"marginBottom": "20px"}),

        # Contenido de las pestañas
        html.Div(id='tab-content')

    ], style={
        "padding": "20px",
        "fontFamily": "Arial, sans-serif",
        "backgroundColor": colors['background'],
        "maxWidth": "1400px",
        "margin": "0 auto"
    })
