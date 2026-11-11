# CIRCE MVP

CIRCE (Conversational Intelligence for Response and Cybersecurity Education) es un MVP local orientado a educación en ciberseguridad mediante simulación interactiva con voz y un escape room conversacional.

## Objetivo del MVP

- Un único escenario: filtración de datos / acceso no autorizado a información corporativa.
- Árbol de decisiones corto: 3 nodos de decisión iniciales.
- Interacción principal: voz + audio de retorno.
- Ejecución local para privacidad y latencia.

## Stack recomendado

- STT: faster-whisper o Whisper local de OpenAI.
- LLM: Ollama con modelos locales como `llama3.1`, `mistral`, o `qwen2.5`.
- TTS: pyttsx3 (offline) o Piper TTS.
- Orquestación: Python puro con clases y prompt-driven evaluation.
- Base de conocimiento: reglas en Python + estructura de escenarios.

## Estructura del proyecto

```text
circe_mvp/
├── main.py
├── requirements.txt
├── README.md
├── circe_app/
│   ├── __init__.py
│   ├── config.py
│   ├── orchestrator.py
│   ├── ai/
│   │   ├── __init__.py
│   │   └── llm_client.py
│   ├── audio/
│   │   ├── __init__.py
│   │   ├── stt.py
│   │   └── tts.py
│   └── knowledge/
│       ├── __init__.py
│       └── scenario.py
└── .gitignore
```

## Cómo ejecutar

1. Crear entorno virtual.
2. Instalar dependencias:
   `pip install -r requirements.txt`
3. Iniciar Ollama local y descargar un modelo, por ejemplo:
   `ollama run llama3.1`
4. Ejecutar:
   `python main.py --demo-text "Aísla el servidor afectado y revisa los logs"`

Se puede usar `--mic` para grabar audio desde el micrófono.

## Escenario base

El caso trata de una filtración de datos desde un sistema de archivos interno de una empresa. El Narrador Virtual presenta un incidente y pregunta al estudiante qué acción toma en cada nodo.

La lógica del MVP evalúa si la acción es:
- correcta,
- parcialmente correcta,
- incorrecta o grave.

## Nota importante

Este MVP prioriza una arquitectura funcional y un ejemplo operativo de flujo completo de audio + evaluación + respuesta. Está preparado para ampliarse con más escenario, mayor robustez de validación y un front-end más rico.
