# callbacks/summary_callbacks.py

from dash import Input, Output, html
from components.charts import colors  # usamos colores en los estilos
from subs_metrics import SubscriptionMetrics

metrics = SubscriptionMetrics()

def register_summary_callbacks(app):
    @app.callback(
        Output('subs-summary', 'children'),
        Output('ingresos-summary', 'children'),
        Input('dollar-value', 'value')
    )
    def update_summary_metrics(dolar_value):
        if dolar_value == "No se pudo extraer el valor del dólar, ingrese manualmente":
            dolar_value = 1200

        # Métricas suscripciones
        active_stripe_subs = metrics.get_total_active_stripe_subs()
        authorized_mp_subs = metrics.get_total_active_mp_subs()
        total_active_subs = active_stripe_subs + authorized_mp_subs

        # Métricas de ingresos
        ingresos_mp = round (metrics.get_mp_income(),2)
        ingresos_stripe=round(metrics.get_stripe_income(),2)
        total_ingresos = round(ingresos_mp/dolar_value + ingresos_stripe, 2)

        return (
            html.Div([
                html.Div([
                    html.Span("Total: ", style={"fontWeight": "bold"}),
                    html.Span(f"{total_active_subs}", style={"fontSize": "24px", "color": colors['primary']})
                ], style={"marginBottom": "10px"}),
                html.Div([
                    html.Span("Stripe: ", style={"fontWeight": "bold"}),
                    html.Span(f"{active_stripe_subs}")
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
                    html.Span("Stripe: ", style={"fontWeight": "bold"}),
                    html.Span(f"{ingresos_stripe} USD (placeholder)")
                ], style={"marginBottom": "5px"}),
                html.Div([
                    html.Span("Mercado Pago: ", style={"fontWeight": "bold"}),
                    html.Span(f"{ingresos_mp} ARS")
                ])
            ])
        )
