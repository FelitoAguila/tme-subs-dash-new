# callbacks/summary_callbacks.py

from dash import Input, Output, html
from components.charts import colors  # usamos colores en los estilos
from subs_metrics import SubscriptionMetrics

metrics = SubscriptionMetrics()

def register_summary_callbacks(app):
    @app.callback(
        Output('total-subs-summary', 'children'),
        Output('stripe-subs-summary', 'children'),
        Input('date-range', 'start_date'),
        Input('date-range', 'end_date')
    )
    def update_summary_metrics(start_date, end_date):
        total = metrics.total_subs(start_date, end_date)
        total_stripe = metrics.total_stripe_subs(start_date, end_date)
        total_active = metrics.total_active_subs()
        active_stripe = metrics.active_stripe_subs()
        authorized_mp = metrics.authorized_mp_subs()
        total_mp = metrics.total_mp_subs(start_date, end_date)

        return (
            html.Div([
                html.Div([
                    html.Span("Total: ", style={"fontWeight": "bold"}),
                    html.Span(f"{total}", style={"fontSize": "24px", "color": colors['primary']})
                ], style={"marginBottom": "10px"}),
                html.Div([
                    html.Span("Stripe: ", style={"fontWeight": "bold"}),
                    html.Span(f"{total_stripe}")
                ], style={"marginBottom": "5px"}),
                html.Div([
                    html.Span("Mercado Pago: ", style={"fontWeight": "bold"}),
                    html.Span(f"{total_mp}")
                ])
            ]),
            html.Div([
                html.Div([
                    html.Span("Total: ", style={"fontWeight": "bold"}),
                    html.Span(f"{total_active}", style={"fontSize": "24px", "color": colors['stripe']})
                ], style={"marginBottom": "10px"}),
                html.Div([
                    html.Span("Stripe: ", style={"fontWeight": "bold"}),
                    html.Span(f"{active_stripe}")
                ], style={"marginBottom": "5px"}),
                html.Div([
                    html.Span("Mercado Pago: ", style={"fontWeight": "bold"}),
                    html.Span(f"{authorized_mp}")
                ])
            ])
        )
