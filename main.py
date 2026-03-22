import streamlit as st
from google import genai
from google.genai import types
import os
import json
import re
from datetime import datetime

# ==========================================
# ⚙️ CONFIGURACIÓN DEL ADMINISTRADOR
# ==========================================
# Change this word to control the test difficulty for everyone: "Fácil", "Medio", or "Difícil"
DIFICULTAD_DEL_EXAMEN = "Difícil" 

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
# Ensuring the AI knows the correct departments (no cremeria)
generador_instrucciones = f"""
Eres un generador de exámenes para gerentes de La Vaquita Meat Market. 
Departamentos: taquería, carnicería, panadería, pastelería, paletería, frutas/verduras y abarrotes en general.
Genera UNA sola queja de cliente realista en español. No des introducciones ni saludos, solo describe directamente la situación y lo que dice el cliente.
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
    st.session_state.nombre = ""
    st.session_state.escenario = ""
    st.session_state.respuesta_usuario = ""
    st.session_state.resultado = None

# ==========================================
# INTERFAZ DE LA APLICACIÓN
# ==========================================
st.title("📝 Examen Oficial de Certificación HEART")

# FASE 1: Registro
if st.session_state.fase == "login":
    st.write("Bienvenido al examen de resolución de clientes. El sistema generará un escenario único para ti.")
    st.info(f"**Dificultad actual del examen:** {DIFICULTAD_DEL_EXAMEN}")
    
    nombre_input = st.text_input("Ingresa tu nombre completo para comenzar:")
    if st.button("Comenzar Examen"):
        if nombre_input.strip() == "":
            st.warning("Debes ingresar tu nombre.")
        else:
            st.session_state.nombre = nombre_input
            
            # Generar el escenario único
            with st.spinner("Generando tu examen..."):
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=f"Genera el escenario de dificultad {DIFICULTAD_DEL_EXAMEN}.",
                    config=types.GenerateContentConfig(system_instruction=generador_instrucciones)
                )
                st.session_state.escenario = response.text
                st.session_state.fase = "examen"
                st.rerun()

# FASE 2: Tomar el Examen
elif st.session_state.fase == "examen":
    st.write(f"👤 **Gerente evaluado:** {st.session_state.nombre}")
    st.divider()
    
    st.subheader("🔴 Situación del Cliente:")
    st.error(st.session_state.escenario)
    
    st.write("¿Cómo resolverías esta situación utilizando el método HEART? Escribe exactamente lo que dirías y harías.")
    respuesta = st.text_area("Tu respuesta:", height=200)
    
    if st.button("Enviar Respuesta para Calificación"):
        if respuesta.strip() == "":
            st.warning("No puedes enviar un examen en blanco.")
        else:
            st.session_state.respuesta_usuario = respuesta
            
            with st.spinner("El examinador de la IA está evaluando tu respuesta..."):
                prompt_evaluacion = f"Escenario: {st.session_state.escenario}\n\nRespuesta del Gerente: {respuesta}"
                
                eval_response = client.models.generate_content(
                    model='gemini-3.0-pro',
                    contents=prompt_evaluacion,
                    config=types.GenerateContentConfig(
                        system_instruction=evaluador_instrucciones,
                        temperature=0.1 # Keep grading strict and consistent
                    )
                )
                
                # Extraer el JSON de la respuesta de la IA
                try:
                    match = re.search(r'\{.*\}', eval_response.text, re.DOTALL)
                    json_str = match.group(0) if match else eval_response.text
                    resultado_json = json.loads(json_str)
                    st.session_state.resultado = resultado_json
                    st.session_state.fase = "resultados"
                    st.rerun()
                except:
                    st.error("Hubo un error al procesar tu calificación. Por favor, avísale al administrador.")

# FASE 3: Resultados y Boleta de Calificaciones
elif st.session_state.fase == "resultados":
    calificacion = st.session_state.resultado.get("calificacion", 0)
    retro = st.session_state.resultado.get("retroalimentacion", "")
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    if calificacion >= 85:
        st.balloons()
        st.success("¡EXAMEN APROBADO!")
    else:
        st.error("EXAMEN REPROBADO. Necesitas un 85% para pasar.")
    
    # Tarjeta de reporte visual para tomar captura de pantalla
    st.markdown(f"""
    <div style="padding: 20px; border: 2px solid {'#28a745' if calificacion >= 85 else '#dc3545'}; border-radius: 10px; background-color: {'#eafaf1' if calificacion >= 85 else '#fdeded'}; color: black;">
        <h2 style="text-align: center; margin-bottom: 0;">Boleta Oficial La Vaquita</h2>
        <p style="text-align: center; font-size: 14px; margin-top: 0;">{fecha}</p>
        <hr style="border-top: 1px solid black;">
        <p><b>Gerente:</b> {st.session_state.nombre}</p>
        <p><b>Dificultad del Examen:</b> {DIFICULTAD_DEL_EXAMEN}</p>
        <p><b>Calificación Final:</b> <span style="font-size: 24px; font-weight: bold; color: {'#28a745' if calificacion >= 85 else '#dc3545'};">{calificacion}%</span></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    st.subheader("🔍 Análisis del Examinador:")
    st.info(retro)
    
    st.warning("📸 **INSTRUCCIÓN:** Toma una captura de pantalla de tu boleta de calificaciones y envíasela al dueño de la tienda.")
    
    if st.button("Volver al Inicio (Reiniciar)"):
        st.session_state.clear()
        st.rerun()
