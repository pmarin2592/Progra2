import os
from pydoc import html

import pandas as pd
from flask import request, redirect, url_for
from app.database.database import obtener_comentarios_db
from app.models.analisis import create_dashboard
from werkzeug.utils import secure_filename

import subprocess

ALLOWED_EXTENSIONS = {'csv'}

# Verificar si el archivo tiene una extensión válida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Función para cargar CSV
def load_csv(file, delimiter):
    df = pd.read_csv(file, delimiter=delimiter, encoding="ISO-8859-1",  quotechar='"')
    return df

# Función para procesar y mostrar datos
def load_data():
    print("Cargando datos...")
    print(request.files)  # Esto te mostrará todos los archivos enviados en la solicitud

    # Determina si el usuario ha cargado un archivo CSV o si desea usar la base de datos
    if 'csv_file' in request.files and request.files['csv_file'].filename != '' :
        file = request.files['csv_file']
        print("Entrering CSV")
        if "csv_file" not in request.files:
            return "No se encontró el archivo."
        file = request.files["csv_file"]

        if file.filename == "":
            return "Nombre de archivo vacío."

        filename = secure_filename("comentarios.csv")  # Asegurar un nombre seguro
        filepath = os.path.join("static/Carga/", filename)

        # Si el archivo ya existe, eliminarlo
        if os.path.exists(filepath):
            os.remove(filepath)

        file.save(filepath)  # Guardar el nuevo archivo

        ruta_pdi = "C:/pentaho/data-integration/pan.bat"  # Ruta a Pentaho Data Integration
        ruta_transformacion = "static\carga_archivo.ktr"

        cmd = [ruta_pdi, f'/file:{ruta_transformacion}']

        try:
            proceso = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            salida, error = proceso.communicate()

            if proceso.returncode == 0:
                print("✅ Transformación ejecutada con éxito:\n", salida)
            else:
                print("❌ Error al ejecutar la transformación:\n", error)

        except Exception as e:
            print(f"⚠️ Error inesperado: {e}")

        df = obtener_comentarios_db()
        return df
    else:
        print("Usando base de datos...")
        # Si no es CSV, carga desde la base de datos
        df = obtener_comentarios_db()
        return df

    print("Datos cargados correctamente.")

def load_dashboard(app,df):
    create_dashboard(app,df)
