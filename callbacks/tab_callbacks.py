# callbacks/tab_callbacks.py
from dash import Input, Output, html, dcc, State, no_update
from subs_metrics import SubscriptionMetrics
import base64, io
import traceback
import pandas as pd
import plotly.graph_objs as go
from style.styles import (
    colors,
    graph_card_style
)
from components.charts import (
    create_stacked_bar_chart,
    stripe_tme_subscriptions_chart,
    net_stripe_tme_subs_chart,
    plot_mp_planes,
    mp_monthly_subscriptions_chart,
    mp_net_subscriptions_chart,
    mp_unique_payments_per_month,
    income_mp_per_month,
    mp_subscription_payments_per_month,
    total_subscriptions_chart,
    net_subscriptions_chart,
    tgo_income_chart,
    tme_subs_income_chart,
    total_stripe_recargas_per_month_chart,
    total_income_chart
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

    # Callback para cargar datos de Mongo DB
    @app.callback(
        Output('stripe-tme-monthly-subs-store', 'data'),            
        Output('stripe-tme-monthly-canceled-subs-store', 'data'),
        Output('stripe-tme-monthly-incomplete-subs-store', 'data'),
        Output('tgo-monthly-subs-store', 'data'),
        Output('tgo-monthly-canceled-subs-store', 'data'),
        Output('tgo-monthly-incomplete-subs-store', 'data'),
        Output('stripe-creation-by-country-store', 'data'),
        Output('stripe-cancelation-by-country-store', 'data'),
        Output('succeeded-stripe-payments-store', 'data'),
        Output('total-stripe-recargas-per-month-store', 'data'),
        Output('mp-active-subs-per-plan-store', 'data'),
        Output('mp-payments-store', 'data'),
        Output('carga-data-mongo', 'children'), 
        Input('date-range', 'start_date'),
        Input('date-range', 'end_date'),    
        Input('load-mongo-button', 'n_clicks'),
        prevent_initial_call=True  # Evita la llamada inicial sin valor
    )
    def cargar_datos_mongo(start_date, end_date, n_clicks):
        if n_clicks is None or n_clicks == 0:
            # Retorna no_update para no actualizar nada inicialmente
            return [no_update] * 13
        # if n_clicks > 0:
        try:
                # CARGA DE DATOS DESDE MONGO DB
                
                #------------------------------------ STRIPE -------------------------------------------|
                # Suscripciones creadas/canceladas/incompletas de TME-Stripe
                stripe_tme_subs_per_month = metrics.get_stripe_subs_per_month(start_date, end_date)
                canceladas_tme_stripe_per_month = metrics.get_canceladas_stripe_per_month(start_date, end_date)
                incomplete_tme_stripe_per_month = metrics.get_incomplete_stripe_per_month(start_date, end_date)
                stripe_tme_subs_per_month = stripe_tme_subs_per_month.reset_index()
                canceladas_tme_stripe_per_month = canceladas_tme_stripe_per_month.reset_index()
                incomplete_tme_stripe_per_month = incomplete_tme_stripe_per_month.reset_index()
                # Suscripciones creadas/canceladas/incompletas de TGO-Stripe
                tgo_2025_subs_per_month, tgo_canceled_per_month, tgo_incomplete_per_month = metrics.get_tgo_subs(selector='Total')
                tgo_2025_subs_per_month = tgo_2025_subs_per_month.reset_index()
                tgo_canceled_per_month = tgo_canceled_per_month.reset_index()
                tgo_incomplete_per_month = tgo_incomplete_per_month.reset_index()
                # Suscripciones creadas/canceladas de TME- Stripe por país
                stripe_creation_data = metrics.get_stripe_creation_data(start_date, end_date)
                stripe_cancelation_data = metrics.get_stripe_cancelation_data (start_date, end_date)
                # Asignación de países
                stripe_creation_full = metrics.asign_countries(stripe_creation_data)
                stripe_cancelation_full = metrics.asign_countries(stripe_cancelation_data)
                # Cambio de nombre la columna de la fecha para que sea compatible con la función subs_all y agrego provider: stripe
                stripe_creation_full = stripe_creation_full.rename(columns={'timestamp': 'start_date'})
                stripe_cancelation_full = stripe_cancelation_full.rename(columns={'timestamp': 'start_date'}) 
                stripe_creation_full['provider'] = 'stripe'
                stripe_cancelation_full['provider'] = "stripe"
                monthly_stripe_subs_by_country = metrics.subs_all(stripe_creation_full, group_by='month', country="all", provider="stripe")
                monthly_cancel_stripe_by_country = metrics.subs_all(stripe_cancelation_full, group_by='month', country="all", provider="stripe")

                # Ingresos de Stripe
                succeeded_stripe_payments = metrics.get_stripe_succeeded_subscription_payments(start_date, end_date)
                total_stripe_recargas_per_month = metrics.get_stripe_succeeded_extra_credit_payments(start_date, end_date)
                
                #-------------------------------- MERCADO PAGO ------------------------------------------|
                # Suscripciones  authorized por cada Plan de MP 
                mp_active_subs_per_plan = metrics.get_mp_planes()

                # Pagos de MP
                all_mp_payments = metrics.get_mp_payments(start_date, end_date)

                # Guardamos como dict para dcc.Store
                return (stripe_tme_subs_per_month.to_dict('records'), 
                        canceladas_tme_stripe_per_month.to_dict('records'),
                        incomplete_tme_stripe_per_month.to_dict('records'),
                        tgo_2025_subs_per_month.to_dict('records'),
                        tgo_canceled_per_month.to_dict('records'),
                        tgo_incomplete_per_month.to_dict('records'),
                        monthly_stripe_subs_by_country.to_dict('records'),
                        monthly_cancel_stripe_by_country.to_dict('records'),
                        succeeded_stripe_payments.to_dict('records'),
                        total_stripe_recargas_per_month.to_dict('records'),
                        mp_active_subs_per_plan.to_dict('records'),
                        all_mp_payments.to_dict('records'),
                        f"Datos cargados desde MongoDB correctamente")
        except Exception as e:
            print(f"Error en callback: {e}")
            print("Traceback completo:")
            traceback.print_exc()  # Esto imprime el stacktrace detallado
            return ([], [], [], [], [], [], [], [], [], [], [], [], f"Error al cargar: {str(e)}")

    # Callback para renderizar los charts
    @app.callback(
        Output('tab-content', 'children'),
        Input('tabs', 'value'),
        State('mp-data-store', 'data'),
        State('stripe-tme-monthly-subs-store', 'data'),
        State('stripe-tme-monthly-canceled-subs-store', 'data'),
        State('stripe-tme-monthly-incomplete-subs-store', 'data'),
        State('tgo-monthly-subs-store', 'data'),
        State('tgo-monthly-canceled-subs-store', 'data'),   
        State('tgo-monthly-incomplete-subs-store', 'data'),
        State('stripe-creation-by-country-store', 'data'),
        State('stripe-cancelation-by-country-store', 'data'),
        State('succeeded-stripe-payments-store', 'data'),
        State('total-stripe-recargas-per-month-store', 'data'),
        State('mp-active-subs-per-plan-store', 'data'),
        State('mp-payments-store', 'data'),
        prevent_initial_call=True
    )
    def render_tab_content(tab, mp_csv_data, stripe_tme_subs_per_month,
                           canceladas_tme_stripe_per_month, incomplete_tme_stripe_per_month,
                           tgo_2025_subs_per_month, tgo_canceled_per_month,
                           tgo_incomplete_per_month, monthly_stripe_subs_by_country, 
                           monthly_cancel_stripe_by_country, succeeded_stripe_payments, 
                           total_stripe_recargas_per_month, mp_active_subs_per_plan, all_mp_payments):
        # Carga de datos del csv de MP
        mp_monthly_data = metrics.process_mp_subscriptions_data(mp_csv_data)
            
        # Carga de datos de MongoDB de los store
        mp_active_subs_per_plan = pd.DataFrame(mp_active_subs_per_plan)
        all_mp_payments = pd.DataFrame(all_mp_payments)
        stripe_tme_subs_per_month = pd.DataFrame(stripe_tme_subs_per_month)
        canceladas_tme_stripe_per_month = pd.DataFrame(canceladas_tme_stripe_per_month)
        incomplete_tme_stripe_per_month = pd.DataFrame(incomplete_tme_stripe_per_month)
        tgo_2025_subs_per_month = pd.DataFrame(tgo_2025_subs_per_month)
        tgo_canceled_per_month = pd.DataFrame(tgo_canceled_per_month)
        tgo_incomplete_per_month = pd.DataFrame(tgo_incomplete_per_month)
        monthly_stripe_subs_by_country = pd.DataFrame(monthly_stripe_subs_by_country)
        monthly_cancel_stripe_by_country = pd.DataFrame(monthly_cancel_stripe_by_country)
        succeeded_stripe_payments = pd.DataFrame(succeeded_stripe_payments)
        total_stripe_recargas_per_month = pd.DataFrame(total_stripe_recargas_per_month)
            
        # Conversión de las columnas de fecha a datetime y seteo como índice
        stripe_tme_subs_per_month['timestamp'] = pd.to_datetime(stripe_tme_subs_per_month['timestamp'])
        stripe_tme_subs_per_month = stripe_tme_subs_per_month.set_index('timestamp')                       
        canceladas_tme_stripe_per_month['timestamp'] = pd.to_datetime(canceladas_tme_stripe_per_month['timestamp'])
        canceladas_tme_stripe_per_month = canceladas_tme_stripe_per_month.set_index('timestamp')
        incomplete_tme_stripe_per_month['timestamp'] = pd.to_datetime(incomplete_tme_stripe_per_month['timestamp'])
        incomplete_tme_stripe_per_month = incomplete_tme_stripe_per_month.set_index('timestamp')
        tgo_2025_subs_per_month['created'] = pd.to_datetime(tgo_2025_subs_per_month['created'])
        tgo_2025_subs_per_month = tgo_2025_subs_per_month.set_index('created')
        tgo_canceled_per_month['ended_at'] = pd.to_datetime(tgo_canceled_per_month['ended_at'])
        tgo_canceled_per_month = tgo_canceled_per_month.set_index('ended_at')
        tgo_incomplete_per_month['ended_at'] = pd.to_datetime(tgo_incomplete_per_month['ended_at'])
        tgo_incomplete_per_month = tgo_incomplete_per_month.set_index('ended_at')
        # Cálculo de neto
        neto_stripe_tme_subs = (
            stripe_tme_subs_per_month["count"]
            - canceladas_tme_stripe_per_month["count"]
            - incomplete_tme_stripe_per_month["count"]
        )
        neto_tgo = (
            tgo_2025_subs_per_month["count"]
            .sub(tgo_canceled_per_month["count"], fill_value=0)
            .sub(tgo_incomplete_per_month["count"], fill_value=0)
        )

        # Contenido para cada pestaña
        if tab == 'tab-overview':
            # Total
            total_df = metrics.get_totales_por_mes(mp_monthly_data,stripe_tme_subs_per_month,
                                               canceladas_tme_stripe_per_month, 
                                               incomplete_tme_stripe_per_month,
                                               tgo_2025_subs_per_month, 
                                               tgo_canceled_per_month,
                                               tgo_incomplete_per_month)
        
            # Búsqueda de subs en Mongo
            raw_data = metrics.get_subs_data()
            # Asignación de países según el user_id
            data_with_countries = metrics.asign_countries(raw_data)
            # Asignando provider: "mp" a las suscripciones en MP sin provider
            full_data = metrics.assign_provider_default(data_with_countries)
            active_subs_df = metrics.subs_all(full_data, status=["active", "authorized"], provider = "all", country="all", source = "all").groupby(['provider', 'country'])['count'].sum().reset_index()
            inactive_subs = metrics.subs_all(full_data, provider = "all", status=["paused", "incomplete", "past_due"], country="all", source="all").groupby(['status', 'country'])['count'].sum().reset_index()
            
            # Gráfico de suscripciones totales
            fig_total_subs = total_subscriptions_chart(total_df)
            fig_net_subs = net_subscriptions_chart(total_df)

            # Ingresos Totales
            total = metrics.total_income(all_mp_payments, succeeded_stripe_payments, total_stripe_recargas_per_month)
            total_income_fig = total_income_chart(total)
            
            # Gráfico de estado de las suscripciones en general
            # Suscriptores activos por país actualmente
            fig_active_subs = create_stacked_bar_chart(
                data_df = active_subs_df, x = "provider", y = "count", stack_column = 'country',
                title="Suscripciones Activas por país (TME)", x_label="Plataforma", y_label="Cantidad", bar_width_days=0.4
            )

            # Suscriptores inactivos por país actualmente
            fig_inactive_subs = create_stacked_bar_chart(
                data_df = inactive_subs, x = "status", y = "count", stack_column = 'country',
                title="Suscripciones con problemas de pago (TME)", x_label="Status", y_label="Cantidad", bar_width_days=0.4
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
                        dcc.Graph(figure=total_income_fig)
                    ], style=graph_card_style),
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
            # ----------------------------- GRAFICOS DE STRIPE ------------------------------
            # TME Stripe subs creadas/canceladas/incompletas por mes
            fig_monthly_stripe_all = stripe_tme_subscriptions_chart(stripe_tme_subs_per_month,
                                                                    canceladas_tme_stripe_per_month,
                                                                    incomplete_tme_stripe_per_month,
                                                                    title=f"Stripe TranscribeMe Subscriptions")
            # TME Stripe subs netas por mes
            print (neto_stripe_tme_subs)
            fig_monthly_stripe_balance = net_stripe_tme_subs_chart(neto_stripe_tme_subs, 
                                                               title=f"Net Stripe TranscribeMe Subscriptions")
            # TME Stripe subs creadas por país
            fig_stripe_monthly = create_stacked_bar_chart(
                data_df=monthly_stripe_subs_by_country, stack_column = "country",
                title="Stripe TranscribeMe Created Subscriptions", x_label="Mes", y_label="Cantidad")

            # TME Stripe subs canceladas por país
            fig_monthly_stripe_cancel = create_stacked_bar_chart(
                data_df=monthly_cancel_stripe_by_country, stack_column = "country",
                title="Stripe TranscribeMe Canceled Subscriptions", x_label="Fecha", y_label="Cantidad")

            # TGO subs creadas/canceladas/incompletas por mes
            tgo_subs_chart = stripe_tme_subscriptions_chart(tgo_2025_subs_per_month, tgo_canceled_per_month, 
                                                        tgo_incomplete_per_month, 
                                                        title=None)
            # TGO subs netas por mes
            print (neto_tgo)
            tgo_net_chart = net_stripe_tme_subs_chart(neto_tgo, title=None)

            # Recargas de Stripe (TOTAL)
            recargas_stripe_fig = total_stripe_recargas_per_month_chart(total_stripe_recargas_per_month)

            # Ingresos Suscripciones - TGO
            tgo_income_fig = tgo_income_chart (succeeded_stripe_payments, selector = 'Total')

            # Ingresos Suscripciones - TME
            tme_subs_income_fig = tme_subs_income_chart (succeeded_stripe_payments, selector = 'Total')
            
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
                        html.H3("Stripe TranscribeGo Subscriptions", style={'textAlign': 'center'}), 
                        dcc.RadioItems(id = 'tgo-subs-selector', 
                                       options = ['Total', 'Plan Basic', 'Plan Plus','Plan Business'], 
                                       value = 'Total', inline=True, 
                                       labelStyle={'margin-right': '20px'}, 
                                       style={'marginTop': '10px', 'textAlign': 'center'}), 
                        dcc.Graph(figure=tgo_subs_chart, id = 'tgo-subs')
                    ], style=graph_card_style),
                    html.Div([
                        html.H3("Net Stripe TranscribeGo Subscriptions", style={'textAlign': 'center'}), 
                        dcc.Graph(figure=tgo_net_chart, id = 'tgo-net-subs')
                    ], style=graph_card_style),
                ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),
                html.Div([
                    html.Div([
                        html.H3("TranscribeGo Income", style={'textAlign': 'center'}), 
                        dcc.RadioItems(id = 'tgo-income-selector', 
                                       options = ['Total', 'Plan Basic', 'Plan Plus',
                                                  'Plan Business'], 
                                       value = 'Total', inline=True, 
                                       labelStyle={'margin-right': '20px'}, 
                                       style={'marginTop': '10px', 'textAlign': 'center'}), 
                        dcc.Graph(figure=tgo_income_fig, id = 'tgo-income')
                    ], style=graph_card_style),
                    html.Div([
                        html.H3("Ingresos por recargas", style={'textAlign': 'center'}), 
                        dcc.Graph(figure=recargas_stripe_fig)
                    ], style=graph_card_style),
                ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),
                html.Div([
                    html.Div([
                        html.H3("TranscribeMe Subscriptions Income", style={'textAlign': 'center'}), 
                        dcc.RadioItems(id = 'tme-subs-income-selector', 
                                       options = ['Total','Plus RoW', 'Telegram', 'Plus US / ESP', 
                                                  'Plus RoW Anual', 'Plus US / ESP Anual'], 
                                       value = 'Total', inline=True, 
                                       labelStyle={'margin-right': '20px'}, 
                                       style={'marginTop': '10px', 'textAlign': 'center'}), 
                        dcc.Graph(figure=tme_subs_income_fig, id = 'tme-subs-income')
                    ], style=graph_card_style),
                ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"})
            ])
    
        elif tab == 'tab-mp':
            # ---------------- GRAFICOS DE MERCADO PAGO ------------------------------
            # TME MP creadas/canceladas por mes
            fig_subs_mp = mp_monthly_subscriptions_chart(mp_monthly_data)

            # TME MP netas por mes
            fig_subs_neto_mp = mp_net_subscriptions_chart(mp_monthly_data)
            
            # Status suscripciones de MP por plan
            fig_mp_active_plans = plot_mp_planes(mp_active_subs_per_plan)
            
            # Pagos por suscripciones MP por mes 
            fig_mp_subs_payments_per_month = mp_subscription_payments_per_month(all_mp_payments)
            
            # Pagos únicos por mes (recargas + mp-discount)
            fig_unique_mp_payments_per_month = mp_unique_payments_per_month(all_mp_payments)

            # Ingresos MP por mes
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
                        html.H3("Ingresos Mercado Pago (ARS)", style={'textAlign': 'center'}), 
                        dcc.RadioItems(id = 'mp-income-selector', 
                                       options = ['Total', 'Suscripciones', 'Plan de 3 meses',
                                                  'Recargas de tokens', 'Recargas de minutos'], 
                                       value = 'Total', inline=True, 
                                       labelStyle={'margin-right': '20px'}, 
                                       style={'marginTop': '10px', 'textAlign': 'center'}), 
                        dcc.Graph(figure=fig_income_mp_per_month, id = 'ingresos-mp')
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
    
    # Callback del chart de Ingresos de MP
    @app.callback(
        Output('ingresos-mp', 'figure'),
        Input('date-range', 'start_date'),
        Input('date-range', 'end_date'),
        Input('mp-income-selector', 'value')
    )
    def update_mp_income(start_date, end_date, selector):
        all_mp_payments = metrics.get_mp_payments(start_date, end_date)
        fig = income_mp_per_month(all_mp_payments, selector)
        return fig

    # Callback del chart de Planes de TGO
    @app.callback(
        Output('tgo-subs', 'figure'),
        Output('tgo-net-subs', 'figure'),
        Input('tgo-subs-selector', 'value')
    )
    def update_tgo_planes(selector):
        tgo_2025_subs_per_month, tgo_canceled_per_month, tgo_incomplete_per_month = metrics.get_tgo_subs(selector)
        # Cálculo de neto
        neto_tgo = (
            tgo_2025_subs_per_month["count"]
            .sub(tgo_canceled_per_month["count"], fill_value=0)
            .sub(tgo_incomplete_per_month["count"], fill_value=0)
        )
        tgo_subs_chart = stripe_tme_subscriptions_chart(tgo_2025_subs_per_month, tgo_canceled_per_month, 
                                                        tgo_incomplete_per_month, 
                                                        title=None)
        tgo_net_chart = net_stripe_tme_subs_chart(neto_tgo, title=None)
        return tgo_subs_chart, tgo_net_chart
    
    # Callback TGO Income
    @app.callback(
        Output('tgo-income', 'figure'),
        Input('tgo-income-selector', 'value'),
        Input('date-range', 'start_date'),
        Input('date-range', 'end_date'),  
    )
    def update_tgo_income(selector, start_date, end_date):
        succeeded_stripe_payments = metrics.get_stripe_succeeded_subscription_payments(start_date, end_date)
        tgo_income_fig = tgo_income_chart (succeeded_stripe_payments, selector)
        return tgo_income_fig

    # Callback TME Income
    @app.callback(
        Output('tme-subs-income', 'figure'),
        Input('tme-subs-income-selector', 'value'),
        Input('date-range', 'start_date'),
        Input('date-range', 'end_date'),  
    )
    def update_tme_income(selector, start_date, end_date):
        succeeded_stripe_payments = metrics.get_stripe_succeeded_subscription_payments(start_date, end_date)
        tme_subs_income_fig = tme_subs_income_chart (succeeded_stripe_payments, selector)
        return tme_subs_income_fig
