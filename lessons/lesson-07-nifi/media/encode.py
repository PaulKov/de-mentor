"""Generate Russian narration, H.264 lessons and subtitles from rendered scenes."""

import argparse
import asyncio
import json
from pathlib import Path
import re
import subprocess

import edge_tts
import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
VOICE = "ru-RU-DmitryNeural"


def ffmpeg(*arguments):
    completed = subprocess.run(
        [FFMPEG, "-hide_banner", "-loglevel", "error", "-y", *map(str, arguments)],
        capture_output=True, text=True,
    )
    if completed.returncode:
        raise RuntimeError(completed.stderr.strip())


def duration(file):
    output = subprocess.run([FFMPEG, "-hide_banner", "-i", str(file)], capture_output=True, text=True)
    match = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", output.stderr)
    if not match:
        raise ValueError(f"Cannot read media duration: {file}")
    hours, minutes, seconds = map(float, match.groups())
    return hours * 3600 + minutes * 60 + seconds


async def speak(text, audio, timing, semaphore):
    if audio.exists() and timing.exists():
        return
    async with semaphore:
        for retry in range(4):
            words = []
            try:
                talk = edge_tts.Communicate(text, VOICE, rate="-9%", boundary="WordBoundary")
                with audio.open("wb") as writer:
                    async for message in talk.stream():
                        if message["type"] == "audio":
                            writer.write(message["data"])
                        elif message["type"] == "WordBoundary":
                            words.append([message["offset"], message["duration"], message["text"]])
                if audio.stat().st_size < 3000 or not words:
                    raise ValueError("Narration is empty")
                timing.write_text(json.dumps(words, ensure_ascii=False), encoding="utf-8")
                return
            except Exception:
                if retry == 3:
                    raise
                await asyncio.sleep(2 ** retry)


def captions(words, offset, end):
    batch = []
    for start, length, word in words:
        if batch and (len(batch) >= 11 or len(" ".join(item[2] for item in batch)) + len(word) > 72):
            yield caption(batch, offset, end)
            batch = []
        batch.append((start, length, word))
    if batch:
        yield caption(batch, offset, end)


def caption(batch, offset, end):
    start = offset + batch[0][0] / 10_000_000
    last, length, _ = batch[-1]
    stop = min(end, offset + (last + length) / 10_000_000 + 0.15)
    text = " ".join(word for _, _, word in batch)
    return start, max(stop, start + 0.10), text


def srt_time(value):
    ms = round(value * 1000)
    hours, ms = divmod(ms, 3_600_000)
    minutes, ms = divmod(ms, 60_000)
    seconds, ms = divmod(ms, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{ms:03}"


def encode_episode(episode, build, destination):
    slug = episode["slug"]
    clips = []
    subtitles = []
    running = 0.0
    for index, scene in enumerate(episode["scenes"], 1):
        base = f"{slug}-{index}"
        audio = build / f"{base}.mp3"
        clip = build / f"{base}.mp4"
        if not clip.exists() or clip.stat().st_mtime < max(
            (build / scene["image"]).stat().st_mtime, audio.stat().st_mtime
        ):
            ffmpeg("-loop", "1", "-framerate", "5", "-i", build / scene["image"], "-i", audio,
                   "-shortest", "-c:v", "libx264", "-preset", "veryfast", "-tune", "stillimage",
                   "-crf", "25", "-pix_fmt", "yuv420p", "-threads", "2", "-c:a", "aac",
                   "-ac", "1", "-b:a", "64k", clip)
        playtime = duration(clip)
        words = json.loads((build / f"{base}.timing.json").read_text(encoding="utf-8"))
        subtitles.extend(captions(words, running, running + playtime))
        clips.append(f"file '{clip.name}'")
        running += playtime
    concat = build / f"{slug}.concat"
    concat.write_text("\n".join(clips) + "\n", encoding="utf-8")
    srt = destination / f"{slug}.srt"
    entries = []
    for index, (start, stop, text) in enumerate(subtitles, 1):
        if index < len(subtitles):
            stop = min(stop, subtitles[index][0] - 0.01)
        entries.append(f"{index}\n{srt_time(start)} --> {srt_time(max(stop, start + 0.03))}\n{text}\n")
    srt.write_text("\n".join(entries), encoding="utf-8")
    result = destination / f"{slug}.mp4"
    ffmpeg("-f", "concat", "-safe", "0", "-i", concat, "-i", srt,
           "-map", "0:v", "-map", "0:a", "-map", "1:s", "-c:v", "copy", "-c:a", "copy",
           "-c:s", "mov_text", "-metadata:s:s:0", "language=rus", "-movflags", "+faststart", result)
    print(f"{slug}: {duration(result):.2f}s, {result.stat().st_size:,} bytes", flush=True)


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("build", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    args.destination.mkdir(parents=True, exist_ok=True)
    episodes = json.loads((args.build / "episodes.json").read_text(encoding="utf-8"))
    semaphore = asyncio.Semaphore(5)

    async def make_episode(episode):
        await asyncio.gather(*[
            speak(scene["narration"], args.build / f"{episode['slug']}-{index}.mp3",
                  args.build / f"{episode['slug']}-{index}.timing.json", semaphore)
            for index, scene in enumerate(episode["scenes"], 1)
        ])
        await asyncio.to_thread(encode_episode, episode, args.build, args.destination)

    await asyncio.gather(*(make_episode(episode) for episode in episodes))


if __name__ == "__main__":
    asyncio.run(main())
