# callbacks/tab_callbacks.py
from dash import Input, Output, html, dcc
from subs_metrics import SubscriptionMetrics
import plotly.graph_objs as go
from style.styles import (
    colors,
    graph_card_style
)
from components.charts import (
    create_stacked_bar_chart,
    create_comparison_chart,
    create_mp_type_charts
)


metrics = SubscriptionMetrics()

def register_tab_callbacks(app):
    @app.callback(
    Output('tab-content', 'children'),
    Input('tabs', 'value'),
    Input('date-range', 'start_date'),
    Input('date-range', 'end_date')
)
    def render_tab_content(tab, start_date, end_date):
        # Búsqueda de subs en Mongo
        raw_data = metrics.get_subs_data(start_date, end_date)

        # Asignación de países según el user_id
        data_with_countries = metrics.asign_countries(raw_data)

        # Asignando provider: "mp" a las suscripciones en MP sin provider
        full_data = metrics.assign_provider_default(data_with_countries)
        
        # Daily subs por países
        daily_subs_by_country = metrics.subs_all(full_data, group_by='day', country="all")
        daily_stripe_subs_by_country = metrics.subs_all(full_data, group_by='day', country="all", provider="stripe")
        daily_mp_subs_by_country = metrics.subs_all(full_data, group_by='day', country="all", provider = ["mp", "mp_discount", "free", "manual"])
        
        # Monthly subs por países
        monthly_subs_by_country = metrics.subs_all(full_data, group_by='month', country="all")
        monthly_stripe_subs_by_country = metrics.subs_all(full_data, group_by='month', country="all", provider="stripe")
        monthly_mp_subs_by_country = metrics.subs_all(full_data, group_by='month', country="all", provider = ["mp", "mp_discount", "free", "manual"])
        
        # Status de suscripciones en general
        active_subs = metrics.subs_all(full_data, status=["active", "authorized"], provider = "all", country="all", source = "all").groupby(['provider', 'country'])['count'].sum().reset_index()
        inactive_subs = metrics.subs_all(full_data, provider = "all", status=["paused", "incomplete", "past_due"], country="all", source="all").groupby(['status', 'country'])['count'].sum().reset_index()
        cancelled_subs = metrics.subs_all(full_data, provider = "all", status="cancelled", country="all", source="all").groupby(['provider', 'country'])['count'].sum().reset_index()

        # Status suscripciones de Stripe
        stripe_status_data = metrics.subs_all(full_data, provider = "stripe", status = "all", country="all", source="all").groupby(['status', 'country'])['count'].sum().reset_index()
        

        # Status suscripciones de MP
        mp_active_plans_TMEP_TMEP2 = metrics.subs_all(full_data, provider = "mp", status = "authorized", country = "all", reason=["TranscribeMe Plus","TranscribeMe Plus 2" ]).groupby(['reason', "country"])['count'].sum().reset_index()
        mp_active_plans_others = metrics.subs_all(full_data, status = "authorized", country = "all",
                                                      reason=["TranscribeMe Plus discount", "TranscribeMe Plus 10d",
                                                              "TranscribeMe Plus - mensual 20% off",
                                                              "TranscribeMe Plus - Anual con 3 meses gratis",
                                                              ]).groupby(['reason', "country"])['count'].sum().reset_index()
        mp_free = metrics.subs_all(full_data, provider = "free", country = "all", reason="all").groupby(['reason', "country"])['count'].sum().reset_index()
        mp_discount_daily = metrics.subs_all(full_data, group_by='day', provider = "mp_discount", country="all")
        mp_discount_monthly = metrics.subs_all(full_data, group_by='month', provider = "mp_discount", country="all")
        
        # Comparación de totales MP-Stripe
        total_monthly_subs = metrics.subs_all(full_data, group_by="month")
        stripe_monthly_subs = metrics.subs_all(full_data, group_by="month", provider="stripe")
        mp_monthly_subs = metrics.subs_all(full_data, group_by="month", provider=["mp", "mp_discount", "free", "manual"]).groupby('date')['count'].sum().reset_index()

    
        # Gráfico de barras apiladas de monthly subs
        fig_monthly_total = create_stacked_bar_chart(
            data_df=monthly_subs_by_country, stack_column = "country",
            title="Total de Suscripciones creadas por Mes", x_label="Mes", y_label="Cantidad"
        )
    
         # Gráfico de barras apiladas de daily subs
        fig_daily_total = create_stacked_bar_chart(
            data_df = daily_subs_by_country, stack_column = 'country', 
            title="Total de Suscripciones creadas por Día", x_label="Fecha", y_label="Cantidad"
        )

        # Gráfico de barras apiladas de monthly stripe subs
        fig_stripe_monthly = create_stacked_bar_chart(
            data_df=monthly_stripe_subs_by_country, stack_column = "country",
            title="Suscripciones creadas por mes - Stripe", x_label="Mes", y_label="Cantidad"
        )
        
        # Gráfico de barras apiladas de monthly mp subs
        fig_mp_monthly = create_stacked_bar_chart(
            data_df=monthly_mp_subs_by_country, stack_column = "country",
            title="Suscripciones creadas por mes - MercadoPago", x_label="Mes", y_label="Cantidad"
        )
    
        # Gráfico de barras apiladas de daily stripe subs
        fig_stripe_daily = create_stacked_bar_chart(
            data_df=daily_stripe_subs_by_country, stack_column = "country",
            title="Suscripciones creadas por día - Stripe", x_label="Fecha", y_label="Cantidad"
        )
    
        # Gráfico de barras apiladas de daily mp subs
        fig_mp_daily = create_stacked_bar_chart(
            data_df=daily_mp_subs_by_country, stack_column = "country",
            title="Suscripciones creadas por día - MercadoPago", x_label="Fecha", y_label="Cantidad"
        )

        # Gráfico de estado de las suscripciones en general
        # Suscriptores activos por país actualmente
        fig_active_subs = create_stacked_bar_chart(
            data_df = active_subs, x = "provider", y = "count", stack_column = 'country',
            title="Suscripciones Activas por país", x_label="Plataforma", y_label="Cantidad", bar_width_days=0.4
        )

        # Suscriptores inactivos por país actualmente
        fig_inactive_subs = create_stacked_bar_chart(
            data_df = inactive_subs, x = "status", y = "count", stack_column = 'country',
            title="Status de las suscripciones inactivas", x_label="Status", y_label="Cantidad", bar_width_days=0.4
        )

        # Suscripciones canceladas por país
        fig_cancelled_subs = create_stacked_bar_chart(
            data_df=cancelled_subs, x = "provider", y = "count", stack_column = 'country',
            title="Suscripciones canceladas por país", x_label="Plataforma", y_label="Cantidad", bar_width_days=0.4
        )

        # Gráficos de estados de Stripe
        fig_stripe_status_data = create_stacked_bar_chart(
            data_df=stripe_status_data, x = "status", y = "count", stack_column = 'country',
            title="Status de las suscripciones de Stripe", x_label="Status", y_label="Cantidad", bar_width_days=0.4
        )

        # Gráfico de planes TMEP y TMPE2
        fig_mp_active_plans_TMEP_TMEP2 = create_stacked_bar_chart(
            data_df=mp_active_plans_TMEP_TMEP2, x = "reason", y = "count", stack_column = 'country',
            title="Suscripciones activas por planes de MP", x_label="Plan", y_label="Cantidad", bar_width_days=0.4
        )

        # Gráfico de otros planes en MP
        fig_mp_active_plans_others = create_stacked_bar_chart(
            data_df=mp_active_plans_others, x = "reason", y = "count", stack_column = 'country',
            title="Suscripciones activas por planes de MP", x_label="Plan", y_label="Cantidad", bar_width_days=0.4
        )

        # Gráfico de suscriptores free
        fig_mp_free = create_stacked_bar_chart(
            data_df=mp_free, x = "reason", y = "count", stack_column = 'country',
            title="Suscripciones free en MP", x_label="Plan", y_label="Cantidad", bar_width_days=0.4
        )

        # Gráfico de pagos por 3 meses por mes
        fig_mp_discount_monthly = create_stacked_bar_chart(
            data_df=mp_discount_monthly, x = "date", y = "count", stack_column = 'country',
            title="Compras de tres meses de TME por mes", x_label="Fecha", y_label="Cantidad", bar_width_days=None
        )

        # Gráfico de pagos por 3 meses por día
        fig_mp_discount_daily = create_stacked_bar_chart(
            data_df=mp_discount_daily, x = "date", y = "count", stack_column = 'country',
            title="Compras de tres meses de TME por día", x_label="Fecha", y_label="Cantidad", bar_width_days=None
        )
    
        # Crear gráfico comparativo
        fig_comparison = create_comparison_chart(
            total_monthly_subs, stripe_monthly_subs, mp_monthly_subs,
            "Comparación de Suscripciones Mensuales",
            "Mes"
        )
    
        # Comparación de suscripctores activos
        stripe = metrics.subs_all(full_data, group_by="month", status = "active", provider="stripe")['count'].sum()
        mp = metrics.subs_all(full_data, group_by="month", status = "authorized", provider="mp")['count'].sum()

        total_by_platform = {
            'Stripe': stripe, 
            'MercadoPago': mp
        }
        fig_proportion = go.Figure(data=[go.Pie(
            labels=list(total_by_platform.keys()),
            values=list(total_by_platform.values()),
            marker=dict(colors=[colors['stripe'], colors['mp']])
        )])
        fig_proportion.update_layout(
            title_text="Proporción de Suscripciones Activos por Plataforma",
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
                        dcc.Graph(figure=fig_active_subs)
                    ], style=graph_card_style),
                    html.Div([
                        dcc.Graph(figure=fig_inactive_subs)
                    ], style=graph_card_style),
                ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),
                html.Div([
                    html.Div([
                        dcc.Graph(figure=fig_proportion)
                    ], style=graph_card_style),
                    html.Div([
                        dcc.Graph(figure=fig_cancelled_subs)
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
                        dcc.Graph(figure=fig_stripe_status_data)
                    ], style=graph_card_style),
                ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),
            ])
    
        elif tab == 'tab-mp':
            return html.Div([
                html.Div([
                    html.Div([
                        dcc.Graph(figure=fig_mp_monthly)
                    ], style=graph_card_style),
                    html.Div([
                        dcc.Graph(figure=fig_mp_daily)
                    ], style=graph_card_style),
                ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),

                #Nueva sección para los pagos por 3 meses
                html.Div([
                    html.Div([
                        dcc.Graph(figure=fig_mp_discount_monthly)
                    ], style=graph_card_style),
                    html.Div([
                        dcc.Graph(figure=fig_mp_discount_daily)
                    ], style=graph_card_style),
                ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),
        
                # Nueva sección para los gráficos de tipo de suscripción
                html.Div([
                    html.Div([
                        dcc.Graph(figure=fig_mp_active_plans_TMEP_TMEP2)
                    ], style=graph_card_style),
                ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),   
                html.Div([
                    html.Div([
                        dcc.Graph(figure=fig_mp_active_plans_others)
                    ], style=graph_card_style),
                ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),                     
            
                      # Nueva sesión para sol ususarios free
                html.Div([
                    html.Div([
                        dcc.Graph(figure=fig_mp_free)
                    ], style=graph_card_style),
                ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),
            ])
      
        elif tab == 'tab-compare':
            return html.Div([
                html.Div([
                    html.Div([
                        dcc.Graph(figure=fig_comparison)
                    ], style=graph_card_style),
                ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),
            ])
