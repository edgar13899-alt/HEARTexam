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

# --- BÓVEDA DE ESCENARIOS SEPARADA POR DIFICULTAD ---

# FÁCIL: Errores indiscutibles de la tienda. H-E-A-R-T de manual. Cero trampas.
problemas_faciles = [
    "un cliente en la carnicería que pidió 2 libras de fajita, pero el carnicero se equivocó y le empaquetó bistec regular. El cliente se dio cuenta antes de ir a la caja y está molesto por el descuido",
    "un cliente en la taquería que está molesto porque su orden de tacos se le entregó fría por un descuido de la cocina",
    "un cliente en la panadería que compró un café, pero la máquina estaba mal calibrada y le sirvieron agua manchada en lugar de café, por lo que exige que se lo cambien"
]

# MEDIO: Requiere investigación, recibos, manejo de empleados o fricciones normales de la tienda (filas/agotados).
problemas_medios = [
    "un cliente que se queja porque la fila para pagar en la caja principal está muy larga y lleva esperando 15 minutos",
    "un cliente que está molesto porque llegó a buscar su corte de carne o pan dulce favorito y ya se agotó por el día",
    "un cliente frustrado que intenta devolver un producto básico (como pan o fruta) argumentando que salió de mala calidad o echado a perder",
    "un empleado que supuestamente le dio un mal trato, lo ignoró o le habló con mala actitud al cliente",
    "un cliente que quiere cambiar un producto básico y cerrado (como unas papas o refresco) pero no tiene el recibo de compra",
    "un cliente que YA PAGÓ y llegó a su casa, pero tuvo que regresar muy molesto porque descubrió que le dieron el producto equivocado o le falta un artículo en sus bolsas"
]

# CASOS ESPECIALES: El error es 100% del cliente (Trampa de la Disculpa)
errores_cliente = [
    "un cliente que por error agarró el producto equivocado (ej. papas picantes en lugar de regulares) y quiere cambiarlo, sintiéndose un poco a la defensiva o avergonzado por su propio error",
    "un cliente que accidentalmente tiró y rompió un frasco de vidrio que ya había pagado antes de salir de la tienda, y pregunta un poco apenado si le pueden dar otro gratis",
    "un cliente que exige un descuento porque leyó mal un letrero de oferta que estaba claramente marcado para otro producto diferente, sintiéndose frustrado"
]

# EXTREMO/DIFÍCIL: Escenarios de alta tensión
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

st.info("Selecciona el Nivel de tu Examen. Esto definirá tanto las preguntas teóricas como la dificultad de tu simulación práctica.")
difficulty_exam = st.selectbox(
    "Nivel del Examen:",
    ["Fácil", "Medio", "Difícil", "Extremo (Abusivo)", "Casos Especiales (Errores del Cliente)"]
)
st.divider()

tab1, tab2 = st.tabs(["📚 Parte 1: Examen Teórico", "🥩 Parte 2: Examen Práctico (3 Escenarios)"])

# ==========================================
# PARTE 1: EXAMEN TEÓRICO (Multiple Choice Dinámico)
# ==========================================
with tab1:
    st.header("Examen de Políticas y Procedimientos")
    st.write(f"Preguntas para el nivel: **{difficulty_exam}**")

    if difficulty_exam == "Fácil":
        q1 = st.radio("1. ¿En cuál de las siguientes situaciones deberías usar el método HEART?", 
                      ["A) Cuando un cliente regular está pagando sus compras felizmente en la caja.", 
                       "B) Cuando un cliente molesto y frustrado exige hablar contigo porque le dieron un pedido equivocado.", 
                       "C) Cuando un empleado te pide sus vacaciones.",
                       "D) Cuando un proveedor llega a entregar mercancía por la puerta trasera."], index=None, key="e1")

        q2 = st.radio("2. ¿Qué significa la letra 'H' (Hear) en el método de La Vaquita y cuál es tu trabajo en este paso?", 
                      ["A) Significa interrogar al cliente inmediatamente para saber qué pasó.", 
                       "B) Significa 'Escucha Silenciosa': Debes guardar silencio absoluto y dejar que el cliente se desahogue sin interrumpirlo.", 
                       "C) Significa explicarle las políticas de la tienda al cliente en cuanto empiece a hablar."], index=None, key="e2")

        q3 = st.radio("3. ¿Cuál es el propósito principal de la etapa 'E' (Empatizar)?", 
                      ["A) Validar las emociones del cliente (ej. 'Entiendo su frustración') para conectar con ellos.", 
                       "B) Darle la razón al cliente en absolutamente todo lo que diga.", 
                       "C) Ofrecer una disculpa por el error."], index=None, key="e3")

        q4 = st.radio("4. En la etapa 'A' (Apologize), ¿por qué ofrecemos una disculpa cuando la tienda comete un error real?", 
                      ["A) Para que el cliente se vaya más rápido.", 
                       "B) Para asumir la responsabilidad profesionalmente en nombre de la empresa.", 
                       "C) Para echarle la culpa al cajero o al cocinero frente al cliente."], index=None, key="e4")

        q5 = st.radio("5. ¿Cuál es la regla básica para usar una 'Cortesía de Bajo Costo' (como regalar un agua fresca o un pan dulce)?", 
                      ["A) Se debe regalar a cualquier cliente que lo pida.", 
                       "B) Se debe usar a diario porque la tienda siempre está muy llena.", 
                       "C) Es EXCLUSIVAMENTE para calmar a clientes que sufrieron una demora o inconveniente causado por un error comprobado de la tienda."], index=None, key="e5")

        if st.button("Calificar Teoría (Fácil)"):
            score = 0
            if q1 and q1.startswith("B"): score += 20
            if q2 and q2.startswith("B"): score += 20
            if q3 and q3.startswith("A"): score += 20
            if q4 and q4.startswith("B"): score += 20
            if q5 and q5.startswith("C"): score += 20
            st.divider()
            if score == 100: st.success(f"¡Calificación: {score}/100! Excelente. Ve a la Parte 2.")
            elif score >= 80: st.warning(f"Calificación: {score}/100. Casi perfecto.")
            else: st.error(f"Calificación: {score}/100. Necesitas repasar el manual básico.")

    elif difficulty_exam == "Medio":
        q1 = st.radio("1. Un cliente te está contando frustrado que su pedido salió mal. ¿Cuál es tu trabajo en la etapa 'Hear' (Escuchar)?", 
                      ["A) Hacerle preguntas de inmediato para saber a qué hora compró el producto.", 
                       "B) Guardar silencio absoluto y dejar que termine de desahogarse sin interrumpir.", 
                       "C) Empezar a buscar el recibo en el sistema mientras habla."], index=None, key="m1")

        q2 = st.radio("2. Estás en la etapa de Empatía (E). ¿Qué frase es la correcta según el manual?", 
                      ["A) 'Tiene usted toda la razón, nosotros fallamos.'", 
                       "B) 'Lamento mucho las molestias.'", 
                       "C) 'Entiendo perfectamente lo frustrante que es esta situación.'"], index=None, key="m2")

        q3 = st.radio("3. Un cliente quiere devolver un producto pero NO tiene recibo. ¿En qué etapa le haces preguntas para buscar la transacción en el sistema?", 
                      ["A) En la etapa Hear (H), interrumpiéndolo de inmediato.", 
                       "B) En la etapa Resolve (R), después de haberlo escuchado y empatizado con él.", 
                       "C) Nunca, simplemente le digo que 'no' inmediatamente."], index=None, key="m3")

        q4 = st.radio("4. Es domingo y la tienda está llenísima. Un cliente en la fila regular se queja de que lleva 15 minutos esperando. ¿Qué haces?", 
                      ["A) Le regalo un agua fresca por la molestia.", 
                       "B) Le ofrezco un 10% de descuento en sus compras.", 
                       "C) Empatizo con su espera y le agradezco su paciencia, pero NO le doy cortesías, ya que regalar producto por filas normales destruye la rentabilidad."], index=None, key="m4")

        q5 = st.radio("5. Un cliente se queja de un empleado. ¿Qué debes hacer en la etapa Apologize (A)?", 
                      ["A) Disculparme por el mal comportamiento del empleado frente al cliente.", 
                       "B) Disculparme ÚNICAMENTE por la 'mala experiencia' del cliente, sin admitir la culpa del empleado antes de investigar internamente.", 
                       "C) No disculparme de nada."], index=None, key="m5")

        if st.button("Calificar Teoría (Medio)"):
            score = 0
            if q1 and q1.startswith("B"): score += 20
            if q2 and q2.startswith("C"): score += 20
            if q3 and q3.startswith("B"): score += 20
            if q4 and q4.startswith("C"): score += 20
            if q5 and q5.startswith("B"): score += 20
            st.divider()
            if score == 100: st.success(f"¡Calificación: {score}/100! Excelente. Ve a la Parte 2.")
            elif score >= 80: st.warning(f"Calificación: {score}/100. Casi perfecto.")
            else: st.error(f"Calificación: {score}/100. Necesitas repasar el manual.")

    else:
        q1 = st.radio("1. Un cliente se equivocó y agarró papas picantes en lugar de regulares. Quiere cambiarlas y está a la defensiva. ¿Cuál es la manera correcta de manejar esto?", 
                      ["A) Usar Empatía Neutral ('Entiendo la confusión') y SALTARSE la disculpa (A) para no admitir culpa de la tienda por un error del cliente.", 
                       "B) Decir 'Siento mucho la confusión' y cambiarle las papas.", 
                       "C) Decirle que él tuvo la culpa por no leer bien, pero que se las cambiarás esta vez."], index=None, key="h1")

        q2 = st.radio("2. Un cliente te está insultando con lenguaje vulgar porque la terminal rechazó su tarjeta. ¿Qué haces?", 
                      ["A) Tratas de ignorar los insultos y te enfocas en cobrarle para que se vaya rápido.", 
                       "B) Le regalas la compra para evitar un escándalo.", 
                       "C) Aplicas la Regla Cero: Estableces un límite de respeto inmediatamente y, si continúa, le pides que abandone la tienda."], index=None, key="h2")

        q3 = st.radio("3. En la regla de 'Rentabilidad Suprema', ¿cuándo está justificado ofrecer un descuento de porcentaje en la cuenta total?", 
                      ["A) Para cualquier queja menor, como un cliente que esperó 5 minutos extra.", 
                       "B) Cuando el cliente amenaza con no volver a la tienda.", 
                       "C) EXCLUSIVAMENTE para errores mayores de la tienda (ej. vender un producto caducado o un cobro doble grave)."], index=None, key="h3")

        q4 = st.radio("4. Un cliente no tiene recibo y exige un reembolso en efectivo. Hiciste preguntas de investigación en la etapa Resolve y el sistema NO muestra ninguna transacción. ¿Qué haces?", 
                      ["A) Le das el dinero en efectivo de todas formas para no perderlo como cliente.", 
                       "B) Usas el sistema como escudo neutral ('Revisé minuciosamente y al no aparecer la transacción, no me es posible autorizar un reembolso').", 
                       "C) Le ofreces una tarjeta de regalo (Gift Card) por el monto."], index=None, key="h4")

        q5 = st.radio("5. ¿Cuál es la regla estricta sobre sugerir Tarjetas de Regalo (Gift Cards) o Crédito de Tienda en La Vaquita para resolver quejas?", 
                      ["A) Usarlas solo para clientes muy enojados.", 
                       "B) Usarlas si no tenemos el producto que buscan.", 
                       "C) CERO Tarjetas de Regalo. Jamás se deben ofrecer porque no somos una mega-cadena corporativa."], index=None, key="h5")

        if st.button("Calificar Teoría (Avanzado)"):
            score = 0
            if q1 and q1.startswith("A"): score += 20
            if q2 and q2.startswith("C"): score += 20
            if q3 and q3.startswith("C"): score += 20
            if q4 and q4.startswith("B"): score += 20
            if q5 and q5.startswith("C"): score += 20
            st.divider()
            if score == 100: st.success(f"¡Calificación: {score}/100! Eres un maestro avanzado. Ve a la Parte 2.")
            elif score >= 80: st.warning(f"Calificación: {score}/100. Casi perfecto. Revisa tus errores.")
            else: st.error(f"Calificación: {score}/100. Reprobado. Necesitas volver a leer el manual avanzado.")

# ==========================================
# PARTE 2: EXAMEN PRÁCTICO (3 Escenarios Consolidado)
# ==========================================
with tab2:
    st.header("El Examen Final: Prueba Práctica")
    st.write("Atenderás a **3 clientes diferentes** de forma consecutiva. Al terminar con el tercer cliente, se evaluará tu desempeño global y recibirás tu calificación final.")

    actor_instrucciones = """
    Eres el Actor del examen final interactivo en La Vaquita Meat Market. 
    TU ÚNICO OBJETIVO: Actuar como un cliente realista. NO evalúas al gerente. 

    REGLAS DE FORMATO Y UBICACIÓN FÍSICA:
    1. Primer mensaje:
    **Escenario:** [Describe tu lenguaje corporal en TERCERA PERSONA].
    **Cliente:** "[Escribe tu queja inicial en voz alta]".
    2. El resto de la conversación es solo tu diálogo. 

    REGLA DEL GAME MASTER (CÁMARAS Y SISTEMA) - ¡OBLIGATORIA!: 
    Si el gerente te pide el recibo para revisarlo, o te dice que va a revisar las cámaras o el sistema POS, DEBES salir de personaje INMEDIATAMENTE en ese mismo turno. 
    Añade esto al principio de tu respuesta: "[Sistema: Revisas las cámaras/sistema y confirmas que el cliente dice la verdad]". Luego, responde como cliente. ¡NUNCA ignores la revisión de cámaras ni congeles la interacción! (En dificultad Extrema, a veces el sistema no encuentra nada).

    REGLAS DE DIFICULTAD:
    - FÁCIL: Educado. Problemas sencillos y directos (errores claros de la tienda). NUNCA insultes.
    - MEDIO: Frustrado pero razonable. Reclamos de recibos, filas o empleados. Si te ayudan de forma justa, ACEPTA.
    - DIFÍCIL/ESPECIAL: Pasivo-agresivo. Si son firmes y neutrales, te rindes con indignación.
    - EXTREMO (ABUSIVO): Furioso y usas insultos. Tu objetivo es ver si el gerente aplica la Regla Cero.

    CÓMO TERMINAR: Escribe "FIN DE LA SIMULACIÓN" en una línea nueva si el gerente completó la interacción, si te pidió que te fueras, o si llegan a 4 turnos.
    """

    examiner_instrucciones = """
    Eres el EXAMINADOR FINAL IMPLACABLE de La Vaquita Meat Market.
    
    Tu trabajo es evaluar el desempeño del gerente a través de 3 ESCENARIOS DIFERENTES que se te proporcionarán en la transcripción. 
    Debes dar UNA SOLA calificación final (promedio general) de 0 a 100 y un veredicto de APROBADO (80+) o REPROBADO.

    REGLAS ESTRICTAS DE PENALIZACIONES:
    1. SILENCIO EN 'H': ESTÁ ESTRICTAMENTE PROHIBIDO penalizar al gerente por no escribir frases como "lo escucho". 
    2. PREGUNTAS EN RESOLVE (-20 pts): Las preguntas de investigación SOLO deben hacerse en Resolve (R), después de empatizar (E). Si interroga al cliente al principio, penaliza.
    3. LA TRAMPA DE LA DISCULPA / ERROR DEL CLIENTE (-30 pts): Si el cliente causó el problema, el gerente NO debe disculparse. Si dijeron "lo siento", RESTA PUNTOS.
    4. QUEJAS SOBRE EMPLEADOS (-30 pts): No deben admitir culpa del empleado frente al cliente antes de investigar.
    5. RENTABILIDAD Y CORTESÍAS (-40 pts): Si regalaron producto, dinero o cortesías por "experiencia normal" (filas, tienda llena), penaliza severamente. Cortesías son SOLO para errores de la tienda. Cero "Gift Cards".
    6. REGLA CERO (-40 pts): Si el cliente usó insultos y el gerente no puso un límite firme, penaliza.

    FORMATO DE RESPUESTA REQUERIDO:
    1. CALIFICACIÓN FINAL GLOBAL: [0-100]
    2. VEREDICTO: [APROBADO / REPROBADO]
    3. DESGLOSE POR CLIENTE:
       - Cliente 1: [Breve análisis de sus aciertos/errores en este escenario]
       - Cliente 2: [Breve análisis...]
       - Cliente 3: [Breve análisis...]
    4. COMENTARIO FINAL DE GERENCIA: [Tu consejo final como examinador implacable].
    """

    # Iniciar variables de sesión para el flujo
    if "exam_scenarios" not in st.session_state:
        st.session_state.exam_scenarios = []
    if "current_scenario_idx" not in st.session_state:
        st.session_state.current_scenario_idx = 0
    if "exam_history" not in st.session_state:
        st.session_state.exam_history = []
    if "all_transcripts" not in st.session_state:
        st.session_state.all_transcripts = [] 
    if "scenario_concluido" not in st.session_state:
        st.session_state.scenario_concluido = False
    if "examen_total_concluido" not in st.session_state:
        st.session_state.examen_total_concluido = False
    if "final_feedback" not in st.session_state:
        st.session_state.final_feedback = ""

    # PASO 1: Iniciar el Examen y Generar los 3 Escenarios
    if len(st.session_state.exam_scenarios) == 0:
        if st.button("Comenzar Examen Práctico (3 Escenarios)"):
            with st.spinner("Seleccionando a tus 3 clientes..."):
                if difficulty_exam == "Fácil":
                    elegidos = random.sample(problemas_faciles, 3)
                elif difficulty_exam == "Medio":
                    elegidos = random.sample(problemas_medios, 3)
                elif difficulty_exam == "Casos Especiales (Errores del Cliente)":
                    elegidos = random.sample(errores_cliente, 3)
                else:
                    elegidos = random.sample(pesadillas_la_vaquita, 3)

                scenarios_prompts = []
                for prob in elegidos:
                    scenarios_prompts.append(f"Inicia la simulación. Complejidad {difficulty_exam}. Trata sobre: {prob}. REGLA FÍSICA: Si el cliente ya pagó y regresa a la tienda con un reclamo post-compra, el escenario DEBE ocurrir obligatoriamente en las Cajas Principales o Servicio al Cliente. Si es un pedido activo o fila normal, ocurre en ese departamento. ASEGÚRATE de incluir la pista en tercera persona en Escenario, dejar salto de línea y luego hablar como Cliente.")
                
                st.session_state.exam_scenarios = scenarios_prompts
                
                # Lanzar el primer escenario
                primer_prompt = st.session_state.exam_scenarios[0]
                try:
                    chat = client.chats.create(
                        model="gemini-2.5-flash",
                        config=types.GenerateContentConfig(system_instruction=actor_instrucciones, safety_settings=seguridad_baja)
                    )
                    resp = chat.send_message(primer_prompt)
                    st.session_state.exam_history.append({"role": "user", "content": primer_prompt, "hidden": True})
                    st.session_state.exam_history.append({"role": "model", "content": resp.text, "hidden": False})
                    st.rerun()
                except Exception as e:
                    st.error("⚠️ *Ups, el servidor está ocupado. Intenta nuevamente en unos segundos.*")
                    st.session_state.exam_scenarios = []

    # PASO 4: Calificación Final
    elif st.session_state.examen_total_concluido:
        st.subheader("🛑 EXAMEN CONCLUIDO")
        
        if not st.session_state.final_feedback:
            with st.spinner("El Examinador Implacable está evaluando los 3 escenarios..."):
                
                mega_transcripcion = ""
                for idx, transcript in enumerate(st.session_state.all_transcripts):
                    mega_transcripcion += f"=== INTERACCIÓN CON CLIENTE {idx + 1} ===\n{transcript}\n\n"
                
                prompt_examiner = f"El gerente ha completado sus 3 escenarios. Aquí están las transcripciones completas:\n\n{mega_transcripcion}\n\nPor favor, entrega la Calificación Final, el Veredicto y el Desglose por Cliente según tus instrucciones."
                
                try:
                    examiner_response = client.models.generate_content(
                        model="gemini-2.5-pro",
                        contents=prompt_examiner,
                        config=types.GenerateContentConfig(system_instruction=examiner_instrucciones, safety_settings=seguridad_baja)
                    )
                    st.session_state.final_feedback = examiner_response.text
                except Exception as e:
                    st.error("⚠️ *Ups, el servidor del Evaluador está un poco saturado. Por favor, recarga la página o intenta de nuevo.*")

        if st.session_state.final_feedback:
            with st.chat_message("assistant", avatar="🎓"):
                st.markdown(st.session_state.final_feedback)
                
            st.divider()
            if st.button("Reiniciar Examen Completo"):
                st.session_state.exam_scenarios = []
                st.session_state.current_scenario_idx = 0
                st.session_state.exam_history = []
                st.session_state.all_transcripts = []
                st.session_state.scenario_concluido = False
                st.session_state.examen_total_concluido = False
                st.session_state.final_feedback = ""
                st.rerun()

    # PASO 2 & 3: Manejando un Escenario Activo
    else:
        idx = st.session_state.current_scenario_idx
        st.subheader(f"Cliente {idx + 1} de 3")
        
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.exam_history:
                if not message.get("hidden", False):
                    ui_role = "assistant" if message["role"] == "model" else "user"
                    with st.chat_message(ui_role):
                        st.markdown(message["content"])

        if not st.session_state.scenario_concluido:
            exam_input = st.chat_input("Escribe tu respuesta como Gerente...")

            if exam_input:
                st.session_state.exam_history.append({"role": "user", "content": exam_input, "hidden": False})

                with chat_container:
                    with st.chat_message("user"):
                        st.markdown(exam_input)

                    formatted_history = [{"role": msg["role"], "parts": [{"text": msg["content"]}]} for msg in st.session_state.exam_history[:-1]]

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
                            st.session_state.scenario_concluido = True
                            st.rerun()
                    except Exception as e:
                        st.session_state.exam_history.pop() 
                        st.error("⚠️ *Ups, el servidor está ocupado. Espera 10 segundos y vuelve a enviar.*")

            st.divider()
            if st.button("Terminar Interacción con este Cliente"):
                st.session_state.scenario_concluido = True
                st.rerun()

        # Transición: El escenario actual terminó, guardar en la bóveda y avanzar
        else:
            st.info(f"✅ Has terminado con el Cliente {idx + 1}. Tus respuestas han sido guardadas de forma segura.")
            
            btn_text = f"Siguiente Cliente ({idx + 2} de 3)" if idx < 2 else "Calificar Examen Final"
            
            if st.button(btn_text):
                # 1. Extraer y guardar la transcripción en la bóveda
                transcripcion_actual = ""
                for m in st.session_state.exam_history:
                    if not m.get("hidden", False):
                        rol = "Cliente" if m["role"] == "model" else "Gerente"
                        transcripcion_actual += f"{rol}: {m['content']}\n"
                st.session_state.all_transcripts.append(transcripcion_actual)
                
                # 2. Limpiar el historial para el próximo cliente
                st.session_state.exam_history = []
                st.session_state.scenario_concluido = False
                st.session_state.current_scenario_idx += 1
                
                # 3. Avanzar o Terminar
                if st.session_state.current_scenario_idx == 3:
                    st.session_state.examen_total_concluido = True
                else:
                    # Iniciar el próximo cliente
                    next_prompt = st.session_state.exam_scenarios[st.session_state.current_scenario_idx]
                    try:
                        chat = client.chats.create(
                            model="gemini-2.5-flash",
                            config=types.GenerateContentConfig(system_instruction=actor_instrucciones, safety_settings=seguridad_baja)
                        )
                        resp = chat.send_message(next_prompt)
                        st.session_state.exam_history.append({"role": "user", "content": next_prompt, "hidden": True})
                        st.session_state.exam_history.append({"role": "model", "content": resp.text, "hidden": False})
                    except Exception as e:
                        pass # El try-except principal lo atrapará si hay un error al recargar
                
                st.rerun()
