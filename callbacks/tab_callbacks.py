# callbacks/tab_callbacks.py
from dash import Input, Output, html, dcc, State, no_update
from subs_metrics import SubscriptionMetrics
import base64, io
import pandas as pd
import plotly.graph_objs as go
from style.styles import (
    colors,
    graph_card_style
)
from components.charts import (
    create_stacked_bar_chart,
    plot_subscription_balance,
    plot_monthly_creations_cancellations,
    stripe_tme_subscriptions_chart,
    net_stripe_tme_subs_chart,
    plot_mp_planes,
    mp_monthly_subscriptions_chart,
    mp_net_subscriptions_chart,
    mp_unique_payments_per_month,
    income_mp_per_month,
    mp_subscription_payments_per_month,
    total_subscriptions_chart,
    net_subscriptions_chart
)


metrics = SubscriptionMetrics()

def register_tab_callbacks(app):
    # Callback para cargar el archivo de MP
    @app.callback(
        Output('mp-data-store', 'data'),
        Output('output-data-upload', 'children'),
        Input('upload-data', 'contents'),
        State('upload-data', 'filename')
    )
    def handle_upload(contents, filename):
        if contents is None:
            return no_update, ""
    
        try:
            # contents viene como "data:<mime>;base64,<contenido>"
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
        
            # Convertimos a DataFrame
            if filename.endswith('.csv'):
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            else:
                return no_update, "Formato no soportado"
        
            # Guardamos como dict para dcc.Store
            return df.to_dict('records'), f"Archivo '{filename}' cargado correctamente. {len(df)} filas."
    
        except Exception as e:
            return no_update, f"Error al procesar el archivo: {str(e)}"



    # Callback para renderizar los charts
    @app.callback(
        Output('tab-content', 'children'),
        Input('tabs', 'value'),
        Input('date-range', 'start_date'),
        Input('date-range', 'end_date'),
        State('mp-data-store', 'data')
    )
    def render_tab_content(tab, start_date, end_date, mp_csv_data):
        # Carga de datos de Stripe
        stripe_tme_subs_per_month = metrics.get_stripe_subs_per_month()
        canceladas_tme_stripe_per_month = metrics.get_canceladas_stripe_per_month()
        incomplete_tme_stripe_per_month = metrics.get_incomplete_stripe_per_month()
        neto_stripe_tme_subs = (
                stripe_tme_subs_per_month["count"]
                - canceladas_tme_stripe_per_month["count"]
                - incomplete_tme_stripe_per_month["count"]
        )

        tgo_2025_subs_per_month, tgo_canceled_per_month, tgo_incomplete_per_month = metrics.get_tgo_subs()
        neto_tgo = (
                tgo_2025_subs_per_month["count"]
                - tgo_canceled_per_month["count"]
                - tgo_incomplete_per_month["count"]
        )

        # Carga de datos de MP
        mp_monthly_data = metrics.process_mp_subscriptions_data(mp_csv_data)
        
        # Total
        total_df = metrics.get_totales_por_mes(mp_monthly_data,stripe_tme_subs_per_month,
                                               canceladas_tme_stripe_per_month, 
                                               incomplete_tme_stripe_per_month,
                                               tgo_2025_subs_per_month, 
                                               tgo_canceled_per_month,
                                               tgo_incomplete_per_month)
        
        # Contenido para cada pestaña
        if tab == 'tab-overview':
            # Búsqueda de subs en Mongo
            raw_data = metrics.get_subs_data(start_date, end_date)
            # Asignación de países según el user_id
            data_with_countries = metrics.asign_countries(raw_data)
            # Asignando provider: "mp" a las suscripciones en MP sin provider
            full_data = metrics.assign_provider_default(data_with_countries)
            # Monthly subs por países
            monthly_subs_by_country = metrics.subs_all(full_data, group_by='month', country="all")
            # Status de suscripciones en general
            active_subs = metrics.get_active_subs_data()
            active_subs_with_countries = metrics.asign_countries(active_subs)
            full_active_subs = metrics.assign_provider_default(active_subs_with_countries)
            active_subs_df = metrics.subs_all(full_active_subs, status=["active", "authorized"], provider = "all", country="all", source = "all").groupby(['provider', 'country'])['count'].sum().reset_index()
            inactive_subs = metrics.subs_all(full_data, provider = "all", status=["paused", "incomplete", "past_due"], country="all", source="all").groupby(['status', 'country'])['count'].sum().reset_index()
            
            # Gráfico de suscripciones totales
            fig_total_subs = total_subscriptions_chart(total_df)
            fig_net_subs = net_subscriptions_chart(total_df)
            
            # Gráfico de estado de las suscripciones en general
            # Suscriptores activos por país actualmente
            fig_active_subs = create_stacked_bar_chart(
                data_df = active_subs_df, x = "provider", y = "count", stack_column = 'country',
                title="Suscripciones Activas por país", x_label="Plataforma", y_label="Cantidad", bar_width_days=0.4
            )

            # Suscriptores inactivos por país actualmente
            fig_inactive_subs = create_stacked_bar_chart(
                data_df = inactive_subs, x = "status", y = "count", stack_column = 'country',
                title="Status de las suscripciones inactivas", x_label="Status", y_label="Cantidad", bar_width_days=0.4
            )
            
            return html.Div([
                html.Div([
                    html.Div([
                        dcc.Graph(figure=fig_total_subs)
                    ], style=graph_card_style),
                    html.Div([
                        dcc.Graph(figure=fig_net_subs)
                    ], style=graph_card_style)
                ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),
                html.Div([
                    html.Div([
                        dcc.Graph(figure=fig_active_subs)
                    ], style=graph_card_style),
                    html.Div([
                        dcc.Graph(figure=fig_inactive_subs)
                    ], style=graph_card_style),
                ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),    
            ])
    
        elif tab == 'tab-stripe':
            # Gráficos
            fig_monthly_stripe_all = stripe_tme_subscriptions_chart(stripe_tme_subs_per_month,
                                                                    canceladas_tme_stripe_per_month,
                                                                    incomplete_tme_stripe_per_month,
                                                                    title=f"Stripe TranscribeMe Subscriptions")

            fig_monthly_stripe_balance = net_stripe_tme_subs_chart(neto_stripe_tme_subs, 
                                                               title=f"Net Stripe TranscribeMe Subscriptions")
            
            # Busqueda de Stripe TME subs en Mongo DB
            stripe_cancelation_data = metrics.get_stripe_cancelation_data (start_date, end_date)
            stripe_creation_data = metrics.get_stripe_creation_data(start_date, end_date)
            # Stripe TME subs por país
            stripe_creation_full = metrics.asign_countries(stripe_creation_data)
            stripe_cancelation_full = metrics.asign_countries(stripe_cancelation_data)
            # Cambio de nombre la columna de la fecha para que sea compatible con la función subs_all y agrego provider: stripe
            stripe_creation_full = stripe_creation_full.rename(columns={'timestamp': 'start_date'})
            stripe_cancelation_full = stripe_cancelation_full.rename(columns={'timestamp': 'start_date'}) 
            stripe_creation_full['provider'] = 'stripe'
            stripe_cancelation_full['provider'] = "stripe"
            monthly_stripe_subs_by_country = metrics.subs_all(stripe_creation_full, group_by='month', country="all", provider="stripe")
            monthly_cancel_stripe_by_country = metrics.subs_all(stripe_cancelation_full, group_by='month', country="all", provider="stripe")
            fig_stripe_monthly = create_stacked_bar_chart(
                data_df=monthly_stripe_subs_by_country, stack_column = "country",
                title="Stripe TranscribeMe Created Subscriptions", x_label="Mes", y_label="Cantidad"
            )
            fig_monthly_stripe_cancel = create_stacked_bar_chart(
                data_df=monthly_cancel_stripe_by_country, stack_column = "country",
                title="Stripe TranscribeMe Canceled Subscriptions", x_label="Fecha", y_label="Cantidad"
            )

            # TGO 
            tgo_subs_chart = stripe_tme_subscriptions_chart(tgo_2025_subs_per_month, tgo_canceled_per_month, 
                                                        tgo_incomplete_per_month, 
                                                        title=f"Stripe TranscribeGo Subscriptions")
            tgo_net_chart = net_stripe_tme_subs_chart(neto_tgo, title=f"Net Stripe TranscribeGo Subscriptions")
            
            return html.Div([
                html.Div([
                    html.Div([
                        dcc.Graph(figure=fig_monthly_stripe_all)
                    ], style=graph_card_style),
                    html.Div([
                        dcc.Graph(figure=fig_monthly_stripe_balance)
                    ], style=graph_card_style),
                ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),
                html.Div([
                    html.Div([
                        dcc.Graph(figure=fig_stripe_monthly)
                    ], style=graph_card_style),
                    html.Div([
                        dcc.Graph(figure=fig_monthly_stripe_cancel)
                    ], style=graph_card_style),
                ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),
                html.Div([
                    html.Div([
                        dcc.Graph(figure=tgo_subs_chart)
                    ], style=graph_card_style),
                    html.Div([
                        dcc.Graph(figure=tgo_net_chart)
                    ], style=graph_card_style),
                ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),
            ])
    
        elif tab == 'tab-mp':
            # Gráficos de suscripciones de MP
            fig_subs_mp = mp_monthly_subscriptions_chart(mp_monthly_data)
            fig_subs_neto_mp = mp_net_subscriptions_chart(mp_monthly_data)
            
            # Status suscripciones de MP
            mp_active_subs_per_plan = metrics.get_mp_planes()
            fig_mp_active_plans = plot_mp_planes(mp_active_subs_per_plan)
            
            # INGRESOS
            # Pagos únicos
            all_mp_payments = metrics.get_mp_payments(start_date, end_date)
            fig_unique_mp_payments_per_month = mp_unique_payments_per_month(all_mp_payments)
            fig_mp_subs_payments_per_month = mp_subscription_payments_per_month(all_mp_payments)
            fig_income_mp_per_month = income_mp_per_month(all_mp_payments)
            
            return html.Div([
                # Suscripciones creadas y canceladas
                html.Div([
                    html.Div([
                        dcc.Graph(figure=fig_subs_mp)
                    ], style=graph_card_style),
                    html.Div([
                        dcc.Graph(figure=fig_subs_neto_mp)
                    ], style=graph_card_style),
                ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),

                # Pagos MP
                html.Div([
                    # Pagos de suscripciones por mes
                    html.Div([
                        dcc.Graph(figure=fig_mp_subs_payments_per_month)
                    ], style=graph_card_style),
                    # Pagos únicos por mes
                    html.Div([
                        dcc.Graph(figure=fig_unique_mp_payments_per_month)
                    ], style=graph_card_style),
                ],style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),

                # Ingresos Totales MP
                html.Div([
                    html.Div([
                        dcc.Graph(figure=fig_income_mp_per_month)
                    ], style=graph_card_style),
                ],style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),

                #Nueva sección para los pagos por 3 meses
                html.Div([
                    # Tipos de planes MP
                    html.Div([
                        dcc.Graph(figure=fig_mp_active_plans)
                    ], style=graph_card_style),
                ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),
            ])
      
