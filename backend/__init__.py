from .image_processing import extract_notes_from_image
from .xml_generator import makexml
from dotenv import load_dotenv



from .music_renderer import (
    convert_xml_to_midi,
    generate_visualizer_video,
    generate_midi_audio,
    merge_with_ffmpeg  # or merge_with_moviepy
)

load_dotenv(dotenv_path=r"final\.gitignore\.env")

def process_sheet_music(image_path):
    notes = extract_notes_from_image(image_path)
    xml_path = makexml(notes)
    midi_path = "temp_output.mid"
    video_path = "temp_visualization.mp4"
    audio_path = "fluidsynth.wav"
    final_path = "final_output.mp4"

    convert_xml_to_midi(xml_path, midi_path)
    generate_visualizer_video(midi_path, video_path)
    generate_midi_audio(midi_path, audio_path)
    merge_with_ffmpeg(video_path, audio_path, final_path)

    return {
        "notes": notes,
        "video": final_path
    }