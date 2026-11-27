"""Prueba de paráfrasis: frases NUEVAS (no copiadas de la rúbrica) contra el evaluador completo.

Uso (con el entorno activado):
    python tests/probar_parafrasis.py                      # con LLM
    CIRCE_DISABLE_LLM=1 python tests/probar_parafrasis.py  # solo evaluador local
    CIRCE_LLM_MODEL=qwen3:14b python tests/probar_parafrasis.py

Si un caso falla, puede ser del modelo o de la rúbrica: revisa la columna "razon" del CSV.
"""
import asyncio
import csv
import os
import time

from circe_app.orchestrator import CIRCEOrchestrator

C, P, W = "correct", "partial", "wrong"

CASOS = {
    ("level_1", "node_1"): [
        ("Desconecto el servidor comprometido de la red para frenar la fuga", C),
        ("Aíslo el servidor de la red sin apagarlo ni formatearlo para conservar la memoria", C),
        ("Voy a monitorear el tráfico del servidor para ver qué se llevan", P),
        ("Tomo medidas para resolver el incidente lo antes posible", P),
        ("Apago el servidor y lo formateo para limpiarlo", W),
        ("Aíslo el servidor de la red y después lo formateo", P),
        ("No aíslo nada y espero", W),
    ],
    ("level_1", "node_2"): [
        ("Hago una imagen forense del equipo y reviso los registros de acceso para ver qué archivos salieron", C),
        ("Documento el incidente de forma preliminar y pregunto al responsable del área", P),
        ("Reinicio el servidor y limpio los registros para empezar de cero", W),
    ],
    ("level_1", "node_3"): [
        ("Cierro las sesiones activas del administrador, bloqueo la cuenta y cambio las credenciales privilegiadas", C),
        ("Le pido al administrador que cambie su contraseña", P),
        ("Dejo la cuenta funcionando unos días para ver qué hace el atacante", W),
    ],
    ("level_1", "node_4"): [
        ("Aviso a la dirección, a legal y a protección de datos y activo el protocolo de notificación de brechas", C),
        ("Mando un mensaje a algunos departamentos para que estén al tanto", P),
        ("Prefiero no decir nada para evitar una multa", W),
    ],
    ("level_1", "node_5"): [
        ("Elimino las puertas traseras, restauro desde un respaldo limpio, parcho y hago una revisión posterior al incidente", C),
        ("Instalo las actualizaciones pendientes y cierro el ticket", P),
        ("Reconecto el servidor a la red como estaba sin revisar nada", W),
    ],
    ("level_2", "node_1"): [
        ("Saco de la red los equipos infectados y bloqueo el SMB entre segmentos", C),
        ("Corro el antivirus en uno de los equipos afectados", P),
        ("Reinicio el servidor de archivos para ver si se detiene", W),
    ],
    ("level_2", "node_2"): [
        ("Desconecto el servidor de respaldos de la red y compruebo que las copias estén offline o inmutables", C),
        ("Reviso cuánto espacio queda en el disco de respaldos", P),
        ("Conecto mi disco externo al equipo infectado para sacar los archivos", W),
    ],
    ("level_2", "node_3"): [
        ("Reviso los registros del EDR y del correo para encontrar al paciente cero y saco los hashes del malware", C),
        ("Pregunto a los usuarios quién abrió algún archivo raro", P),
        ("Reinstalo el equipo del paciente cero de inmediato sin guardar nada", W),
    ],
    ("level_2", "node_4"): [
        ("No pago el rescate, activo el plan de continuidad y aviso a las autoridades y a legal", C),
        ("No voy a pagar el rescate y aviso a las autoridades", C),
        ("Aviso a la dirección y espero sus instrucciones", P),
        ("Pago el rescate en bitcoin sin consultar a nadie", W),
    ],
    ("level_2", "node_5"): [
        ("Restauro desde copias limpias, cambio todas las credenciales del dominio, parcho y dejo monitoreo con EDR", C),
        ("Restauro los archivos encima del sistema que estaba infectado", P),
        ("Apago el firewall para que la restauración sea más rápida", W),
    ],
    ("level_3", "node_1"): [
        ("Cierro la sesión del director, invalido sus tokens y le obligo a cambiar la contraseña", C),
        ("Le escribo un correo al director para preguntarle si fue él", P),
        ("Borro la cuenta del director junto con todos sus correos", W),
        ("Bloqueo la sesión y luego elimino la cuenta del director con todos sus correos", P),
    ],
    ("level_3", "node_2"): [
        ("Llamo por teléfono a tesorería y al banco para frenar la transferencia", C),
        ("Le mando un correo normal a tesorería", P),
        ("Dejo que se haga la transferencia para ver a qué cuenta llega", W),
    ],
    ("level_3", "node_3"): [
        ("Reviso las reglas de reenvío del buzón, las delegaciones y las aplicaciones OAuth y borro las sospechosas", C),
        ("Solo reviso la bandeja de entrada", P),
        ("Doy el análisis por terminado sin mirar la configuración del buzón", W),
    ],
    ("level_3", "node_4"): [
        ("Aviso a los clientes afectados por un canal verificado y emito una alerta oficial", C),
        ("Publico un comunicado en el sitio web de la empresa", P),
        ("Espero a que algún cliente pregunte", W),
        ("Les digo a los clientes que esos correos no salieron de nuestra empresa", W),
    ],
    ("level_3", "node_5"): [
        ("Pongo MFA resistente al phishing, configuro SPF, DKIM y DMARC y exijo doble aprobación en los pagos", C),
        ("Mando un folleto sobre phishing una vez al año", P),
        ("Dejo que los directivos entren sin MFA para que sea más cómodo", W),
    ],
    ("level_4", "node_1"): [
        ("Desactivo y revoco ya las llaves IAM expuestas y cierro las sesiones temporales", C),
        ("Le pido al desarrollador que borre el commit", P),
        ("Borro toda la cuenta de la nube de producción", W),
    ],
    ("level_4", "node_2"): [
        ("Detengo las instancias que no son nuestras, saco un snapshot para forense y cierro los security groups", C),
        ("Reviso la factura de la nube del próximo mes", P),
        ("Dejo las instancias corriendo conectadas a la base de datos de producción", W),
    ],
    ("level_4", "node_3"): [
        ("Analizo los registros de CloudTrail para ver si crearon usuarios, roles o descargaron objetos", C),
        ("Miro solo el panel principal de la consola", P),
        ("Reviso rápido la consola", P),
        ("Apago CloudTrail para que no se llene de eventos", W),
    ],
    ("level_4", "node_4"): [
        ("Purgo el historial de Git, paso los secretos a un gestor de secretos y activo escaneo de secretos antes del commit", C),
        ("Hago un commit nuevo comentando la línea de la clave", P),
        ("Subo las llaves nuevas en un archivo de texto al mismo repositorio", W),
    ],
    ("level_4", "node_5"): [
        ("Aplico mínimo privilegio, uso roles temporales con OIDC y configuro alertas de anomalías", C),
        ("Les pido a los programadores que tengan más cuidado", P),
        ("Doy permisos de administrador global a todas las cuentas de servicio", W),
    ],
    ("level_5", "node_1"): [
        ("Bloqueo la transferencia en el DLP y suspendo sus accesos privilegiados de inmediato", C),
        ("Reporto el caso a su jefe directo", P),
        ("Lo llamo para preguntarle qué está copiando", W),
        ("Ignoro la alerta porque es un empleado de confianza", W),
    ],
    ("level_5", "node_2"): [
        ("Hago una imagen forense, calculo los hashes y documento la cadena de custodia", C),
        ("Abro sus archivos en su computadora sin protección contra escritura", P),
        ("Formateo su laptop para dársela a otro empleado", W),
        ("Hago la imagen forense con hashes y luego formateo la laptop para reutilizarla", P),
    ],
    ("level_5", "node_3"): [
        ("Reviso llaves SSH, tareas programadas, cuentas ocultas y cambios recientes en producción", C),
        ("Reviso solo su historial de navegación", P),
        ("Supongo que solo quería copiar archivos y no reviso los servidores", W),
    ],
    ("level_5", "node_4"): [
        ("Coordino de forma confidencial con legal, recursos humanos y dirección y les entrego el informe forense", C),
        ("Aviso solo a su jefe directo", P),
        ("Lo comento en el comedor con otros compañeros", W),
        ("Publico el nombre del empleado en el chat general", W),
    ],
    ("level_5", "node_5"): [
        ("Implemento control dual con PAM, políticas DLP y monitoreo de comportamiento UEBA", C),
        ("Hago una capacitación sobre confidencialidad", P),
        ("Prohíbo internet para toda la empresa", W),
        ("Todos los administradores usarán una misma cuenta root compartida", W),
    ],
}


async def main() -> None:
    modelo = os.getenv("CIRCE_LLM_MODEL", "llama3.2")
    llm_activo = os.getenv("CIRCE_DISABLE_LLM") != "1"
    filas = []

    for level_id in sorted({k[0] for k in CASOS}):
        o = CIRCEOrchestrator(level_id=level_id)
        o.tts.enabled = False
        for (lvl, node_id), casos in CASOS.items():
            if lvl != level_id:
                continue
            for texto, esperado in casos:
                o.current_node = node_id
                o.engine.advance(node_id)
                o.session.active_node = node_id
                o.history = []
                t0 = time.perf_counter()
                r = await o.process_student_turn(texto, auto_advance=False, speak_response=False)
                ev = r["evaluation"]
                filas.append({
                    "nivel": lvl, "nodo": node_id, "esperado": esperado,
                    "obtenido": ev["verdict"], "score": ev["score"],
                    "confianza": ev.get("confidence", "-"),
                    "peligrosa": ev.get("dangerous_action"),
                    "fuera_tema": ev.get("off_topic"),
                    "respaldo": llm_activo and ev["engine_used"] == "Evaluador Semántico Local",
                    "segundos": round(time.perf_counter() - t0, 1),
                    "texto": texto, "razon": ev["reason"], "accion": ev["recommended_action"],
                })
        print(f"{level_id} listo")

    total = len(filas)
    ok = sum(f["esperado"] == f["obtenido"] for f in filas)
    graves = [f for f in filas if
              (f["esperado"] != "correct" and f["obtenido"] == "correct") or
              (f["esperado"] == "correct" and f["obtenido"] == "wrong")]
    respaldos = sum(f["respaldo"] for f in filas)
    tiempos = [f["segundos"] for f in filas if f["segundos"] > 0.5]

    print(f"\n=== Paráfrasis | modelo: {modelo} | LLM {'activo' if llm_activo else 'desactivado'} ===")
    print(f"Aciertos: {ok}/{total}")
    print(f"Errores GRAVES (sobrecalificado o correcta→wrong): {len(graves)}")
    print(f"Caídas al evaluador local: {respaldos}")
    if tiempos:
        print(f"Tiempo medio por caso con LLM: {sum(tiempos) / len(tiempos):.1f}s")

    print("\n--- Casos a revisar ---")
    for f in filas:
        if f["esperado"] != f["obtenido"]:
            marca = "GRAVE" if f in graves else "revisar"
            print(f"[{marca}] {f['nivel']}/{f['nodo']}: esperado={f['esperado']} "
                  f"obtenido={f['obtenido']} score={f['score']} peligrosa={f['peligrosa']} | {f['texto']}")

    nombre = f"parafrasis_{modelo.replace(':', '_').replace('/', '_')}.csv"
    with open(nombre, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)
    print(f"\nDetalle completo en {nombre}")


if __name__ == "__main__":
    asyncio.run(main())