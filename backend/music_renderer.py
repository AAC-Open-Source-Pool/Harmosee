import os
import subprocess
import time
from music21 import converter
from piano_visualizer import Piano, Video

# --- CONFIGURATION ---
FLUIDSYNTH_EXE_PATH = r"ENTER PATH"
SOUNDFONT_PATH = r"ENTER PATH"
FFMPEG_EXE_PATH = r"ENTER PATH"

# --- STEP 1: Convert MusicXML to MIDI ---
def convert_xml_to_midi(xml_path, midi_path):
    print("🎼 Step 1: Converting MusicXML → MIDI...")
    try:
        score = converter.parse(xml_path)
        score.write('midi', fp=midi_path)
        print(f"✅ Saved MIDI: {midi_path}")
        return True
    except Exception as e:
        print(f"❌ MIDI conversion failed: {e}")
        return False

# --- STEP 2: Generate Piano Visualizer Video ---
def generate_visualizer_video(midi_path, video_path):
    print("\n🎥 Step 2: Generating Piano Visualizer Video...")
    try:
        piano = Piano([midi_path])
        video = Video((1920, 1080), 30)
        video.add_piano(piano)
        print(f"   Rendering video to {video_path}...")
        video.export(video_path, num_cores=1, music=False)
        print(f"✅ Saved Video: {video_path}")
        return True
    except Exception as e:
        print(f"❌ Video generation failed: {e}")
        return False

def generate_midi_audio(midi_path, wav_path, soundfont_path=SOUNDFONT_PATH, timeout_sec=15):
    print("\n🎧 Step 3: Generating Audio (WAV) using FluidSynth...")

    if not os.path.exists(soundfont_path):
        print(f"❌ SoundFont file not found: {soundfont_path}")
        return False

    if not os.path.exists(midi_path):
        print(f"❌ MIDI file not found: {midi_path}")
        return False

    cmd = [
        FLUIDSYNTH_EXE_PATH, "-a", "file", "-ni",
        soundfont_path, midi_path, "-F", wav_path, "-r", "44100"
    ]

    print("   Running FluidSynth command:")
    print("   " + " ".join(cmd))

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=timeout_sec)
        print(f"✅ FluidSynth completed within {timeout_sec} seconds.")
    except subprocess.TimeoutExpired:
        print(f"⚠ FluidSynth timed out after {timeout_sec} seconds.")
    except subprocess.CalledProcessError as e:
        print(f"❌ FluidSynth error:\n{e.stderr.decode().strip()}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

    # Fallback: check if WAV file exists anyway
    if os.path.exists(wav_path):
        print(f"✅ WAV file found: {wav_path} — proceeding to next step.")
        return True
    else:
        print(f"❌ WAV file not created — cannot proceed.")
        return False
    

# --- STEP 4: Merge Audio and Video (MoviePy) ---
def merge_with_moviepy(video_path, audio_path, output_path='output-moviepy.mp4', fps=24):
    import moviepy as mpe
    print('🎬 Merging with MoviePy...')
    try:
        video = mpe.VideoFileClip(video_path)
        video = video.set_audio(mpe.AudioFileClip(audio_path))
        video.write_videofile(output_path, fps=fps)
        print(f"✅ Final video saved: {output_path}")
        return True
    except Exception as e:
        print(f"❌ MoviePy merge failed: {e}")
        return False



# --- STEP 5: Merge Audio and Video (FFmpeg CLI) ---
def merge_with_ffmpeg(video_path, audio_path, output_path='output-ffmpeg.mp4', fps=24, ffmpeg_path=FFMPEG_EXE_PATH):
    print('🎬 Merging with FFmpeg...')
    
    if not os.path.exists(ffmpeg_path):
        print(f"❌ FFmpeg executable not found: {ffmpeg_path}")
        return False

    """cmd = [
        ffmpeg_path,
        '-i', video_path,
        '-i', audio_path,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-strict', 'experimental',
        '-y', output_path
    ]"""
    cmd = [
    ffmpeg_path,
    '-i', video_path,
    '-i', audio_path,
    '-c:v', 'libx264',
    '-c:a', 'aac',
    '-strict', 'experimental',
    '-y', output_path
    ]

    print("   Running FFmpeg command:")
    print("   " + " ".join(cmd))

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print(f"✅ Final video saved: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg error:\n{e.stderr.decode().strip()}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
