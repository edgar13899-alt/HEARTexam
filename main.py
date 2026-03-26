import streamlit as st
from google import genai
from google.genai import types
import os
import random

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Examen Final - La Vaquita", 
    page_icon="📝",
    layout="centered"
)

hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """
st.markdown(hide_menu_style, unsafe_allow_html=True)

# --- CONEXIÓN IA Y SEGURIDAD ---
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("¡Falta la clave API! Por favor, configúrala en los Secrets de Streamlit.")
    st.stop()

client = genai.Client(api_key=api_key)

seguridad_baja = [
    types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_ONLY_HIGH"),
    types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_ONLY_HIGH"),
    types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_ONLY_HIGH"),
]

# --- BÓVEDA DE ESCENARIOS ---
departamentos = ["la Carnicería", "la Taquería", "la Panadería", "la Paletería", "las Cajas Principales", "el Pasillo de Abarrotes", "el área de Frutas y Verduras"]
problemas_comunes = [
    "un producto equivocado o faltante", 
    "un tiempo de espera inaceptable", 
    "un problema de calidad o frescura genérico", 
    "un precio cobrado incorrectamente en el sistema", 
    "un derrame o accidente menor en la tienda",
    "un empleado que supuestamente le dio un mal trato, lo ignoró o le habló con mala actitud",
    "un cliente que quiere cambiar un producto básico y cerrado (como unas papas o refresco) pero no tiene el recibo de compra"
]
pesadillas_la_vaquita = [
    "un cliente que recoge un pastel de cumpleaños personalizado en la panadería y exige un reembolso completo más el pastel gratis porque el nombre está mal escrito, a pesar de que el gerente tiene la hoja de pedido donde el cliente mismo escribió mal el nombre",
    "un cliente furioso que, después de recibir su pedido en el mostrador de la carnicería, hace un escándalo al enterarse de que no hay caja registradora ahí y se niega a hacer una segunda fila en las cajas principales para pagar",
    "un cliente que le pide al carnicero que le corte de manera especial 15 libras de una carne cara. El carnicero la corta, la empaqueta, y cuando el cliente ve el precio impreso, dice 'siempre no lo quiero' y lo deja ahí, dejando a la tienda con producto mermado.",
    "una mujer que quiere devolver una sopa de pollo de la taquería argumentando agresivamente que está 'demasiado picante', a pesar de que la receta de la tienda NO lleva picante.",
    "un cliente se queja furioso de que un empleado fue grosero al pedirle ayuda. Exige que lo despidan frente a él, PERO el gerente sabe que el familiar de ese empleado acaba de fallecer.",
    "un cliente que llega con $50 dólares en cortes caros de carne, no tiene ningún recibo de compra, y exige agresivamente un reembolso en efectivo, amenazando con hacer un escándalo."
]

st.title("📝 Examen Final de Gerencia")
st.write("Demuestra que dominas las políticas de La Vaquita Meat Market y el Método HEART.")

tab1, tab2 = st.tabs(["📚 Parte 1: Examen Teórico", "🥩 Parte 2: Examen Práctico (Simulación)"])

# ==========================================
# PARTE 1: EXAMEN TEÓRICO (Multiple Choice)
# ==========================================
with tab1:
    st.header("Examen de Políticas y Procedimientos")
    st.write("Responde las siguientes preguntas basadas en el manual de entrenamiento.")

    q1 = st.radio("1. Un cliente se queja con groserías e insultos personales hacia ti por un error en su ticket. ¿Cuál es tu primera acción?", 
                  ["A) Ofrecerle una disculpa inmediata para calmarlo.", 
                   "B) Aplicar la Regla Cero: Establecer un límite de respeto firme o pedirle que se retire.", 
                   "C) Darle un descuento del 10% por las molestias.",
                   "D) Escuchar en silencio hasta que termine de insultar."], index=None)

    q2 = st.radio("2. Estás en la etapa 'E' (Empatizar) del método HEART. ¿Qué palabra o frase tienes ESTRICTAMENTE PROHIBIDO usar en este paso?", 
                  ["A) 'Comprendo su frustración.'", 
                   "B) 'Me imagino lo molesto que debe ser.'", 
                   "C) 'Lo siento mucho.'",
                   "D) 'Entiendo por qué está enojado.'"], index=None)

    q3 = st.radio("3. Hubo un retraso menor en la Taquería y el cliente lleva 15 minutos esperando. Está molesto pero no es un error grave. ¿Qué debes ofrecerle?", 
                  ["A) Un reembolso en efectivo de $10 dólares.", 
                   "B) Un reembolso total de su orden.", 
                   "C) Una 'Cortesía de bajo costo' (ej. un agua fresca o un pan dulce) para calmarlo mientras espera.",
                   "D) Un descuento del 20% en su próxima compra."], index=None)

    q4 = st.radio("4. Un cliente exige que regañes a una cajera frente a él porque asegura que le hizo 'mala cara'. ¿Qué debes hacer?", 
                  ["A) Llamar a la cajera y reprenderla frente al cliente para que vea que tomas acción.", 
                   "B) Decirle al cliente 'usted tiene toda la razón, ella siempre hace eso'.", 
                   "C) Darle la razón al cliente y ofrecerle mercancía gratis.",
                   "D) Validar la emoción del cliente ('Entiendo que se sintió ignorado') y prometer una investigación interna sin admitir la culpa del empleado públicamente."], index=None)

    q5 = st.radio("5. Un cliente exige un reembolso en efectivo por cortes de carne caros, pero no tiene su recibo de compra. ¿Cuál es la acción correcta?", 
                  ["A) Darle el dinero si hace mucho escándalo para evitar que espante a otros.", 
                   "B) Negar el reembolso en efectivo de manera firme y profesional, ya que sin recibo no hay prueba de compra en nuestra tienda.", 
                   "C) Aceptar la devolución solo si la carne todavía se ve fresca.",
                   "D) Ofrecerle un descuento en su próxima compra para compensarlo."], index=None)

    if st.button("Calificar Teoría"):
        score = 0
        if q1 and q1.startswith("B"): score += 20
        if q2 and q2.startswith("C"): score += 20
        if q3 and q3.startswith("C"): score += 20
        if q4 and q4.startswith("D"): score += 20
        if q5 and q5.startswith("B"): score += 20

        st.divider()
        if score == 100:
            st.success(f"¡Calificación: {score}/100! Eres un maestro de las políticas. Ve a la Parte 2.")
        elif score >= 80:
            st.warning(f"Calificación: {score}/100. Casi perfecto. Revisa tus errores antes de la práctica.")
        else:
            st.error(f"Calificación: {score}/100. Reprobado. Necesitas volver a leer el portal de entrenamiento.")

# ==========================================
# PARTE 2: EXAMEN PRÁCTICO (Simulador)
# ==========================================
with tab2:
    st.header("El Examen Final: Prueba Práctica")
    st.write("En este examen **NO habrá un tutor ayudándote**. Tendrás que manejar al cliente tú solo usando el método HEART de principio a fin. Al terminar, el Evaluador Maestro te dará tu calificación final (Aprobado/Reprobado).")

    actor_instrucciones = """
    Eres el Actor del examen final interactivo en La Vaquita Meat Market. 
    TU ÚNICO OBJETIVO: Actuar como un cliente realista según el nivel de dificultad. TÚ NO EVALÚAS AL GERENTE. 

    REGLAS DE FORMATO:
    1. Primer mensaje: Describe el escenario y tu lenguaje corporal en TERCERA PERSONA. Salto de línea. Luego lo que dices en voz alta.
    2. En el resto de la conversación, SOLO escribe lo que dices en voz alta. 

    REGLA DE SENTIDO COMÚN: 
    Si el gerente ofrece arreglar tu problema o te da una solución justa (o una cortesía si es demora), acéptalo. NO termines la simulación en ese mismo mensaje; espera a que el gerente se despida.

    REGLAS DE DIFICULTAD:
    - FÁCIL: Eres educado. Si te ayudan, acéptalo rápido.
    - MEDIO: Estás frustrado pero eres razonable.
    - DIFÍCIL: Eres manipulador, pasivo-agresivo y exiges más de lo justo.
    - EXTREMO (ABUSIVO): Eres furioso, irracional y usas insultos. Tu objetivo es ver si el gerente aplica la Regla Cero (poner límites).

    CÓMO TERMINAR: Escribe "FIN DE LA SIMULACIÓN" en una línea nueva si el gerente completó la interacción (te dio la solución/se despidió) o si te marcan un límite estricto y te vas.
    """

    examiner_instrucciones = """
    Eres el EXAMINADOR FINAL IMPLACABLE de La Vaquita Meat Market.
    
    Tu trabajo es calificar la transcripción de la simulación del gerente de 0 a 100 y dar un veredicto de APROBADO o REPROBADO. Eres muy estricto con las políticas de la empresa.

    REGLAS DE CALIFICACIÓN (Resta puntos por cada infracción):
    1. ORDEN HEART (-20 pts): ¿Hicieron Hear, Empathize, Apologize, Resolve, Thank en orden? ¿Preguntaron detalles investigativos en la etapa 'Hear' si aplicaba?
    2. VOCABULARIO DE EMPATÍA (-20 pts): ¿Usaron la palabra "lo siento" o "perdón" en la etapa de Empatía? (Deben separar validación de disculpa).
    3. ACUERDO PROHIBIDO (-20 pts): ¿Le dieron la razón al cliente ("usted tiene razón") en lugar de solo validar su emoción?
    4. RENTABILIDAD SUPREMA (-40 pts): ESTA ES LA REGLA DE ORO. Si el gerente regaló dinero, aceptó una devolución sin recibo, o le dio un descuento al cliente cuando era culpa del cliente... REPRUÉBALOS INMEDIATAMENTE. Solo se permiten "Cortesías de bajo costo" (agua fresca/pan dulce) para demoras, o mantenerse firmes con las reglas de salubridad y reembolsos.
    5. CULPAR AL EMPLEADO (-30 pts): Si la queja era sobre un empleado, ¿admitieron la culpa del empleado frente al cliente?
    6. REGLA CERO (-40 pts): Si la dificultad era Extrema (insultos) y el gerente NO puso un límite de respeto, reprueba al gerente por permitir abuso.

    FORMATO DE RESPUESTA:
    1. CALIFICACIÓN FINAL: [0-100]
    2. VEREDICTO: [APROBADO (80+) / REPROBADO]
    3. ANÁLISIS DETALLADO: Explica exactamente qué reglas rompieron o cuáles aplicaron a la perfección. Da ejemplos de lo que escribieron.
    """

    if "exam_history" not in st.session_state:
        st.session_state.exam_history = []

    if len(st.session_state.exam_history) == 0:
        st.info("Selecciona la dificultad asignada para tu examen de esta semana.")
        difficulty_exam = st.selectbox(
            "Nivel del Examen:",
            ["Fácil", "Medio", "Difícil", "Extremo (Abusivo)"]
        )

        if st.button("Comenzar Examen Práctico"):
            
            # Lógica para elegir el escenario según la dificultad
            if difficulty_exam in ["Fácil", "Medio"]:
                depto_elegido = random.choice(departamentos)
                problema_elegido = random.choice(problemas_comunes)
                descripcion_problema = f"El escenario DEBE ocurrir en {depto_elegido}. La queja trata sobre {problema_elegido}."
            else:
                pesadilla_elegida = random.choice(pesadillas_la_vaquita)
                descripcion_problema = f"La queja principal DEBE ser exactamente esta: {pesadilla_elegida}."

            hidden_prompt = f"Inicia el examen final. Entra en personaje generando un problema de complejidad {difficulty_exam}. {descripcion_problema} RECUERDA: La dificultad define la gravedad inicial y tu actitud. ASEGÚRATE de incluir la pista de lenguaje corporal en TERCERA PERSONA en la sección Escenario, mencionando explícitamente si hay otros clientes cerca o no, y DEJAR UN SALTO DE LÍNEA ANTES DEL CLIENTE."
            
            with st.spinner("Generando escenario de examen..."):
                chat = client.chats.create(
                    model="gemini-2.5-flash",
                    config=types.GenerateContentConfig(system_instruction=actor_instrucciones, safety_settings=seguridad_baja)
                )
                response = chat.send_message(hidden_prompt)
                
            texto_seguro = response.text if response.text else "⚠️ *Filtro activado.*"
            st.session_state.exam_history.append({"role": "user", "content": hidden_prompt, "hidden": True})
            st.session_state.exam_history.append({"role": "model", "content": texto_seguro, "hidden": False})
            st.rerun()

    else:
        formatted_history = []
        for msg in st.session_state.exam_history:
            formatted_history.append({"role": msg["role"], "parts": [{"text": msg["content"]}]})

        for message in st.session_state.exam_history:
            if not message.get("hidden", False):
                ui_role = "assistant" if message["role"] == "model" else "user"
                with st.chat_message(ui_role):
                    st.markdown(message["content"])

        exam_input = st.chat_input("Escribe tu respuesta como Gerente...")

        if exam_input:
            with st.chat_message("user"):
                st.markdown(exam_input)
            
            st.session_state.exam_history.append({"role": "user", "content": exam_input, "hidden": False})

            chat_actor = client.chats.create(
                model="gemini-2.5-flash", 
                config=types.GenerateContentConfig(system_instruction=actor_instrucciones, safety_settings=seguridad_baja),
                history=formatted_history
            )

            with st.chat_message("assistant"):
                with st.spinner("El cliente responde..."):
                    response_actor = chat_actor.send_message(exam_input)
                
                texto_actor = response_actor.text if response_actor.text else "⚠️ *Filtro activado.*"
                st.markdown(texto_actor)
            
            st.session_state.exam_history.append({"role": "model", "content": texto_actor, "hidden": False})
            
            if "FIN DE LA SIMULACIÓN" in texto_actor.upper():
                st.divider()
                st.subheader("🛑 TIEMPO FUERA. EXAMEN CONCLUIDO.")
                with st.spinner("El Examinador Maestro está calificando tu desempeño..."):
                    
                    transcripcion = ""
                    for m in st.session_state.exam_history:
                        if not m.get("hidden", False):
                            rol = "Cliente" if m["role"] == "model" else "Gerente"
                            transcripcion += f"{rol}: {m['content']}\n\n"
                    
                    prompt_examiner = f"Evalúa la siguiente interacción del examen final y entrega la calificación, veredicto y análisis según tus instrucciones:\n\n{transcripcion}"
                    
                    try:
                        examiner_response = client.models.generate_content(
                            model="gemini-2.5-pro",
                            contents=prompt_examiner,
                            config=types.GenerateContentConfig(system_instruction=examiner_instrucciones, safety_settings=seguridad_baja)
                        )
                        texto_examiner = examiner_response.text
                    except Exception as e:
                        texto_examiner = f"⚠️ *Error al calificar: {e}*"
                    
                with st.chat_message("assistant", avatar="🎓"):
                    st.markdown(texto_examiner)
                
                st.session_state.exam_history.append({"role": "model", "content": texto_examiner, "hidden": False})
                
        st.divider()
        if st.button("Reiniciar Examen"):
            st.session_state.exam_history = []
            st.rerun()
