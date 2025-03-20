import os
import subprocess
import pandas as pd
import asyncio
from flask import request
from werkzeug.utils import secure_filename
from app.database.database import obtener_comentarios_db
from app.models.analisis import create_dashboard

ALLOWED_EXTENSIONS = {'csv'}


# Verificar si el archivo tiene una extensión válida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Función para cargar CSV
def load_csv(file, delimiter):
    try:
        df = pd.read_csv(file, delimiter=delimiter, encoding="ISO-8859-1", quotechar='"')
        return df
    except Exception as e:
        print(f"⚠️ Error al cargar el archivo CSV: {e}")
        return None


# Función para procesar y mostrar datos
def load_data():
    try:
        print("Cargando datos...")
        print(request.files)  # Mostrar archivos enviados

        if 'csv_file' in request.files and request.files['csv_file'].filename != '':
            file = request.files['csv_file']
            print("Procesando archivo CSV...")

            if file.filename == "":
                return "Nombre de archivo vacío."

            filename = secure_filename("comentarios.csv")
            filepath = os.path.join("static/Carga/", filename)

            # Eliminar archivo existente si ya hay uno cargado previamente
            if os.path.exists(filepath):
                os.remove(filepath)

            file.save(filepath)  # Guardar archivo

            ruta_pdi = "C:/pentaho/data-integration/pan.bat"  # Ruta de Pentaho
            ruta_transformacion = "static\carga_archivo.ktr"
            cmd = [ruta_pdi, f'/file:{ruta_transformacion}']

            try:
                proceso = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                salida, error = proceso.communicate()

                if proceso.returncode == 0:
                    print("✅ Transformación ejecutada con éxito:", salida)
                else:
                    print("❌ Error al ejecutar la transformación:", error)

            except Exception as e:
                print(f"⚠️ Error inesperado al ejecutar Pentaho: {e}")

            df = obtener_comentarios_db()
            return df
        else:
            print("Usando base de datos...")
            df = obtener_comentarios_db()
            return df
    except Exception as e:
        print(f"⚠️ Error general en load_data: {e}")
        return None


def load_dashboard(app, df):
    try:
        asyncio.run(create_dashboard(app, df))
    except Exception as e:
        print(f"⚠️ Error al cargar el dashboard: {e}")
