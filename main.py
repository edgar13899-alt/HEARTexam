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
    "un cliente que YA PAGÓ y llegó a su casa, pero tuvo que regresar muy molesto porque descubrió que le dieron el producto equivocado o le falta un artículo en sus bolsas", 
    "un error en la cocina que causó que una orden previa para recoger se retrasara 20 minutos más de lo prometido, y el cliente está impaciente", 
    "un cliente que YA PAGÓ y revisando su recibo nota que se le cobró de más por un error en el sistema o un letrero confuso, exigiendo la diferencia", 
    "un cliente frustrado que intenta devolver un producto argumentando que salió de mala calidad o echado a perder, PERO NO TIENE SU RECIBO DE COMPRA",
    "un empleado que supuestamente le dio un mal trato, lo ignoró o le habló con mala actitud al cliente"
]

errores_cliente = [
    "un cliente que por error agarró el producto equivocado (ej. papas picantes en lugar de regulares) y quiere cambiarlo, sintiéndose un poco a la defensiva o avergonzado por su propio error",
    "un cliente que accidentalmente tiró y rompió un frasco de vidrio que ya había pagado antes de salir de la tienda, y pregunta un poco apenado si le pueden dar otro gratis",
    "un cliente que exige un descuento porque leyó mal un letrero de oferta que estaba claramente marcado para otro producto diferente, sintiéndose frustrado"
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

    q3 = st.radio("3. Es domingo a mediodía y hay una fila larguísima en la Taquería. Un cliente que lleva 15 minutos en la fila regular se queja del tiempo de espera. Por otro lado, un cliente que ordenó barbacoa para recoger a las 12:00 PM llega y le dices que su orden tardará 20 minutos más por un error en la cocina. ¿A quién de los dos le ofreces una 'Cortesía de Bajo Costo' (agua fresca/pan dulce)?", 
                  ["A) Al de la fila regular, para que no se desespere.", 
                   "B) A los dos, para mantener un excelente servicio al cliente.", 
                   "C) SOLO al cliente de la orden previa retrasada, ya que la fila regular es un tiempo de espera normal de fin de semana y regalar producto por filas normales destruiría la rentabilidad.",
                   "D) A ninguno. En La Vaquita nunca se regala nada."], index=None)

    q4 = st.radio("4. Un cliente exige que regañes a una cajera frente a él porque asegura que le hizo 'mala cara'. ¿Qué debes hacer?", 
                  ["A) Llamar a la cajera y reprenderla frente al cliente para que vea que tomas acción.", 
                   "B) Decirle al cliente 'usted tiene toda la razón, ella siempre hace eso'.", 
                   "C) Darle la razón al cliente y ofrecerle mercancía gratis.",
                   "D) Validar la emoción del cliente ('Entiendo que se sintió ignorado') y prometer una investigación interna sin admitir la culpa del empleado públicamente."], index=None)

    q5 = st.radio("5. Un cliente quiere devolver un artículo pero no tiene recibo y pagó en efectivo. ¿Cuál es el procedimiento correcto?", 
                  ["A) Decirle inmediatamente 'sin recibo no hay devolución' para no perder tiempo.", 
                   "B) Hacer preguntas para intentar buscar la transacción en el sistema POS, sabiendo que el cliente suele equivocarse con la hora. Si la búsqueda falla, usar el sistema como escudo para negar el reembolso.", 
                   "C) Darle el reembolso de todas formas si hace mucho escándalo para que no asuste a otros clientes.",
                   "D) Ofrecerle un descuento de 50% en su próxima compra como compensación."], index=None)

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
    st.write("En este examen **NO habrá un tutor ayudándote**. Tendrás que manejar al cliente tú solo usando el método HEART de principio a fin. Al terminar, presiona el botón 'Terminar y Calificar' para recibir tu calificación.")

    if "exam_history" not in st.session_state:
        st.session_state.exam_history = []
    if "examen_concluido" not in st.session_state:
        st.session_state.examen_concluido = False
    if "examiner_feedback" not in st.session_state:
        st.session_state.examiner_feedback = ""
    if "api_error" not in st.session_state:
        st.session_state.api_error = False

    actor_instrucciones = """
    Eres el Actor del examen final interactivo en La Vaquita Meat Market. 
    TU ÚNICO OBJETIVO: Actuar como un cliente realista según el nivel de dificultad. TÚ NO EVALÚAS AL GERENTE. 

    REGLAS DE FORMATO (MUY IMPORTANTE):
    1. Para tu PRIMER mensaje, debes separar el contexto objetivo de lo que dices en voz alta. Usa este formato:
    **Escenario:** [Describe tu lenguaje corporal estrictamente en TERCERA PERSONA].
    **Cliente:** "[Escribe tu queja inicial en voz alta]".
    
    2. En el resto de la conversación, SOLO escribe lo que dices en voz alta. 

    NUEVA REGLA DEL GAME MASTER (CÁMARAS Y SISTEMA): 
    Si el gerente te dice que va a revisar las cámaras, el recibo o el sistema POS, debes salir brevemente de tu personaje para darle el resultado de su búsqueda. 
    Añade una línea al principio de tu respuesta que diga: "[Sistema: Revisa la cámara/sistema y efectivamente encuentras el recibo / la transacción]". Luego, responde como cliente (ej. "¿Pudo encontrarlo?"). Si la dificultad es Difícil/Extrema, a veces el sistema NO encuentra la transacción para hacer la situación más tensa.

    DETALLES CONTEXTUALES UNIVERSALES: 
    Usa excusas de la vida real. Si perdiste tu recibo y te preguntan cómo pagaste, inventa si fue tarjeta o efectivo. Si dices efectivo, a menudo confúndete ligeramente con la hora exacta de la compra. Si es un error Tuyo (ej. agarrar mal producto), muéstrate un poco a la defensiva o apenado para salvar tu orgullo. Si el gerente busca la transacción y te dice que NO aparece, te frustrarás, pero si se mantienen firmes con las reglas, eventualmente te rendirás.

    REGLAS DE DIFICULTAD:
    - FÁCIL: Eres educado. Si te ayudan, acéptalo rápido.
    - MEDIO: Estás frustrado pero eres razonable.
    - DIFÍCIL: Eres manipulador, pasivo-agresivo.
    - EXTREMO (ABUSIVO): Eres furioso y usas insultos. Tu objetivo es ver si el gerente aplica la Regla Cero.

    CÓMO TERMINAR: Escribe "FIN DE LA SIMULACIÓN" en una línea nueva si el gerente completó la interacción (te dio la solución/se despidió) o si te marcan un límite estricto y te vas.
    """

    examiner_instrucciones = """
    Eres el EXAMINADOR FINAL IMPLACABLE de La Vaquita Meat Market.
    
    Tu trabajo es calificar la transcripción de la simulación del gerente de 0 a 100 y dar un veredicto de APROBADO o REPROBADO.

    REGLAS DE CALIFICACIÓN (Resta puntos por cada infracción):
    1. PROTOCOLO SIN RECIBO (-30 pts): Si no hay recibo, ¿preguntó el método de pago e intentó buscar en el POS? Si negaron el reembolso inmediatamente, resta puntos. Si regaló dinero sin encontrar la transacción, REPRUÉBALO.
    2. QUEJAS SOBRE EMPLEADOS (-30 pts): Si la queja es sobre un empleado, el gerente DEBIÓ escuchar en silencio en (H), disculparse SOLO por la experiencia en (A) sin admitir culpa del empleado, y hacer preguntas de investigación en (R) prometiendo revisión interna. Si el gerente interrogó en (H) o admitió la culpa del empleado en (A), RESTA PUNTOS FUERTEMENTE.
    3. LA TRAMPA DE LA DISCULPA / ERROR DEL CLIENTE (-30 pts): Si el cliente causó el problema (ej. agarró mal el producto, leyó mal el letrero), el gerente NO debe disculparse ("lo siento", "siento la confusión"). También resta puntos si el gerente culpó a la tienda ("nuestros letreros están muy juntos") o asumió el estado del cliente ("estaba de prisa"). Debieron usar "Empatía Neutral" ("Entiendo la confusión, a todos nos pasa") y saltar a Resolve.
    4. ORDEN HEART (-20 pts): ¿Hicieron H, E, A, R, T? (Excluyendo la A si es error del cliente).
    5. RENTABILIDAD SUPREMA (-40 pts): CERO descuentos injustificados. CERO regalos por filas normales.
    6. REGLA CERO (-40 pts): Si hay insultos, deben poner límites.

    FORMATO DE RESPUESTA:
    1. CALIFICACIÓN FINAL: [0-100]
    2. VEREDICTO: [APROBADO (80+) / REPROBADO]
    3. ANÁLISIS DETALLADO: Explica exactamente qué reglas rompieron o cuáles aplicaron a la perfección. Da ejemplos de lo que escribieron.
    """

    if len(st.session_state.exam_history) == 0 and not st.session_state.examen_concluido:
        st.info("Selecciona la dificultad asignada para tu examen de esta semana.")
        difficulty_exam = st.selectbox(
            "Nivel del Examen:",
            ["Fácil", "Medio", "Difícil", "Extremo (Abusivo)", "Casos Especiales (Errores del Cliente)"]
        )

        if st.button("Comenzar Examen Práctico"):
            
            if difficulty_exam in ["Fácil", "Medio"]:
                depto_elegido = random.choice(departamentos)
                problema_elegido = random.choice(problemas_comunes)
                descripcion_problema = f"La queja trata sobre {problema_elegido}. FÍSICAMENTE: El cliente se acerca a ti en las Cajas Principales."
            elif difficulty_exam == "Casos Especiales (Errores del Cliente)":
                problema_elegido = random.choice(errores_cliente)
                descripcion_problema = f"ESTE ES UN CASO ESPECIAL DE ERROR DEL CLIENTE. La situación es: {problema_elegido}. FÍSICAMENTE: El cliente se acerca a ti en las Cajas Principales."
            else:
                pesadilla_elegida = random.choice(pesadillas_la_vaquita)
                descripcion_problema = f"La queja principal DEBE ser exactamente esta: {pesadilla_elegida}."

            hidden_prompt = f"Inicia el examen final. Complejidad {difficulty_exam}. {descripcion_problema}. RECUERDA: La dificultad define la gravedad inicial y tu actitud. ASEGÚRATE de incluir la pista de lenguaje corporal en TERCERA PERSONA en la sección Escenario, mencionando explícitamente si hay otros clientes cerca o no, y DEJAR UN SALTO DE LÍNEA ANTES DEL CLIENTE."
            
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
                    st.error("⚠️ Los servidores de Google están experimentando alta demanda (Error 503). Por favor, intenta iniciar el examen de nuevo en unos segundos.")

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
                    st.error("⚠️ El servidor de Google tuvo un problema de conexión (Error 503). Por favor, vuelve a enviar tu mensaje.")

        st.divider()
        st.caption("¿Resolviste el problema? Haz clic abajo para recibir tu calificación. No esperes a que el cliente se vaya solo.")
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
                    st.session_state.examiner_feedback = examiner_response.text
                    st.session_state.api_error = False
                except Exception as e:
                    st.session_state.api_error = True

        if st.session_state.api_error:
            st.error("⚠️ Los servidores de Google están experimentando alta demanda (Error 503). No hemos podido generar tu calificación.")
            if st.button("🔄 Reintentar Calificación"):
                st.session_state.examiner_feedback = ""
                st.session_state.api_error = False
                st.rerun()
        else:
            with st.chat_message("assistant", avatar="🎓"):
                st.markdown(st.session_state.examiner_feedback)
                
            st.divider()
            if st.button("Reiniciar Examen"):
                st.session_state.exam_history = []
                st.session_state.examen_concluido = False
                st.session_state.examiner_feedback = ""
                st.session_state.api_error = False
                st.rerun()
