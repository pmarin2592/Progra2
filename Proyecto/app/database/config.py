from app.database.encryption import decrypt_message

# -------------------------------
# 🔒 CONFIGURACIÓN DE BASE DE DATOS
# -------------------------------
class Config:
    """
    Clase de configuración para la conexión a la base de datos SQL Server.
    Contiene los parámetros necesarios para la conexión, incluyendo el
    método para desencriptar la contraseña almacenada de forma segura.
    """
    DRIVER = '{ODBC Driver 18 for SQL Server}'
    SERVER = 'localhost'
    DATABASE = 'Proyecto'
    USERNAME = 'sa'
    PASSWORD_ENCRYPTED = 'gAAAAABnzhoR5cyjVDRG6Z7gH6STWJ3ngVq8ouF5NmznUhKHR7fNHyvzFHRMkC3E02m_PSd8Ti10uK3sVm3SZzpjBl-lWp2jKw=='  # Reemplaza con tu contraseña encriptada

    @classmethod
    def get_decrypted_password(cls):
        """
        Método para obtener la contraseña desencriptada.
        Utiliza la función `decrypt_message` del módulo `encryption`.
        Maneja posibles errores de desencriptación.
        """
        try:
            return decrypt_message(cls.PASSWORD_ENCRYPTED)
        except Exception as e:
            print(f"Error al desencriptar la contraseña: {e}")
            return None
