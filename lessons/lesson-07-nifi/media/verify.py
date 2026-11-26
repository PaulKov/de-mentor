"""Check the published MP4s against their Markdown scripts, without a TTS cache."""
import re
import subprocess
from pathlib import Path
from statistics import median

import av
import imageio_ffmpeg
import numpy as np

MEDIA = Path(__file__).resolve().parent
VIDEO = MEDIA.parent / "artifacts" / "video"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
HZ = 24000


def decode(path, *args):
    return subprocess.run([FFMPEG, "-v", "error", "-threads", "2", "-i", str(path), *args],
                          capture_output=True, check=True).stdout


def cues(text):
    def seconds(value):
        hours, minutes, seconds = value.replace(",", ".").split(":")
        return int(hours) * 3600 + int(minutes) * 60 + float(seconds)

    result = []
    for block in text.strip().split("\n\n"):
        _, times, *lines = block.splitlines()
        start, end = times.split(" --> ")
        if not 1 <= len(lines) <= 2 or any(len(line) > 46 for line in lines):
            raise ValueError(f"Caption line length: {lines}")
        result.append((seconds(start), seconds(end), " ".join(lines)))
    return result


def verify(script):
    scenes = [re.findall(r"^> (.+)$", section, re.M)
              for section in re.split(r"^## ", script.read_text(encoding="utf-8"), flags=re.M)[1:]]
    path = VIDEO / f"{script.stem}.mp4"
    sidecar = cues(path.with_suffix(".srt").read_text(encoding="utf-8"))
    embedded = cues(decode(path, "-map", "0:s:0", "-f", "srt", "-").decode("utf-8").replace("\r\n", "\n"))
    if sidecar != embedded or [text for _, _, text in sidecar] != sum(scenes, []):
        raise ValueError(f"{script.stem}: script, SRT and MP4 captions disagree")

    with av.open(str(path)) as container:
        video, audio = container.streams.video[0], container.streams.audio[0]
        sub = container.streams.subtitles[0]
        if audio.metadata.get("language") != "rus" or sub.metadata.get("language") != "rus":
            raise ValueError("Missing Russian audio or subtitle label")
        fps = float(video.average_rate)
        video_end = float((video.start_time + video.duration) * video.time_base)
        audio_end = float((audio.start_time + audio.duration) * audio.time_base)
        if abs(video_end - audio_end) > 0.08:
            raise ValueError(f"{path.name}: different track lengths {video_end}, {audio_end}")

    # Detect slide changes from decoded pixels independently of encoder timings.
    raw = decode(path, "-an", "-sn", "-vf", "scale=128:72", "-pix_fmt", "gray", "-f", "rawvideo", "-")
    frames = np.frombuffer(raw, np.uint8).reshape(-1, 128 * 72)
    diff = np.abs(np.diff(frames.astype(np.int16), axis=0)).mean(axis=1)
    changes = (np.flatnonzero(diff > 0.8) + 1) / fps
    if len(changes) != len(scenes) - 1:
        raise ValueError(f"{path.name}: expected {len(scenes) - 1} slide changes, found {changes}")

    raw = decode(path, "-vn", "-sn", "-af", "aresample=24000:async=1:first_pts=0",
                 "-ac", "1", "-f", "s16le", "-")
    pcm = np.frombuffer(raw, "<i2")
    block = HZ // 100
    samples = pcm[:len(pcm) // block * block].astype(float).reshape(-1, block)
    active = np.sqrt((samples ** 2).mean(axis=1)) > 32768 * 10 ** (-48 / 20)
    times = (np.flatnonzero(active) + 0.5) / 100
    if not times.size:
        raise ValueError(f"{path.name}: silent track")

    def bounds(moment):
        idx = np.searchsorted(times, moment)
        return times[idx - 1] if idx else 0.0, times[idx] if idx < len(times) else audio_end

    slide_gaps, cue_errors = [], []
    for change, boundary in zip(changes, np.cumsum([len(scene) for scene in scenes])):
        if not sidecar[boundary-1][1] < change < sidecar[boundary][0]:
            raise ValueError(f"{path.name}: captions cross slide at {change:.2f}")
        before, after = bounds(change)
        slide_gaps.append(after - before)
    for index, (start, end, _) in enumerate(sidecar):
        prior = sidecar[index-1][1] if index else 0.0
        following = sidecar[index+1][0] if index + 1 < len(sidecar) else video_end
        if not prior <= start < end <= video_end:
            raise ValueError(f"{path.name}: invalid times at caption {index + 1}")
        _, first = bounds((prior + start) / 2)
        last, _ = bounds((end + following) / 2)
        cue_errors.append(abs(first - start))
        if first >= end or abs(last - end) > 0.16:
            raise ValueError(f"{path.name}: speech does not fit caption {index + 1}")
    tail = video_end - times[-1]
    if not (min(slide_gaps) >= 0.65 and max(slide_gaps) <= 1.35 and 0.35 <= tail <= 0.85):
        raise ValueError(f"{path.name}: transition or ending gap {slide_gaps}, tail={tail}")
    if max(cue_errors) > 0.16:
        raise ValueError(f"{path.name}: speech and cue differ by {max(cue_errors):.3f}s")
    return video_end, len(sidecar), slide_gaps, tail, cue_errors


if __name__ == "__main__":
    results = []
    for source in sorted(MEDIA.glob("[0-9][0-9]-*.md")):
        row = verify(source)
        results.append(row)
        print(f"{source.stem}: {row[0]:.1f}s, {row[1]} captions, ending {row[3]:.2f}s")
    joins = [gap for row in results for gap in row[2]]
    errors = [gap for row in results for gap in row[4]]
    print(f"Total {sum(r[0] for r in results):.1f}s, {len(errors)} captions; "
          f"{len(joins)} transitions {min(joins):.2f}–{max(joins):.2f}s; "
          f"caption onset error median {median(errors):.3f}s, max {max(errors):.3f}s")
