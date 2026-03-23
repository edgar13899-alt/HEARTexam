import streamlit as st
from google import genai
from google.genai import types
import os
import json
import re
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import random

# ==========================================
# ⚙️ CONFIGURACIÓN DEL ADMINISTRADOR
# ==========================================
DIFICULTAD_DEL_EXAMEN = "Fácil" 
URL_DE_TU_HOJA = "https://docs.google.com/spreadsheets/d/1XI1QnWKtp2BQUKWQqjsWRThKd6axbEHjfnfqv3AKTNY/edit?gid=0#gid=0"

# --- LISTAS ALEATORIAS PARA FORZAR VARIEDAD ---
DEPARTAMENTOS = ["la taquería", "la carnicería", "la panadería", "la pastelería", "la paletería", "frutas y verduras", "las cajas registradoras"]
PROBLEMAS = [
    "un producto echado a perder o de mala calidad", 
    "un empleado que ignoró al cliente o le contestó mal", 
    "un tiempo de espera excesivamente largo", 
    "un cobro doble en la tarjeta o problema con el cambio", 
    "un pedido que le entregaron completamente equivocado", 
    "un precio en el estante que no coincide con el de la caja"
]

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Examen HEART - La Vaquita", page_icon="📝", layout="centered")

hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """
st.markdown(hide_menu_style, unsafe_allow_html=True)

# --- CONEXIÓN IA ---
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("¡Falta la clave API! Configúrala en los Secrets de Streamlit.")
    st.stop()

client = genai.Client(api_key=api_key)

# --- INSTRUCCIONES DEL SISTEMA ---
generador_instrucciones = f"""
Eres un generador de exámenes para gerentes de La Vaquita Meat Market. 
Genera UNA sola queja de cliente realista en español. No des introducciones ni saludos, solo describe directamente la situación y las palabras exactas que dice el cliente.
El nivel de dificultad EXIGIDO para este examen es: {DIFICULTAD_DEL_EXAMEN}.
"""

evaluador_instrucciones = """
Eres un examinador estricto. Evalúa la respuesta del gerente al escenario dado usando el método HEART.
- H (Escuchar/Silencio)
- E (Empatizar sin darle la razón absoluta)
- A (Disculpa específica y asumiendo responsabilidad)
- R (Resolver. DEBEN reubicar al cliente si hace un escándalo público. Cuidado con los descuentos inmerecidos).
- T (Agradecer)

Debes devolver TU EVALUACIÓN EXCLUSIVAMENTE en el siguiente formato JSON, sin texto adicional:
{
  "calificacion": [Un número del 0 al 100],
  "retroalimentacion": "[Tu análisis detallado de qué hicieron bien y qué les faltó según las reglas]"
}
"""

# --- GESTIÓN DEL ESTADO ---
if "fase" not in st.session_state:
    st.session_state.fase = "login"
if "nombre" not in st.session_state:
    st.session_state.nombre = ""
if "numero_actual" not in st.session_state:
    st.session_state.numero_actual = 1
if "escenario_actual" not in st.session_state:
    st.session_state.escenario_actual = ""
if "evaluaciones" not in st.session_state:
    st.session_state.evaluaciones = []

# ==========================================
# INTERFAZ DE LA APLICACIÓN
# ==========================================
st.title("📝 Examen Oficial de Certificación HEART")

# FASE 1: Registro
if st.session_state.fase == "login":
    st.write("Bienvenido al examen de resolución de clientes. El sistema generará **3 escenarios únicos** para ti.")
    st.info(f"**Dificultad actual del examen:** {DIFICULTAD_DEL_EXAMEN}")
    
    nombre_input = st.text_input("Ingresa tu nombre completo para comenzar:")
    if st.button("Comenzar Examen"):
        if nombre_input.strip() == "":
            st.warning("Debes ingresar tu nombre.")
        else:
            st.session_state.nombre = nombre_input
            
            depto1 = random.choice(DEPARTAMENTOS)
            problema1 = random.choice(PROBLEMAS)
            prompt_aleatorio = f"Genera el escenario número 1 de dificultad {DIFICULTAD_DEL_EXAMEN}. El escenario DEBE ocurrir en {depto1} y el problema del cliente DEBE ser sobre {problema1}."
            
            with st.spinner("Generando tu primer escenario..."):
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt_aleatorio,
                    config=types.GenerateContentConfig(system_instruction=generador_instrucciones)
                )
                st.session_state.escenario_actual = response.text
                st.session_state.fase = "examen"
                st.rerun()

# FASE 2: Tomar el Examen
elif st.session_state.fase == "examen":
    st.write(f"👤 **Gerente:** {st.session_state.nombre} | 📝 **Escenario {st.session_state.numero_actual} de 3**")
    st.divider()
    
    st.subheader("🔴 Situación del Cliente:")
    st.error(st.session_state.escenario_actual)
    
    st.write("¿Cómo resolverías esta situación utilizando el método HEART? Escribe exactamente lo que dirías y harías.")
    
    respuesta = st.text_area("Tu respuesta:", key=f"respuesta_{st.session_state.numero_actual}", height=200)
    
    if st.button("Enviar Respuesta"):
        if respuesta.strip() == "":
            st.warning("No puedes enviar una respuesta en blanco.")
        else:
            with st.spinner("El examinador de la IA está evaluando tu respuesta..."):
                prompt_evaluacion = f"Escenario: {st.session_state.escenario_actual}\n\nRespuesta del Gerente: {respuesta}"
                
                eval_response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt_evaluacion,
                    config=types.GenerateContentConfig(
                        system_instruction=evaluador_instrucciones,
                        temperature=0.1,
                        response_mime_type="application/json"
                    )
                )
                
                try:
                    resultado_json = json.loads(eval_response.text)
                    
                    st.session_state.evaluaciones.append({
                        "escenario": st.session_state.escenario_actual,
                        "respuesta": respuesta,
                        "calificacion": resultado_json.get("calificacion", 0),
                        "retroalimentacion": resultado_json.get("retroalimentacion", "")
                    })
                    
                    # Cambio a 3 escenarios
                    if st.session_state.numero_actual < 3:
                        st.session_state.numero_actual += 1
                        
                        depto_nuevo = random.choice(DEPARTAMENTOS)
                        problema_nuevo = random.choice(PROBLEMAS)
                        prompt_gen_nuevo = f"Genera OTRO escenario de dificultad {DIFICULTAD_DEL_EXAMEN}. DEBE ocurrir en {depto_nuevo} y el problema DEBE ser sobre {problema_nuevo}. Tiene que ser completamente diferente a este escenario anterior: '{st.session_state.escenario_actual}'"
                        
                        with st.spinner(f"Generando el escenario {st.session_state.numero_actual}..."):
                            response_nuevo = client.models.generate_content(
                                model='gemini-2.5-flash',
                                contents=prompt_gen_nuevo,
                                config=types.GenerateContentConfig(system_instruction=generador_instrucciones)
                            )
                            st.session_state.escenario_actual = response_nuevo.text
                        st.rerun()
                    else:
                        st.session_state.fase = "resultados"
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Error técnico de lectura: {e}")

# FASE 3: Resultados y Registro en Base de Datos
elif st.session_state.fase == "resultados":
    
    # Se divide entre 3 para el promedio exacto
    suma_calificaciones = sum(evaluacion["calificacion"] for evaluacion in st.session_state.evaluaciones)
    calificacion_final = round(suma_calificaciones / 3)
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    if "guardado" not in st.session_state:
        try:
            cred_dict = json.loads(st.secrets["google_credentials"])
            scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
            creds = Credentials.from_service_account_info(cred_dict, scopes=scopes)
            gclient = gspread.authorize(creds)
            
            sheet = gclient.open_by_url(URL_DE_TU_HOJA).sheet1
            sheet.append_row([st.session_state.nombre, DIFICULTAD_DEL_EXAMEN, calificacion_final, fecha])
            
            st.session_state.guardado = True
            st.toast("✅ Calificación final registrada en el sistema.")
        except Exception as e:
            st.error(f"Error de base de datos: {e}")

    if calificacion_final >= 85:
        st.balloons()
        st.success("¡EXAMEN APROBADO!")
    else:
        st.error("EXAMEN REPROBADO. Necesitas un promedio de 85% para pasar.")
    
    color_borde = '#28a745' if calificacion_final >= 85 else '#dc3545'
    color_fondo = '#eafaf1' if calificacion_final >= 85 else '#fdeded'
    
    boleta_html = f"""
    <div style="padding: 20px; border: 2px solid {color_borde}; border-radius: 10px; background-color: {color_fondo}; color: black;">
        <h2 style="text-align: center; margin-bottom: 0;">Boleta Oficial La Vaquita</h2>
        <p style="text-align: center; font-size: 14px; margin-top: 0;">{fecha}</p>
        <hr style="border-top: 1px solid black;">
        <p><b>Gerente:</b> {st.session_state.nombre}</p>
        <p><b>Dificultad del Examen:</b> {DIFICULTAD_DEL_EXAMEN}</p>
        <p><b>Calificación Promedio:</b> <span style="font-size: 24px; font-weight: bold; color: {color_borde};">{calificacion_final}%</span></p>
    </div>
    """
    st.markdown(boleta_html, unsafe_allow_html=True)
    
    st.write("---")
    st.header("🔍 Desglose de Resultados")
    
    for i, evaluacion in enumerate(st.session_state.evaluaciones):
        with st.expander(f"Ver retroalimentación del Escenario {i+1} (Calificación: {evaluacion['calificacion']}%)", expanded=True):
            st.info(evaluacion["retroalimentacion"])
            st.write("**Tu respuesta fue:**")
            st.caption(evaluacion["respuesta"])
    
    st.divider()
    if st.button("Volver al Inicio"):
        st.session_state.clear()
        st.rerun()
