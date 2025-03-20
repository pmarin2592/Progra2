import os
import re
from collections import Counter


import nltk
import asyncio
import base64
from textblob import TextBlob
import numpy as np
import pandas as pd
import plotly.express as px
from dash import dcc, html, dash
from dash.dependencies import Input, Output, State
from io import BytesIO
from wordcloud import WordCloud
from nltk.sentiment import SentimentIntensityAnalyzer
from googletrans import Translator
import dash_bootstrap_components as dbc




# Descargar los datos necesarios de NLTK
nltk.download("vader_lexicon")



# Inicializar analizador de sentimientos y traductor
analyzer = SentimentIntensityAnalyzer()
translator = Translator()

# Función asíncrona para traducir texto
async def traducir_texto(texto):
    try:
        traduccion = await translator.translate(texto, dest='en')
        return traduccion.text
    except Exception as e:
        print(f"Error en la traducción: {e}")
        return texto  # Si hay un error, usa el texto original


# Función para limpiar el texto
def limpiar_texto(texto):
    try:
        # Lista de artículos comunes en español
        articulos = [
            "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "al", "en", "y", "a",
            "que", "es", "fue", "muy", "por", "para", "con", "sin", "sobre", "entre", "ser", "está",
            "estaba", "cuando", "hasta", "desde", "durante", "porque", "si", "nos", "me", "te", "lo",
            "la", "le", "nosotros", "vosotros", "ellos", "ellas", "mi", "tu", "su", "nuestro", "vuestro",
            "este", "esta", "estos", "estas", "ese", "esa", "esos", "esas", "aquello", "aquel", "aquella",
            "aquellos", "aquellas", "uno", "una", "dos", "tres", "cuatro", "cinco", "seis", "nueve",
            "siete", "o", "pero", "también", "ya", "siempre", "nunca", "cuando", "donde", "como", "estoy",
            "están", "más", "estaba", "ser", "que", "se", "es", "fue", "esos", "estas", "esto", "esto",
            "esos", "muy", "nos", "tú", "todo", "todos", "esta", "estas", "aquí", "allí", "lo", "la",
            "algo", "alguien", "ese", "ella", "él", "ella", "ustedes", "nosotros", "vosotros", "ella",
            "ella", "mismo", "misma", "al", "la", "el", "yo", "nosotros", "en", "si", "puedo", "tengo",
            "quiero", "puedes", "puedo", "cuando", "como", "hace", "hace", "donde","no", "mis"
        ]
        # Convertir el texto a minúsculas y dividir en palabras
        palabras = texto.lower().split()

        # Eliminar artículos
        palabras_limpias = [palabra for palabra in palabras if palabra not in articulos and len(palabra) > 1]

        # Regenerar el texto limpio
        return " ".join(palabras_limpias)
    except Exception as e:
        print(f"Error en la limpieza de texto: {e}")
        return texto

 # Función para analizar sentimientos con Vader
async def analizar_sentimiento(texto):
    try:
        texto_traducido = await traducir_texto(texto)
        sentimiento = analyzer.polarity_scores(texto_traducido)
        if sentimiento["compound"] > 0.05:
            return 1  # Positivo
        elif sentimiento["compound"] < -0.05:
            return -1  # Negativo
        else:
            return 0  # Neutro
    except Exception as e:
        print(f"Error en el análisis de sentimiento: {e}")
        return 0

def analyze_graph(fig, graph_type, img_str = None, wordcloud_df = None):
    if graph_type == "bar1":
        data = pd.DataFrame(fig["data"][0]["y"])
        most_frequent_category = fig["data"][0]["x"][np.argmax(fig["data"][0]["y"])]
        return f"El gráfico muestra la distribución de sentimientos. La categoría más frecuente es {most_frequent_category}."
    elif graph_type == "bar2":
        data = pd.DataFrame(fig["data"][0]["y"])
        variance = data.var().values[0]

        # Clasificación de la dispersión
        if variance < 1:
            dispersion = "baja"
        elif variance < 5:
            dispersion = "moderada"
        else:
            dispersion = "alta"

        return f"Este gráfico representa la cantidad de datos analizados por categoría. La variabilidad en los datos es {variance:.2f}, indicando una dispersión {dispersion}."
    elif graph_type == "heatmap":
        corr_matrix = np.array(fig["data"][0]["z"])  # Extrae matriz de correlación
        strongest_corr = np.max(np.abs(corr_matrix[np.triu_indices_from(corr_matrix, k=1)]))
        return f"El mapa de calor muestra correlaciones entre variables. La correlación más fuerte es {strongest_corr:.2f}."
    elif  graph_type == "wordcloud":
        try:
            # Limpiar el texto
            texto_limpio = limpiar_texto(wordcloud_df)

            # Tokenizar usando TextBlob
            blob = TextBlob(texto_limpio)
            words = blob.words  # Devuelve una lista de palabras

            # Contar las frecuencias de las palabras
            word_counts = Counter(words)
            top_words = word_counts.most_common(5)
            word_analysis = ", ".join([f'"{word}" aparece {count} veces' for word, count in top_words])

            return f"Las palabras más frecuentes son: {word_analysis}"
        except Exception as e:
            return f"Error en el procesamiento del texto: {str(e)}"

    return "No se pudo realizar un análisis debido a la falta de datos."


async def create_dashboard(app, df):
    try:
        if df.empty:
            app.layout = html.Div("No hay datos para mostrar.")
            return

        df.columns = ["texto", "sentimiento_real", "categoria"]
        df["sentimiento_tip_real"] = df["sentimiento_real"].map({1: 'Positivo', 0: 'Negativo'})
        df["sentimiento_predicho"] = await asyncio.gather(
            *[analizar_sentimiento(texto) for texto in df["texto"].astype(str)])
        df["sentimiento_tip_predicho"] = df["sentimiento_predicho"].map({1: 'Positivo', 0: 'Neutro', -1: 'Negativo'})


        fig_bar1 = px.bar(df["sentimiento_tip_real"].value_counts(),
                          x=df["sentimiento_tip_real"].unique(),
                          y=df["sentimiento_tip_real"].value_counts(),
                          title="Distribución de Sentimientos reales",
                          labels={"x": "Sentimiento Real", "y": "Cantidad"})

        fig_bar2 = px.bar(df["sentimiento_tip_predicho"].value_counts(),
                          x=df["sentimiento_tip_predicho"].unique(),
                          y=df["sentimiento_tip_predicho"].value_counts(),
                          title="Distribución de Sentimientos Calculados",
                          labels={"x": "Sentimiento Calculado", "y": "Cantidad"})

        df_numeric = df.select_dtypes(include=['number'])
        fig_heatmap = px.imshow(df_numeric.corr(), title="Mapa de Calor de Correlación")

        text_data = " ".join(df.iloc[:, 0].dropna())
        text_data_limpio = limpiar_texto(text_data)
        wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text_data_limpio)

        if not os.path.exists("static"):
            os.makedirs("static")
        wordcloud.to_file("static/wordcloud.png")

        img_buffer = BytesIO()
        wordcloud.to_image().save(img_buffer, format="PNG")
        img_str = base64.b64encode(img_buffer.getvalue()).decode()

        # Estructura del Dashboard con el CSS integrado

        def create_modal(modal_id, content, graph_type, img_str=None, wordcloud_df = None ):
            analysis_text = analyze_graph(content[0].figure if isinstance(content[0], dcc.Graph) else None, graph_type, img_str, wordcloud_df)
            return dbc.Modal([
                dbc.ModalHeader(f"Detalle {modal_id}"),
                dbc.ModalBody(content + [html.P(analysis_text)]),
                dbc.ModalFooter(dbc.Button("Cerrar", id=f"close-{modal_id}", n_clicks=0))
            ], id=f"modal-{modal_id}", is_open=False)

        app.layout = html.Div([
            html.H1("Análisis de Sentimientos",
                    style={"background-color": "green", "color": "white", "padding": "10px", "textAlign": "center"}),

            dbc.Row([
                dbc.Col(dbc.Card([html.H3("Distribución de Sentimientos"), dcc.Graph(id="graph1", figure=fig_bar1),
                                  dbc.Button("Ver más", id="open-1", n_clicks=0)]), width=6),
                dbc.Col(dbc.Card(
                    [html.H3("Distribución de Sentimientos Analizados"), dcc.Graph(id="graph2", figure=fig_bar2),
                     dbc.Button("Ver más", id="open-2", n_clicks=0)]), width=6)
            ], style={"margin-bottom": "30px"}),

            dbc.Row([
                dbc.Col(dbc.Card([html.H3("Mapa de Calor de Correlación"), dcc.Graph(id="graph3", figure=fig_heatmap),
                                  dbc.Button("Ver más", id="open-3", n_clicks=0)]), width=6),
                dbc.Col(dbc.Card([html.H3("Nube de Palabras"),
                                  html.Img(src=f"data:image/png;base64,{img_str}",
                                           style={"width": "100%", "max-width": "800px"}),
                                  dbc.Button("Ver más", id="open-4", n_clicks=0)]), width=6)
            ], style={"margin-bottom": "30px"}),

            create_modal("1", [dcc.Graph(figure=fig_bar1)], "bar1"),
            create_modal("2", [dcc.Graph(figure=fig_bar2)], "bar2"),
            create_modal("3", [dcc.Graph(figure=fig_heatmap)], "heatmap"),
            create_modal("4", [html.Img(src=f"data:image/png;base64,{img_str}", style={"width": "100%", "max-width": "800px"})], "wordcloud", img_str,text_data_limpio)
        ])

        # Callbacks para manejar la apertura y cierre de modales
        for i in range(1, 5):
            app.callback(
                Output(f"modal-{i}", "is_open"),
                [Input(f"open-{i}", "n_clicks"), Input(f"close-{i}", "n_clicks")],
                [State(f"modal-{i}", "is_open")]
            )(lambda open_clicks, close_clicks, is_open: not is_open if open_clicks or close_clicks else is_open)



        # app.layout = html.Div([
        #      html.H1("Análisis de Sentimientos", style={"textAlign": "center"}),
        #      html.Div([html.H3("Distribución de Sentimientos"), dcc.Graph(figure=fig_bar1)],
        #               style={"margin-bottom": "30px"}),
        #      html.Div([html.H3("Distribución de Sentimientos Analizados"), dcc.Graph(figure=fig_bar2)],
        #               style={"margin-bottom": "30px"}),
        #      html.Div([html.H3("Mapa de Calor de Correlación"), dcc.Graph(figure=fig_heatmap)],
        #               style={"margin-bottom": "30px"}),
        #      html.Div([html.H3("Nube de Palabras"),
        #                html.Img(src=f"data:image/png;base64,{img_str}", style={"width": "100%", "max-width": "800px"})])
        #  ])
    except Exception as e:
        print(f"Error en la creación del dashboard: {e}")
        app.layout = html.Div("Error al generar el dashboard.")