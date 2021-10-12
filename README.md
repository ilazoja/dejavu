dejavu
==========

Audio fingerprinting and recognition algorithm implemented in Python, see the explanation here:  
[How it works](http://willdrevo.com/fingerprinting-and-audio-recognition-with-python/)

Dejavu can memorize audio by listening to it once and fingerprinting it. Then by playing a song, Dejavu attempts to match the audio against the fingerprints held in the database, returning the song being played. 

This fork was made specifically to help identify unlabeled songs from an ost rip using a labeled soundtracks and rename their corresponding brstm files to the proper song title.

## Instructions for ost recognition
1. Obtain raw ost rip (e.g. from vgm hcs64) and convert to brstm using LoopingAudioConverter (these are referred to as unlabeled brstms)
2. Convert above brstms to mp3s using LoopingAudioConverter (make sure to check Convert to mono) (these are referred to as unlabeled songs)
3. Obtain soundtrack (e.g. from SittingOnClouds) and convert to single channel mp3s using LoopingAudioConverter (by checking Convert to mono) (these are referred to as labeled songs)
Note: It is advised that the unlabeled songs and labeld songs should have the same sample rate and maybe the same filetype
4. In ost_recognizer.py Set the UNLABELED_BRSTM_DIR, UNLABELED_SONG_DIR and LABELED_SONG_DIR folders. They must be somewhere within the dejavu folder and the paths must be relative to the dejavu folder.
5. Run docker (steps below) then run ost_recognizer.py

## Running the script with Docker

First, install [Docker](https://docs.docker.com/get-docker/).

```shell
# build and then run our containers
$ docker-compose build
$ docker-compose up -d

# get a shell inside the container
$ docker-compose run python /bin/bash
Starting dejavu_db_1 ... done
root@f9ea95ce5cea:/code# ost_recognizer.py 
Recognizing ./vgm/brstms/MEPROFS_000017CA.mp3
Result: b'1.05 Elegant Summer' - 0.48
...

# then to shut it all down...
$ docker-compose down
```

