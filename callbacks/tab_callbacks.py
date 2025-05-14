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
        # DAU
        dau_by_country = metrics.daily_subs_by_country(start_date, end_date)
        stripe_dau_by_country = metrics.daily_stripe_subs_by_country(start_date, end_date)
        mp_dau_by_country = metrics.daily_mp_subs_by_country(start_date, end_date)
        
        # MAU
        mau_by_country = metrics.monthly_subs_by_country(start_date, end_date)
        stripe_mau_by_country = metrics.monthly_stripe_subs_by_country(start_date, end_date)
        mp_mau_by_country = metrics.monthly_mp_subs_by_country(start_date, end_date)
        
        # Status de suscripciones
        stripe_status_data = metrics.status_stripe_subs()
        tme_plus_status_data = metrics.status_tme_plus()
        tme_plus2_status_data = metrics.status_tme_plus2()

        # Comparación de totales MP-Stripe
        monthly_total = metrics.monthly_subs(start_date, end_date)
        stripe_monthly = metrics.monthly_stripe_subs(start_date, end_date)
        mp_monthly = metrics.monthly_mp_subs(start_date, end_date)

    
        # Crear gráficos comunes
        fig_monthly_total = create_stacked_bar_chart(
            mau_by_country, "Total de Suscripciones por Mes", "Mes", "Cantidad", colors_dict=None
        )
    
        fig_daily_total = create_stacked_bar_chart(
            dau_by_country, "Total de Suscripciones por Día", "Fecha", "Cantidad", colors_dict=None
        )
    
        fig_stripe_monthly = create_stacked_bar_chart(
            stripe_mau_by_country, "Stripe - Suscripciones Mensuales", "Mes", "Cantidad", colors_dict=None
        )
    
        fig_stripe_daily = create_stacked_bar_chart(
            stripe_dau_by_country, "Stripe - Suscripciones Diarias", "Fecha", "Cantidad", colors_dict=None
        )
    
        fig_mp_monthly = create_stacked_bar_chart(
            mp_mau_by_country, "MercadoPago - Suscripciones Mensuales", "Mes", "Cantidad", colors_dict=None
        )
    
        fig_mp_daily = create_stacked_bar_chart(
            mp_dau_by_country, "MercadoPago - Suscripciones Diarias", "Fecha", "Cantidad", colors_dict=None
        )
    
        # Gráfico de estados de Stripe
        statuses = [item['_id'] for item in stripe_status_data]
        counts = [item['count'] for item in stripe_status_data]
        fig_stripe_status = go.Figure(data=[go.Bar(
            x=statuses, 
            y=counts,
            marker_color=colors['stripe']
        )])
        fig_stripe_status.update_layout(
            title_text="Estado de Suscripciones de Stripe",
            xaxis_title="Estado",
            yaxis_title="Cantidad",
            plot_bgcolor=colors['light_gray'],
            paper_bgcolor=colors['card_bg'],
            font=dict(color=colors['text']),
            margin=dict(l=40, r=40, t=50, b=40),
        )

        # Gráfico de estados de TME Plus
        statuses = [item['_id'] for item in tme_plus_status_data]
        counts = [item['count'] for item in tme_plus_status_data]
        fig_tme_plus_status = go.Figure(data=[go.Bar(
            x=statuses, 
            y=counts,
            marker_color=colors['mp']
        )])
        fig_tme_plus_status.update_layout(
            title_text="Estado de Suscripciones de TranscribeMe Plus",
            xaxis_title="Estado",
            yaxis_title="Cantidad",
            plot_bgcolor=colors['light_gray'],
            paper_bgcolor=colors['card_bg'],
            font=dict(color=colors['text']),
            margin=dict(l=40, r=40, t=50, b=40),
        )

        # Gráfico de estados de TME Plus 2
        statuses = [item['_id'] for item in tme_plus2_status_data]
        counts = [item['count'] for item in tme_plus2_status_data]
        fig_tme_plus2_status = go.Figure(data=[go.Bar(
            x=statuses, 
            y=counts,
            marker_color=colors['mp']
        )])
        fig_tme_plus2_status.update_layout(
            title_text="Estado de Suscripciones de TranscribeMe Plus 2",
            xaxis_title="Estado",
            yaxis_title="Cantidad",
            plot_bgcolor=colors['light_gray'],
            paper_bgcolor=colors['card_bg'],
            font=dict(color=colors['text']),
            margin=dict(l=40, r=40, t=50, b=40),
        )
    
        # Crear gráfico comparativo
        fig_comparison = create_comparison_chart(
            monthly_total, stripe_monthly, mp_monthly,
            "Comparación de Suscripciones Mensuales",
            "Mes"
        )
    
        # Crear gráfico de proporción
        total_by_platform = {
            'Stripe': sum(stripe_monthly.values()), 
            'MercadoPago': sum(mp_monthly.values())
        }
        fig_proportion = go.Figure(data=[go.Pie(
            labels=list(total_by_platform.keys()),
            values=list(total_by_platform.values()),
            marker=dict(colors=[colors['stripe'], colors['mp']])
        )])
        fig_proportion.update_layout(
            title_text="Proporción de Suscripciones por Plataforma",
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
                        dcc.Graph(figure=fig_proportion)
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
                        dcc.Graph(figure=fig_stripe_status)
                    ], style=graph_card_style),
                ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),
            ])
    
        elif tab == 'tab-mp':
            # Obtener datos para los gráficos de tipo de suscripción
            mp_types_data = metrics.contar_suscripciones_mercado_pago()
            fig_mp_top_types, fig_mp_other_types = create_mp_type_charts(mp_types_data)
    
            return html.Div([
                html.Div([
                    html.Div([
                        dcc.Graph(figure=fig_mp_monthly)
                    ], style=graph_card_style),
                    html.Div([
                        dcc.Graph(figure=fig_mp_daily)
                    ], style=graph_card_style),
                ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),
        
                # Nueva sección para los gráficos de tipo de suscripción
                html.Div([
                    html.Div([
                        dcc.Graph(figure=fig_mp_top_types)
                    ], style=graph_card_style),
                    html.Div([
                        dcc.Graph(figure=fig_mp_other_types)
                    ], style=graph_card_style),
                ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),
                html.Div([
                    html.Div([
                        dcc.Graph(figure=fig_tme_plus_status)
                    ], style=graph_card_style),
                ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),   
                html.Div([
                    html.Div([
                        dcc.Graph(figure=fig_tme_plus2_status)
                    ], style=graph_card_style),
                ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),                     
            ])
    
        elif tab == 'tab-compare':
            return html.Div([
                html.Div([
                    html.Div([
                        dcc.Graph(figure=fig_comparison)
                    ], style=graph_card_style),
                    html.Div([
                        dcc.Graph(figure=fig_proportion)
                    ], style=graph_card_style),
                ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between"}),
            ])
