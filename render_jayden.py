import json
from moviepy import AudioFileClip, ColorClip, CompositeVideoClip, TextClip, CompositeAudioClip
import numpy as np

W, H = 1080, 1920

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

audio = AudioFileClip("audio/jayden_voiceover.mp3")
total_dur = audio.duration

# Estimate per-line duration proportional to character length
char_counts = [len(l) for l in lines]
total_chars = sum(char_counts)
durations = [total_dur * c / total_chars for c in char_counts]

# Build start times
starts = []
t = 0.0
for d in durations:
    starts.append(t)
    t += d

bg = ColorClip(size=(W, H), color=(10, 14, 26), duration=total_dur)

text_clips = []
for line, start, dur in zip(lines, starts, durations):
    txt = TextClip(
        text=line,
        font_size=78,
        color="#FFD400",
        font="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        method="caption",
        size=(W - 160, None),
        stroke_color="black",
        stroke_width=6,
        text_align="center",
    ).with_position(("center", "center")).with_start(start).with_duration(dur)
    text_clips.append(txt)

video = CompositeVideoClip([bg] + text_clips, size=(W, H)).with_audio(audio)
video.write_videofile("video/jayden_draft.mp4", fps=30, codec="libx264", audio_codec="aac", threads=4)

with open("captions/jayden_timing.json", "w") as f:
    json.dump([{"line": l, "start": round(s,2), "dur": round(d,2)} for l,s,d in zip(lines, starts, durations)], f, indent=2)

print("DONE", total_dur)
