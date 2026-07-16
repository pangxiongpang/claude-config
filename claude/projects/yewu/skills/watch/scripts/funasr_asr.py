#!/usr/bin/env python3
"""Transcribe a video via local FunASR (SenseVoiceSmall).

Extracts audio with ffmpeg, feeds it to the local FunASR model, and returns
segments in the same {start, end, text} format as whisper.py so the rest of the
watch pipeline (filter_range, format_transcript) doesn't care which ASR was used.
"""
from __future__ import annotations

import json
import math
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


# Default model config
MODEL_NAME = "iic/SenseVoiceSmall"
VAD_MODEL = "fsmn-vad"
VAD_KWARGS = {"max_single_segment_time": 30000}


def _import_funasr():
    """Lazy-import funasr — raises ImportError with a clear message if missing."""
    try:
        from funasr import AutoModel
        return AutoModel
    except ImportError:
        raise SystemExit(
            "FunASR is not installed. Install it with:\n"
            "  pip install funasr\n"
            "Or check your installation at D:/AI/funasr"
        )


def extract_audio(video_path: str, out_path: Path) -> Path:
    """Extract mono 16kHz 64kbps mp3 — identical to whisper.py's approach."""
    if shutil.which("ffmpeg") is None:
        raise SystemExit("ffmpeg is not installed. Install with: winget install ffmpeg")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-y",
        "-i", str(Path(video_path).resolve()),
        "-vn",
        "-acodec", "libmp3lame",
        "-ar", "16000",
        "-ac", "1",
        "-b:a", "64k",
        str(out_path.resolve()),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(f"ffmpeg audio extraction failed: {result.stderr.strip()}")
    if not out_path.exists() or out_path.stat().st_size == 0:
        raise SystemExit("ffmpeg produced no audio — video may have no audio track")
    return out_path


def load_model(device: str | None = None):
    """Load the FunASR model. Returns an AutoModel instance.

    Device detection: prefers CUDA if available, otherwise CPU.
    """
    AutoModel = _import_funasr()

    try:
        import torch
        if device is None:
            device = "cuda:0" if torch.cuda.is_available() else "cpu"
    except ImportError:
        device = "cpu"

    print(f"[watch] loading FunASR model ({MODEL_NAME}) on {device}…", file=sys.stderr)
    t0 = time.time()
    model = AutoModel(
        model=MODEL_NAME,
        vad_model=VAD_MODEL,
        vad_kwargs=VAD_KWARGS,
        device=device,
        disable_update=True,
    )
    print(f"[watch] FunASR model loaded in {time.time() - t0:.1f}s", file=sys.stderr)
    return model


def transcribe_audio(model, audio_path: str) -> tuple[list[dict], str]:
    """Run FunASR inference on an audio file, return (segments, text).

    Segments are in the same format as whisper.py:
        [{"start": float_seconds, "end": float_seconds, "text": str}, …]

    FunASR's sentence_info returns start/end in MILLISECONDS. We convert to
    seconds for pipeline compatibility.
    """
    # FunASR's generate expects model-specific kwargs
    gen_kw = {
        "input": audio_path,
        "batch_size": 1,
    }

    result = model.generate(**gen_kw)

    if not result or not isinstance(result, list):
        return [], ""

    # Clean FunASR's special tokens from the text
    # SenseVoice outputs tags like <|zh|><|EMO_UNKNOWN|><|Speech|>
    import re
    result_data = result[0]

    raw_text = result_data.get("text", "")
    text = re.sub(r"<\|[^|]*\|>", "", raw_text).strip()

    segments: list[dict] = []
    if "sentence_info" in result_data:
        for seg in result_data["sentence_info"]:
            seg_text = seg.get("sentence") or seg.get("text", "")
            seg_text = re.sub(r"<\|[^|]*\|>", "", seg_text).strip()
            if not seg_text:
                continue
            segments.append({
                "start": round(float(seg.get("start", 0)) / 1000.0, 2),
                "end": round(float(seg.get("end", 0)) / 1000.0, 2),
                "text": seg_text,
            })

    # If no sentence_info but we have text, create a single segment
    if not segments and text:
        segments.append({"start": 0.0, "end": 0.0, "text": text})

    return segments, text


def transcribe_video(
    video_path: str,
    audio_out: Path,
    model=None,
) -> tuple[list[dict], str]:
    """Full flow: extract audio → transcribe with FunASR → return segments.

    Returns (segments, backend_name). Raises SystemExit on failure.
    """
    print("[watch] extracting audio for FunASR…", file=sys.stderr)
    audio_path = extract_audio(video_path, audio_out)

    if model is None:
        model = load_model()

    print(
        f"[watch] transcribing with FunASR ({MODEL_NAME})…",
        file=sys.stderr,
    )
    t0 = time.time()
    segments, text = transcribe_audio(model, str(audio_path))
    elapsed = time.time() - t0

    if not segments:
        raise SystemExit("FunASR returned no transcript segments")

    print(
        f"[watch] transcribed {len(segments)} segments via FunASR in {elapsed:.1f}s",
        file=sys.stderr,
    )
    return segments, f"funasr ({MODEL_NAME.split('/')[-1]})"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: funasr_asr.py <video-path> [<audio-out.mp3>]", file=sys.stderr)
        raise SystemExit(2)

    video = sys.argv[1]
    audio_out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("audio.mp3")

    segments, backend = transcribe_video(video, audio_out)
    print(json.dumps({"backend": backend, "segments": segments}, indent=2, ensure_ascii=False))
