from flask import Flask, render_template, request
from app.controllers.analisis_controller import load_data, load_dashboard  # Importar la función para configurar Dash
from dash import Dash, html
import dash_bootstrap_components as dbc

# Configurar la ruta de las plantillas para Flask
app = Flask(__name__, template_folder="app/templates")
# Crear la instancia de Dash, pasándole la aplicación Flask
dash_app = Dash(__name__, server=app, routes_pathname_prefix='/dashboard/',  external_stylesheets=[dbc.themes.BOOTSTRAP])
# Establecer un layout inicial para evitar el error
dash_app.layout = html.Div("Cargando Dashboard...")

data = []

# Ruta principal para servir el archivo index.html
@app.route('/', methods=['GET', 'POST'])
def home():
    summary = {}
    data_html = []

    if request.method == 'POST':
        try:
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
        except Exception as e:
            print(f"⚠️ Error al cargar los datos: {e}")
            summary = {"error": "Ocurrió un error al procesar los datos."}

    return render_template('index.html', data=data_html, summary=summary)

@app.route('/graficos')
def graficos():
    try:
        # Cargar los datos
        df = load_data()
        # Configurar el dashboard con Dash
        load_dashboard(dash_app, df)
    except Exception as e:
        print(f"⚠️ Error al cargar el dashboard: {e}")
        return render_template('graficos.html', error="Ocurrió un error al generar los gráficos.")

    return render_template('graficos.html')

if __name__ == "__main__":
    try:
        app.run(debug=True)
    except Exception as e:
        print(f"⚠️ Error al iniciar el servidor Flask: {e}")