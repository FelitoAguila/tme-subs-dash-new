# style/styles.py

# Definir colores
colors = {
    'background': '#f9f9f9',
    'text': '#333333',
    'primary': '#2c3e50',
    'secondary': '#3498db',
    'accent': '#e74c3c',
    'stripe': '#6772E5',
    'mp': '#009EE3',
    'card_bg': '#ffffff',
    'light_gray': '#ecf0f1'
}

# Estilos
card_style = {
    'backgroundColor': colors['card_bg'],
    'borderRadius': '8px',
    'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
    'padding': '20px',
    'margin': '10px',
}

metric_card_style = {
    **card_style,
    'textAlign': 'center',
    'flex': '1',
    'minWidth': '200px',
}

graph_card_style = {
    **card_style,
    'flex': '1',
    'minWidth': '45%',
}

tab_style = {
    'padding': '10px 15px',
    'borderBottom': '1px solid #d6d6d6',
    'fontWeight': 'bold',
    'backgroundColor': colors['light_gray'],
    'borderRadius': '5px 5px 0 0',
    'margin': '0 2px',
}

tab_selected_style = {
    'padding': '10px 15px',
    'borderBottom': '1px solid #d6d6d6',
    'borderTop': f'3px solid {colors["secondary"]}',
    'backgroundColor': colors['card_bg'],
    'color': colors['secondary'],
    'borderRadius': '5px 5px 0 0',
    'margin': '0 2px',
}