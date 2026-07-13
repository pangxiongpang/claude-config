#!/usr/bin/env python3
"""
LK888 API Image Generation Backend

Generates images via LK888's custom API interface.
Used by image_gen.py as a backend module.

Configuration keys:
  LK888_API_KEY    (required) API key
  LK888_BASE_URL   (optional) Custom API endpoint (default: https://api.lk888.ai)
  LK888_MODEL      (optional) Model name (default: gpt-image-2)

Dependencies:
  pip install requests Pillow
"""

import sys

if __name__ == "__main__":
    print(__doc__)
    print("Use via: python3 skills/ppt-master/scripts/image_gen.py \"prompt\" --backend lk888")
    raise SystemExit(0 if any(arg in {"-h", "--help", "help"} for arg in sys.argv[1:]) else 1)

import os
import time
import threading
import requests
from image_backends.backend_common import (
    download_image,
    resolve_output_path,
)

DEFAULT_MODEL = "gpt-image-2"
DEFAULT_BASE_URL = "https://api.lk888.ai"

# Aspect ratio -> size mapping
ASPECT_RATIO_TO_SIZE = {
    "1:1":  "auto",
    "16:9": "1920x1088",
    "9:16": "1088x1920",
    "3:2":  "1536x1024",
    "2:3":  "1024x1536",
    "4:3":  "1280x960",
    "3:4":  "960x1280",
    "4:5":  "1024x1280",
    "5:4":  "1280x1024",
    "21:9": "1920x816",
}

IMAGE_SIZE_TO_QUALITY = {
    "512px": "low",
    "1K":    "medium",
    "2K":    "high",
    "4K":    "high",
}


def _read_api_key() -> str:
    """Read API key from environment."""
    key = os.environ.get("LK888_API_KEY", "")
    if not key:
        raise RuntimeError("LK888_API_KEY not set. Please configure it in .env file.")
    return key


def _read_base_url() -> str:
    """Read base URL from environment."""
    return os.environ.get("LK888_BASE_URL", DEFAULT_BASE_URL)


def _read_model() -> str:
    """Read model name from environment."""
    return os.environ.get("LK888_MODEL", DEFAULT_MODEL)


def generate(prompt: str,
             aspect_ratio: str = "1:1",
             image_size: str = "1K",
             output_dir: str = None,
             filename: str = None,
             model: str = None) -> str:
    """
    Image generation via LK888 API.

    Args:
        prompt: Text description of the image to generate
        aspect_ratio: Image aspect ratio (e.g., "1:1", "16:9")
        image_size: Image size category ("512px", "1K", "2K", "4K")
        output_dir: Directory to save the generated image
        filename: Output filename (without extension)
        model: Model name override (optional)

    Returns:
        Path of the saved image file

    Raises:
        RuntimeError: When generation fails
    """
    api_key = _read_api_key()
    base_url = _read_base_url()
    if model is None:
        model = _read_model()

    # Map parameters
    size = ASPECT_RATIO_TO_SIZE.get(aspect_ratio, "auto")
    quality = IMAGE_SIZE_TO_QUALITY.get(image_size, "auto")

    # Build request
    request = {
        "model": model,
        "prompt": prompt,
        "params": {
            "size": size,
            "quality": quality,
            "n": 1,
            "response_format": "url",
        }
    }

    mode_label = f"Proxy: {base_url}"
    print(f"[LK888 - {mode_label}]")
    print(f"  Model:        {model}")
    print(f"  Prompt:       {prompt[:120]}{'...' if len(prompt) > 120 else ''}")
    print(f"  Size:         {size} (from aspect_ratio={aspect_ratio})")
    print(f"  Quality:      {quality} (from image_size={image_size})")
    print()

    # Submit task
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    start_time = time.time()
    print(f"  [..] Submitting task...", end="", flush=True)

    try:
        response = requests.post(
            f"{base_url}/v1/media/generate",
            headers=headers,
            json=request,
            timeout=60,
        )
        if not response.ok:
            error_msg = response.text[:200] if response.text else "Unknown error"
            raise RuntimeError(f"LK888 API error ({response.status_code}): {error_msg}")

        result = response.json()
        # Handle nested response format
        if "data" in result:
            result = result["data"]

        task_id = result.get("task_id")
        if not task_id:
            raise RuntimeError(f"No task_id in response: {result}")

        print(f" OK (task_id={task_id})")

    except requests.exceptions.RequestException as e:
        print(f" FAILED")
        raise RuntimeError(f"Failed to submit task: {e}") from e

    # Poll for result
    print(f"  [..] Waiting for result...", end="", flush=True)
    poll_interval = 5
    max_wait = 300  # 5 minutes

    while True:
        elapsed = time.time() - start_time
        if elapsed > max_wait:
            print(f" TIMEOUT ({max_wait}s)")
            raise RuntimeError(f"Task {task_id} timed out after {max_wait}s")

        time.sleep(poll_interval)

        try:
            poll_response = requests.get(
                f"{base_url}/v1/media/status",
                params={"task_id": task_id},
                headers=headers,
                timeout=30,
            )
            if not poll_response.ok:
                print(f" (poll error {poll_response.status_code})", end="", flush=True)
                continue

            poll_result = poll_response.json()
            # Handle nested response format
            if "data" in poll_result:
                poll_result = poll_result["data"]

            is_final = poll_result.get("is_final", False)
            state = poll_result.get("state", "")
            progress = poll_result.get("progress", "")
            result_url = poll_result.get("result_url", "")

            if is_final:
                if state == "success" and result_url:
                    print(f" DONE ({elapsed:.1f}s)")
                    print(f"  [..] Downloading image...", end="", flush=True)

                    # Download and save image
                    if not filename:
                        # Generate a filename from prompt
                        safe_prompt = "".join(c for c in prompt[:30] if c.isalnum() or c in " _-").strip()
                        safe_prompt = safe_prompt.replace(" ", "_") or "image"
                        filename = f"{safe_prompt}_{int(time.time())}"

                    output_path = resolve_output_path(prompt, output_dir, filename, ".png")
                    download_image(result_url, output_path)

                    print(f" OK")
                    print(f"\n  Output: {output_path}\n")
                    return output_path
                else:
                    error = poll_result.get("error", "Unknown error")
                    print(f" FAILED (state={state})")
                    raise RuntimeError(f"Task {task_id} failed: {error}")
            else:
                print(f" {progress}", end="", flush=True)

        except requests.exceptions.RequestException as e:
            print(f" (poll error: {e})", end="", flush=True)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate image via LK888 API")
    parser.add_argument("prompt", help="Image description")
    parser.add_argument("--aspect_ratio", default="1:1", help="Aspect ratio (e.g., 1:1, 16:9)")
    parser.add_argument("--image_size", default="1K", help="Image size (512px, 1K, 2K, 4K)")
    parser.add_argument("-o", "--output_dir", default=".", help="Output directory")
    parser.add_argument("-f", "--filename", default=None, help="Output filename")

    args = parser.parse_args()
    try:
        result = generate(
            args.prompt,
            args.aspect_ratio,
            args.image_size,
            args.output_dir,
            args.filename,
        )
        print(f"Generated: {result}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
