from music21 import stream, note

def makexml(notes, output_path="output_music.xml"):
    s = stream.Stream()
    duration_map = {1: 'whole', 2: 'half', 4: 'quarter', 8: 'eighth', 16: '16th'}

    for n in notes:
        pitch_part, dur_part = n.rsplit('-', 1)
        m21_note = note.Note(pitch_part.upper())
        m21_note.duration.type = duration_map[int(dur_part)]
        s.append(m21_note)

    s.write('musicxml', fp=output_path)
    return output_path