import json
from moviepy import (VideoFileClip, concatenate_videoclips, AudioFileClip,
                      CompositeVideoClip, TextClip, vfx)

W, H = 1080, 1920

clip_files = [f"video/clips/scene{i}.mp4" for i in range(1, 8)]
clips = []
for f in clip_files:
    c = VideoFileClip(f).without_audio()
    c = c.resized(height=H)
    if c.w > W:
        c = c.cropped(x_center=c.w/2, width=W)
    elif c.w < W:
        c = c.resized(width=W)
        if c.h > H:
            c = c.cropped(y_center=c.h/2, height=H)
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
durations = [total_dur * c / total_chars for c in char_counts]
starts = []
t = 0.0
for d in durations:
    starts.append(t)
    t += d

text_clips = []
for line, start, dur in zip(lines, starts, durations):
    txt = TextClip(
        text=line,
        font_size=72,
        color="#FFD400",
        font="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        method="caption",
        size=(W - 160, None),
        stroke_color="black",
        stroke_width=6,
        text_align="center",
    ).with_position(("center", 0.78), relative=True).with_start(start).with_duration(dur)
    text_clips.append(txt)

final = CompositeVideoClip([stitched] + text_clips, size=(W, H)).with_audio(audio).with_duration(total_dur)
final.write_videofile("video/jayden_final.mp4", fps=30, codec="libx264", audio_codec="aac", threads=4, bitrate="6000k")
print("DONE", total_dur)
