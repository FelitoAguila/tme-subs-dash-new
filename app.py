from dash import Dash
from subs_metrics import SubscriptionMetrics
import os
from components.layout import serve_layout
from callbacks.summary_callbacks import register_summary_callbacks
from callbacks.tab_callbacks import register_tab_callbacks

# Instanciar la clase
metrics = SubscriptionMetrics()

# Crear la app con hoja de estilos externa
app = Dash(__name__)
app.title = "Dashboard de Suscripciones- TranscribeMe"
server = app.server  # Esto es importante para Gunicorn

# Layout
app.layout = serve_layout()

register_summary_callbacks(app)
register_tab_callbacks(app)



if __name__ == '__main__':
    # Obtener puerto de variable de entorno (para Render) o usar 8050 por defecto (para desarrollo local)
    app.run(debug=False, port = 8050)
