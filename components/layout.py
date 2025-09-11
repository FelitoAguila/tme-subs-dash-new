# components/layout.py

from dash import dcc, html
from datetime import date
from style.styles import (
    colors, card_style, metric_card_style, graph_card_style,
    tab_style, tab_selected_style
)
from subs_metrics import SubscriptionMetrics

metrics = SubscriptionMetrics()

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
                html.Label("Rango de Fechas:", style={"fontWeight": "bold", "marginBottom": "30px"}),
                dcc.DatePickerRange(
                    id='date-range',
                    start_date=date(2025, 1, 1),
                    end_date=date.today(),
                    display_format='YYYY-MM-DD',
                    style={"width": "100%","marginTop": "10px"}
                ),
            ], style={**card_style, "width": "100%", "marginTop": "10px"}),
            html.Div([
                html.Label([
                            "Valor de venta del Dólar Oficial",
                            html.Br(),  # Salto de línea
                            "(en ARS, según dolarapi.com):",
                            ], style={"fontWeight": "bold", "marginBottom": "5px", "display": 'block'}),
                html.Button('Buscar Valor', id='get-dollar-value-button', n_clicks=0, className='btn btn-primary',
                            style={'width': '100%', 'height': '40px', 'fontSize': '18px', 'marginTop': '10px'}),                            
                dcc.Input(
                    id='dollar-value',
                    type='number',
                    placeholder='Valor',
                    # placeholder=metrics.get_dolar_argentina(),
                    # value = metrics.get_dolar_argentina(),
                    min=0,
                    step=1,
                    style={"width": "50%", "marginTop": "10px", "height": "40px", "fontSize": "18px"}
                ),
            ], style={**card_style, "width": "100%"}),
            html.Div([
                html.Label([
                            "Subir archivo csv de Mercado Pago",
                            html.Br(), # salto de línea
                            "(todos los suscriptores)"
                            ], style ={"fontWeight": "bold", "marginBottom": "5px"}),
                dcc.Upload(id='upload-data', 
                           children=html.Button('Cargar archivo', className='btn btn-primary'),
                        #    multiple=False,  # Allow only one file
                           multiple=True,
                           accept='.csv',   # Restrict to CSV files (adjust as needed)
                           style={'width': '100%', 'height': '60px', 'lineHeight': '60px', 'borderWidth': '1px',
                                  'borderStyle': 'dashed','borderRadius': '5px','textAlign': 'center','margin': '10px'}
                ),
                html.Div(id='output-data-upload'),  # Placeholder for upload feedback
                dcc.Store(id='mp-data-store')
            ], style={**card_style, "width": "100%"}),
            html.Div([
                html.Label("Cargar datos de Mongo DB", 
                           style ={"fontWeight": "bold", "marginBottom": "5px"}),
                html.Button('Cargar datos', id='load-mongo-button', n_clicks=0, className='btn btn-primary',
                            style={'width': '100%', 'height': '40px', 'fontSize': '18px', 'marginTop': '10px'}),
                html.Div(id='carga-data-mongo'),  # Placeholder for upload feedback
                dcc.Store(id='stripe-tme-monthly-subs-store'),
                dcc.Store(id='stripe-tme-monthly-canceled-subs-store'),
                dcc.Store(id='stripe-tme-monthly-incomplete-subs-store'),
                dcc.Store(id='tgo-monthly-subs-store'),
                dcc.Store(id='tgo-monthly-canceled-subs-store'),
                dcc.Store(id='tgo-monthly-incomplete-subs-store'),
                dcc.Store(id='neto-stripe-tme-subs-store'),
                dcc.Store(id='neto-tgo-subs-store'),
                dcc.Store(id='stripe-creation-by-country-store'),
                dcc.Store(id='stripe-cancelation-by-country-store'),
                dcc.Store(id='succeeded-stripe-payments-store'),
                dcc.Store(id='total-stripe-recargas-per-month-store'),
                dcc.Store(id='mp-active-subs-per-plan-store'),
                dcc.Store(id='mp-payments-store'),
            ], style={**card_style, "width": "100%"}),
        ], style={"marginBottom": "20px", "display": 'flex'}),

        # Tarjetas de Métricas Resumen
        html.Div([
            html.Div([
                html.H3("Suscripciones Activas Actualmente", style={"color": colors['stripe'], "marginBottom": "15px"}),
                html.Div(id='subs-summary', style={"fontSize": "16px"})
            ], style={**metric_card_style, "borderTop": f"4px solid {colors['stripe']}"}),
            html.Div([
                html.H3("Ingresos último mes completo", style={"color": colors['primary'], "marginBottom": "15px"}),
                html.Div(id='ingresos-summary', style={"fontSize": "16px"})
            ], style={**metric_card_style, "borderTop": f"4px solid {colors['primary']}"}),
        ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between", "marginBottom": "20px"}),
            
        # Pestañas para organizar gráficos
        dcc.Tabs(id="tabs", value=None, 
                 children=[
            dcc.Tab(label='Vista General', 
                    value='tab-overview', style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(label='Stripe', 
                    value='tab-stripe', style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(label='MercadoPago', 
                    value='tab-mp', style=tab_style, selected_style=tab_selected_style),
        ], style={"marginBottom": "20px"}),
        # Contenido de las pestañas
        html.Div(id='tab-content')

    ], 
        style={
                "padding": "20px",
                "fontFamily": "Arial, sans-serif",
                "backgroundColor": colors['background'],
                "maxWidth": "1400px",
                "margin": "0 auto"
            }
    )
