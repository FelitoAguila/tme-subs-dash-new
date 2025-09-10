# callbacks/summary_callbacks.py

from dash import Input, Output, html
from components.charts import colors  # usamos colores en los estilos
from subs_metrics import SubscriptionMetrics

metrics = SubscriptionMetrics()

def register_summary_callbacks(app):
    @app.callback(
        Output('dollar-value', 'value'),
        Input('get-dollar-value-button', 'n_clicks'),
        prevent_initial_call=True  # Evita la llamada inicial sin valor
    )
    def fetch_dollar_value(n_clicks):
        if n_clicks > 0:
            try:
                dolar_value = metrics.get_dolar_argentina()
                return dolar_value
            except Exception as e:
                print(f"Error fetching dollar value: {e}")
                return "No se pudo extraer el valor del dólar, ingrese manualmente"
        return ""


    @app.callback(
        Output('subs-summary', 'children'),
        Output('ingresos-summary', 'children'),
        Input('dollar-value', 'value'),
        prevent_initial_call=True  # Evita la llamada inicial sin valor
    )
    def update_summary_metrics(dolar_value):
        
        # Métricas suscripciones
        active_tme_stripe_subs = metrics.get_tme_active_stripe_subs()
        active_tgo_stripe_subs = metrics.get_tgo_active_stripe_subs()
        authorized_mp_subs = metrics.get_total_active_mp_subs()
        total_active_subs = active_tme_stripe_subs + active_tgo_stripe_subs + authorized_mp_subs

        # Métricas de ingresos
        ingresos_mp = round (metrics.get_last_month_mp_income(),2)
        ingresos_stripe=round(metrics.get_last_month_stripe_income(),2)
        total_ingresos = round(ingresos_mp/dolar_value + ingresos_stripe, 2)

        return (
            html.Div([
                html.Div([
                    html.Span("Total: ", style={"fontWeight": "bold"}),
                    html.Span(f"{total_active_subs}", style={"fontSize": "24px", "color": colors['primary']})
                ], style={"marginBottom": "10px"}),
                html.Div([
                    html.Span("Stripe TranscribeMe: ", style={"fontWeight": "bold"}),
                    html.Span(f"{active_tme_stripe_subs}")
                ], style={"marginBottom": "5px"}),
                html.Div([
                    html.Span("Stripe TranscribeGo: ", style={"fontWeight": "bold"}),
                    html.Span(f"{active_tgo_stripe_subs}")
                ], style={"marginBottom": "5px"}),
                html.Div([
                    html.Span("Mercado Pago: ", style={"fontWeight": "bold"}),
                    html.Span(f"{authorized_mp_subs}")
                ])
            ]),
            html.Div([
                html.Div([
                    html.Span("Total: ", style={"fontWeight": "bold"}),
                    html.Span(f"{total_ingresos} USD", style={"fontSize": "24px", "color": colors['stripe']})
                ], style={"marginBottom": "10px"}),
                html.Div([
                    html.Span("Stripe TranscribeMe: ", style={"fontWeight": "bold"}),
                    html.Span(f"{ingresos_stripe} USD")
                ], style={"marginBottom": "5px"}),
                html.Div([
                    html.Span("Mercado Pago: ", style={"fontWeight": "bold"}),
                    html.Span(f"{ingresos_mp} ARS")
                ])
            ])
        )
