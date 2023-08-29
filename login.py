import streamlit as st
import requests

BASE_URL = 'http://jisparking.com/api/test'

def obtener_usuarios():
    response = requests.get(BASE_URL)
    if response.status_code == 200:
        return response.json()
    else:
        return []

def validar_credenciales(rut, contrasena):
    usuarios = obtener_usuarios()
    for usuario in usuarios:
        if str(usuario['rut']) == rut and usuario['visual_rut'] == contrasena:
            return usuario
    return None

def main():
    st.title("Inicio de Sesión")

    rut = st.text_input("RUT")
    contrasena = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        if rut and contrasena:
            usuario = validar_credenciales(rut, contrasena)
            if usuario is not None and "access_token" in usuario:
                st.success("Inicio de sesión exitoso!")
                st.write(f"Bienvenido, {usuario['nickname']}")

                # Simulamos guardar el token en la sesión
                st.session_state.token = usuario['access_token']

                st.write("Página de bienvenida:")
                st.write("Aquí puedes mostrar contenido exclusivo para usuarios autenticados.")
            else:
                st.error("Credenciales inválidas. No tienes permiso para ingresar.")

if __name__ == "__main__":
    main()



