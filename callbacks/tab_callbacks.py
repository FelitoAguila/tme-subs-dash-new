# callbacks/tab_callbacks.py
from fileinput import filename
from importlib.resources import contents
from dash import Input, Output, html, dcc, State, no_update, dash_table
from subs_metrics import SubscriptionMetrics
import base64, io
import traceback
import pandas as pd
import plotly.graph_objs as go
from style.styles import (
    colors, card_style, metric_card_style, graph_card_style,
    tab_style, tab_selected_style
)
from components.stripe_revenue_recovery_charts import *
from components.airtable import map_fig, expired_per_day_fig, total_funnel_fig
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
    total_income_chart,
    plot_tgo_onboardings,
    table_tgo_onboardings
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
    def handle_upload(contents, filenames):
        if contents is None:
            return no_update, ""
        
        # contents y filenames son listas si multiple=True
        dataframes = []
    
        try:
            for content, filename in zip(contents, filenames):
                if not filename.endswith('.csv'):
                    return no_update, f"Formato no soportado para '{filename}'. Solo CSV permitidos."
            
                # Decodificar el contenido
                content_type, content_string = content.split(',')
                decoded = base64.b64decode(content_string)
            
                # Leer como DataFrame
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
                dataframes.append(df)
        
            if not dataframes:
                return no_update, "No se cargaron archivos válidos."
        
            # Concatenar todos los DataFrames (asumiendo mismas columnas)
            combined_df = pd.concat(dataframes, ignore_index=True)

            # NUEVO: Verificar y eliminar duplicados
            num_dups = combined_df.duplicated().sum()  # Número de filas duplicadas
            if num_dups > 0:
                combined_df = combined_df.drop_duplicates()  # Elimina duplicados exactos
                message_suffix = f" (se eliminaron {num_dups} filas duplicadas)"
            else:
                message_suffix = ""

            # Guardar como dict para dcc.Store
            return combined_df.to_dict('records'), (
                f"{len(filenames)} archivos CSV cargados correctamente. "
                f"Total: {len(combined_df)} filas."
            )
    
        except Exception as e:
            return no_update, f"Error al procesar los archivos: {str(e)}"
    

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
            inactive_subs = metrics.subs_all(full_data, provider = "all", status=["paused", "incomplete", "past_due", 'unpaid'], country="all", source="all").groupby(['status', 'country'])['count'].sum().reset_index()
            
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
                        dcc.Dropdown(id = 'tgo-subs-selector',
                                    options=[
                                        {'label': 'Total', 'value': 'Total'},
                                        {'label': 'Plan Basic', 'value': 'Plan Basic'},
                                        {'label': 'Plan Plus', 'value': 'Plan Plus'},
                                        {'label': 'Plan Business', 'value': 'Plan Business'},
                                        {'label': 'Basic-monthly', 'value': 'Basic-monthly'},
                                        {'label': 'Plus-monthly', 'value': 'Plus-monthly'},
                                        {'label': 'Unlimited-monthly', 'value': 'Unlimited-monthly'},
                                        {'label': 'Basic-yearly', 'value': 'Basic-yearly'},
                                        {'label': 'Plus-yearly', 'value': 'Plus-yearly'},
                                        {'label': 'Unlimited-yearly', 'value': 'Unlimited-yearly'}
                                    ],
                                    value='Total',
                                    clearable=False,
                                    style={'marginTop': '10px', 'textAlign': 'center'},
                                ),                                       
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
                        dcc.Dropdown(id='tgo-income-selector',
                                    options=[
                                        {'label': 'Total', 'value': 'Total'},
                                        {'label': 'Plan Basic', 'value': 'Plan Basic'},
                                        {'label': 'Plan Plus', 'value': 'Plan Plus'},
                                        {'label': 'Plan Business', 'value': 'Plan Business'},
                                        {'label': 'Basic-monthly', 'value': 'Basic-monthly'},
                                        {'label': 'Plus-monthly', 'value': 'Plus-monthly'},
                                        {'label': 'Unlimited-monthly', 'value': 'Unlimited-monthly'},
                                        {'label': 'Basic-yearly', 'value': 'Basic-yearly'},
                                        {'label': 'Plus-yearly', 'value': 'Plus-yearly'},
                                        {'label': 'Unlimited-yearly', 'value': 'Unlimited-yearly'}
                                    ],
                                    value='Total',
                                    clearable=False,
                                    style={'marginTop': '10px', 'textAlign': 'center'},
                                ),
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
                        html.H3("Pagos recibidos por suscripciones", style={'textAlign': 'center'}), 
                        dcc.RadioItems(id = 'mp-subs-payments-selector', 
                                       options = ['Total', 'Aprobados', 'Rechazados'], 
                                       value = 'Total', inline=True, 
                                       labelStyle={'margin-right': '20px'}, 
                                       style={'marginTop': '10px', 'textAlign': 'center'}), 
                        dcc.Graph(figure=fig_mp_subs_payments_per_month, id='mp-subs-payments')
                    ], style=graph_card_style),
                    # Pagos únicos por mes
                    html.Div([
                        html.H3("Pagos únicos recibidos", style={'textAlign': 'center'}), 
                        dcc.RadioItems(id = 'mp-unique-payments-selector', 
                                       options = ['Total', 'Aprobados', 'Rechazados'], 
                                       value = 'Total', inline=True, 
                                       labelStyle={'margin-right': '20px'}, 
                                       style={'marginTop': '10px', 'textAlign': 'center'}), 
                        dcc.Graph(figure=fig_unique_mp_payments_per_month, id='mp-unique-payments')
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
        
        elif tab == 'tab-tgo':
            # ---------------- GRAFICOS DE TGO ------------------------------
            # Onboardings de TGO por mes
            tgo_onboardings_df = metrics.get_tgo_onboardings_info()
            fig_tgo_onboardings = plot_tgo_onboardings(tgo_onboardings_df)
            # table = table_tgo_onboardings(tgo_onboardings_df)

            return html.Div([
                # Onboardings de TGO
                html.Div([
                    html.Div([
                        html.H3("Onboarding TGO", style={'textAlign': 'center'}), 
                        dcc.RadioItems(id = 'tgo-onboarding-selector', 
                                       options = ['Role', 'Use Case', 'First Project','How Did You Hear'], 
                                       value = 'Role', inline=True, 
                                       labelStyle={'margin-right': '20px'}, 
                                       style={'marginTop': '10px', 'textAlign': 'center'}), 
                        dcc.Graph(figure=fig_tgo_onboardings, id= 'tgo-onboarding-chart')
                    ], style=graph_card_style),
                    html.Div([
                        html.H3("Detalle de Onboardings TGO", style={'textAlign': 'center'}), 
                        html.Div(id='onboardings-table')
                    ], style=graph_card_style),
                ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),
            ])
        
        elif tab == 'tab-revenue-recovery':  
            # ------------------- DASHBOARD REVENUE RECOVERY --------------------------------------------------
            return html.Div([
                # Recovery de los expired-incomplete
                html.Div([
                    html.Div([
                        html.H3("Total Expired Stripe Checkout Sessions per Country", style={'textAlign': 'center'}), 
                        dcc.Graph(figure = map_fig, id = 'total-expired-checkout-per-country')
                    ], style=graph_card_style),
                    html.Div([
                        html.H3("Expired Stripe Checkout Sessions per Day", style={'textAlign': 'center'}), 
                        dcc.Graph(figure = expired_per_day_fig, id = 'expired-checkout-per-day')
                    ], style=graph_card_style),
                ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),
                html.Div([
                    html.Div([
                        html.H3("Total Expired Checkout Sessions - Funnel", style={'textAlign': 'center'}), 
                        dcc.Graph(figure = total_funnel_fig, id = 'expired-chechkout-funnel-chart')
                    ], style=graph_card_style),
                ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),

                html.Div([
                    html.Div([
                        html.Label([
                                "Load Stripe Revenue Recovery data",
                                html.Br(), # salto de línea
                                "(csv file)"
                                ], style ={"fontWeight": "bold", "marginBottom": "5px"}),
                        dcc.Upload(id='upload-stripe-revenue-recovery-data', 
                               children=html.Button('Load file', className='btn btn-primary'),
                            multiple=False,
                            accept='.csv',   # Restrict to CSV files (adjust as needed)
                            style={'width': '100%', 'height': '60px', 'lineHeight': '60px', 'borderWidth': '1px',
                                  'borderStyle': 'dashed','borderRadius': '5px','textAlign': 'center','margin': '10px'}
                        ),
                        html.Div(id='stripe-revenue-recovery-data-upload'),  # Placeholder for upload feedback
                        dcc.Store(id='stripe-revenue-recovery-data-store')
                    ], style={**card_style, "width": "25%"}),

                    html.Div([
                        html.Label("Cargar recovery data", 
                               style ={"fontWeight": "bold", "marginBottom": "5px"}),
                        html.Button('Cargar datos', id='load-mongo-recovery-data-button', n_clicks=0, className='btn btn-primary',
                                style={'width': '100%', 'height': '40px', 'fontSize': '18px', 'marginTop': '10px'}),
                        html.Div(id='mongo-recovery-data-feedback'),  # Placeholder for upload feedback
                        dcc.Store(id='mongo-recovery-data-store'),
                
                    ], style={**card_style, "width": "25%"}),
                ], style={"marginBottom": "20px", "display": 'flex'}),

                # Revenue recovery status y método de recuperación
                html.Div([
                    html.Div([
                        dcc.Graph(id = 'revenue-recovery-status-chart')
                    ], style=graph_card_style),
                    html.Div([
                        dcc.Graph(id = 'revenue-recovered-method-chart')
                    ], style=graph_card_style),
                ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),

                # Failed volume by decline reason
                html.Div([
                    html.Div([
                        html.H3("Failed volume by decline reason", style={'textAlign': 'center'}), 
                        dcc.Graph(id= 'stripe-decline-reason-chart')
                    ], style=graph_card_style),
                ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),

                # Funnel chart subs
                html.Div([
                    html.Div([
                        html.H3("Funnel - Subscriptions in Recovery", style={'textAlign': 'center'}), 
                        dcc.Graph(id= 'recovery-subs-funnel-chart')
                    ], style=graph_card_style),
                ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),
            ])
    
    # Callback de Onboardings de TGO
    @app.callback(
        Output('tgo-onboarding-chart', 'figure'),
        Output('onboardings-table', 'children'),
        Input('tgo-onboarding-selector', 'value')
    )
    def update_tgo_onboarding(selector):
        tgo_onboardings_df = metrics.get_tgo_onboardings_info()
        fig = plot_tgo_onboardings(tgo_onboardings_df, selector)
        table = table_tgo_onboardings(tgo_onboardings_df, selector)
        return fig, table

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
    
    # Callback del chart de Pagos por suscripciones de MP
    @app.callback(
        Output('mp-subs-payments', 'figure'),
        Input('date-range', 'start_date'),
        Input('date-range', 'end_date'),
        Input('mp-subs-payments-selector', 'value')
    )
    def update_mp_subs_payments(start_date, end_date, selector):
        all_mp_payments = metrics.get_mp_payments(start_date, end_date)
        fig = mp_subscription_payments_per_month(all_mp_payments, selector)
        return fig
    
    # Callback del chart de Pagos únicos de MP
    @app.callback(
        Output('mp-unique-payments', 'figure'),
        Input('date-range', 'start_date'),
        Input('date-range', 'end_date'),
        Input('mp-unique-payments-selector', 'value')
    )
    def update_mp_unique_payments(start_date, end_date, selector):
        all_mp_payments = metrics.get_mp_payments(start_date, end_date)
        fig = mp_unique_payments_per_month(all_mp_payments, selector)
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

    # Callback Stripe Revenue Recovery Upload
    @app.callback(
        Output('stripe-revenue-recovery-data-store', 'data'),
        Output('stripe-revenue-recovery-data-upload', 'children'),
        Input('upload-stripe-revenue-recovery-data', 'contents'),
        State('upload-stripe-revenue-recovery-data', 'filename'),
        prevent_initial_call=True
    )
    def upload_and_store_csv(contents, filename):
        if contents is None:
            return no_update, no_update

        # Decodificar el contenido (viene en base64)
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
    
        try:
            if filename.endswith('.csv'):
                # Leer el CSV directamente desde bytes
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            elif filename.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(io.BytesIO(decoded))
            else:
                return None, html.Div(f'Formato no soportado: {filename}', className='text-danger')
        
            # Convertir el DataFrame a dict para que sea JSON-serializable y almacenable en dcc.Store
            data_to_store = df.to_dict('records')   # o df.to_json(orient='records') si prefieres string
        
            feedback = html.Div([
                html.Span(f'Archivo "{filename}" cargado correctamente ', 
                         className='text-success'),
                html.Small(f"({len(df)} filas, {len(df.columns)} columnas)")
            ])
        
            return data_to_store, feedback
        
        except Exception as e:
            return None, html.Div(f'Error al procesar el archivo: {str(e)}', className='text-danger')

    # Callback para renderizar los charts de revenue recover
    @app.callback(
        Output('revenue-recovery-status-chart', 'figure'),  
        Output ('revenue-recovered-method-chart', 'figure'),
        Output ('stripe-decline-reason-chart', 'figure'),
        Input('stripe-revenue-recovery-data-store', 'data'),
        prevent_initial_call=True
    )
    def render_revenue_recovery_content(stripe_revenue_recovery_data):
        if stripe_revenue_recovery_data is None or len(stripe_revenue_recovery_data) == 0:
            return "No hay datos cargados aún."
        print("Datos de revenue recovery cargados")
        
        data = pd.DataFrame(stripe_revenue_recovery_data)
        recovery_status = []
        for idx, row in data.iterrows():
            retries_exhausted = row['retries_exhausted']
            recovered_amount = row['recovered_amount']
            if not retries_exhausted:
                recovery_status.append('In recovery')
            elif pd.isna(recovered_amount) or recovered_amount == 0:
                recovery_status.append('Not recovered')
            else:
                recovery_status.append('Recovered')
        data['recovery_status'] = recovery_status
        revenue_recovery_status_fig = recovery_status_stacked_bar_chart(data)
        revenue_recovered_method_fig = recovery_reason_stacked_bar_chart(data)
        failed_volume_reason_fig = failed_volume_by_decline_reason_stacked_bar_chart(data)
        
        return revenue_recovery_status_fig, revenue_recovered_method_fig, failed_volume_reason_fig
    
    # Callback para cargar revenue recovery data de Mongo DB
    @app.callback(
        # Output('mongo-recovery-data-store', 'data'),
        Output('mongo-recovery-data-feedback', 'children'),    
        Output ('recovery-subs-funnel-chart', 'figure'),
        Input('load-mongo-recovery-data-button', 'n_clicks'),
        prevent_initial_call=True  # Evita la llamada inicial sin valor
    )
    def cargar_datos_mongo(n_clicks):
        if n_clicks is None or n_clicks == 0:
            # Retorna no_update para no actualizar nada inicialmente
            return [no_update] * 2
        # if n_clicks > 0:
        try:
            # Pagos de MP
            recovery_data = metrics.get_mongo_recovery_data()
            fig = recovery_subs_funnel_chart(recovery_data)

                # Guardamos como dict para dcc.Store
            return (
                    # recovery_data.to_dict('records'), 
                    f"Datos cargados desde MongoDB correctamente",
                    fig
                    )
        except Exception as e:
            print(f"Error en callback: {e}")
            print("Traceback completo:")
            traceback.print_exc()  # Esto imprime el stacktrace detallado
            return (# [], 
                    f"Error al cargar: {str(e)}",
                    no_update
                    )
