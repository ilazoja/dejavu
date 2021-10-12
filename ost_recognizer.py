import os
import json
import glob
import subprocess
from pathlib import Path

from dejavu import Dejavu
from dejavu.logic.recognizer.file_recognizer import FileRecognizer
from dejavu.logic.recognizer.microphone_recognizer import MicrophoneRecognizer

## This script labels unlabeled files obtained from an ost rip using a labeled soundtrack. Useful for renaming converted brstm files that are unlabeled

### Instructions
# 1. Obtain raw ost rip (e.g. from vgm hcs64) and convert to brstm using LoopingAudioConverter (these are referred to as unlabeled brstms)
# 2. Convert above brstms to mp3s using LoopingAudioConverter (make sure to check Convert to mono) (these are referred to as unlabeled songs)
# 3. Obtain soundtrack (e.g. from SittingOnClouds) and convert to single channel mp3s using LoopingAudioConverter (by checking Convert to mono) (these are referred to as labeled songs)
# Note: It is advised that the unlabeled songs and labeld songs should have the same sample rate and maybe the same filetype
# 4. Set the UNLABELED_BRSTM_DIR, UNLABELED_SONG_DIR and LABELED_SONG_DIR folders. They must be somewhere within the dejavu folder and the paths must be relative to the dejavu folder.
# 5. Run docker then run this script

# Note: Needs to have same sample rate as input
UNLABELED_BRSTM_DIR = "./vgm/brstms/" # newly converted unlabeled brstms from ost rip preferably with desired sample rate
UNLABELED_SONG_DIR = "./vgm/brstms/" # has to have matching filenames as above, files should be single channel
LABELED_SONG_DIR = "./vgm/labeled/" # files should be single channel (preferably sample sample rate as above) not sure if same file type matters

INPUT_CONFIDENCE_THRESHOLD = 0.1 # minimum input confidence to consider a match
# Additional settings can be modified in config/settings.py

# load config from a JSON file (or anything outputting a python dictionary)
config = {
    "database": {
        "host": "db",
        "user": "postgres",
        "password": "password",
        "database": "dejavu"
    },
    "database_type": "postgres"
}

if __name__ == '__main__':
    djv = Dejavu(config)

    ## Fingerprint all the labeled songs in the directory we give it
    print("Fingerprinting labeled songs...")

    djv.fingerprint_directory(LABELED_SONG_DIR, [".wav", ".mp3", ".flac", "m4a"])

    ## Create labeled songs dict
    labeled_songs = []
    for ext in ["*.wav", "*.mp3", "*.flac", "*.m4a"]:
        labeled_songs.extend(glob.glob(os.path.join(glob.escape(LABELED_SONG_DIR), ext)))
    labeled_songs_dict = {}
    for labeled_song in labeled_songs:
        labeled_songs_dict[Path(labeled_song).stem] = []

    ## Gather all unlabeled songs in folder
    unlabeled_songs = []
    for ext in ["/*.wav", "/*.mp3", "/*.flac", "/*.m4a"]:
        unlabeled_songs.extend(glob.glob(glob.escape(UNLABELED_SONG_DIR) + ext))

    ## Recognize unlabeled songs (match unlabeled songs with labeled songs)
    print("Recognizing unlabeled songs...")

    for unlabeled_song in unlabeled_songs:
        print(f"Recognizing {unlabeled_song}")
        results = djv.recognize(FileRecognizer, unlabeled_song)

        print(f"Result: {results['results'][0]['song_name']} - {results['results'][0]['input_confidence']}")
        if results['results'][0]['input_confidence'] >= INPUT_CONFIDENCE_THRESHOLD:
            labeled_songs_dict[results['results'][0]['song_name'].decode("utf-8")] += [(unlabeled_song, results['results'][0]['input_confidence'])]
        else:
            print("Not matched")

    ## Rename brstms to labeled matches
    print("Renaming brstms...")

    for labeled_song, matched_unlabeled_songs in labeled_songs_dict.items():
        matched_unlabeled_songs.sort(key=lambda x:x[1], reverse=True)
        if not len(matched_unlabeled_songs):
            print(f"{labeled_song} has no matches")
        for i, (unlabeled_song, input_confidence) in enumerate(matched_unlabeled_songs):
            if i == 0:
                os.rename(os.path.splitext(unlabeled_song)[0] + ".brstm", os.path.join(UNLABELED_BRSTM_DIR, labeled_song + ".brstm"))
            else:
                os.rename(os.path.splitext(unlabeled_song)[0] + ".brstm", os.path.join(UNLABELED_BRSTM_DIR, labeled_song + f" ({i}).brstm"))

    ## Clear fingerprint database
    print("Clearing fingerprint database...")

    fingerprinted_song_ids = [song['song_id'] for song in djv.get_fingerprinted_songs()]
    djv.delete_songs_by_id(fingerprinted_song_ids)

    print("Finished")
