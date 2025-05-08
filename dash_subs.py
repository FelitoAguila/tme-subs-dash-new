from dash import Dash, dcc, html, Input, Output
import plotly.graph_objs as go
from datetime import date
from subs_metrics import SubscriptionMetrics

# Instanciar la clase
metrics = SubscriptionMetrics()

# Crear la app
app = Dash(__name__)
app.title = "Dashboard de Suscripciones"

app.layout = html.Div([
    html.H1("Dashboard de Suscripciones", style={"textAlign": "center"}),

    dcc.DatePickerRange(
        id='date-range',
        start_date=date(2024, 1, 1),
        end_date=date.today(),
        display_format='YYYY-MM-DD',
        style={"marginBottom": "40px", "width": "100%"}
    ),

    # Métricas Resumen
    html.Div([
        html.Div(id='total-subs-summary', style={'flex': '1', 'padding': '10px', 'textAlign': 'center', 'fontSize': '18px', 'fontWeight': 'bold'}),
        html.Div(id='stripe-subs-summary', style={'flex': '1', 'padding': '10px', 'textAlign': 'center', 'fontSize': '18px', 'fontWeight': 'bold'}),
        html.Div(id='mp-subs-summary', style={'flex': '1', 'padding': '10px', 'textAlign': 'center', 'fontSize': '18px', 'fontWeight': 'bold'}),
    ], style={"display": "flex", "justifyContent": "space-around", "marginBottom": "30px"}),

    # Gráficos de Total de Suscripciones
    html.Div([
        dcc.Graph(id='monthly-total-subs-bar'),
        dcc.Graph(id='daily-total-subs-bar'),
    ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-around"}),

    # Gráficos de Suscripciones de Stripe
    html.Div([
        dcc.Graph(id='monthly-stripe-bar'),
        dcc.Graph(id='daily-stripe-bar'),
        dcc.Graph(id='stripe-status-bar'),
    ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-around"}),

    # Gráficos de Suscripciones de MercadoPago
    html.Div([
        dcc.Graph(id='monthly-mp-bar'),
        dcc.Graph(id='daily-mp-bar'),
    ], style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-around"}),
])

@app.callback(
    Output('total-subs-summary', 'children'),
    Output('stripe-subs-summary', 'children'),
    Output('mp-subs-summary', 'children'),
    Input('date-range', 'start_date'),
    Input('date-range', 'end_date')
)
def update_summary_metrics(start_date, end_date):
    total = metrics.total_subs(start_date, end_date)
    avg_daily = metrics.average_daily_subs(start_date, end_date)
    avg_monthly = metrics.average_monthly_subs(start_date, end_date)
    total_stripe = metrics.total_stripe_subs(start_date, end_date)
    avg_daily_stripe = metrics.average_stripe_daily_subs(start_date, end_date)
    avg_monthly_stripe = metrics.average_stripe_monthly_subs(start_date, end_date)
    total_mp = metrics.total_mp_subs(start_date, end_date)
    avg_daily_mp = metrics.average_mp_daily_subs(start_date, end_date)
    avg_monthly_mp = metrics.average_mp_monthly_subs(start_date, end_date)

    return (
        html.Div([
            html.H3("Total Suscripciones"),
            f"Total: {total}",
            html.Br(),
            f"Promedio Diario: {avg_daily:.2f}",
            html.Br(),
            f"Promedio Mensual: {avg_monthly:.2f}",
        ]),
        html.Div([
            html.H3("Suscripciones Stripe"),
            f"Total: {total_stripe}",
            html.Br(),
            f"Promedio Diario: {avg_daily_stripe:.2f}",
            html.Br(),
            f"Promedio Mensual: {avg_monthly_stripe:.2f}",
        ]),
        html.Div([
            html.H3("Suscripciones MercadoPago"),
            f"Total: {total_mp}",
            html.Br(),
            f"Promedio Diario: {avg_daily_mp:.2f}",
            html.Br(),
            f"Promedio Mensual: {avg_monthly_mp:.2f}",
        ]),
    )


@app.callback(
    Output('monthly-total-subs-bar', 'figure'),
    Output('daily-total-subs-bar', 'figure'),
    Output('daily-stripe-bar', 'figure'),
    Output('monthly-stripe-bar', 'figure'),
    Output('daily-mp-bar', 'figure'),
    Output('monthly-mp-bar', 'figure'),
    Output('stripe-status-bar', 'figure'),
    Input('date-range', 'start_date'),
    Input('date-range', 'end_date'),
)
def update_graphs(start_date, end_date):
    # 1. Total suscripciones por mes
    monthly_total = metrics.monthly_subs(start_date, end_date)
    fig_monthly_total = go.Figure(data=[
        go.Bar(x=list(monthly_total.keys()), y=list(monthly_total.values()))
    ])
    fig_monthly_total.update_layout(title="Total de Suscripciones por Mes", xaxis_title="Mes", yaxis_title="Cantidad")

    # 2. Total suscripciones por día
    daily_total = metrics.daily_subs(start_date, end_date)
    fig_daily_total = go.Figure(data=[
        go.Bar(x=list(daily_total.keys()), y=list(daily_total.values()))
    ])
    fig_daily_total.update_layout(title="Total de Suscripciones por Día", xaxis_title="Fecha", yaxis_title="Cantidad")

    # 3. Stripe - Mensuales (primero para mantener el orden)
    stripe_monthly = metrics.monthly_stripe_subs(start_date, end_date)
    fig_stripe_monthly = go.Figure(data=[
        go.Bar(x=list(stripe_monthly.keys()), y=list(stripe_monthly.values()))
    ])
    fig_stripe_monthly.update_layout(title="Stripe - Suscripciones Mensuales", xaxis_title="Mes", yaxis_title="Cantidad")

    # 4. Stripe - Diarias
    stripe_daily = metrics.daily_stripe_subs(start_date, end_date)
    fig_stripe_daily = go.Figure(data=[
        go.Bar(x=list(stripe_daily.keys()), y=list(stripe_daily.values()))
    ])
    fig_stripe_daily.update_layout(title="Stripe - Suscripciones Diarias", xaxis_title="Fecha", yaxis_title="Cantidad")

    # 5. MP - Mensuales (primero para mantener el orden)
    mp_monthly = metrics.monthly_mp_subs(start_date, end_date)
    fig_mp_monthly = go.Figure(data=[
        go.Bar(x=list(mp_monthly.keys()), y=list(mp_monthly.values()))
    ])
    fig_mp_monthly.update_layout(title="MercadoPago - Suscripciones Mensuales", xaxis_title="Mes", yaxis_title="Cantidad")

    # 6. MP - Diarias
    mp_daily = metrics.daily_mp_subs(start_date, end_date)
    fig_mp_daily = go.Figure(data=[
        go.Bar(x=list(mp_daily.keys()), y=list(mp_daily.values()))
    ])
    fig_mp_daily.update_layout(title="MercadoPago - Suscripciones Diarias", xaxis_title="Fecha", yaxis_title="Cantidad")

    # 7. Stripe - Status
    stripe_status_data = metrics.status_stripe_subs()
    statuses = [item['_id'] for item in stripe_status_data]
    counts = [item['count'] for item in stripe_status_data]
    fig_stripe_status = go.Figure(data=[go.Bar(x=statuses, y=counts)])
    fig_stripe_status.update_layout(title_text="Status de Suscripciones de Stripe",
                      xaxis_title="Status",
                      yaxis_title="Cantidad de Suscripciones")
     
    return (
        fig_monthly_total,
        fig_daily_total,
        fig_stripe_daily,
        fig_stripe_monthly,
        fig_mp_daily,
        fig_mp_monthly,
        fig_stripe_status
    )


if __name__ == '__main__':
    app.run_server(debug=True)