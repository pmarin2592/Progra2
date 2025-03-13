from cryptography.fernet import Fernet

def generate_key():
    """
    Genera una clave de cifrado y la guarda en un archivo llamado `secret.key`.

    Este método solo debe ejecutarse una vez para generar la clave de cifrado.
    """
    key = Fernet.generate_key()
    with open("./app/database/secret.key", "wb") as key_file:
        key_file.write(key)

def load_key():
    """
    Carga la clave de cifrado desde el archivo `secret.key`.

    Retorna:
        bytes: Clave de cifrado.
    """

    return open("./app/database/secret.key", "rb").read()

def encrypt_message(message):
    """
    Cifra un mensaje utilizando la clave de cifrado.

    Parámetros:
        message (str): El mensaje en texto plano a cifrar.

    Retorna:
        str: Mensaje cifrado en formato de string.
    """
    key = load_key()
    return Fernet(key).encrypt(message.encode()).decode()

def decrypt_message(encrypted_message):
    """
    Descifra un mensaje cifrado utilizando la clave de cifrado.

    Parámetros:
        encrypted_message (str): Mensaje cifrado en formato string.

    Retorna:
        str: Mensaje original en texto plano.
    """
    key = load_key()
    return Fernet(key).decrypt(encrypted_message.encode()).decode()

# Bloque principal para generar la clave de cifrado (solo debe ejecutarse una vez)
if __name__ == "__main__":
    generate_key()  # Ejecutar solo una vez para generar la clave
    print(encrypt_message("Progra2025$"))
    print("Clave generada. Ahora encripta tus credenciales con encrypt_message().")