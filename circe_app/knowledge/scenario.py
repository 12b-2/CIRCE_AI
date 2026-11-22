"""Catálogo de niveles y rúbricas de decisión de CIRCE.

Cómo se lee este archivo
------------------------
Cada nivel es una lista de 5 "specs" (diccionarios con los campos de ScenarioNode).
`_build_nodes()` añade `id`, `level_number` y `next_node` automáticamente, así que
ya no se escriben a mano ni pueden quedar mal encadenados.

Convención de palabras clave (la usa circe_app/evaluator.py):
  "aislar"       palabra completa; también acepta conjugaciones (aislo, aislando) y plurales.
  "format*"      cualquier palabra que EMPIECE con "format" (formatear, formateo...).
  "post mortem"  varias palabras: deben aparecer en ese orden, con a lo sumo 2 palabras en medio.
Las apariciones negadas ("sin apagarlo", "no formateo") no cuentan como coincidencia.

Reglas para escribir rúbricas (las comprueba `validate_catalog()`):
  * keywords_wrong NUNCA debe coincidir con una acción correcta del mismo nodo.
  * Cada acción correcta debe activar al menos una keyword_correct.
  * Evita palabras genéricas como keyword_correct ("red", "plan", "usuario"): hacen que
    respuestas parciales o peligrosas parezcan correctas.
  * Mínimo 3 acciones correctas, 2 parciales y 2 incorrectas por nodo.
"""
from __future__ import annotations

from typing import Any

from circe_app.config import LevelScenario, ScenarioNode

NodeSpec = dict[str, Any]


def _build_nodes(specs: list[NodeSpec]) -> dict[str, ScenarioNode]:
    """Convierte los specs en ScenarioNode numerados y encadenados (node_1 -> node_2 -> ...)."""
    nodes: dict[str, ScenarioNode] = {}
    total = len(specs)
    for number, spec in enumerate(specs, start=1):
        node_id = f"node_{number}"
        nodes[node_id] = ScenarioNode(
            id=node_id,
            level_number=number,
            next_node=f"node_{number + 1}" if number < total else None,
            **spec,
        )
    return nodes


# ============================================================================
# Nivel 1: Filtración de datos corporativos
# ============================================================================
LEVEL_1_NODES = _build_nodes([
    dict(
        title="Nivel 1 · Detección y contención",
        prompt=(
            "Nivel 1: Detección del evento. El sistema SIEM alerta una exfiltración activa de datos: "
            "alguien está extrayendo archivos confidenciales desde el servidor interno fuera de horario. "
            "¿Qué acción realizas primero para detener el incidente?"
        ),
        hint="Antes de investigar a fondo o apagar el equipo perdiendo memoria RAM, debes aislar el servidor de la red y bloquear el acceso activo.",
        correct_actions=[
            "aislar el sistema afectado",
            "aislar el servidor de la red",
            "bloquear el acceso y aislar la máquina",
            "desconectar el equipo comprometido de la red",
            "segmentar o cortar la conexión de red del servidor",
            "cortar la conexión del servidor para frenar la extracción de datos",
        ],
        partial_actions=[
            "revisar los logs",
            "notificar al equipo de seguridad",
            "hacer una copia forense",
            "monitorear el tráfico",
        ],
        wrong_actions=[
            "restaurar el sistema sin investigar",
            "eliminar todo sin análisis",
            "formatear el servidor inmediatamente",
            "apagar el servidor sin capturar evidencia",
            "compartir credenciales para probar",
            "ignorar la amenaza",
        ],
        keywords_correct=["aislar", "aislamiento", "desconectar", "bloquear", "contener", "cortar", "segmentar", "vlan", "cuarentena"],
        keywords_partial=["revisar", "logs", "avisar", "notificar", "investigar", "monitorear", "copia forense"],
        keywords_wrong=["format*", "borr*", "elimin*", "ignor*", "apag*", "reinici*", "compart* credencial*"],
        consequences=[
            "El atacante puede seguir extrayendo información crítica.",
            "La evidencia volátil se puede perder si se apaga o formatea.",
        ],
    ),
    dict(
        title="Nivel 2 · Preservación y alcance",
        prompt=(
            "Nivel 2: Análisis de alcance y evidencia. El servidor ya fue aislado de la red, "
            "pero aún no sabemos qué archivos fueron extraídos ni cómo ingresó el atacante. "
            "¿Cuál es tu siguiente decisión técnica?"
        ),
        hint="Preserva la evidencia forense (memoria y registros) y analiza los logs de acceso y tráfico para saber exactamente qué datos se filtraron.",
        correct_actions=[
            "revisar los logs de acceso y preservar evidencia forense",
            "analizar permisos, conexiones y registros de auditoría",
            "capturar una imagen forense y revisar registros de acceso",
            "identificar usuarios y archivos afectados en los logs",
            "preservar la memoria y los registros para el análisis forense",
        ],
        partial_actions=[
            "revisar los archivos más importantes manualmente",
            "preguntar al responsable del área",
            "documentar la incidencia preliminar",
        ],
        wrong_actions=[
            "borrar los logs",
            "reiniciar todo sin evidencia",
            "revelar la brecha a todos los empleados por chat",
            "modificar los archivos del servidor",
        ],
        keywords_correct=["logs", "registros", "forense", "evidencia", "auditoría", "alcance", "analizar", "permisos", "imagen forense"],
        keywords_partial=["archivos", "preguntar", "documentar", "revisar"],
        keywords_wrong=["borr*", "elimin*", "reinici*", "format*", "modific*", "revel*"],
        consequences=[
            "Se pierde la trazabilidad forense del ataque.",
            "No se podrá demostrar qué información fue comprometida.",
        ],
    ),
    dict(
        title="Nivel 3 · Control de credenciales",
        prompt=(
            "Nivel 3: Contención de identidad y movimiento lateral. Descubres en los logs que el atacante "
            "utilizó una cuenta de administrador comprometida y creó un token de sesión activo. "
            "¿Qué haces para impedir que salte a otros servidores?"
        ),
        hint="Debes revocar las sesiones activas, deshabilitar o rotar las credenciales comprometidas y verificar si hay accesos laterales.",
        correct_actions=[
            "revocar sesiones activas y rotar credenciales comprometidas",
            "bloquear la cuenta comprometida y revocar tokens de acceso",
            "cambiar contraseñas privilegiadas y auditar movimiento lateral",
            "deshabilitar las credenciales afectadas y forzar autenticación multifactor",
        ],
        partial_actions=[
            "cambiar solo la contraseña del usuario",
            "pedir al administrador que cierre sesión",
            "escanear con antivirus el servidor",
        ],
        wrong_actions=[
            "dejar la cuenta activa para observar al atacante",
            "eliminar el directorio activo completo",
            "enviar las nuevas contraseñas por correo sin cifrar",
        ],
        keywords_correct=["revocar", "credenciales", "token", "sesiones", "rotar", "bloquear cuenta", "mfa", "privilegiadas", "deshabilitar", "movimiento lateral", "multifactor"],
        keywords_partial=["contraseña", "clave", "antivirus", "usuario", "cierre sesión"],
        keywords_wrong=["dej* activ*", "dej* funcion*", "observ* atacante", "elimin* directorio", "contrasen* correo", "sin cifrar"],
        consequences=[
            "El atacante mantiene persistencia usando el token activo en otros nodos.",
            "El incidente escala a toda la red corporativa.",
        ],
    ),
    dict(
        title="Nivel 4 · Comunicación y protocolo",
        prompt=(
            "Nivel 4: Comunicación e informe regulatorio. Confirmas que se filtraron datos personales "
            "de clientes. Debes coordinar la comunicación interna y el protocolo legal. "
            "¿Cómo procedes?"
        ),
        hint="Activa el comité de respuesta a incidentes, notifica a Dirección, Legal y Privacidad de Datos siguiendo el canal oficial documentado.",
        correct_actions=[
            "notificar a dirección, seguridad y área legal siguiendo el plan de respuesta",
            "documentar medidas y comunicar a stakeholders y protección de datos",
            "activar el protocolo oficial de notificación de brecha de datos",
            "convocar al comité de respuesta a incidentes e informar a dirección, legal y privacidad de datos",
        ],
        partial_actions=[
            "avisar a algunos departamentos por mensaje",
            "esperar unos días antes de avisar a legal",
            "iniciar un reporte informal",
        ],
        wrong_actions=[
            "publicar la información en un correo masivo a toda la empresa",
            "ocultar la incidencia para evitar multas o alarma",
            "cancelar el proceso de respuesta",
        ],
        keywords_correct=["notificar", "dirección", "legal", "protocolo", "comunicar", "documentar", "comité", "privacidad", "protección de datos", "stakeholders"],
        keywords_partial=["avisar", "departamentos", "reporte", "mensaje", "informal"],
        keywords_wrong=["ocult*", "escond*", "correo masivo", "toda la empresa", "cancel*", "no decir nada", "no avis*", "no notific*"],
        consequences=[
            "Sanciones legales graves por incumplimiento de notificación de brecha.",
            "Caos comunicacional y pérdida de confianza reputacional.",
        ],
    ),
    dict(
        title="Nivel 5 · Erradicación y mejora",
        prompt=(
            "Nivel 5: Erradicación, recuperación y lecciones aprendidas. La amenaza está contenida "
            "y notificada. Para restaurar la operación de forma segura y evitar que se repita, "
            "¿qué medidas finales ejecutas?"
        ),
        hint="Elimina cualquier puerta trasera, restaura desde copias limpias verificadas, aplica parches/controles DLP y realiza la reunión post-mortem.",
        correct_actions=[
            "erradicar la persistencia, restaurar desde backup limpio y aplicar controles DLP y monitoreo",
            "verificar integridad, parchar vulnerabilidades y documentar lecciones aprendidas",
            "restaurar servicios seguros, reforzar reglas del SIEM y realizar análisis post mortem",
            "eliminar puertas traseras y restaurar desde una copia limpia verificada",
        ],
        partial_actions=[
            "instalar solo las actualizaciones pendientes",
            "cerrar el ticket del incidente",
            "poner el servidor otra vez en línea tras una limpieza rápida",
        ],
        wrong_actions=[
            "volver a conectar el servidor sin limpiar puertas traseras",
            "reconectar el servidor a la red como estaba",
            "desactivar las alertas del SIEM para evitar falsos positivos",
            "borrar toda la documentación del incidente",
        ],
        keywords_correct=["erradicar", "backup", "respaldo", "copia limpia", "limpio", "parchar", "parche", "monitoreo", "dlp", "post mortem", "lecciones", "restaurar", "integridad", "puertas traseras"],
        keywords_partial=["actualizar", "actualizaciones", "ticket"],
        keywords_wrong=["reconect* sin", "desactiv* alert*", "apag* alert*", "borr* document*", "elimin* document*", "sin limpiar"],
        consequences=[
            "El atacante vuelve a entrar mediante una puerta trasera no erradicada.",
            "La organización repite los mismos errores de seguridad.",
        ],
    ),
])


# ============================================================================
# Nivel 2: Ataque de ransomware
# ============================================================================
LEVEL_2_NODES = _build_nodes([
    dict(
        title="Nivel 1 · Contención de cifrado",
        prompt=(
            "Nivel 1: Estallido de Ransomware. Varias estaciones de finanzas muestran una nota de rescate "
            "y el cifrado se propaga por carpetas compartidas SMB. ¿Cuál es tu primera acción inmediata?"
        ),
        hint="Corta la propagación en red aislando el segmento afectado y bloqueando el tráfico SMB lateral.",
        correct_actions=[
            "aislar el segmento de red afectado y bloquear puertos SMB",
            "desconectar los equipos infectados de la red y contener la propagación",
            "bloquear el tráfico SMB lateral y sacar de la red las estaciones cifradas",
        ],
        partial_actions=[
            "ejecutar un escaneo antivirus en un equipo",
            "avisar por correo al área de soporte",
        ],
        wrong_actions=[
            "pagar el rescate inmediatamente",
            "reiniciar el servidor central de archivos",
            "ignorar la alerta y seguir trabajando",
        ],
        keywords_correct=["aislar", "segmento", "smb", "desconectar", "bloquear", "contener", "propagación", "cuarentena", "cortar"],
        keywords_partial=["antivirus", "avisar", "soporte"],
        keywords_wrong=["pag* rescat*", "reinici*", "ignor*"],
        consequences=["El ransomware cifra los servidores centrales de producción."],
    ),
    dict(
        title="Nivel 2 · Protección de Backups",
        prompt=(
            "Nivel 2: Resguardo de copias de seguridad. El malware busca destruir las copias sombra (VSS) "
            "y alcanzar el servidor de backups. ¿Qué medida tomas sobre los respaldos?"
        ),
        hint="Verifica el aislamiento offline/inmutable de los backups y revoca el acceso desde la red comprometida.",
        correct_actions=[
            "aislar el servidor de backups y verificar copias inmutables u offline",
            "proteger los respaldos desconectando su acceso desde la red infectada",
            "revocar el acceso a los respaldos y comprobar que las copias sombra estén protegidas",
        ],
        partial_actions=[
            "revisar el espacio en disco",
            "revisar el estado de los respaldos sin aislarlos",
            "preguntar al administrador de los respaldos",
        ],
        wrong_actions=[
            "conectar el disco de backup externo al equipo infectado",
            "borrar los backups antiguos",
            "iniciar un nuevo backup desde las máquinas infectadas",
        ],
        keywords_correct=["backup", "respaldos", "inmutable", "offline", "aislar", "proteger", "copias", "desconectar"],
        keywords_partial=["espacio", "revisar", "preguntar"],
        keywords_wrong=["conect* extern*", "conect* infectad*", "borr* backup*", "borr* respald*", "elimin* backup*", "elimin* respald*"],
        consequences=["Los respaldos quedan cifrados y se pierde la capacidad de recuperación."],
    ),
    dict(
        title="Nivel 3 · Identificación del vector",
        prompt=(
            "Nivel 3: Análisis forense del paciente cero. Necesitas identificar la variante del ransomware "
            "y cómo entró para cerrar la brecha. ¿Qué realizas?"
        ),
        hint="Analiza los artefactos forenses, logs de EDR/correo y el hash del binario para hallar el vector inicial.",
        correct_actions=[
            "analizar logs del EDR y del correo para identificar el paciente cero y el vector de entrada",
            "extraer indicadores de compromiso y hashes, y preservar evidencia forense",
            "analizar el binario del ransomware, sus hashes y los indicadores de compromiso (IOC)",
        ],
        partial_actions=[
            "preguntar a los usuarios quién abrió un archivo",
            "revisar solo el navegador web",
        ],
        wrong_actions=[
            "formatear el paciente cero sin recoger evidencia",
            "subir documentos confidenciales a foros públicos",
            "reinstalar el equipo del paciente cero sin guardar nada",
        ],
        keywords_correct=["edr", "paciente cero", "vector", "hash", "forense", "logs", "indicadores", "ioc", "analizar", "evidencia"],
        keywords_partial=["preguntar", "navegador"],
        keywords_wrong=["format*", "reinstal*", "foros"],
        consequences=["El vector de entrada sigue abierto y el atacante reingresa."],
    ),
    dict(
        title="Nivel 4 · Gestión de crisis",
        prompt=(
            "Nivel 4: Decisión ante la extorsión. Los atacantes exigen pago en criptomonedas en 24 horas. "
            "La directiva pregunta si deben pagar. ¿Qué recomiendas y ejecutas?"
        ),
        hint="No pagar el rescate, activar el plan de continuidad de negocio y notificar a las autoridades y al CERT.",
        correct_actions=[
            "no pagar el rescate, activar continuidad de negocio y notificar a autoridades y equipo legal",
            "coordinar con dirección, legal y CERT usando nuestros respaldos verificados",
            "no negociar ni pagar y restaurar desde respaldos verificados informando a las autoridades",
        ],
        partial_actions=[
            "avisar a la dirección y esperar instrucciones",
            "esperar a que venza el plazo",
        ],
        wrong_actions=[
            "pagar el rescate sin garantías ni autorización",
            "ocultar el ataque a la junta directiva",
            "negociar con los atacantes por cuenta propia sin avisar a la dirección",
        ],
        keywords_correct=["no pag*", "continuidad", "autoridades", "legal", "cert", "respaldos", "protocolo"],
        keywords_partial=["avisar", "esperar", "instrucciones"],
        keywords_wrong=["pag* rescat*", "ocult*", "negoci* cuenta"],
        consequences=["Financiamiento criminal sin garantía de descifrado y sanciones legales."],
    ),
    dict(
        title="Nivel 5 · Restauración limpia",
        prompt=(
            "Nivel 5: Recuperación del entorno. Ya tienes las copias limpias listas. "
            "¿Cómo restauras la operación sin riesgo de reinfección?"
        ),
        hint="Reconstruye los sistemas limpios, rota todas las credenciales del dominio, aplica parches y monitorea con EDR.",
        correct_actions=[
            "restaurar desde copias limpias, rotar credenciales de dominio, aplicar parches y monitorear con EDR",
            "reconstruir servidores verificando integridad y reforzar segmentación de red",
            "reconstruir los sistemas desde imágenes limpias y aplicar parches antes de reconectarlos",
        ],
        partial_actions=[
            "restaurar los archivos encima del sistema infectado",
            "cambiar solo una contraseña",
        ],
        wrong_actions=[
            "deshabilitar el firewall para restaurar más rápido",
            "reconectar equipos cifrados a producción",
        ],
        keywords_correct=["restaurar", "limpias", "rotar", "credenciales", "parches", "edr", "segmentación", "reconstruir", "integridad"],
        keywords_partial=["encima", "una contraseña"],
        keywords_wrong=["deshabilit* firewall", "desactiv* firewall", "apag* firewall", "reconect* cifrad*"],
        consequences=["Reinfección inmediata durante la restauración."],
    ),
])


# ============================================================================
# Nivel 3: Phishing ejecutivo y fraude BEC
# ============================================================================
LEVEL_3_NODES = _build_nodes([
    dict(
        title="Nivel 1 · Bloqueo de buzón comprometido",
        prompt=(
            "Nivel 1: Alerta de Phishing Ejecutivo (BEC). Detectas que la cuenta de correo del Director Financiero "
            "inició sesión desde una IP anómala y envió órdenes de pago urgentes. ¿Qué haces primero?"
        ),
        hint="Suspende la sesión activa, revoca los tokens de acceso del buzón y bloquea el acceso no autorizado.",
        correct_actions=[
            "bloquear el acceso, revocar tokens de sesión y forzar el cambio de credenciales del director",
            "cerrar las sesiones del director, invalidar sus tokens y restablecer su contraseña",
            "suspender la cuenta comprometida, revocar sesiones activas y exigir autenticación multifactor",
        ],
        partial_actions=[
            "enviar un correo preguntando al director si fue él",
            "llamar al director para preguntarle si envió esas órdenes",
        ],
        wrong_actions=[
            "eliminar la cuenta de correo junto con todos sus mensajes",
            "ignorar la alerta porque parece una orden legítima",
        ],
        keywords_correct=["bloquear", "revocar", "token", "sesión", "credenciales", "suspender", "aislar cuenta", "contraseña", "invalidar"],
        keywords_partial=["preguntar", "correo", "llamar"],
        keywords_wrong=["elimin* cuenta", "borr* cuenta", "ignor*"],
        consequences=["El atacante sigue operando desde el buzón ejecutivo."],
    ),
    dict(
        title="Nivel 2 · Freno de transferencia",
        prompt=(
            "Nivel 2: Contención del fraude financiero. El equipo de tesorería está a punto de aprobar "
            "una transferencia bancaria ordenada por el atacante. ¿Cómo actúas?"
        ),
        hint="Contacta por vía telefónica o presencial (fuera de banda) a tesorería y al banco para detener la transferencia.",
        correct_actions=[
            "contactar fuera de banda a tesorería y al banco para detener la transferencia fraudulenta",
            "llamar por teléfono a tesorería y al banco para frenar el pago",
            "cancelar la transferencia con el banco y avisar a tesorería por un canal verificado",
        ],
        partial_actions=[
            "mandar un correo normal a tesorería",
            "pedir al director que confirme la orden por correo",
        ],
        wrong_actions=[
            "autorizar el pago para ver a qué cuenta llega",
            "aprobar la transferencia y investigar después",
        ],
        keywords_correct=["detener", "transferencia", "tesorería", "banco", "teléfono", "fuera de banda", "frenar", "cancelar"],
        keywords_partial=["mandar correo", "esperar", "confirme"],
        keywords_wrong=["autoriz*", "aprob*", "aprueb*", "dej* que", "dej* transferencia", "dej* pago"],
        consequences=["Pérdida financiera directa e irreversible de fondos corporativos."],
    ),
    dict(
        title="Nivel 3 · Auditoría de reglas ocultas",
        prompt=(
            "Nivel 3: Persistencia en el correo. Los atacantes BEC suelen ocultar sus rastros dentro del buzón. "
            "¿Qué auditas técnicamente en la cuenta afectada?"
        ),
        hint="Revisa y elimina reglas de reenvío automático, filtros ocultos a carpetas RSS/Papelera y aplicaciones OAuth maliciosas.",
        correct_actions=[
            "auditar y eliminar reglas de reenvío ocultas, delegaciones y aplicaciones OAuth no autorizadas",
            "revisar reglas de bandeja, reenvíos automáticos y permisos delegados del buzón",
            "inspeccionar filtros ocultos, reglas de reenvío y aplicaciones con acceso OAuth al buzón",
        ],
        partial_actions=[
            "revisar solo la bandeja de entrada principal",
            "revisar los últimos correos enviados",
        ],
        wrong_actions=[
            "dar por cerrado el análisis sin revisar la configuración del buzón",
            "asumir que el atacante no dejó reglas ni accesos",
        ],
        keywords_correct=["reglas", "reenvío", "oauth", "filtros", "delegación", "auditar", "buzón", "aplicaciones"],
        keywords_partial=["bandeja", "entrada", "enviados"],
        keywords_wrong=["sin revis*", "sin mir*", "por terminado", "asum*", "supon*"],
        consequences=["Todos los correos entrantes siguen reenviándose en secreto al atacante."],
    ),
    dict(
        title="Nivel 4 · Alerta a terceros",
        prompt=(
            "Nivel 4: Protección de socios y clientes. Descubres que el atacante también envió facturas falsas "
            "a tres clientes importantes desde el correo real. ¿Qué acción tomas?"
        ),
        hint="Notifica formalmente a los clientes afectados por un canal seguro verificando que no paguen las cuentas bancarias alteradas.",
        correct_actions=[
            "notificar a los clientes afectados por canal verificado y emitir una alerta oficial de seguridad",
            "avisar a los clientes por teléfono o canal oficial de que ignoren las facturas falsas y no paguen a las cuentas alteradas",
            "comunicar el fraude a los clientes y confirmar las cuentas bancarias legítimas por un medio seguro",
        ],
        partial_actions=[
            "publicar un comunicado en el sitio web de la empresa",
            "enviar un correo general de seguridad sin indicar las cuentas alteradas",
        ],
        wrong_actions=[
            "negar que el correo provino de la empresa",
            "ocultar el incidente a los clientes",
            "esperar a que los clientes pregunten",
        ],
        keywords_correct=["notificar", "clientes", "avisar", "canal seguro", "canal verificado", "facturas", "alerta", "comunicar", "confirmar"],
        keywords_partial=["sitio web", "comunicado", "correo general"],
        keywords_wrong=["neg*", "nieg*", "ocult*", "no sali* empresa"],
        consequences=["Los clientes sufren fraude financiero y demandan a la organización."],
    ),
    dict(
        title="Nivel 5 · Blindaje anti-phishing",
        prompt=(
            "Nivel 5: Prevención estructural. Para evitar futuros ataques BEC y suplantación de identidad, "
            "¿qué controles técnicos y de proceso implementas?"
        ),
        hint="Implementa MFA resistente al phishing (FIDO2), políticas SPF/DKIM/DMARC y verificación en dos pasos para pagos.",
        correct_actions=[
            "implementar MFA resistente a phishing, configurar SPF, DKIM y DMARC y exigir doble aprobación en pagos",
            "activar MFA con llaves FIDO2 y políticas anti-suplantación de correo con DMARC",
            "exigir verificación en dos pasos para pagos y capacitar a los directivos contra phishing",
        ],
        partial_actions=[
            "enviar un folleto informativo una vez al año",
            "dar una capacitación general sin cambiar ningún control técnico",
        ],
        wrong_actions=[
            "permitir inicios de sesión sin MFA para comodidad de los directivos",
            "desactivar el filtro antiphishing porque genera falsos positivos",
        ],
        keywords_correct=["mfa", "dmarc", "spf", "dkim", "doble aprobación", "fido", "fido2", "autenticación", "capacitación", "verificación"],
        keywords_partial=["folleto", "charla"],
        keywords_wrong=["sin mfa", "desactiv* filtro", "desactiv* mfa", "deshabilit* mfa"],
        consequences=["La organización vuelve a caer en ataques de phishing."],
    ),
])


# ============================================================================
# Nivel 4: Intrusión cloud y fuga de credenciales IAM
# ============================================================================
LEVEL_4_NODES = _build_nodes([
    dict(
        title="Nivel 1 · Revocación de API Keys",
        prompt=(
            "Nivel 1: Alerta en la Nube. Una llave de acceso AWS/Cloud fue expuesta en un repositorio "
            "y un atacante está creando instancias de alto costo y leyendo buckets S3. ¿Qué haces primero?"
        ),
        hint="Desactiva y revoca de inmediato las llaves IAM comprometidas y aplica una política de denegación temporal.",
        correct_actions=[
            "desactivar y revocar inmediatamente las llaves IAM comprometidas y sesiones temporales",
            "rotar las credenciales expuestas y bloquear el acceso del atacante con una política de denegación",
            "deshabilitar la access key filtrada e invalidar las sesiones activas",
        ],
        partial_actions=[
            "enviar un mensaje al desarrollador para que borre el commit",
            "avisar al equipo de desarrollo del repositorio expuesto",
        ],
        wrong_actions=[
            "eliminar toda la cuenta de nube en producción",
            "ignorar la alerta hasta revisar la factura",
        ],
        keywords_correct=["revocar", "desactivar", "iam", "llaves", "keys", "credenciales", "bloquear", "rotar", "deshabilitar", "access key"],
        keywords_partial=["commit", "desarrollador", "desarrollo"],
        keywords_wrong=["elimin* cuenta", "borr* cuenta", "ignor*"],
        consequences=["El atacante continúa escalando privilegios y extrayendo datos del bucket."],
    ),
    dict(
        title="Nivel 2 · Contención de recursos",
        prompt=(
            "Nivel 2: Instancias no autorizadas. El atacante desplegó 15 máquinas virtuales y abrió grupos "
            "de seguridad a internet. ¿Cómo contienes la infraestructura?"
        ),
        hint="Aísla o detén las instancias maliciosas conservando snapshots para forense y cierra los Security Groups abiertos.",
        correct_actions=[
            "aislar y detener instancias no autorizadas, tomar snapshot forense y cerrar security groups",
            "cerrar los grupos de seguridad abiertos a internet y aislar las máquinas virtuales del atacante",
            "detener las instancias maliciosas conservando snapshots para forense",
        ],
        partial_actions=[
            "revisar la factura de la nube del próximo mes",
            "avisar al equipo de finanzas del consumo anómalo",
        ],
        wrong_actions=[
            "dejar las instancias corriendo conectadas a la base de datos productiva",
            "borrar las instancias del atacante sin conservar evidencia",
        ],
        keywords_correct=["aislar", "detener", "instancias", "snapshot", "security group", "firewall", "contener", "cerrar puertos", "grupos de seguridad"],
        keywords_partial=["factura", "finanzas"],
        keywords_wrong=["dej* corriendo", "dej* conectad*", "borr* instancias", "elimin* instancias"],
        consequences=["Consumo masivo de recursos y puente hacia la base de datos interna."],
    ),
    dict(
        title="Nivel 3 · Auditoría de CloudTrail",
        prompt=(
            "Nivel 3: Trazabilidad en la nube. Necesitas saber si el atacante creó nuevos usuarios IAM, "
            "roles ocultos o descargó objetos confidenciales. ¿Qué analizas?"
        ),
        hint="Audita los registros de CloudTrail / Activity Logs buscando llamadas API de creación de usuarios, roles y acceso a datos.",
        correct_actions=[
            "auditar registros de CloudTrail y logs de acceso para detectar nuevos roles, usuarios o descargas",
            "revisar las llamadas API de CloudTrail para ver qué usuarios, roles y objetos creó o leyó el atacante",
            "analizar los eventos de CloudTrail y los logs de acceso a los buckets",
        ],
        partial_actions=[
            "mirar únicamente el panel principal de la consola web",
            "revisar la lista de usuarios IAM sin consultar los registros",
        ],
        wrong_actions=[
            "desactivar el registro de auditoría de CloudTrail",
            "borrar los logs de CloudTrail",
        ],
        keywords_correct=["cloudtrail", "logs", "auditar", "roles", "usuarios", "api", "registros", "analizar"],
        keywords_partial=["consola", "panel"],
        keywords_wrong=["desactiv* cloudtrail", "desactiv* registr*", "apag* cloudtrail", "deshabilit* cloudtrail", "borr* log*", "elimin* log*"],
        consequences=["Un usuario puerta trasera creado por el atacante pasa desapercibido."],
    ),
    dict(
        title="Nivel 4 · Limpieza del repositorio",
        prompt=(
            "Nivel 4: Remediación en código fuente. La llave comprometida sigue visible en el historial "
            "de Git. ¿Cómo corriges la gestión de secretos con el equipo de desarrollo?"
        ),
        hint="Purga el historial del repositorio, migra las credenciales a un gestor de secretos (Vault/Secrets Manager) y activa escaneo pre-commit.",
        correct_actions=[
            "eliminar secretos del historial de Git, usar un gestor de secretos y activar escaneo automático",
            "purgar el historial del repositorio, rotar la llave y activar escaneo pre-commit",
            "mover las credenciales a Vault o Secrets Manager y limpiar el historial de Git",
        ],
        partial_actions=[
            "hacer un nuevo commit comentando la línea de la clave",
            "pedir al equipo que no vuelva a subir claves",
        ],
        wrong_actions=[
            "subir las nuevas llaves en otro archivo de texto al mismo repositorio",
            "dejar la llave en el historial porque ya fue revocada",
        ],
        keywords_correct=["secretos", "vault", "secrets manager", "historial", "git", "escaneo", "variables de entorno", "purgar", "rotar"],
        keywords_partial=["comentar", "nuevo commit", "commit"],
        keywords_wrong=["sub* llaves", "sub* claves", "texto plano", "dej* historial", "dej* llave"],
        consequences=["Las credenciales vuelven a filtrarse en el historial del repositorio."],
    ),
    dict(
        title="Nivel 5 · Mínimo privilegio y alertas",
        prompt=(
            "Nivel 5: Arquitectura Cloud Segura. Para impedir que una credencial futura tenga control total, "
            "¿qué políticas implementas?"
        ),
        hint="Aplica el principio de mínimo privilegio en IAM, usa roles temporales (OIDC) sin llaves estáticas y activa alertas de anomalías.",
        correct_actions=[
            "aplicar mínimo privilegio, usar roles temporales con OIDC y configurar alertas de seguridad cloud",
            "eliminar llaves estáticas y usar roles temporales con permisos mínimos y alertas de anomalías",
            "definir políticas IAM de privilegio mínimo y activar detección de anomalías",
        ],
        partial_actions=[
            "pedir a los programadores que tengan más cuidado",
            "hacer una capacitación sobre seguridad en la nube sin cambiar permisos",
        ],
        wrong_actions=[
            "dar permisos de Administrador Global a todas las cuentas de servicio",
            "mantener las llaves estáticas con permisos amplios por comodidad",
        ],
        keywords_correct=["mínimo privilegio", "privilegio mínimo", "roles", "temporales", "oidc", "alertas", "monitoreo", "políticas", "iam", "permisos mínimos"],
        keywords_partial=["cuidado", "capacitación"],
        keywords_wrong=["administrador global", "todos los permisos", "permisos amplios"],
        consequences=["Cualquier filtración futura comprometerá toda la infraestructura cloud."],
    ),
])


# ============================================================================
# Nivel 5: Amenaza interna y exfiltración crítica (insider threat)
# ============================================================================
LEVEL_5_NODES = _build_nodes([
    dict(
        title="Nivel 1 · Contención silenciosa",
        prompt=(
            "Nivel 1: Alerta de Amenaza Interna. El sistema DLP detecta que un ingeniero con altos privilegios "
            "está copiando propiedad intelectual y esquemas de base de datos a un servicio externo. "
            "¿Qué haces primero?"
        ),
        hint="Bloquea la transferencia saliente y suspende los accesos privilegiados en coordinación con Seguridad sin destruir las pruebas.",
        correct_actions=[
            "bloquear la transferencia en el DLP o proxy y suspender los accesos privilegiados de inmediato",
            "cortar la salida de datos hacia el servicio externo y revocar los privilegios del ingeniero",
            "bloquear el destino externo y suspender las credenciales privilegiadas sin avisar al empleado",
        ],
        partial_actions=[
            "reportar el caso a su jefe directo",
            "abrir un ticket de seguridad y esperar la revisión del equipo",
        ],
        wrong_actions=[
            "ignorar la alerta porque es un empleado de confianza",
            "esperar a ver si termina de copiar para tener más pruebas",
            "llamar directamente al ingeniero para preguntarle qué está copiando",
        ],
        keywords_correct=["bloquear", "suspender", "accesos", "privilegios", "privilegiados", "dlp", "proxy", "contener", "revocar", "cortar"],
        keywords_partial=["jefe", "ticket", "reportar"],
        keywords_wrong=["ignor*", "esper* termin*", "llam* pregunt*", "llam* ingeniero"],
        consequences=["El empleado alerta que fue descubierto, borra huellas y completa el robo."],
    ),
    dict(
        title="Nivel 2 · Cadena de custodia",
        prompt=(
            "Nivel 2: Preservación legal y forense. El caso requerirá investigación legal formal. "
            "¿Cómo aseguras la evidencia digital del equipo y de los servidores?"
        ),
        hint="Asegura la estación de trabajo, realiza copia forense bit a bit con hash criptográfico y documenta la cadena de custodia.",
        correct_actions=[
            "preservar evidencia con imagen forense, calcular hashes y documentar la cadena de custodia",
            "hacer una copia forense bit a bit con bloqueador de escritura y registrar quién la manipula",
            "aislar el equipo, calcular el hash de la imagen y llevar registro de custodia",
        ],
        partial_actions=[
            "abrir los archivos en la computadora del empleado sin protección de escritura",
            "guardar la laptop en un cajón sin documentar quién la tiene",
        ],
        wrong_actions=[
            "reutilizar y formatear la laptop para entregársela a otro empleado",
            "reinstalar el sistema de la laptop antes de analizarla",
        ],
        keywords_correct=["forense", "custodia", "hash", "evidencia", "imagen", "preservar", "documentar", "bloqueador de escritura"],
        keywords_partial=["abrir archivos", "cajón"],
        keywords_wrong=["format*", "reutiliz*", "reinstal*"],
        consequences=["Las pruebas son invalidadas en un proceso legal por romper la cadena de custodia."],
    ),
    dict(
        title="Nivel 3 · Búsqueda de bombas lógicas",
        prompt=(
            "Nivel 3: Verificación de sabotaje. Como el usuario tenía permisos de administrador en producción, "
            "existe riesgo de que haya dejado puertas traseras o tareas programadas maliciosas. ¿Qué realizas?"
        ),
        hint="Audita tareas programadas (cron), llaves SSH, cuentas secundarias, cambios recientes en código y configuraciones de producción.",
        correct_actions=[
            "auditar llaves SSH, tareas programadas, cuentas ocultas y cambios recientes en producción",
            "revisar cron jobs, claves SSH, cuentas secundarias y cambios de código recientes",
            "buscar puertas traseras y verificar la integridad de los servidores en producción",
        ],
        partial_actions=[
            "revisar solo su historial de navegación web",
            "revisar únicamente su correo corporativo",
        ],
        wrong_actions=[
            "asumir que solo quería copiar archivos y no revisar los servidores",
            "dar el caso por cerrado tras bloquear su cuenta",
        ],
        keywords_correct=["auditar", "ssh", "tareas", "cron", "puertas traseras", "backdoor", "producción", "integridad", "claves"],
        keywords_partial=["navegación", "correo"],
        keywords_wrong=["asum*", "supon*", "no revis*", "por cerrado"],
        consequences=["Una bomba lógica se activa días después deteniendo los sistemas críticos."],
    ),
    dict(
        title="Nivel 4 · Coordinación Legal y RRHH",
        prompt=(
            "Nivel 4: Gestión interdepartamental. Con la evidencia técnica asegurada, debes articular "
            "la respuesta organizacional. ¿Con qué áreas y de qué forma actúas?"
        ),
        hint="Coordina confidencialmente con Dirección, Legal y Recursos Humanos entregando el informe forense documentado.",
        correct_actions=[
            "coordinar confidencialmente con área legal, recursos humanos y dirección entregando el informe forense",
            "informar de forma reservada a legal y a RRHH y compartir la evidencia documentada",
            "reunir a dirección, legal y recursos humanos para definir la acción disciplinaria con el informe técnico",
        ],
        partial_actions=[
            "avisar solo a su jefe directo",
            "documentar el caso en privado sin avisar a nadie más",
        ],
        wrong_actions=[
            "publicar el nombre del empleado en el chat general de la empresa",
            "confrontar al empleado antes de hablar con legal",
            "comentar el caso en el comedor con otros compañeros",
        ],
        keywords_correct=["legal", "recursos humanos", "rrhh", "dirección", "confidencial", "confidencialmente", "informe", "coordinar", "reservada"],
        keywords_partial=["jefe", "documentar"],
        keywords_wrong=["public*", "chat general", "confront*", "comedor"],
        consequences=["Demandas laborales y filtración de la investigación en curso."],
    ),
    dict(
        title="Nivel 5 · Control dual y DLP",
        prompt=(
            "Nivel 5: Reducción de riesgo interno. Para evitar que un solo administrador pueda extraer datos "
            "masivos o alterar producción sin supervisión, ¿qué controles implementas?"
        ),
        hint="Implementa control dual (PAM / aprobación de cuatro ojos), políticas DLP estrictas y monitoreo de comportamiento (UEBA).",
        correct_actions=[
            "implementar control dual, gestión de accesos privilegiados (PAM), DLP y monitoreo UEBA",
            "exigir aprobación de cuatro ojos para cambios en producción y registrar las sesiones privilegiadas",
            "aplicar segregación de funciones, PAM y alertas de comportamiento anómalo",
        ],
        partial_actions=[
            "hacer una capacitación sobre confidencialidad",
            "revisar manualmente las cuentas de administrador cada mes",
        ],
        wrong_actions=[
            "compartir una única cuenta root entre todos los administradores",
            "dar acceso total a producción a todos los ingenieros",
            "prohibir el uso de internet a toda la empresa",
        ],
        keywords_correct=["control dual", "pam", "dlp", "ueba", "privilegiados", "monitoreo", "segregación", "alertas", "cuatro ojos"],
        keywords_partial=["capacitación", "manualmente"],
        keywords_wrong=["cuenta root", "compart* cuenta", "acceso total", "prohib* internet"],
        consequences=["Un solo administrador puede abusar de sus privilegios sin trazabilidad individual."],
    ),
])


# ============================================================================
# Catálogo de niveles
# ============================================================================
def _level(
    number: int,
    title: str,
    subtitle: str,
    icon: str,
    difficulty: str,
    description: str,
    nodes: dict[str, ScenarioNode],
) -> LevelScenario:
    return LevelScenario(
        id=f"level_{number}",
        level_number=number,
        title=title,
        subtitle=subtitle,
        icon=icon,
        difficulty=difficulty,
        description=description,
        start_node_id="node_1",
        nodes=nodes,
    )


_LEVELS = [
    _level(
        1,
        "Nivel 1 · Filtración de Datos Corporativos",
        "Exfiltración en servidor interno · 5 decisiones por voz o texto",
        "🗄",
        "Básico",
        "Detecta, aísla, analiza el alcance forense, controla credenciales, comunica legalmente y erradica una brecha de datos.",
        LEVEL_1_NODES,
    ),
    _level(
        2,
        "Nivel 2 · Ataque de Ransomware en Red",
        "Contención SMB, resguardo de backups y recuperación · 5 decisiones",
        "🛡",
        "Intermedio",
        "Frena el cifrado lateral en red, protege los respaldos inmutables, identifica el paciente cero y recupera sin pagar rescate.",
        LEVEL_2_NODES,
    ),
    _level(
        3,
        "Nivel 3 · Phishing Ejecutivo y Fraude BEC",
        "Compromiso de cuenta directiva y desvío de fondos · 5 decisiones",
        "✉",
        "Intermedio",
        "Revoca sesiones secuestradas, detén una transferencia fraudulenta fuera de banda, limpia reglas ocultas y blinda el correo.",
        LEVEL_3_NODES,
    ),
    _level(
        4,
        "Nivel 4 · Intrusión Cloud y Fuga de API Keys",
        "Credenciales IAM expuestas e instancias maliciosas · 5 decisiones",
        "☁",
        "Avanzado",
        "Revoca llaves IAM filtradas, aísla instancias en la nube, audita CloudTrail, limpia secretos en Git y aplica mínimo privilegio.",
        LEVEL_4_NODES,
    ),
    _level(
        5,
        "Nivel 5 · Amenaza Interna y Sabotaje Crítico",
        "Exfiltración privilegiada, custodia forense y PAM · 5 decisiones",
        "🕵",
        "Experto",
        "Contén una fuga interna privilegiada, asegura la cadena de custodia legal, busca puertas traseras e implementa control dual.",
        LEVEL_5_NODES,
    ),
]

LEVELS_CATALOG: dict[str, LevelScenario] = {level.id: level for level in _LEVELS}

# Compatibilidad directa con código existente
SCENARIO_TREE: dict[str, ScenarioNode] = LEVEL_1_NODES
START_NODE_ID = "node_1"


def get_level_scenario(level_id: str) -> LevelScenario:
    return LEVELS_CATALOG.get(level_id, LEVELS_CATALOG["level_1"])


def list_levels() -> list[LevelScenario]:
    return [LEVELS_CATALOG[k] for k in sorted(LEVELS_CATALOG.keys())]


# ============================================================================
# Validación de rúbricas (se ejecuta en pytest, no al importar)
# ============================================================================
def validate_catalog() -> list[str]:
    """Devuelve la lista de problemas del catálogo (vacía si todo está bien)."""
    from circe_app.evaluator import DecisionValidator as V  # import local: evita dependencias circulares

    errors: list[str] = []
    for level in LEVELS_CATALOG.values():
        ids = [f"node_{i}" for i in range(1, 6)]
        if list(level.nodes) != ids:
            errors.append(f"{level.id}: los nodos deben ser {ids}")
            continue
        for number, node_id in enumerate(ids, start=1):
            node = level.nodes[node_id]
            where = f"{level.id}/{node_id}"
            expected_next = f"node_{number + 1}" if number < 5 else None
            if node.next_node != expected_next:
                errors.append(f"{where}: next_node={node.next_node!r}, se esperaba {expected_next!r}")
            if len(node.correct_actions) < 3:
                errors.append(f"{where}: hacen falta al menos 3 correct_actions")
            if len(node.partial_actions) < 2:
                errors.append(f"{where}: hacen falta al menos 2 partial_actions")
            if len(node.wrong_actions) < 2:
                errors.append(f"{where}: hacen falta al menos 2 wrong_actions")
            if not node.keywords_correct or not node.keywords_wrong:
                errors.append(f"{where}: faltan keywords_correct o keywords_wrong")

            for action in node.correct_actions:
                tokens = V._normalize(action).split()
                if not V._hits(node.keywords_correct, tokens):
                    errors.append(f"{where}: ninguna keyword_correct reconoce «{action}»")
                bad = V._hits(node.keywords_wrong, tokens, skip_negated=True)
                if bad:
                    errors.append(f"{where}: keywords_wrong {bad} coinciden con la acción correcta «{action}»")
    return errors


if __name__ == "__main__":
    problems = validate_catalog()
    print("\n".join(problems) if problems else "Catálogo válido.")