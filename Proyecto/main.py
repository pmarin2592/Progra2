

from flask import Flask, render_template, request
from app.controllers.analisis_controller import load_data, load_dashboard  # Importar la función para configurar Dash
from dash import Dash, html

# Configurar la ruta de las plantillas para Flask
app = Flask(__name__, template_folder="app/templates")
# Crear la instancia de Dash, pasándole la aplicación Flask
dash_app = Dash(__name__, server=app, routes_pathname_prefix='/dashboard/')
# Establecer un layout inicial para evitar el error
dash_app.layout = html.Div("Cargando Dashboard...")
data = []
# Ruta principal para servir el archivo index.html
@app.route('/', methods=['GET', 'POST'])
def home():

    summary = {}
    data_html = []

    if request.method == 'POST':
        # Cargar datos desde la base de datos o CSV según la elección
        data = load_data()
        print(data)
        data_html = data.to_dict(orient='records')
        print(data)


        # Resumen de los datos
        summary = {
            "row_count": len(data),
            "column_count": len(data.columns),
            "first_comment": data.iloc[0, 0] if len(data) > 0 else "No disponible"
        }

    return render_template('index.html', data=data_html, summary=summary)

@app.route('/graficos')
def graficos():
    # Cargar los datos
    df = load_data()
    # Configurar el dashboard con Dash
    load_dashboard(dash_app, df)


    return render_template('graficos.html')

if __name__ == "__main__":
    app.run(debug=True)
