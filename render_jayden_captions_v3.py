import json, re
from moviepy import (VideoFileClip, concatenate_videoclips, AudioFileClip,
                      CompositeVideoClip, TextClip)

W, H = 1080, 1920
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

clip_files = [f"video/clips/scene{i}.mp4" for i in range(1, 8)]
clips = []
for f in clip_files:
    c = VideoFileClip(f).without_audio().resized(height=H)
    if c.w > W:
        c = c.cropped(x_center=c.w / 2, width=W)
    elif c.w < W:
        c = c.resized(width=W)
        if c.h > H:
            c = c.cropped(y_center=c.h / 2, height=H)
    clips.append(c)

stitched = concatenate_videoclips(clips, method="compose")
audio = AudioFileClip("audio/jayden_voiceover_seed7.mp3")
total_dur = audio.duration
if stitched.duration > total_dur:
    stitched = stitched.subclipped(0, total_dur)

with open("captions/jayden_alignment_seed7.json") as f:
    align = json.load(f)

chars = align["characters"]
starts = align["character_start_times_seconds"]
ends = align["character_end_times_seconds"]

# Group characters into words on whitespace boundaries using REAL timestamps
words = []
cur_chars = []
cur_start = None
for ch, s, e in zip(chars, starts, ends):
    if ch == " ":
        if cur_chars:
            words.append(("".join(cur_chars), cur_start, prev_end))
            cur_chars = []
            cur_start = None
    else:
        if cur_start is None:
            cur_start = s
        cur_chars.append(ch)
        prev_end = e
if cur_chars:
    words.append(("".join(cur_chars), cur_start, prev_end))

HIGHLIGHT_COLOR = "#39FF14"
BASE_COLOR = "#FFE400"

def pop_scale(t, pop_dur=0.12, hold_overshoot=0.06):
    if t < pop_dur:
        frac = t / pop_dur
        return 0.3 + 0.95 * frac
    elif t < pop_dur + hold_overshoot:
        frac = (t - pop_dur) / hold_overshoot
        return 1.25 - 0.2 * frac
    else:
        return 1.05

word_clips = []
for w, s, e in words:
    clean = re.sub(r"[^\w$'-]", "", w).lower()
    is_hi = clean.isdigit() or w.startswith("$") or clean in {
        "five", "hundred", "forty", "six", "two", "zero", "guru", "gurus",
        "jayden", "doesnt", "shortcut", "gone", "lamborghini", "months", "himself"
    }
    color = HIGHLIGHT_COLOR if is_hi else BASE_COLOR
    fsize = 104 if is_hi else 92
    dur = max(e - s, 0.05)
    txt = TextClip(
        text=w.upper(),
        font_size=fsize,
        color=color,
        font=FONT,
        method="label",
        stroke_color="black",
        stroke_width=9,
    )
    txt = txt.resized(lambda t: pop_scale(t))
    txt = txt.with_position(("center", 0.80), relative=True)
    txt = txt.with_start(s).with_duration(dur)
    word_clips.append(txt)

final = CompositeVideoClip([stitched] + word_clips, size=(W, H)).with_audio(audio).with_duration(total_dur)
final.write_videofile("video/jayden_captions_v3.mp4", fps=30, codec="libx264", audio_codec="aac", threads=4, bitrate="6000k")
print("DONE", total_dur, "words:", len(words))
