import pandas as pd
import pyodbc
from app.database.config import Config

def get_db_connection():
    """
    Establece y retorna una conexión a la base de datos SQL Server.

    Retorna:
        pyodbc.Connection: Objeto de conexión a la base de datos.

    Excepciones:
        Lanza un error si la conexión falla.
    """
    conn = pyodbc.connect(
        f"DRIVER={Config.DRIVER};"
        f"SERVER={Config.SERVER};"
        f"DATABASE={Config.DATABASE};"
        f"UID={Config.USERNAME};"
        f"PWD={Config.get_decrypted_password()};"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
    )
    return conn


# Función para obtener los comentarios de la base de datos
def obtener_comentarios_db():
    print("Obteniendo datos de la base de datos...")
    engine = get_db_connection()
    query = "SELECT texto,sentimiento,categoria FROM datos;"  # Cambia esta consulta a lo que necesites
    df = pd.read_sql(query, engine)
    print("Datos obtenidos correctamente.")
    return df