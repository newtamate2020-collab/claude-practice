"""
Kling AI text-to-video generator.

Usage:
    export KLING_ACCESS_KEY=xxxx
    export KLING_SECRET_KEY=xxxx
    python kling_text_to_video.py "a cat surfing on a wave" --out video.mp4

Requires: pip install requests pyjwt
"""

import argparse
import os
import time

import jwt
import requests

API_BASE = "https://api-singapore.klingai.com"


def make_jwt(access_key: str, secret_key: str) -> str:
    now = int(time.time())
    payload = {
        "iss": access_key,
        "exp": now + 1800,  # token valid 30 minutes
        "nbf": now - 5,
    }
    return jwt.encode(payload, secret_key, algorithm="HS256", headers={"alg": "HS256", "typ": "JWT"})


def create_task(token: str, prompt: str, duration: str, aspect_ratio: str, mode: str) -> str:
    resp = requests.post(
        f"{API_BASE}/v1/videos/text2video",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={
            "model_name": "kling-v1",
            "prompt": prompt,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "mode": mode,
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"Kling API error: {data}")
    return data["data"]["task_id"]


def poll_task(token: str, task_id: str, interval: int = 5, timeout: int = 600) -> str:
    deadline = time.time() + timeout
    while time.time() < deadline:
        resp = requests.get(
            f"{API_BASE}/v1/videos/text2video/{task_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()["data"]
        status = data["task_status"]
        print(f"status: {status}")

        if status == "succeed":
            return data["task_result"]["videos"][0]["url"]
        if status == "failed":
            raise RuntimeError(f"Task failed: {data.get('task_status_msg')}")

        time.sleep(interval)

    raise TimeoutError("Timed out waiting for video generation")


def download(url: str, out_path: str) -> None:
    resp = requests.get(url, stream=True, timeout=60)
    resp.raise_for_status()
    with open(out_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=1 << 16):
            f.write(chunk)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a video from text via Kling AI")
    parser.add_argument("prompt", help="Text prompt describing the video")
    parser.add_argument("--duration", default="5", choices=["5", "10"], help="Video length in seconds")
    parser.add_argument("--aspect-ratio", default="16:9", choices=["16:9", "9:16", "1:1"])
    parser.add_argument("--mode", default="std", choices=["std", "pro"], help="Generation quality mode")
    parser.add_argument("--out", default="kling_output.mp4", help="Output file path")
    args = parser.parse_args()

    access_key = os.environ["KLING_ACCESS_KEY"]
    secret_key = os.environ["KLING_SECRET_KEY"]

    token = make_jwt(access_key, secret_key)
    task_id = create_task(token, args.prompt, args.duration, args.aspect_ratio, args.mode)
    print(f"task created: {task_id}")

    video_url = poll_task(token, task_id)
    print(f"video ready: {video_url}")

    download(video_url, args.out)
    print(f"saved to {args.out}")


if __name__ == "__main__":
    main()
