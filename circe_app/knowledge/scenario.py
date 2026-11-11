from __future__ import annotations

from circe_app.config import LevelScenario, ScenarioNode

# Nivel 1 (y árbol principal por compatibilidad): Filtración de datos corporativos (5 niveles/decisiones)
LEVEL_1_NODES: dict[str, ScenarioNode] = {
    "node_1": ScenarioNode(
        id="node_1",
        level_number=1,
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
            "bloquear el acceso y aislar la maquina",
            "desconectar el equipo comprometido de la red",
            "segmentar o cortar la conexion de red del servidor",
        ],
        partial_actions=[
            "revisar los logs",
            "notificar al equipo de seguridad",
            "hacer copia forense",
            "monitorear el trafico",
        ],
        wrong_actions=[
            "restaurar el sistema sin investigar",
            "eliminar todo sin analisis",
            "formatear el servidor inmediatamente",
            "compartir credenciales para probar",
            "ignorar la amenaza",
        ],
        keywords_correct=["aislar", "aislo", "desconectar", "bloquear", "contener", "red", "vlan", "cortar"],
        keywords_partial=["revisar", "logs", "avisar", "notificar", "investigar", "monitorear"],
        keywords_wrong=["formatear", "borrar", "eliminar", "ignorar", "apagar", "reiniciar"],
        consequences=[
            "El atacante puede seguir extrayendo información crítica.",
            "La evidencia volátil se puede perder si se apaga o formatea.",
        ],
        next_node="node_2",
    ),
    "node_2": ScenarioNode(
        id="node_2",
        level_number=2,
        title="Nivel 2 · Preservación y alcance",
        prompt=(
            "Nivel 2: Análisis de alcance y evidencia. El servidor ya fue aislado de la red, "
            "pero aún no sabemos qué archivos fueron extraídos ni cómo ingresó el atacante. "
            "¿Cuál es tu siguiente decisión técnica?"
        ),
        hint="Preserva la evidencia forense (memoria y registros) y analiza los logs de acceso y tráfico para saber exactamente qué datos se filtraron.",
        correct_actions=[
            "revisar los logs de acceso y preservar evidencia forense",
            "analizar permisos conexiones y registros de auditoria",
            "capturar imagen forense y revisar registros de acceso",
            "identificar usuarios y archivos afectados en los logs",
        ],
        partial_actions=[
            "revisar los archivos mas importantes manualmente",
            "preguntar al responsable del area",
            "documentar la incidencia preliminar",
        ],
        wrong_actions=[
            "borrar los logs",
            "reiniciar todo sin evidencia",
            "revelar la brecha a todos los empleados por chat",
            "modificar los archivos del servidor",
        ],
        keywords_correct=["logs", "registros", "forense", "evidencia", "auditoria", "alcance", "analizar", "permisos"],
        keywords_partial=["archivos", "preguntar", "documentar", "revisar"],
        keywords_wrong=["borrar", "reiniciar", "ocultar", "formatear"],
        consequences=[
            "Se pierde la trazabilidad forense del ataque.",
            "No se podrá demostrar qué información fue comprometida.",
        ],
        next_node="node_3",
    ),
    "node_3": ScenarioNode(
        id="node_3",
        level_number=3,
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
            "cambiar contrasenas privilegiadas y auditar movimiento lateral",
            "deshabilitar las credenciales afectadas y forzar autenticacion multifactor",
        ],
        partial_actions=[
            "cambiar solo la contrasena del usuario",
            "pedir al administrador que cierre sesion",
            "escanear con antivirus el servidor",
        ],
        wrong_actions=[
            "dejar la cuenta activa para observar al atacante",
            "eliminar el directorio activo completo",
            "enviar las nuevas contrasenas por correo sin cifrar",
        ],
        keywords_correct=["revocar", "credenciales", "token", "sesiones", "rotar", "bloquear cuenta", "mfa", "privilegios", "deshabilitar"],
        keywords_partial=["contrasena", "clave", "antivirus", "usuario"],
        keywords_wrong=["dejar activa", "correo sin cifrar", "ignorar cuenta"],
        consequences=[
            "El atacante mantiene persistencia usando el token activo en otros nodos.",
            "El incidente escala a toda la red corporativa.",
        ],
        next_node="node_4",
    ),
    "node_4": ScenarioNode(
        id="node_4",
        level_number=4,
        title="Nivel 4 · Comunicación y protocolo",
        prompt=(
            "Nivel 4: Comunicación e informe regulatorio. Confirmas que se filtraron datos personales "
            "de clientes. Debes coordinar la comunicación interna y el protocolo legal. "
            "¿Cómo procedes?"
        ),
        hint="Activa el comité de respuesta a incidentes, notifica a Dirección, Legal y Privacidad de Datos siguiendo el canal oficial documentado.",
        correct_actions=[
            "notificar a direccion seguridad y area legal siguiendo el plan de respuesta",
            "documentar medidas y comunicar a stakeholders y proteccion de datos",
            "activar el protocolo oficial de notificacion de brecha de datos",
        ],
        partial_actions=[
            "avisar a algunos departamentos por mensaje",
            "esperar unos dias antes de avisar a legal",
            "iniciar un reporte informal",
        ],
        wrong_actions=[
            "publicar la informacion en un correo masivo a toda la empresa",
            "ocultar la incidencia para evitar multas o alarma",
            "cancelar el proceso de respuesta",
        ],
        keywords_correct=["notificar", "direccion", "legal", "protocolo", "plan", "comunicar", "documentar", "comite", "privacidad"],
        keywords_partial=["avisar", "departamentos", "reporte", "mensaje"],
        keywords_wrong=["ocultar", "esconder", "correo masivo", "publicar en redes", "cancelar"],
        consequences=[
            "Sanciones legales graves por incumplimiento de notificación de brecha.",
            "Caos comunicacional y pérdida de confianza reputacional.",
        ],
        next_node="node_5",
    ),
    "node_5": ScenarioNode(
        id="node_5",
        level_number=5,
        title="Nivel 5 · Erradicación y mejora",
        prompt=(
            "Nivel 5: Erradicación, recuperación y lecciones aprendidas. La amenaza está contenida "
            "y notificada. Para restaurar la operación de forma segura y evitar que se repita, "
            "¿qué medidas finales ejecutas?"
        ),
        hint="Elimina cualquier puerta trasera, restaura desde copias limpias verificadas, aplica parches/controles DLP y realiza la reunión post-mortem.",
        correct_actions=[
            "erradicar persistencia restaurar desde backup limpio y aplicar controles dlp y monitoreo",
            "verificar integridad parchar vulnerabilidades y documentar lecciones aprendidas",
            "restaurar servicios seguros reforzar reglas del siem y realizar analisis post mortem",
        ],
        partial_actions=[
            "reconectar el servidor a la red como estaba",
            "instalar actualizaciones pendientes solamente",
            "cerrar el ticket del incidente",
        ],
        wrong_actions=[
            "volver a conectar el servidor sin limpiar puertas traseras",
            "desactivar las alertas del siem para evitar falsos positivos",
            "borrar toda la documentacion del incidente",
        ],
        keywords_correct=["erradicar", "backup", "limpio", "parchar", "monitoreo", "dlp", "post mortem", "lecciones", "restaurar", "integridad"],
        keywords_partial=["actualizar", "cerrar ticket", "reconectar"],
        keywords_wrong=["sin limpiar", "desactivar alertas", "borrar documentacion"],
        consequences=[
            "El atacante vuelve a entrar mediante una puerta trasera no erradicada.",
            "La organización repite los mismos errores de seguridad.",
        ],
        next_node=None,
    ),
}

# Nivel 2: Ataque de Ransomware
LEVEL_2_NODES: dict[str, ScenarioNode] = {
    "node_1": ScenarioNode(
        id="node_1",
        level_number=1,
        title="Nivel 1 · Contención de cifrado",
        prompt=(
            "Nivel 1: Estallido de Ransomware. Varias estaciones de finanzas muestran una nota de rescate "
            "y el cifrado se propaga por carpetas compartidas SMB. ¿Cuál es tu primera acción inmediata?"
        ),
        hint="Corta la propagación en red aislando el segmento afectado y bloqueando el tráfico SMB lateral.",
        correct_actions=[
            "aislar el segmento de red afectado y bloquear puertos smb",
            "desconectar los equipos infectados de la red y contener la propagacion",
        ],
        partial_actions=["ejecutar un escaneo antivirus en un equipo", "avisar por correo al área de soporte"],
        wrong_actions=["pagar el rescate inmediatamente", "reiniciar el servidor central de archivos"],
        keywords_correct=["aislar", "segmento", "smb", "red", "desconectar", "bloquear", "contener", "propagacion"],
        keywords_partial=["antivirus", "avisar", "soporte"],
        keywords_wrong=["pagar", "rescate", "ignorar"],
        consequences=["El ransomware cifra los servidores centrales de producción."],
        next_node="node_2",
    ),
    "node_2": ScenarioNode(
        id="node_2",
        level_number=2,
        title="Nivel 2 · Protección de Backups",
        prompt=(
            "Nivel 2: Resguardo de copias de seguridad. El malware busca destruir las copias sombra (VSS) "
            "y alcanzar el servidor de backups. ¿Qué medida tomas sobre los respaldos?"
        ),
        hint="Verifica el aislamiento offline/inmutable de los backups y revoca el acceso desde la red comprometida.",
        correct_actions=[
            "aislar el servidor de backups y verificar copias inmutables u offline",
            "proteger los respaldos desconectando su acceso desde la red infectada",
        ],
        partial_actions=["iniciar un nuevo backup desde las máquinas infectadas", "revisar el espacio en disco"],
        wrong_actions=["conectar el disco de backup externo al equipo infectado", "borrar los backups antiguos"],
        keywords_correct=["backup", "respaldos", "inmutable", "offline", "aislar", "proteger", "copias"],
        keywords_partial=["espacio", "revisar"],
        keywords_wrong=["conectar al infectado", "borrar backups"],
        consequences=["Los respaldos quedan cifrados y se pierde la capacidad de recuperación."],
        next_node="node_3",
    ),
    "node_3": ScenarioNode(
        id="node_3",
        level_number=3,
        title="Nivel 3 · Identificación del vector",
        prompt=(
            "Nivel 3: Análisis forense del paciente cero. Necesitas identificar la variante del ransomware "
            "y cómo entró para cerrar la brecha. ¿Qué realizas?"
        ),
        hint="Analiza los artefactos forenses, logs de EDR/correo y el hash del binario para hallar el vector inicial.",
        correct_actions=[
            "analizar logs del edr y correo para identificar el paciente cero y el vector de entrada",
            "extraer indicadores de compromiso hashes y preservar evidencia forense",
        ],
        partial_actions=["preguntar a los usuarios quién abrió un archivo", "revisar solo el navegador web"],
        wrong_actions=["formatear el paciente cero sin recoger evidencia", "subir documentos confidenciales a foros públicos"],
        keywords_correct=["edr", "paciente cero", "vector", "hash", "forense", "logs", "indicadores", "ioc", "analizar"],
        keywords_partial=["preguntar", "navegador"],
        keywords_wrong=["formatear sin", "foros publicos"],
        consequences=["El vector de entrada sigue abierto y el atacante reingresa."],
        next_node="node_4",
    ),
    "node_4": ScenarioNode(
        id="node_4",
        level_number=4,
        title="Nivel 4 · Gestión de crisis",
        prompt=(
            "Nivel 4: Decisión ante la extorsión. Los atacantes exigen pago en criptomonedas en 24 horas. "
            "La directiva pregunta si deben pagar. ¿Qué recomiendas y ejecutas?"
        ),
        hint="No pagar el rescate, activar el plan de continuidad de negocio y notificar a las autoridades y al CERT.",
        correct_actions=[
            "no pagar el rescate activar continuidad de negocio y notificar a autoridades y equipo legal",
            "coordinar con direccion legal y cert usando nuestros respaldos verificados",
        ],
        partial_actions=["negociar por cuenta propia sin avisar a dirección", "esperar a que venza el plazo"],
        wrong_actions=["pagar el rescate sin garantías ni autorización", "ocultar el ataque a la junta directiva"],
        keywords_correct=["no pagar", "continuidad", "autoridades", "legal", "cert", "respaldos", "protocolo"],
        keywords_partial=["negociar", "esperar"],
        keywords_wrong=["pagar el rescate", "ocultar"],
        consequences=["Financiamiento criminal sin garantía de descifrado y sanciones legales."],
        next_node="node_5",
    ),
    "node_5": ScenarioNode(
        id="node_5",
        level_number=5,
        title="Nivel 5 · Restauración limpia",
        prompt=(
            "Nivel 5: Recuperación del entorno. Ya tienes las copias limpias listas. "
            "¿Cómo restauras la operación sin riesgo de reinfección?"
        ),
        hint="Reconstruye los sistemas limpios, rota todas las credenciales del dominio, aplica parches y monitorea con EDR.",
        correct_actions=[
            "restaurar desde copias limpias rotar credenciales de dominio aplicar parches y monitorear con edr",
            "reconstruir servidores verificando integridad y reforzar segmentacion de red",
        ],
        partial_actions=["restaurar los archivos encima del sistema infectado", "cambiar solo una contraseña"],
        wrong_actions=["deshabilitar el firewall para restaurar más rápido", "reconectar equipos cifrados a producción"],
        keywords_correct=["restaurar", "limpias", "rotar", "credenciales", "parches", "edr", "segmentacion", "reconstruir"],
        keywords_partial=["encima", "una contrasena"],
        keywords_wrong=["deshabilitar firewall", "equipos cifrados"],
        consequences=["Reinfección inmediata durante la restauración."],
        next_node=None,
    ),
}

# Nivel 3: Phishing Ejecutivo y Fraude BEC
LEVEL_3_NODES: dict[str, ScenarioNode] = {
    "node_1": ScenarioNode(
        id="node_1",
        level_number=1,
        title="Nivel 1 · Bloqueo de buzón comprometido",
        prompt=(
            "Nivel 1: Alerta de Phishing Ejecutivo (BEC). Detectas que la cuenta de correo del Director Financiero "
            "inició sesión desde una IP anómala y envió órdenes de pago urgentes. ¿Qué haces primero?"
        ),
        hint="Suspende la sesión activa, revoca los tokens de acceso del buzón y bloquea el acceso no autorizado.",
        correct_actions=["bloquear acceso revocar tokens de sesion y forzar cambio de credenciales del director"],
        partial_actions=["enviar un correo preguntando al director si fue él"],
        wrong_actions=["eliminar la cuenta de correo junto con todos sus mensajes"],
        keywords_correct=["bloquear", "revocar", "tokens", "sesion", "credenciales", "suspender", "aislar cuenta"],
        keywords_partial=["preguntar", "correo"],
        keywords_wrong=["eliminar la cuenta", "ignorar"],
        consequences=["El atacante sigue operando desde el buzón ejecutivo."],
        next_node="node_2",
    ),
    "node_2": ScenarioNode(
        id="node_2",
        level_number=2,
        title="Nivel 2 · Freno de transferencia",
        prompt=(
            "Nivel 2: Contención del fraude financiero. El equipo de tesorería está a punto de aprobar "
            "una transferencia bancaria ordenada por el atacante. ¿Cómo actúas?"
        ),
        hint="Contacta por vía telefónica o presencial (fuera de banda) a tesorería y al banco para detener la transferencia.",
        correct_actions=["contactar fuera de banda a tesoreria y al banco para detener la transferencia fraudulenta"],
        partial_actions=["mandar un correo normal a tesorería"],
        wrong_actions=["autorizar el pago para ver a qué cuenta llega"],
        keywords_correct=["detener", "transferencia", "tesoreria", "banco", "telefono", "fuera de banda", "frenar", "cancelar pago"],
        keywords_partial=["mandar correo", "esperar"],
        keywords_wrong=["autorizar", "aprobar pago"],
        consequences=["Pérdida financiera directa e irreversible de fondos corporativos."],
        next_node="node_3",
    ),
    "node_3": ScenarioNode(
        id="node_3",
        level_number=3,
        title="Nivel 3 · Auditoría de reglas ocultas",
        prompt=(
            "Nivel 3: Persistencia en el correo. Los atacantes BEC suelen ocultar sus rastros dentro del buzón. "
            "¿Qué auditas técnicamente en la cuenta afectada?"
        ),
        hint="Revisa y elimina reglas de reenvío automático, filtros ocultos a carpetas RSS/Papelera y aplicaciones OAuth maliciosas.",
        correct_actions=["auditar y eliminar reglas de reenvio ocultas delegaciones y aplicaciones oauth no autorizadas"],
        partial_actions=["revisar solo la bandeja de entrada principal"],
        wrong_actions=["dar por cerrado el análisis sin revisar configuración del buzón"],
        keywords_correct=["reglas", "reenvio", "oauth", "filtros", "delegacion", "auditar", "buzon", "eliminar reglas"],
        keywords_partial=["bandeja", "entrada"],
        keywords_wrong=["sin revisar", "cerrar"],
        consequences=["Todos los correos entrantes siguen reenviándose en secreto al atacante."],
        next_node="node_4",
    ),
    "node_4": ScenarioNode(
        id="node_4",
        level_number=4,
        title="Nivel 4 · Alerta a terceros",
        prompt=(
            "Nivel 4: Protección de socios y clientes. Descubres que el atacante también envió facturas falsas "
            "a tres clientes importantes desde el correo real. ¿Qué acción tomas?"
        ),
        hint="Notifica formalmente a los clientes afectados por un canal seguro verificando que no paguen las cuentas bancarias alteradas.",
        correct_actions=["notificar a los clientes afectados por canal verificado y emitir alerta oficial de seguridad"],
        partial_actions=["esperar a que los clientes pregunten"],
        wrong_actions=["negar que el correo provino de la empresa"],
        keywords_correct=["notificar", "clientes", "avisar", "canal seguro", "facturas", "alerta", "comunicar"],
        keywords_partial=["esperar"],
        keywords_wrong=["negar", "ocultar"],
        consequences=["Los clientes sufren fraude financiero y demandan a la organización."],
        next_node="node_5",
    ),
    "node_5": ScenarioNode(
        id="node_5",
        level_number=5,
        title="Nivel 5 · Blindaje anti-phishing",
        prompt=(
            "Nivel 5: Prevención estructural. Para evitar futuros ataques BEC y suplantación de identidad, "
            "¿qué controles técnicos y de proceso implementas?"
        ),
        hint="Implementa MFA resistente al phishing (FIDO2), políticas SPF/DKIM/DMARC y verificación en dos pasos para pagos.",
        correct_actions=["implementar mfa resistente a phishing configurar spf dkim dmarc y doble aprobacion en pagos"],
        partial_actions=["enviar un folleto informativo una vez al año"],
        wrong_actions=["permitir inicios de sesión sin MFA para comodidad de los directivos"],
        keywords_correct=["mfa", "dmarc", "spf", "dkim", "doble aprobacion", "fido", "autenticacion", "capacitacion"],
        keywords_partial=["folleto"],
        keywords_wrong=["sin mfa", "desactivar"],
        consequences=["La organización vuelve a caer en ataques de phishing."],
        next_node=None,
    ),
}

# Nivel 4: Intrusión Cloud y Fuga de Credenciales IAM
LEVEL_4_NODES: dict[str, ScenarioNode] = {
    "node_1": ScenarioNode(
        id="node_1",
        level_number=1,
        title="Nivel 1 · Revocación de API Keys",
        prompt=(
            "Nivel 1: Alerta en la Nube. Una llave de acceso AWS/Cloud fue expuesta en un repositorio "
            "y un atacante está creando instancias de alto costo y leyendo buckets S3. ¿Qué haces primero?"
        ),
        hint="Desactiva y revoca de inmediato las llaves IAM comprometidas y aplica una política de denegación temporal.",
        correct_actions=["desactivar y revocar inmediatamente las llaves iam comprometidas y sesiones temporales"],
        partial_actions=["enviar un mensaje al desarrollador para que borre el commit"],
        wrong_actions=["eliminar toda la cuenta de nube en producción"],
        keywords_correct=["revocar", "desactivar", "iam", "llaves", "keys", "credenciales", "bloquear", "rotar"],
        keywords_partial=["commit", "desarrollador"],
        keywords_wrong=["eliminar cuenta", "ignorar"],
        consequences=["El atacante continúa escalando privilegios y extrayendo datos del bucket."],
        next_node="node_2",
    ),
    "node_2": ScenarioNode(
        id="node_2",
        level_number=2,
        title="Nivel 2 · Contención de recursos",
        prompt=(
            "Nivel 2: Instancias no autorizadas. El atacante desplegó 15 máquinas virtuales y abrió grupos "
            "de seguridad a internet. ¿Cómo contienes la infraestructura?"
        ),
        hint="Aísla o detén las instancias maliciosas conservando snapshots para forense y cierra los Security Groups abiertos.",
        correct_actions=["aislar y detener instancias no autorizadas tomar snapshot forense y cerrar security groups"],
        partial_actions=["revisar la factura de la nube del próximo mes"],
        wrong_actions=["dejar las instancias corriendo conectadas a la base de datos productiva"],
        keywords_correct=["aislar", "detener", "instancias", "snapshot", "security group", "firewall", "contener", "cerrar puertos"],
        keywords_partial=["factura", "revisar"],
        keywords_wrong=["dejar corriendo", "ignorar"],
        consequences=["Consumo masivo de recursos y puente hacia la base de datos interna."],
        next_node="node_3",
    ),
    "node_3": ScenarioNode(
        id="node_3",
        level_number=3,
        title="Nivel 3 · Auditoría de CloudTrail",
        prompt=(
            "Nivel 3: Trazabilidad en la nube. Necesitas saber si el atacante creó nuevos usuarios IAM, "
            "roles ocultos o descargó objetos confidenciales. ¿Qué analizas?"
        ),
        hint="Audita los registros de CloudTrail / Activity Logs buscando llamadas API de creación de usuarios, roles y acceso a datos.",
        correct_actions=["auditar registros de cloudtrail y logs de acceso para detectar nuevos roles usuarios o descargas"],
        partial_actions=["mirar únicamente el panel principal de la consola web"],
        wrong_actions=["desactivar el registro de auditoría CloudTrail"],
        keywords_correct=["cloudtrail", "logs", "auditar", "roles", "usuarios", "api", "registros", "analizar"],
        keywords_partial=["consola", "panel"],
        keywords_wrong=["desactivar", "borrar logs"],
        consequences=["Un usuario puerta trasera creado por el atacante pasa desapercibido."],
        next_node="node_4",
    ),
    "node_4": ScenarioNode(
        id="node_4",
        level_number=4,
        title="Nivel 4 · Limpieza del repositorio",
        prompt=(
            "Nivel 4: Remediación en código fuente. La llave comprometida sigue visible en el historial "
            "de Git. ¿Cómo corriges la gestión de secretos con el equipo de desarrollo?"
        ),
        hint="Purga el historial del repositorio, migra las credenciales a un gestor de secretos (Vault/Secrets Manager) y activa escaneo pre-commit.",
        correct_actions=["eliminar secretos del historial git usar gestor de secretos y activar escaneo automatico"],
        partial_actions=["hacer un nuevo commit comentando la línea de la clave"],
        wrong_actions=["subir las nuevas llaves en otro archivo de texto al mismo repositorio"],
        keywords_correct=["secretos", "vault", "historial", "git", "escaneo", "variables de entorno", "purgar", "rotar"],
        keywords_partial=["comentar", "nuevo commit"],
        keywords_wrong=["subir nuevas llaves", "texto plano"],
        consequences=["Las credenciales vuelven a filtrarse en el historial del repositorio."],
        next_node="node_5",
    ),
    "node_5": ScenarioNode(
        id="node_5",
        level_number=5,
        title="Nivel 5 · Mínimo privilegio y alertas",
        prompt=(
            "Nivel 5: Arquitectura Cloud Segura. Para impedir que una credencial futura tenga control total, "
            "¿qué políticas implementas?"
        ),
        hint="Aplica el principio de mínimo privilegio en IAM, usa roles temporales (OIDC) sin llaves estáticas y activa alertas de anomalías.",
        correct_actions=["aplicar minimo privilegio usar roles temporales oidc y configurar alertas de seguridad cloud"],
        partial_actions=["pedir a los programadores que tengan más cuidado"],
        wrong_actions=["dar permisos de Administrador Global a todas las cuentas de servicio"],
        keywords_correct=["minimo privilegio", "roles", "temporales", "oidc", "alertas", "monitoreo", "politicas", "iam"],
        keywords_partial=["cuidado"],
        keywords_wrong=["administrador global", "todos los permisos"],
        consequences=["Cualquier filtración futura comprometerá toda la infraestructura cloud."],
        next_node=None,
    ),
}

# Nivel 5: Amenaza Interna y Exfiltración Crítica (Insider Threat)
LEVEL_5_NODES: dict[str, ScenarioNode] = {
    "node_1": ScenarioNode(
        id="node_1",
        level_number=1,
        title="Nivel 1 · Contención silenciosa",
        prompt=(
            "Nivel 1: Alerta de Amenaza Interna. El sistema DLP detecta que un ingeniero con altos privilegios "
            "está copiando propiedad intelectual y esquemas de base de datos a un servicio externo. "
            "¿Qué haces primero?"
        ),
        hint="Bloquea la transferencia saliente y suspende los accesos privilegiados en coordinación con Seguridad sin destruir las pruebas.",
        correct_actions=["bloquear la transferencia en el dlp o proxy y suspender los accesos privilegiados de inmediato"],
        partial_actions=["llamar directamente al ingeniero para preguntarle qué está copiando"],
        wrong_actions=["ignorar la alerta porque es un empleado de confianza"],
        keywords_correct=["bloquear", "suspender", "accesos", "privilegios", "dlp", "proxy", "contener", "revocar"],
        keywords_partial=["preguntarle", "llamar"],
        keywords_wrong=["ignorar", "confianza"],
        consequences=["El empleado alerta que fue descubierto, borra huellas y completa el robo."],
        next_node="node_2",
    ),
    "node_2": ScenarioNode(
        id="node_2",
        level_number=2,
        title="Nivel 2 · Cadena de custodia",
        prompt=(
            "Nivel 2: Preservación legal y forense. El caso requerirá investigación legal formal. "
            "¿Cómo aseguras la evidencia digital del equipo y de los servidores?"
        ),
        hint="Asegura la estación de trabajo, realiza copia forense bit a bit con hash criptográfico y documenta la cadena de custodia.",
        correct_actions=["preservar evidencia con imagen forense calcular hashes y documentar la cadena de custodia"],
        partial_actions=["abrir los archivos en la computadora del empleado sin protección de escritura"],
        wrong_actions=["reutilizar y formatear la laptop para entregársela a otro empleado"],
        keywords_correct=["forense", "custodia", "hash", "evidencia", "imagen", "preservar", "legal", "documentar"],
        keywords_partial=["abrir archivos"],
        keywords_wrong=["formatear", "reutilizar"],
        consequences=["Las pruebas son invalidadas en un proceso legal por romper la cadena de custodia."],
        next_node="node_3",
    ),
    "node_3": ScenarioNode(
        id="node_3",
        level_number=3,
        title="Nivel 3 · Búsqueda de bombas lógicas",
        prompt=(
            "Nivel 3: Verificación de sabotaje. Como el usuario tenía permisos de administrador en producción, "
            "existe riesgo de que haya dejado puertas traseras o tareas programadas maliciosas. ¿Qué realizas?"
        ),
        hint="Audita tareas programadas (cron), llaves SSH, cuentas secundarias, cambios recientes en código y configuraciones de producción.",
        correct_actions=["auditar llaves ssh tareas programadas cuentas ocultas y cambios recientes en produccion"],
        partial_actions=["revisar solo su historial de navegación web"],
        wrong_actions=["asumir que solo quería copiar archivos y no revisar los servidores"],
        keywords_correct=["auditar", "ssh", "tareas", "cron", "puertas traseras", "backdoor", "produccion", "cuentas", "integridad"],
        keywords_partial=["navegacion"],
        keywords_wrong=["no revisar", "asumir"],
        consequences=["Una bomba lógica se activa días después deteniendo los sistemas críticos."],
        next_node="node_4",
    ),
    "node_4": ScenarioNode(
        id="node_4",
        level_number=4,
        title="Nivel 4 · Coordinación Legal y RRHH",
        prompt=(
            "Nivel 4: Gestión interdepartamental. Con la evidencia técnica asegurada, debes articular "
            "la respuesta organizacional. ¿Con qué áreas y de qué forma actúas?"
        ),
        hint="Coordina confidencialmente con Dirección, Legal y Recursos Humanos entregando el informe forense documentado.",
        correct_actions=["coordinar confidencialmente con area legal recursos humanos y direccion entregando el informe forense"],
        partial_actions=["comentar el caso en el comedor con otros compañeros"],
        wrong_actions=["publicar el nombre del empleado en el chat general de la empresa"],
        keywords_correct=["legal", "recursos humanos", "rrhh", "direccion", "confidencial", "informe", "coordinar"],
        keywords_partial=["comentar"],
        keywords_wrong=["publicar", "chat general"],
        consequences=["Riesgo de demandas laborales y filtración de la investigación en curso."],
        next_node="node_5",
    ),
    "node_5": ScenarioNode(
        id="node_5",
        level_number=5,
        title="Nivel 5 · Control dual y DLP",
        prompt=(
            "Nivel 5: Reducción de riesgo interno. Para evitar que un solo administrador pueda extraer datos "
            "masivos o alterar producción sin supervisión, ¿qué controles implementas?"
        ),
        hint="Implementa control dual (PAM / aprobación de cuatro ojos), políticas DLP estrictas y monitoreo de comportamiento (UEBA).",
        correct_actions=["implementar control dual gestion de accesos privilegiados pam dlp y monitoreo ueba"],
        partial_actions=["prohibir el uso de internet a toda la empresa"],
        wrong_actions=["compartir una única cuenta root entre todos los administradores"],
        keywords_correct=["control dual", "pam", "dlp", "ueba", "privilegiados", "monitoreo", "segregacion", "alertas"],
        keywords_partial=["prohibir internet"],
        keywords_wrong=["cuenta root compartida", "compartir"],
        consequences=["Persiste el riesgo de abuso de privilegios sin trazabilidad individual."],
        next_node=None,
    ),
}

LEVELS_CATALOG: dict[str, LevelScenario] = {
    "level_1": LevelScenario(
        id="level_1",
        level_number=1,
        title="Nivel 1 · Filtración de Datos Corporativos",
        subtitle="Exfiltración en servidor interno · 5 decisiones por voz o texto",
        icon="🗄",
        difficulty=" Básico",
        description="Detecta, aísla, analiza el alcance forense, controla credenciales, comunica legalmente y erradica una brecha de datos.",
        start_node_id="node_1",
        nodes=LEVEL_1_NODES,
    ),
    "level_2": LevelScenario(
        id="level_2",
        level_number=2,
        title="Nivel 2 · Ataque de Ransomware en Red",
        subtitle="Contención SMB, resguardo de backups y recuperación · 5 decisiones",
        icon="🛡",
        difficulty="Intermedio",
        description="Frena el cifrado lateral en red, protege los respaldos inmutables, identifica el paciente cero y recupera sin pagar rescate.",
        start_node_id="node_1",
        nodes=LEVEL_2_NODES,
    ),
    "level_3": LevelScenario(
        id="level_3",
        level_number=3,
        title="Nivel 3 · Phishing Ejecutivo y Fraude BEC",
        subtitle="Compromiso de cuenta directiva y desvío de fondos · 5 decisiones",
        icon="✉",
        difficulty="Intermedio",
        description="Revoca sesiones secuestradas, detén una transferencia fraudulenta fuera de banda, limpia reglas ocultas y blinda el correo.",
        start_node_id="node_1",
        nodes=LEVEL_3_NODES,
    ),
    "level_4": LevelScenario(
        id="level_4",
        level_number=4,
        title="Nivel 4 · Intrusión Cloud y Fuga de API Keys",
        subtitle="Credenciales IAM expuestas e instancias maliciosas · 5 decisiones",
        icon="☁",
        difficulty="Avanzado",
        description="Revoca llaves IAM filtradas, aísla instancias en la nube, audita CloudTrail, limpia secretos en Git y aplica mínimo privilegio.",
        start_node_id="node_1",
        nodes=LEVEL_4_NODES,
    ),
    "level_5": LevelScenario(
        id="level_5",
        level_number=5,
        title="Nivel 5 · Amenaza Interna y Sabotaje Crítico",
        subtitle="Exfiltración privilegiada, custodia forense y PAM · 5 decisiones",
        icon="🕵",
        difficulty="Experto",
        description="Contén una fuga interna privilegiada, asegura la cadena de custodia legal, busca puertas traseras e implementa control dual.",
        start_node_id="node_1",
        nodes=LEVEL_5_NODES,
    ),
}

# Compatibilidad directa con código existente
SCENARIO_TREE: dict[str, ScenarioNode] = LEVEL_1_NODES
START_NODE_ID = "node_1"


def get_level_scenario(level_id: str) -> LevelScenario:
    return LEVELS_CATALOG.get(level_id, LEVELS_CATALOG["level_1"])


def list_levels() -> list[LevelScenario]:
    return [LEVELS_CATALOG[k] for k in sorted(LEVELS_CATALOG.keys())]
