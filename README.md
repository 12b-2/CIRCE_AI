# CIRCE · Conversational Intelligence for Response and Cybersecurity Education

**CIRCE** es una plataforma modular de entrenamiento en respuesta a incidentes de ciberseguridad mediante simulación interactiva con **Voz (STT + TTS)**, **Texto** e **Inteligencia Artificial (LLM Local + Evaluador Semántico)**.

## Características Principales

- **5 Niveles de Campaña + 5 Etapas de Decisión por Nivel (25 Nodos Interactivos)**:
  1. **Nivel 1 · Filtración de Datos Corporativos** (Detección, Contención, Evidencia Forense, Control de Credenciales, Notificación Regulatoria y Erradicación).
  2. **Nivel 2 · Ataque de Ransomware en Red** (Aislamiento SMB, Backups Inmutables, Paciente Cero, Gestión de Crisis y Restauración Limpia).
  3. **Nivel 3 · Phishing Ejecutivo y Fraude BEC** (Bloqueo de Sesión, Freno de Transferencia Fuera de Banda, Reglas Ocultas OAuth, Alerta a Clientes y Blindaje DMARC/MFA).
  4. **Nivel 4 · Intrusión Cloud y Fuga de API Keys** (Revocación IAM, Contención de Instancias, Auditoría CloudTrail, Limpieza de Secretos en Git y Mínimo Privilegio).
  5. **Nivel 5 · Amenaza Interna y Sabotaje Crítico** (Contención DLP/PAM, Cadena de Custodia Forense, Búsqueda de Bombas Lógicas, Coordinación Legal/RRHH y Control Dual).
- **Interacción Multimodal Completa (Voz y Texto)**:
  - **Instrucciones en Texto y Audio**: Cada nivel presenta las instrucciones en pantalla y las narra automáticamente en voz alta en español (`espeak-ng` / `pyttsx3` no bloqueante).
  - **Respuesta del Estudiante por Audio o Texto**: Grabación interactiva de micrófono en tiempo real (`sounddevice` PCM 16-bit 16kHz + transcripción `faster-whisper`) o entrada directa por teclado.
  - **Evaluación del Modelo en Texto y Audio**: Retroalimentación inmediata hablada y escrita generada por **Ollama (`llama3.1` / `qwen2.5`)** con fallback transparente al **Evaluador Semántico Local** en español.

## Arquitectura Modular

```text
AIAGENT/
├── main.py                         # CLI y punto de entrada (--gui, --mic, --level, --demo-text)
├── run_gui.py                      # Lanzador directo de la Interfaz Gráfica (Tkinter)
├── demo_run.py                     # Demo rápida del pipeline de voz
├── requirements.txt                # Dependencias del proyecto
├── tests/
│   └── test_circe_architecture.py  # Suite de pruebas automatizadas (pytest)
└── circe_app/
    ├── config.py                   # Configuración tipada (CIRCEConfig, LevelScenario, ScenarioNode)
    ├── orchestrator.py             # Orquestador central (Voz STT/TTS + Motor de Juego + IA)
    ├── game_engine.py              # Motor de progresión de los 5 niveles y sus 5 nodos
    ├── session.py                  # Estado de sesión (XP, Vidas, Métricas del incidente, Tiempo)
    ├── evaluator.py                # Evaluador semántico y morfológico local en español
    ├── services.py                 # Diagnóstico en tiempo real de capacidades locales
    ├── voice_pipeline.py           # Pipeline unificado de turno de voz
    ├── ai/
    │   └── llm_client.py           # Cliente asíncrono para Ollama LLM local (JSON estructurado)
    ├── audio/
    │   ├── stt.py                  # Grabación interactiva Start/Stop + faster-whisper STT
    │   └── tts.py                  # Síntesis de voz asíncrona cancelable en español (espeak-ng/pyttsx3)
    ├── knowledge/
    │   ├── scenario.py             # Catálogo de los 5 niveles y sus árboles de 5 decisiones
    │   ├── rules.py                # Reglas de respuesta a incidentes (IR-01 a IR-04)
    │   └── incident_data.py        # Contexto base de incidentes
    └── ui/
        ├── gui_app.py              # Interfaz gráfica interactiva completa (Inicio, Simulación, Resultados)
        └── local_console.py        # Interfaz interactiva por consola (texto y comando /voz)
```

## Cómo Ejecutar

1. **Activar el entorno virtual**:
   ```bash
   source .venv/bin/activate
   ```
2. **Ejecutar la Interfaz Gráfica Interactiva (Recomendado)**:
   ```bash
   python run_gui.py
   # o también:
   python main.py --gui
   ```
3. **Ejecutar desde Consola (CLI)**:
   ```bash
   python main.py --level level_1 --demo-text "Aíslo el servidor afectado de la red y bloqueo el acceso"
   python main.py --level level_2 --mic
   ```
4. **Ejecutar pruebas automatizadas**:
   ```bash
   python -m pytest -v
   ```
