from pydub import AudioSegment
from pydub.playback import play
from os import path

def loadTapeTracks(projectName, encoding="aiff"):
    basePath = path.join("projects", projectName, "tape")
    paths = [path.join(basePath, f"track_{i}.aif") for i in range(1,5)]
    tracks = [AudioSegment.from_file(path, encoding) for path in paths]
    return tracks

def combineTracks(tracks):
    tape = tracks[0]
    for t in tracks[1:]:
        tape = tape.overlay(t)
    return tape 

if __name__ == "__main__":
    print("loading tracks")
    tracks = loadTapeTracks("116_kariba")
    print("combining tracks")
    tape = combineTracks(tracks)
    print("starting playback")
    play(tape)