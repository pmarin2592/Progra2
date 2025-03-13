import os
import re

import pandas as pd
import plotly.express as px
from dash import dcc, html, dash
from wordcloud import WordCloud
import base64
from io import BytesIO
from textblob import TextBlob


# Función para limpiar el texto
def limpiar_texto(texto):
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
    "quiero", "puedes", "puedo", "cuando", "como", "hace", "hace", "donde"
]
    # Convertir el texto a minúsculas y dividir en palabras
    palabras = texto.lower().split()

    # Eliminar artículos
    palabras_limpias = [palabra for palabra in palabras if palabra not in articulos and len(palabra) > 1]

    # Regenerar el texto limpio
    return " ".join(palabras_limpias)
 # Función para analizar sentimientos con TextBlob
def analizar_sentimiento(texto):
    analisis = TextBlob(texto)
    polaridad = analisis.sentiment.polarity
    print(polaridad)
    return 1 if polaridad >= 0 else 0  # 1 = Positivo, 0 = Negativo

def create_dashboard(app, df):
    # Asegurarnos de que el layout se actualiza correctamente
    if df.empty:
        app.layout = html.Div("No hay datos para mostrar.")
        return

    # Renombrar columnas para facilidad de uso
    df.columns = ["texto", "sentimiento_real", "categoria"]
    print(df)

    # Aplicar la función a los textos
    df["sentimiento_predicho"] = df["texto"].astype(str).apply(analizar_sentimiento)

    print(df)

    # 🔹 Gráfico de barras dinámico
    fig_bar = px.bar(df["sentimiento_real"].value_counts(),
                     x=df["sentimiento_real"].unique(),
                     y=df["sentimiento_real"].value_counts(),
                     title="Distribución de Sentimientos",
                     labels={"x": "sentimiento_real", "y": "Cantidad"})

    # 🔹 Mapa de Calor (Correlación) – Selección de columnas numéricas
    df_numeric = df.select_dtypes(include=['number'])  # Solo columnas numéricas
    fig_heatmap = px.imshow(df_numeric.corr(), title="Mapa de Calor de Correlación")

    # 🔹 Nube de palabras

    # Limpiar el texto de la primera columna (comentarios o texto que estás analizando)
    text_data = " ".join(df.iloc[:, 0].dropna())

    # Limpiar el texto (eliminar vocales y artículos)
    text_data_limpio = limpiar_texto(text_data)

    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text_data_limpio)

    # Crear el directorio 'static' si no existe
    if not os.path.exists('static'):
        os.makedirs('static')

    # Guardar la imagen en `static/wordcloud.png`
    wordcloud.to_file("static/wordcloud.png")

    # Convertir imagen en base64
    img_buffer = BytesIO()
    wordcloud.to_image().save(img_buffer, format="PNG")
    img_str = base64.b64encode(img_buffer.getvalue()).decode()



    # Layout de Dash
    app.layout = html.Div([
        html.H1("Análisis de Sentimientos", style={"textAlign": "center"}),

        html.Div([
            html.H3("Distribución de Sentimientos"),
            dcc.Graph(figure=fig_bar)
        ], style={"margin-bottom": "30px"}),

        html.Div([
            html.H3("Mapa de Calor de Correlación"),
            dcc.Graph(figure=fig_heatmap)
        ], style={"margin-bottom": "30px"}),

        html.Div([
            html.H3("Nube de Palabras"),
            html.Img(src=f"data:image/png;base64,{img_str}", style={"width": "100%", "max-width": "800px"})
        ])
    ])
