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
    try:
        conn = pyodbc.connect(
            f"DRIVER={Config.DRIVER};"
            f"SERVER={Config.SERVER};"
            f"DATABASE={Config.DATABASE};"
            f"UID={Config.USERNAME};"
            f"PWD={Config.get_decrypted_password()};"
            "Encrypt=yes;"
            "TrustServerCertificate=yes;"
        )
        print("Conexión a la base de datos establecida correctamente.")
        return conn
    except pyodbc.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None


def obtener_comentarios_db():
    """
    Obtiene los comentarios desde la base de datos y los devuelve como un DataFrame.

    Retorna:
        pd.DataFrame: DataFrame con los comentarios obtenidos.
    """
    try:
        print("Obteniendo datos de la base de datos...")
        engine = get_db_connection()
        if engine is None:
            raise Exception("No se pudo establecer la conexión a la base de datos.")

        query = "SELECT texto, sentimiento, categoria FROM datos;"  # Ajusta la consulta según sea necesario
        df = pd.read_sql(query, engine)
        print("Datos obtenidos correctamente.")
        return df
    except Exception as e:
        print(f"Error al obtener los datos: {e}")
        return pd.DataFrame()