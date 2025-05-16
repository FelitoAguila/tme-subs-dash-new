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
        # Búsqueda de subs en Mongo
        raw_data = metrics.get_data(start_date, end_date)

        # Asignación de países según el user_id
        data_with_countries = metrics.asign_countries(raw_data)

        # Asignando provider: "mp" a las suscripciones en MP sin provider
        full_data = metrics.assign_provider_default(data_with_countries)

        # Métricas de las tarjetas de la main page
        total_subs = metrics.subs_all(full_data)['count'].sum()
        total_stripe_subs = metrics.subs_all(full_data, provider="stripe")['count'].sum()
        total_mp_subs = metrics.subs_all(full_data, provider = ["mp", "mp_discount", "free", "manual"])['count'].sum()
        total_active_subs = metrics.subs_all(full_data, status=["active", "authorized"])['count'].sum()
        active_stripe_subs = metrics.subs_all(full_data, status="active", provider = "stripe")['count'].sum()
        authorized_mp_subs = metrics.subs_all(full_data, status="authorized", provider = "mp")['count'].sum()
        

        return (
            html.Div([
                html.Div([
                    html.Span("Total: ", style={"fontWeight": "bold"}),
                    html.Span(f"{total_subs}", style={"fontSize": "24px", "color": colors['primary']})
                ], style={"marginBottom": "10px"}),
                html.Div([
                    html.Span("Stripe: ", style={"fontWeight": "bold"}),
                    html.Span(f"{total_stripe_subs}")
                ], style={"marginBottom": "5px"}),
                html.Div([
                    html.Span("Mercado Pago: ", style={"fontWeight": "bold"}),
                    html.Span(f"{total_mp_subs}")
                ])
            ]),
            html.Div([
                html.Div([
                    html.Span("Total: ", style={"fontWeight": "bold"}),
                    html.Span(f"{total_active_subs}", style={"fontSize": "24px", "color": colors['stripe']})
                ], style={"marginBottom": "10px"}),
                html.Div([
                    html.Span("Stripe: ", style={"fontWeight": "bold"}),
                    html.Span(f"{active_stripe_subs}")
                ], style={"marginBottom": "5px"}),
                html.Div([
                    html.Span("Mercado Pago: ", style={"fontWeight": "bold"}),
                    html.Span(f"{authorized_mp_subs}")
                ])
            ])
        )
