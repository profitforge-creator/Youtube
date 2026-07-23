import re
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
audio = AudioFileClip("audio/jayden_voiceover.mp3")
total_dur = audio.duration
if stitched.duration > total_dur:
    stitched = stitched.subclipped(0, total_dur)

lines = [
    "This is Jayden.",
    "He had $500 saved up from his birthday and two summers of mowing lawns.",
    "Then he found a guy on his For You page in a rented Lamborghini.",
    "The guy said one course changed his life. Jayden believed him.",
    "$500, gone. The course was 40 videos of stuff he could've Googled.",
    "The guru promised six figures a month within two weeks of work.",
    "It doesn't work that way.",
    "Week two, Jayden made zero dollars. Week six, Jayden made zero dollars.",
    "Jayden's been posting the same day-one-of-my-journey video for three months.",
    "Here's what nobody in that course told him.",
    "The guru doesn't make money from the business. He makes money from the course.",
    "If someone's selling you the shortcut, ask why they're not just taking it themselves.",
    "This is Jayden. Don't be Jayden.",
]

char_counts = [len(l) for l in lines]
total_chars = sum(char_counts)
line_durations = [total_dur * c / total_chars for c in char_counts]
line_starts = []
t = 0.0
for d in line_durations:
    line_starts.append(t)
    t += d

HIGHLIGHT_WORDS = {
    "$500,", "$500.", "$500", "zero", "six", "40", "two", "guru", "guru.",
    "shortcut,", "gone.", "lamborghini.", "months.", "himself.", "jayden.",
    "jayden", "doesn't"
}
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
for line, lstart, ldur in zip(lines, line_starts, line_durations):
    words = line.split()
    wchars = [len(w) for w in words]
    wtotal = sum(wchars) if sum(wchars) > 0 else 1
    wdur = [ldur * c / wtotal for c in wchars]
    wt = lstart
    for w, d in zip(words, wdur):
        clean = re.sub(r"[^\w$'-]", "", w).lower()
        is_hi = clean in {h.strip(".,!?").lower() for h in HIGHLIGHT_WORDS} or w.strip(".,!?").isdigit() or w.startswith("$")
        color = HIGHLIGHT_COLOR if is_hi else BASE_COLOR
        fsize = 104 if is_hi else 92
        txt = TextClip(
            text=w.upper(),
            font_size=fsize,
            color=color,
            font=FONT,
            method="label",
            stroke_color="black",
            stroke_width=9,
        )
        dur = max(d, 0.001)
        txt = txt.resized(lambda t, dd=dur: pop_scale(t))
        txt = txt.with_position(("center", 0.80), relative=True)
        txt = txt.with_start(wt).with_duration(dur)
        word_clips.append(txt)
        wt += d

final = CompositeVideoClip([stitched] + word_clips, size=(W, H)).with_audio(audio).with_duration(total_dur)
final.write_videofile("video/jayden_captions_v2.mp4", fps=30, codec="libx264", audio_codec="aac", threads=4, bitrate="6000k")
print("DONE", total_dur)
