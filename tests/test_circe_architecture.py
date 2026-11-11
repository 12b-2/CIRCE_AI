from __future__ import annotations

import asyncio
import os
import tempfile
import wave

import numpy as np

from circe_app.audio.stt import SpeechToText
from circe_app.audio.tts import TextToSpeech
from circe_app.evaluator import DecisionValidator
from circe_app.knowledge.scenario import LEVELS_CATALOG, list_levels
from circe_app.orchestrator import CIRCEOrchestrator


def test_five_levels_and_five_nodes_each() -> None:
    levels = list_levels()
    assert len(levels) == 5, "Deben existir al menos 5 niveles en el catálogo"
    for idx, lvl in enumerate(levels, start=1):
        assert lvl.level_number == idx
        assert len(lvl.nodes) == 5, f"El {lvl.id} debe tener 5 etapas de decisión"
        for n_idx in range(1, 6):
            node_id = f"node_{n_idx}"
            assert node_id in lvl.nodes
            node = lvl.nodes[node_id]
            assert node.prompt.strip() != ""
            assert len(node.correct_actions) >= 1


def test_semantic_validator_accents_and_conjugations() -> None:
    validator = DecisionValidator()
    node = LEVELS_CATALOG["level_1"].nodes["node_1"]

    res_ok = validator.evaluate(
        "Primero aíslo inmediatamente el servidor de la red y bloqueo el acceso activo.",
        node.prompt,
        node.correct_actions,
        node.partial_actions,
        node.wrong_actions,
        node.keywords_correct,
        node.keywords_partial,
        node.keywords_wrong,
    )
    assert res_ok["verdict"] == "correct"
    assert res_ok["score"] >= 0.8

    res_wrong = validator.evaluate(
        "Voy a formatear el servidor inmediatamente y borrar todo sin investigar.",
        node.prompt,
        node.correct_actions,
        node.partial_actions,
        node.wrong_actions,
        node.keywords_correct,
        node.keywords_partial,
        node.keywords_wrong,
    )
    assert res_wrong["verdict"] == "wrong"


def test_orchestrator_five_step_progression_all_five_levels() -> None:
    for lvl in list_levels():
        orchestrator = CIRCEOrchestrator(level_id=lvl.id)
        orchestrator.tts.enabled = False

        nodes = orchestrator.get_ordered_nodes()
        assert len(nodes) == 5

        for idx, node in enumerate(nodes, start=1):
            sample_correct = node.correct_actions[0]
            result = asyncio.run(
                orchestrator.process_student_turn(
                    sample_correct,
                    auto_advance=True,
                    speak_response=False,
                    input_mode="voice",
                )
            )
            assert result["evaluation"]["verdict"] == "correct"
            if idx < 5:
                assert not result["scenario_completed"]
                assert orchestrator.current_node == f"node_{idx + 1}"
            else:
                assert result["scenario_completed"]
                assert result["score"] >= 85.0
                assert result["xp"] == 100


def test_wav_recording_header_16bit() -> None:
    tmp_wav = os.path.join(tempfile.gettempdir(), "test_circe_pcm16.wav")
    samples = np.sin(np.linspace(0, 2 * np.pi * 440, 16000)).astype(np.float32)
    SpeechToText.save_wav(tmp_wav, samples, sample_rate=16000)

    with wave.open(tmp_wav, "rb") as wf:
        assert wf.getnchannels() == 1
        assert wf.getsampwidth() == 2  # 16-bit PCM
        assert wf.getframerate() == 16000
        assert wf.getnframes() == 16000

    os.remove(tmp_wav)


def test_tts_non_blocking_and_stop() -> None:
    tts = TextToSpeech(engine_name="auto")
    tts.speak("Prueba breve de síntesis de voz para Circe.", blocking=False)
    tts.stop()
    assert not tts.is_speaking
