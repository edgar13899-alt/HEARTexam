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

# Reducimos los filtros de seguridad para permitir simulaciones de clientes enojados
seguridad_baja = [
    types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_ONLY_HIGH"),
    types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_ONLY_HIGH"),
    types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_ONLY_HIGH"),
]

# --- BÓVEDA DE ESCENARIOS (LA MISMA QUE EL ENTRENAMIENTO) ---
departamentos = ["la Carnicería", "la Taquería", "la Panadería", "la Paletería", "las Cajas Principales", "el Pasillo de Abarrotes", "el área de Frutas y Verduras"]

problemas_comunes = [
    "un cliente que YA PAGÓ y llegó a su casa, pero tuvo que regresar muy molesto porque descubrió que le dieron el producto equivocado o le falta un artículo en sus bolsas", 
    "un error en la cocina que causó que una orden previa para recoger se retrasara 20 minutos más de lo prometido, y el cliente está impaciente", 
    "un cliente que YA PAGÓ y revisando su recibo nota que se le cobró de más por un error en el sistema o un letrero confuso, exigiendo la diferencia", 
    "un cliente frustrado que intenta devolver un producto básico (como pan o fruta) argumentando que salió de mala calidad o echado a perder",
    "un empleado que supuestamente le dio un mal trato, lo ignoró o le habló con mala actitud al cliente",
    "un cliente que quiere cambiar un producto básico y cerrado (como unas papas o refresco) pero no tiene el recibo de compra"
]

errores_cliente = [
    "un cliente que por error agarró el producto equivocado (ej. papas picantes en lugar de regulares) y quiere cambiarlo, sintiéndose un poco a la defensiva o avergonzado por su propio error",
    "un cliente que accidentalmente tiró y rompió un frasco de vidrio que ya había pagado antes de salir de la tienda, y pregunta un poco apenado si le pueden dar otro gratis",
    "un cliente que exige un descuento porque leyó mal un letrero de oferta que estaba claramente marcado para otro producto diferente, sintiéndose frustrado"
]

pesadillas_la_vaquita = [
    "un pago que aparece como 'pendiente' en la app del banco del cliente porque la terminal falló, y el cliente se niega rotundamente a volver a pasar la tarjeta por miedo a que se le cobre doble",
    "un cliente que recoge un pastel de cumpleaños personalizado en la panadería y exige un reembolso completo más el pastel gratis porque el nombre está mal escrito, a pesar de que el gerente tiene la hoja de pedido donde el cliente mismo escribió mal el nombre",
    "un cliente furioso que, después de recibir su pedido en el mostrador de la carnicería, hace un escándalo al enterarse de que no hay caja registradora ahí y se niega a hacer una segunda fila en las cajas principales para pagar",
    "un cliente que tiene un carrito lleno con $200 dólares en mandado, pero el sistema de EBT/tarjetas de beneficios del gobierno se cae a nivel nacional. No tiene otra forma de pagar y se niega a dejar el carrito.",
    "un cliente que trae un folleto de ofertas de otro mercado hispano (como La Michoacana) y exige a gritos que le igualen el precio en una venta masiva de fajitas que la tienda físicamente no puede permitirse igualar.",
    "un cliente que le pide al carnicero que le corte de manera especial 15 libras de una carne cara. El carnicero la corta, la empaqueta, y cuando el cliente ve el precio impreso, dice 'siempre no lo quiero' y lo deja ahí, dejando a la tienda con producto mermado que no puede regresar a la vitrina.",
    "una mujer que quiere devolver una sopa de pollo de la taquería argumentando agresivamente que está 'demasiado picante', a pesar de que la receta de la tienda NO lleva absolutamente nada de picante y nadie más se ha quejado de eso jamás.",
    "un cliente se queja furioso de que un empleado fue grosero al pedirle ayuda (lo ignoró, no hizo contacto visual y solo señaló con el dedo). El cliente exige que lo despidan o lo castiguen frente a él, PERO el gerente sabe que el familiar de ese empleado acaba de fallecer, está pasando por un duelo terrible, y solo vino a trabajar porque necesitaba el dinero.",
    "un cliente acusa a una cajera de darle un pésimo servicio y aventarle el recibo, exigiendo hablar con el gerente para que la regañe frente a todos, PERO el gerente sabe que la cajera acaba de ser insultada cruelmente por el cliente anterior y está al borde de las lágrimas tratando de mantener la compostura.",
    "un cliente que llega con $50 dólares en cortes caros de carne, no tiene ningún recibo de compra, y exige agresivamente un reembolso en efectivo, amenazando con hacer un escándalo monumental si el gerente se niega a darle el dinero."
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

    q1 = st.radio("1. Un cliente te está contando furioso que su pedido salió mal. ¿Cuál es tu trabajo en la etapa 'Hear' (Escuchar)?", 
                  ["A) Hacerle preguntas de inmediato para saber a qué hora compró el producto.", 
                   "B) Guardar silencio absoluto, hacer contacto visual y dejar que termine de desahogarse sin interrumpir.", 
                   "C) Decirle que entiendes su molestia para que se calme más rápido.",
                   "D) Empezar a buscar el recibo en el sistema mientras habla."], index=None)

    q2 = st.radio("2. Un cliente se equivocó y agarró papas picantes en lugar de regulares. Quiere cambiarlas y está a la defensiva. ¿Cuál es la manera correcta de manejar esto?", 
                  ["A) Usar Empatía Neutral ('Entiendo la confusión') y SALTARSE la disculpa para no admitir culpa de la tienda.", 
                   "B) Decir 'Siento mucho la confusión' y cambiarle las papas.", 
                   "C) Decirle que él tuvo la culpa por no leer bien, pero que se las cambiarás esta vez.",
                   "D) Darle un descuento del 10% por las molestias."], index=None)

    q3 = st.radio("3. Es domingo y la tienda está llenísima. Un cliente en la fila regular se queja amargamente de que lleva 15 minutos esperando. Por otro lado, un cliente con una orden previa llega y le dices que su comida tardará por un error de la cocina. ¿A quién le ofreces una Cortesía (agua/pan dulce)?", 
                  ["A) A los dos, para mantener el buen servicio.", 
                   "B) Al de la fila regular, para que no haga un escándalo frente a los demás.", 
                   "C) A NINGUNO. En La Vaquita nunca regalamos producto.",
                   "D) SOLO al de la orden retrasada por error de la tienda. Regalar producto por una fila normal destruye la rentabilidad."], index=None)

    q4 = st.radio("4. Un cliente exige que despidas a una cajera porque dice que le hizo 'mala cara'. ¿Qué haces en la etapa Apologize (A)?", 
                  ["A) Te disculpas por el mal comportamiento de la cajera y prometes regañarla.", 
                   "B) Le das la razón al cliente para que se calme.", 
                   "C) Te disculpas SOLO por la 'mala experiencia' del cliente, sin admitir la culpa del empleado antes de investigar.",
                   "D) No te disculpas porque no fue tu culpa."], index=None)

    q5 = st.radio("5. Un cliente te está insultando con lenguaje vulgar porque la terminal rechazó su tarjeta. ¿Qué haces?", 
                  ["A) Tratas de ignorar los insultos y te enfocas en cobrarle para que se vaya rápido.", 
                   "B) Le regalas la compra para evitar un escándalo.", 
                   "C) Te pones a gritarle igual para defender el honor de la tienda.",
                   "D) Aplicas la Regla Cero: Estableces un límite de respeto inmediatamente y, si continúa, le pides que abandone la tienda."], index=None)

    if st.button("Calificar Teoría"):
        score = 0
        if q1 and q1.startswith("B"): score += 20
        if q2 and q2.startswith("A"): score += 20
        if q3 and q3.startswith("D"): score += 20
        if q4 and q4.startswith("C"): score += 20
        if q5 and q5.startswith("D"): score += 20

        st.divider()
        if score == 100:
            st.success(f"¡Calificación: {score}/100! Eres un maestro de las políticas. Ve a la Parte 2.")
        elif score >= 80:
            st.warning(f"Calificación: {score}/100. Casi perfecto. Revisa tus errores antes de la práctica.")
        else:
            st.error(f"Calificación: {score}/100. Reprobado. Necesitas volver a leer el manual.")

# ==========================================
# PARTE 2: EXAMEN PRÁCTICO (Simulador)
# ==========================================
with tab2:
    st.header("El Examen Final: Prueba Práctica")
    st.write("En este examen **NO habrá un tutor ayudándote**. Tendrás que manejar al cliente tú solo usando el método HEART y las políticas de la tienda. Al terminar, presiona 'Terminar y Calificar'.")

    if "exam_history" not in st.session_state:
        st.session_state.exam_history = []
    if "examen_concluido" not in st.session_state:
        st.session_state.examen_concluido = False
    if "examiner_feedback" not in st.session_state:
        st.session_state.examiner_feedback = ""

    actor_instrucciones = """
    Eres el Actor del examen final interactivo en La Vaquita Meat Market. 
    TU ÚNICO OBJETIVO: Actuar como un cliente realista según el nivel de dificultad. TÚ NO EVALÚAS AL GERENTE. 

    REGLAS DE FORMATO:
    1. Primer mensaje:
    **Escenario:** [Describe tu lenguaje corporal estrictamente en TERCERA PERSONA].
    **Cliente:** "[Escribe tu queja inicial en voz alta]".
    2. El resto de la conversación es solo tu diálogo. 

    REGLA DEL GAME MASTER: 
    Si el gerente va a revisar las cámaras, recibo o sistema POS, sal de personaje y dale el resultado: "[Sistema: Efectivamente encuentras la transacción]". Luego responde como cliente. En dificultad Difícil/Extrema, a veces el sistema NO encuentra nada.

    DETALLES CONTEXTUALES: Usa excusas reales. Si el gerente ofrece soluciones lógicas, acéptalas con alivio. Si te dan una cortesía (agua/pan), relaja tu actitud.

    REGLAS DE DIFICULTAD:
    - FÁCIL: Educado.
    - MEDIO: Frustrado pero razonable. Si te ayudan, acepta.
    - DIFÍCIL: Pasivo-agresivo. Si son firmes, te rindes.
    - EXTREMO (ABUSIVO): Furioso y usas insultos. Tu objetivo es ver si el gerente aplica la Regla Cero.

    CÓMO TERMINAR: Escribe "FIN DE LA SIMULACIÓN" en una línea nueva si el gerente completó la interacción, si te pidió que te fueras, o si llegan a 4 turnos.
    """

    examiner_instrucciones = """
    Eres el EXAMINADOR FINAL IMPLACABLE de La Vaquita Meat Market.
    
    Tu trabajo es calificar la transcripción de la simulación del gerente de 0 a 100 y dar un veredicto de APROBADO o REPROBADO. Eres objetivo, estricto y basas tu calificación enteramente en las políticas establecidas.

    REGLAS DE CALIFICACIÓN Y PENALIZACIONES (Empiezan con 100 puntos):
    1. LA REGLA DEL SIMULADOR DE TEXTO (SILENCIO EN 'H'): Dado que es un simulador de texto, la etapa H ocurre implícitamente cuando el gerente lee el primer mensaje. ESTÁ ESTRICTAMENTE PROHIBIDO penalizar al gerente por no escribir en la etapa Hear. 
    2. PREGUNTAS EN RESOLVE (-20 pts): Si el gerente hizo preguntas de investigación (recibos, qué dijo el empleado, etc.) inmediatamente después del primer mensaje del cliente, penalízalos. Las preguntas SOLO deben hacerse en Resolve (R), después de la Empatía (E).
    3. LA TRAMPA DE LA DISCULPA / ERROR DEL CLIENTE (-30 pts): Si el cliente causó el problema (ej. agarró mal el producto), el gerente NO debe disculparse. Si dijeron "lo siento", RESTA PUNTOS. Debieron usar Empatía Neutral.
    4. QUEJAS SOBRE EMPLEADOS (-30 pts): Si la queja fue sobre un empleado y el gerente admitió la culpa del empleado frente al cliente, RESTA PUNTOS. Debieron disculparse solo por la "experiencia".
    5. RENTABILIDAD Y CORTESÍAS (-40 pts): Si regalaron producto, dinero o descuentos por una "experiencia normal" (filas, tienda llena), REPRUÉBALOS. Cortesías son SOLO para errores de la tienda. Regalar "Gift Cards" es un reprobado automático.
    6. REGLA CERO (-40 pts): Si el cliente usó insultos y el gerente no puso un límite firme, REPRUÉBALOS.

    FORMATO DE RESPUESTA:
    1. CALIFICACIÓN FINAL: [0-100]
    2. VEREDICTO: [APROBADO (80+) / REPROBADO]
    3. ANÁLISIS DETALLADO: Explica de manera directa por qué perdieron puntos o por qué fue perfecto. Analiza su ejecución de H-E-A-R-T y las políticas de la tienda.
    """

    if len(st.session_state.exam_history) == 0 and not st.session_state.examen_concluido:
        st.info("Selecciona el nivel de tu examen.")
        difficulty_exam = st.selectbox(
            "Nivel del Examen:",
            ["Fácil", "Medio", "Difícil", "Extremo (Abusivo)", "Casos Especiales (Errores del Cliente)"]
        )

        if st.button("Comenzar Examen Práctico"):
            
            if difficulty_exam in ["Fácil", "Medio"]:
                depto_elegido = random.choice(departamentos)
                problema_elegido = random.choice(problemas_comunes)
                descripcion_problema = f"El escenario ocurre en {depto_elegido}. Trata sobre {problema_elegido}."
            elif difficulty_exam == "Casos Especiales (Errores del Cliente)":
                problema_elegido = random.choice(errores_cliente)
                descripcion_problema = f"CASO ESPECIAL DE ERROR DEL CLIENTE. Situación: {problema_elegido}."
            else:
                pesadilla_elegida = random.choice(pesadillas_la_vaquita)
                descripcion_problema = f"La queja principal DEBE ser exactamente esta: {pesadilla_elegida}."

            hidden_prompt = f"Inicia el examen. Complejidad {difficulty_exam}. {descripcion_problema}. ASEGÚRATE de incluir la pista en tercera persona en Escenario, dejar salto de línea y luego hablar como Cliente."
            
            with st.spinner("Generando escenario de examen..."):
                try:
                    chat = client.chats.create(
                        model="gemini-2.5-flash",
                        config=types.GenerateContentConfig(system_instruction=actor_instrucciones, safety_settings=seguridad_baja)
                    )
                    response = chat.send_message(hidden_prompt)
                    texto_seguro = response.text if response.text else "⚠️ *Filtro activado.*"
                    st.session_state.exam_history.append({"role": "user", "content": hidden_prompt, "hidden": True})
                    st.session_state.exam_history.append({"role": "model", "content": texto_seguro, "hidden": False})
                    st.rerun()
                except Exception as e:
                    st.error("⚠️ Servidor ocupado. Intenta de nuevo.")

    elif not st.session_state.examen_concluido:
        chat_container = st.container()

        with chat_container:
            for message in st.session_state.exam_history:
                if not message.get("hidden", False):
                    ui_role = "assistant" if message["role"] == "model" else "user"
                    with st.chat_message(ui_role):
                        st.markdown(message["content"])

        exam_input = st.chat_input("Escribe tu respuesta como Gerente...")

        if exam_input:
            st.session_state.exam_history.append({"role": "user", "content": exam_input, "hidden": False})

            with chat_container:
                with st.chat_message("user"):
                    st.markdown(exam_input)

                formatted_history = []
                for msg in st.session_state.exam_history[:-1]:
                    formatted_history.append({"role": msg["role"], "parts": [{"text": msg["content"]}]})

                try:
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
                        st.session_state.examen_concluido = True
                        st.rerun()
                except Exception as e:
                    st.session_state.exam_history.pop() 
                    st.error("⚠️ Servidor ocupado. Vuelve a enviar.")

        st.divider()
        st.caption("¿Resolviste el problema? Haz clic abajo para recibir tu calificación.")
        if st.button("Terminar Interacción y Calificar"):
            st.session_state.examen_concluido = True
            st.rerun()

    if st.session_state.examen_concluido:
        for message in st.session_state.exam_history:
            if not message.get("hidden", False):
                ui_role = "assistant" if message["role"] == "model" else "user"
                with st.chat_message(ui_role):
                    st.markdown(message["content"])
                    
        st.divider()
        st.subheader("🛑 TIEMPO FUERA. EXAMEN CONCLUIDO.")
        
        if not st.session_state.examiner_feedback:
            with st.spinner("El Examinador Implacable está calificando tu desempeño..."):
                transcripcion = ""
                for m in st.session_state.exam_history:
                    if not m.get("hidden", False):
                        rol = "Cliente" if m["role"] == "model" else "Gerente"
                        transcripcion += f"{rol}: {m['content']}\n\n"
                
                prompt_examiner = f"Evalúa la siguiente interacción del examen final y entrega la calificación, veredicto y análisis según tus instrucciones estrictas:\n\n{transcripcion}"
                
                try:
                    examiner_response = client.models.generate_content(
                        model="gemini-2.5-pro",
                        contents=prompt_examiner,
                        config=types.GenerateContentConfig(system_instruction=examiner_instrucciones, safety_settings=seguridad_baja)
                    )
                    st.session_state.examiner_feedback = examiner_response.text
                except Exception as e:
                    st.session_state.examiner_feedback = f"⚠️ *Error exacto de Google:* {e}"

        with st.chat_message("assistant", avatar="🎓"):
            st.markdown(st.session_state.examiner_feedback)
            
        st.divider()
        if st.button("Reiniciar Examen"):
            st.session_state.exam_history = []
            st.session_state.examen_concluido = False
            st.session_state.examiner_feedback = ""
            st.rerun()
