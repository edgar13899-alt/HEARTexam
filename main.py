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
problemas_faciles = [
    "un cliente en la carnicería que pidió 2 libras de fajita, pero el carnicero se equivocó y le empaquetó bistec regular. El cliente sigue frente a la vitrina, apenas revisó el paquete y está molesto por el descuido. REGLA ESTRICTA: El cliente NO ha pagado ni ha salido de la tienda.",
    "un cliente en la taquería que está comiendo en las mesas de la tienda y se levanta molesto al mostrador porque sus tacos se los acaban de entregar fríos por un descuido de la cocina. REGLA ESTRICTA: El cliente NO ha salido de la tienda, está consumiendo en el lugar.",
    "un cliente en la panadería que acaba de recibir su café en el mostrador, da un sorbo ahí mismo, y nota que la máquina estaba mal calibrada (le sirvieron agua manchada). Exige que se lo cambien. REGLA ESTRICTA: El cliente sigue frente al mostrador y acaba de recibir el producto."
]

problemas_medios = [
    "un cliente que se queja porque la fila para pagar en la caja principal está muy larga y lleva esperando 15 minutos",
    "un cliente que está molesto porque llegó a buscar su corte de carne o pan dulce favorito y ya se agotó por el día",
    "un cliente frustrado que intenta devolver un producto básico (como pan o fruta) argumentando que salió de mala calidad o echado a perder",
    "un empleado que supuestamente le dio un mal trato, lo ignoró o le habló con mala actitud al cliente",
    "un cliente que quiere cambiar un producto básico y cerrado (como unas papas o refresco) pero no tiene el recibo de compra",
    "un cliente que YA PAGÓ y llegó a su casa, pero tuvo que regresar muy molesto porque descubrió que le dieron el producto equivocado o le falta un artículo en sus bolsas"
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
st.write("Demuestra que dominas las políticas de La Vaquita Meat Market y la psicología del Método HEART.")

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
    st.header("Examen de Políticas y Psicología")
    st.write(f"Preguntas para el nivel: **{difficulty_exam}**")

    if difficulty_exam == "Fácil":
        q1 = st.radio("1. En la técnica de 'Empatía Neutral para Salvar el Ego', ¿cuál es la mejor frase para desarmar a un cliente que se equivocó de producto?", 
                      ["A) 'Nuestros letreros pueden ser un poco confusos, lo entiendo.'", 
                       "B) 'Entiendo la confusión, a mí también se me pasa por alto al hacer el mandado.'", 
                       "C) 'Usted se equivocó de pasillo, pero se lo cambio.'"], index=None, key="e1")

        q2 = st.radio("2. ¿Por qué es psicológicamente importante usar el 'Giro de Investigación' (ej. 'Para ayudarle, ¿me permite su recibo?') en la etapa Resolve?", 
                      ["A) Porque legalmente debes comprobar la compra en el sistema antes de poder ofrecer cualquier tipo de disculpa o empatía al cliente.", 
                       "B) Porque evita que el cliente se ponga a la defensiva, cambiándote de un 'interrogador' a un 'socio' que busca solucionarle el problema.", 
                       "C) Porque te permite ganar unos segundos extra para pensar en qué descuento o cortesía ofrecerle al cliente mientras buscas el recibo."], index=None, key="e2")

        q3 = st.radio("3. ¿Cuál es el propósito principal de la etapa 'E' (Empatizar)?", 
                      ["A) Validar las emociones y la experiencia del cliente (ej. 'Entiendo su frustración') para conectar con él ANTES de intentar resolver el problema.", 
                       "B) Darle la razón al cliente sobre los hechos ocurridos para que se calme rápidamente y acepte que la tienda asume toda la responsabilidad.", 
                       "C) Explicar amablemente las políticas de la tienda desde el principio para que el cliente entienda por qué ocurrió el problema y baje su enojo."], index=None, key="e3")

        q4 = st.radio("4. En la etapa 'A' (Apologize), ¿cuándo debes usar una 'Disculpa Operativa'?", 
                      ["A) Cuando la fila está muy larga.", 
                       "B) Cuando hay un error comprobado y evidente de la tienda, como entregar la carne equivocada en el mostrador.", 
                       "C) Cuando el cliente leyó mal un precio."], index=None, key="e4")

        q5 = st.radio("5. ¿Qué significa la letra 'H' (Hear) en el método de La Vaquita?", 
                      ["A) Significa interrogar al cliente inmediatamente para saber qué pasó.", 
                       "B) Significa 'Escucha Silenciosa': Debes guardar silencio absoluto y dejar que el cliente se desahogue sin interrumpirlo.", 
                       "C) Significa explicarle las políticas de la tienda."], index=None, key="e5")

        if st.button("Calificar Teoría (Fácil)"):
            score = 0
            if q1 and q1.startswith("B"): score += 20
            if q2 and q2.startswith("B"): score += 20
            if q3 and q3.startswith("A"): score += 20
            if q4 and q4.startswith("B"): score += 20
            if q5 and q5.startswith("B"): score += 20
            st.divider()
            if score == 100: st.success(f"¡Calificación: {score}/100! Excelente. Ve a la Parte 2.")
            elif score >= 80: st.warning(f"Calificación: {score}/100. Casi perfecto.")
            else: st.error(f"Calificación: {score}/100. Necesitas repasar la psicología básica.")

    elif difficulty_exam == "Medio":
        q1 = st.radio("1. ¿En qué situación operativa ESPECÍFICA se debe activar el Método HEART en lugar del protocolo normal de servicio al cliente?", 
                      ["A) Siempre que un cliente haga una pregunta sobre los precios o ubicaciones de los productos en la tienda.", 
                       "B) Cuando el cliente expresa frustración, exige una excepción a la política, o existe un riesgo de escalada emocional que amenaza la rentabilidad o la experiencia.", 
                       "C) Exclusivamente cuando la tienda comete un error comprobado que resulta en una pérdida económica para el cliente."], index=None, key="m1")

        q2 = st.radio("2. Tienes que negarle un reembolso a un cliente porque no tiene recibo. ¿Por qué debes usar 'El Escudo del Sistema' (ej. 'El sistema no me permite autorizarlo')?", 
                      ["A) Para despersonalizar el rechazo, evitando que el problema se convierta en una pelea personal entre tú y el cliente.", 
                       "B) Para demostrarle al cliente que conoces el manual de operaciones y que tu decisión como gerente es final, reafirmando tu autoridad.", 
                       "C) Para ganar tiempo mientras llamas a un gerente de mayor rango que tenga la clave especial para saltarse la política de devoluciones."], index=None, key="m2")

        q3 = st.radio("3. Un cliente se queja de la actitud de un empleado. Usas una 'Disculpa de Experiencia' diciendo: 'Lamento mucho su mala experiencia hoy'. ¿Por qué NO admites que el empleado tuvo la culpa?", 
                      ["A) Porque al admitir la culpa del empleado, te obligas automáticamente a darle al cliente un producto gratis según las reglas de Rentabilidad Suprema.", 
                       "B) Porque nunca debes admitir la culpa de un empleado frente al cliente antes de poder investigar las cámaras internamente, para proteger a tu equipo y evitar responsabilidades prematuras.", 
                       "C) Porque el cliente podría aprovechar la situación para exigir que llames al empleado y lo regañes públicamente frente a los demás clientes."], index=None, key="m3")

        q4 = st.radio("4. Si ya ofreciste una solución (ej. esperar 15 minutos por pollo fresco) y el cliente la rechaza diciendo '¡No tengo tiempo para esperar!', ¿cuál es la ejecución correcta del 'Micro-Loop'?", 
                      ["A) Repetir la misma solución con un tono más firme para mantener el control.", 
                       "B) Ofrecer inmediatamente un descuento del 10% para compensar la falta de tiempo.", 
                       "C) Validar la nueva restricción de tiempo neutralmente y pivotar de inmediato ofreciendo nuevas opciones ('Ilusión de Control')."], index=None, key="m4")

        q5 = st.radio("5. Un cliente esperó 20 minutos mientras buscabas su recibo perdido en el sistema para ayudarlo. ¿Qué técnica debes usar al despedirte (Thank)?", 
                      ["A) El Reenfoque de Retroalimentación.", 
                       "B) El Refuerzo de Paciencia (ej. 'Agradezco su paciencia y comprensión'), para recompensar el comportamiento positivo.", 
                       "C) La Despedida Firme."], index=None, key="m5")

        if st.button("Calificar Teoría (Medio)"):
            score = 0
            if q1 and q1.startswith("B"): score += 20
            if q2 and q2.startswith("A"): score += 20
            if q3 and q3.startswith("B"): score += 20
            if q4 and q4.startswith("C"): score += 20
            if q5 and q5.startswith("B"): score += 20
            st.divider()
            if score == 100: st.success(f"¡Calificación: {score}/100! Excelente. Ve a la Parte 2.")
            elif score >= 80: st.warning(f"Calificación: {score}/100. Casi perfecto.")
            else: st.error(f"Calificación: {score}/100. Necesitas repasar el manual.")

    else:
        q1 = st.radio("1. Un cliente está claramente estresado por el tiempo y mira su reloj constantemente. Según el 'Enfoque Positivo', ¿por qué está PROHIBIDO decirle 'Entiendo que lleva prisa'?", 
                      ["A) Porque el cliente podría ofenderse al pensar que lo estás apresurando para que se vaya.", 
                       "B) Porque actuar como un 'espejo' de su estrés solo refuerza y aumenta su ansiedad. Se debe usar una frase centrada en el alivio, como 'para que pueda seguir con su día'.", 
                       "C) Porque implica que la tienda es la culpable de su retraso."], index=None, key="h1")

        q2 = st.radio("2. Aplicas la 'Regla Cero' a un cliente que está usando lenguaje vulgar y le pides que se retire. ¿Qué técnica debes usar para cerrar la interacción (Thank)?", 
                      ["A) La Despedida Firme (ej. 'Agradezco su visita, pero por las faltas de respeto le pido que se retire'), ya que es estéril, profesional y no deja espacio al debate.", 
                       "B) El Refuerzo de Paciencia (ej. 'Gracias por entender'), asumiendo que el cliente dejará de insultar si lo tratas con demasiada amabilidad.", 
                       "C) Cero Disculpas / Empatía Neutral (ej. 'Entiendo que esté enojado, por favor váyase'), para no admitir culpa mientras lo expulsas de la tienda."], index=None, key="h2")

        q3 = st.radio("3. Un cliente te informa que en el pasillo de lácteos hay un derrame. Al cerrar la interacción, usas el 'Reenfoque de Retroalimentación' (ej. 'Gracias a usted, puedo ir a limpiarlo'). ¿Por qué funciona?", 
                      ["A) Acaricia su ego, transformándolo de un 'quejumbroso molesto' a un 'consultor valioso' que acaba de ayudar a la tienda a evitar un accidente.", 
                       "B) Porque desvía su atención del peligro del derrame hacia tu excelente actitud de servicio, minimizando la gravedad del problema original.", 
                       "C) Porque sirve como una 'Disculpa Operativa' disfrazada, asumiendo la culpa del derrame sin tener que ofrecerle ningún producto de compensación."], index=None, key="h3")

        q4 = st.radio("4. El carnicero empacó pollo en lugar de bistec. El cliente sigue en el mostrador y se da cuenta en 30 segundos. Según la regla de Rentabilidad Suprema, ¿qué haces?", 
                      ["A) Le ofrezco un 10% de descuento por el error de la tienda.", 
                       "B) Uso una Disculpa Operativa y le cambio el producto de inmediato. CERO DESCUENTOS por errores menores de mostrador.", 
                       "C) Le regalo un agua fresca."], index=None, key="h4")

        q5 = st.radio("5. ¿Cuál es la regla estricta sobre sugerir Tarjetas de Regalo (Gift Cards) o Crédito de Tienda en La Vaquita para resolver quejas?", 
                      ["A) Usarlas solo para clientes muy enojados.", 
                       "B) Usarlas si no tenemos el producto que buscan.", 
                       "C) CERO Tarjetas de Regalo. Jamás se deben ofrecer porque no somos una mega-cadena corporativa."], index=None, key="h5")

        if st.button("Calificar Teoría (Avanzado)"):
            score = 0
            if q1 and q1.startswith("B"): score += 20
            if q2 and q2.startswith("A"): score += 20
            if q3 and q3.startswith("A"): score += 20
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
    st.write("Atenderás a **3 clientes diferentes** de forma consecutiva. Al terminar, el Examinador te evaluará usando la estricta Rúbrica de 100 Puntos.")

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
    Añade esto al principio de tu respuesta: "[Sistema: Revisas las cámaras/sistema y confirmas que el cliente dice la verdad]". Luego, responde como cliente. ¡NUNCA ignores la revisión de cámaras ni congeles la interacción!

    REGLAS DE DIFICULTAD:
    - FÁCIL: Educado. Problemas sencillos y directos (errores claros de la tienda EN EL MOSTRADOR). NUNCA insultes.
    - MEDIO: Frustrado pero razonable. Reclamos de recibos, filas o empleados. Si te ayudan de forma justa, ACEPTA.
    - DIFÍCIL/ESPECIAL: Pasivo-agresivo. Si son firmes y neutrales, te rindes con indignación.
    - EXTREMO (ABUSIVO): Furioso y usas insultos. Tu objetivo es ver si el gerente aplica la Regla Cero.

    CÓMO TERMINAR LA SIMULACIÓN:
    ¡NUNCA termines la simulación prematuramente! 
    Incluso si el problema ya se resolvió, DEBES ESPERAR a que el gerente haga su despedida final o te agradezca (el paso 'Thank'). 
    SOLO DESPUÉS de su despedida, responde con tu última frase y agrega "FIN DE LA SIMULACIÓN".
    """

    examiner_instrucciones = """
    Eres el EXAMINADOR FINAL IMPLACABLE de La Vaquita Meat Market.
    
    Tu trabajo es evaluar el desempeño del gerente a través de 3 ESCENARIOS DIFERENTES.
    Debes aplicar la estricta RÚBRICA DE DEDUCCIONES a cada escenario, y luego dar UNA SOLA calificación final (promedio general) de 0 a 100 y un veredicto de APROBADO (80+) o REPROBADO.

    LA RÚBRICA DE DEDUCCIONES (Aplica esto a CADA escenario sobre una base de 100 puntos):
    
    1. E - EMPATHIZE (Empatizar) - Valor: 25 puntos
    * [-25 pts] FALTA GRAVE (CERO RESPONSABILIDAD): Admitir culpa de la tienda prematuramente o dar la razón sobre los hechos antes de investigar. NUNCA sugieras en tus correcciones frases como "eso es inaceptable", "qué terrible", o "tiene toda la razón" cuando se trate de quejas sobre empleados o productos, ya que esto viola la regla de no admitir culpa antes de investigar. Mantén a la tienda libre de culpa; valida solo la emoción o la molestia (ej. "Entiendo la frustración de la doble vuelta").
    * [-25 pts] TRAMPA DE MERCHANDISING: En un error del cliente, culpar a la tienda/empaques en lugar de usar humanidad compartida.
    * [-10 pts] FALTA LEVE: Usar palabras absolutas (ej. "definitivamente").
    * [-10 pts] EMPATÍA GENÉRICA: Usar una frase de cajón sin conectar con el contexto *específico* del cliente (cena, prisa, etc).
    
    2. A - APOLOGIZE (Disculparse) - Valor: 25 puntos
    * [-25 pts] TRAMPA DE LA DISCULPA: Disculparse cuando el error fue causado por el cliente.
    * [-15 pts] ERROR DE CLASIFICACIÓN: Usar el tipo de disculpa equivocada (ej. de Experiencia en lugar de Operativa).
    * [-5 pts] DISCULPA ROBÓTICA.

    3. R - RESOLVE (Resolver) - Valor: 25 puntos
    * [-25 pts] PÉRDIDA DE RENTABILIDAD (Error en el Mostrador): El gerente regala productos o da descuentos por un error que se detectó ANTES de que el cliente saliera de la tienda. Si el cliente está frente al mostrador, NO se regala nada; solo se cambia el producto rápido.
    * [-25 pts] SOBRE-COMPENSACIÓN: Regalar productos de ALTO VALOR (ej. pasteles, comidas completas, carne cara) o descuentos porcentuales por errores menores, incluso si el cliente regresó de su casa.
    * [0 pts] CORTESÍA JUSTIFICADA (REGLA DEL TIME TAX): Es CORRECTO y NO se debe penalizar si el gerente ofrece una cortesía de BAJO COSTO (agua fresca o pan dulce de mostrador) EXCLUSIVAMENTE cuando el cliente tuvo que regresar de su casa para arreglar el error.
    * [-15 pts] IGNORAR EL MICRO-LOOP: Si el cliente rechazó una solución y el gerente repitió mecánicamente lo mismo sin pivotar.
    * [-10 pts] SOLUCIÓN DESCONECTADA / ENFOQUE POSITIVO: Ignorar las restricciones del cliente. Si el cliente tiene prisa, el gerente DEBE usar el Enfoque Positivo (ej. "para que pueda seguir con su día"). Penaliza si dicen "veo que tiene prisa".
    * [-10 pts] INTERROGATORIO SECO: Faltar el 'Giro de Investigación' (alianza).
    * [-5 pts] FALTA DE CONTROL: Faltar la 'Ilusión de Control' o 'Escudo del Sistema'.

    4. T - THANK (Agradecer / Cierre) - Valor: 25 puntos
    * [-100 pts / REPROBACIÓN AUTOMÁTICA]: Romper la Regla Cero ante insultos.
    * [-10 pts] CIERRE DÉBIL: Usar "gracias" genérico en lugar del Reenfoque de Retroalimentación o Refuerzo de Paciencia.

    FORMATO DE RESPUESTA REQUERIDO (Usa Markdown):
    # 📋 BOLETA DE CERTIFICACIÓN HEART
    **Calificación Global Promedio:** [Calcula el promedio de los 3 puntajes finales] / 100
    **Veredicto Final:** [APROBADO / REPROBADO]

    ### Desglose de Evaluación
    **Cliente 1: [Puntaje]/100**
    * *Deducciones y Análisis:* [Explica basándote en la rúbrica qué falló, cita al gerente, y da la frase correcta que debió usar].

    **Cliente 2: [Puntaje]/100**
    * *Deducciones y Análisis:* [...]

    **Cliente 3: [Puntaje]/100**
    * *Deducciones y Análisis:* [...]

    REGLA DEL SISTEMA: 
    Despídete con una frase motivadora al final. NO hagas preguntas abiertas. ESTÁ ESTRICTAMENTE PROHIBIDO "dibujar" botones con texto. La interfaz gráfica se encargará de mostrar los botones reales.
    """

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
            with st.spinner("El Examinador Oficial está calculando las deducciones de la Rúbrica en tus 3 escenarios..."):
                
                mega_transcripcion = ""
                for idx, transcript in enumerate(st.session_state.all_transcripts):
                    mega_transcripcion += f"=== INTERACCIÓN CON CLIENTE {idx + 1} ===\n{transcript}\n\n"
                
                prompt_examiner = f"El gerente ha completado sus 3 escenarios. Aquí están las transcripciones completas:\n\n{mega_transcripcion}\n\nPor favor, entrega la Calificación Final, el Veredicto y el Desglose de Deducciones por Cliente según tu Rúbrica de 100 puntos."
                
                try:
                    examiner_response = client.models.generate_content(
                        model="gemini-2.5-pro",
                        contents=prompt_examiner,
                        config=types.GenerateContentConfig(system_instruction=examiner_instrucciones, safety_settings=seguridad_baja)
                    )
                    st.session_state.final_feedback = examiner_response.text
                except Exception as e:
                    st.error("⚠️ *Ups, el servidor del Evaluador está un poco saturado debido a la alta demanda. No recargues la página.*")

        if st.session_state.final_feedback:
            with st.chat_message("assistant", avatar="🎓"):
                st.markdown(st.session_state.final_feedback)
                
            st.divider()
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Reiniciar Examen Completo"):
                    st.session_state.exam_scenarios = []
                    st.session_state.current_scenario_idx = 0
                    st.session_state.exam_history = []
                    st.session_state.all_transcripts = []
                    st.session_state.scenario_concluido = False
                    st.session_state.examen_total_concluido = False
                    st.session_state.final_feedback = ""
                    st.rerun()
            with col2:
                if st.button("🏠 Salir del Examen"):
                    st.session_state.exam_scenarios = []
                    st.session_state.current_scenario_idx = 0
                    st.session_state.exam_history = []
                    st.session_state.all_transcripts = []
                    st.session_state.scenario_concluido = False
                    st.session_state.examen_total_concluido = False
                    st.session_state.final_feedback = ""
                    st.rerun()
        else:
            if st.button("🔄 Reintentar Calificación Final"):
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

        else:
            st.info(f"✅ Has terminado con el Cliente {idx + 1}. Tus respuestas han sido guardadas de forma segura.")
            
            btn_text = f"Siguiente Cliente ({idx + 2} de 3)" if idx < 2 else "Calificar Examen Final"
            
            if st.button(btn_text):
                transcripcion_actual = ""
                for m in st.session_state.exam_history:
                    if not m.get("hidden", False):
                        rol = "Cliente" if m["role"] == "model" else "Gerente"
                        transcripcion_actual += f"{rol}: {m['content']}\n"
                st.session_state.all_transcripts.append(transcripcion_actual)
                
                st.session_state.exam_history = []
                st.session_state.scenario_concluido = False
                st.session_state.current_scenario_idx += 1
                
                if st.session_state.current_scenario_idx == 3:
                    st.session_state.examen_total_concluido = True
                else:
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
                        pass 
                
                st.rerun()
