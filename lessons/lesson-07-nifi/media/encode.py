"""Build narrated slide videos and captions on one sample-accurate timeline."""
import argparse
import asyncio
import hashlib
import json
import re
import subprocess
import tempfile
import shutil
import wave
from pathlib import Path

import edge_tts
import imageio_ffmpeg
import numpy as np


MEDIA = Path(__file__).resolve().parent
VOICE = "ru-RU-DmitryNeural"
RATE = "-4%"
HZ = 24000
FPS = 10
FRAME = HZ // FPS
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
LEXICON = json.loads((MEDIA / "pronunciation.json").read_text(encoding="utf-8"))
TERMS = re.compile(r"(?<!\w)(?:" + "|".join(map(re.escape, sorted(LEXICON, key=len, reverse=True))) + r")(?!\w)")


def spoken(text):
    return TERMS.sub(lambda match: LEXICON[match[0]], text)


def ffmpeg(*args):
    result = subprocess.run([FFMPEG, "-v", "error", "-y", *map(str, args)], capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stderr.decode(errors="replace"))
    return result.stdout


def caption_lines(text):
    if len(text) <= 43:
        return text
    words = text.split()
    candidates = []
    for cut in range(1, len(words)):
        left, right = " ".join(words[:cut]), " ".join(words[cut:])
        if max(len(left), len(right)) <= 46:
            # Prefer a clause boundary and keep prepositions with their objects.
            penalty = 13 if words[cut - 1].lower() in {"в", "с", "и", "у", "на", "к", "по", "из", "от", "для"} else 0
            score = abs(len(left) - len(right)) + penalty - 10 * left.endswith((",", ".", "?", "—"))
            candidates.append((score, left + "\n" + right))
    if not candidates:
        raise ValueError(f"Shorten the narration line: {text}")
    return min(candidates)[1]


async def synthesize(text, cache, semaphore):
    phrase = spoken(text)
    key = hashlib.sha256(f"{VOICE}/{RATE}/{phrase}".encode()).hexdigest()
    output = cache / f"{key}.mp3"
    if output.exists():
        return output
    with tempfile.NamedTemporaryFile(dir=cache, suffix=".part", delete=False) as stream:
        temp = Path(stream.name)
    try:
        for attempt in range(6):
            try:
                async with semaphore:
                    if output.exists():
                        return output
                    await edge_tts.Communicate(phrase, VOICE, rate=RATE).save(str(temp))
                if temp.stat().st_size < 700:
                    raise ValueError(f"Empty voice response: {text}")
                temp.replace(output)
                return output
            except Exception as exc:
                if attempt == 5:
                    raise RuntimeError(f"Could not synthesize: {text}") from exc
                await asyncio.sleep(min(60, 3 ** (attempt + 1)))
    finally:
        temp.unlink(missing_ok=True)


def speech_samples(path):
    raw = ffmpeg("-i", path, "-ac", 1, "-ar", HZ, "-f", "s16le", "-")
    pcm = np.frombuffer(raw, dtype="<i2")
    window = HZ // 100
    samples = pcm[:len(pcm) // window * window].astype(np.float64).reshape(-1, window)
    rms = np.sqrt((samples ** 2).mean(axis=1))
    active = np.flatnonzero(rms > 32768 * 10 ** (-54 / 20))
    if not active.size:
        raise ValueError(f"No speech in {path}")
    # Leave the edges of quiet consonants intact. Only trim the outer silence.
    start = max(0, (active[0] - 6) * window)
    end = min(len(pcm), (active[-1] + 8) * window)
    # The voice can insert a second of silence between clauses in the same cue.
    # Remove only the middle of long silent spans, leaving both speech edges intact.
    parts = []
    cursor = start
    for index in np.flatnonzero(np.diff(active) >= 92):
        parts.append(pcm[cursor:(active[index] + 28) * window])
        cursor = (active[index + 1] - 28) * window
    parts.append(pcm[cursor:end])
    speech = np.concatenate(parts)
    tail = end - (active[-1] + 1) * window
    return speech, active[0] * window - start, len(speech) - tail


def timestamp(sample):
    ms = round(sample * 1000 / HZ)
    hours, ms = divmod(ms, 3600000)
    minutes, ms = divmod(ms, 60000)
    seconds, ms = divmod(ms, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{ms:03}"


def encode(episode, files, build, destination):
    slug = episode["slug"]
    pcm_path = build / f"{slug}.wav"
    captions, clips = [], []
    cursor = 0
    with wave.open(str(pcm_path), "wb") as track:
        track.setparams((1, 2, HZ, 0, "NONE", "not compressed"))

        def silence(count):
            nonlocal cursor
            track.writeframesraw(bytes(count * 2))
            cursor += count

        for index, scene in enumerate(episode["scenes"]):
            scene_start = cursor
            silence(round(HZ * (0.24 if scene.get("code") else 0.16)))
            lines = scene["narrationLines"]
            for number, text in enumerate(lines):
                pcm, first, last = speech_samples(files[text])
                captions.append((cursor + first, cursor + last, caption_lines(text)))
                track.writeframesraw(pcm.tobytes())
                cursor += len(pcm)
                if number < len(lines) - 1:
                    pause = 0.53 if text.endswith("?") else 0.32 if len(text) < 47 else 0.41
                    silence(round(HZ * pause))
            tail = 0.52 if index == len(episode["scenes"]) - 1 else 0.66
            silence(round(HZ * tail))
            silence((-cursor) % FRAME)
            clip = build / f"{slug}-{index + 1}.silent.mp4"
            ffmpeg("-loop", 1, "-framerate", FPS, "-i", build / scene["image"],
                   "-frames:v", (cursor - scene_start) // FRAME, "-an", "-c:v", "libx264",
                   "-preset", "veryfast", "-tune", "stillimage", "-crf", 23,
                   "-threads", 2, "-pix_fmt", "yuv420p", clip)
            clips.append(f"file '{clip.name}'")
    playlist = build / f"{slug}.concat"
    playlist.write_text("\n".join(clips) + "\n", encoding="ascii")
    srt = build / f"{slug}.srt"
    srt.write_text("\n\n".join(f"{i}\n{timestamp(start)} --> {timestamp(end)}\n{label}"
                               for i, (start, end, label) in enumerate(captions, 1)) + "\n", encoding="utf-8")
    result = build / f"{slug}.final.mp4"
    ffmpeg("-f", "concat", "-safe", 0, "-i", playlist, "-i", pcm_path, "-i", srt,
           "-map", "0:v", "-map", "1:a", "-map", "2:s", "-c:v", "copy", "-c:a", "aac",
           "-b:a", "80k", "-c:s", "mov_text", "-metadata:s:s:0", "language=rus",
           "-metadata:s:a:0", "language=rus", "-movflags", "+faststart", result)
    shutil.copyfile(result, destination / f"{slug}.mp4")
    shutil.copyfile(srt, destination / f"{slug}.srt")
    print(f"{slug}: {cursor / HZ:.2f}s, {len(captions)} cues", flush=True)


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("build", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--episode", action="append", help="Build only this episode slug (repeatable)")
    args = parser.parse_args()
    episodes = json.loads((args.build / "episodes.json").read_text(encoding="utf-8"))
    if args.episode:
        unknown = set(args.episode) - {ep["slug"] for ep in episodes}
        if unknown:
            parser.error("Unknown episode: " + ", ".join(sorted(unknown)))
        episodes = [ep for ep in episodes if ep["slug"] in args.episode]
    cache = args.build / "voice-cache"
    cache.mkdir(exist_ok=True)
    args.destination.mkdir(parents=True, exist_ok=True)
    lines = list(dict.fromkeys(text for ep in episodes for scene in ep["scenes"] for text in scene["narrationLines"]))
    for text in lines:
        caption_lines(text)
    semaphore = asyncio.Semaphore(3)
    paths = await asyncio.gather(*(synthesize(text, cache, semaphore) for text in lines),
                                 return_exceptions=True)
    failures = [str(error) for error in paths if isinstance(error, BaseException)]
    if failures:
        raise RuntimeError("\n".join(failures))
    files = dict(zip(lines, paths))
    # Limit CPU, RAM and concurrent ffmpeg processes on a teaching laptop.
    for episode in episodes:
        await asyncio.to_thread(encode, episode, files, args.build, args.destination)


if __name__ == "__main__":
    asyncio.run(main())
