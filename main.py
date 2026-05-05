
##
import vlc
import time
import os
import json
import queue
import threading
import random

#local imports
import song
import song.Song as Song

"""
True Shuffle -- 01       UID (NFCID1): 04  1c  a6  38  ff  61  81
King Gizzard -- 02       UID (NFCID1): 04  c0  d9  38  ff  61  80
Linkin Park  -- 03       UID (NFCID1): 04  eb  2d  39  ff  61  80
Megadeth     -- 04       UID (NFCID1): 04  05  95  39  ff  61  80
05       UID (NFCID1): 04  3e  c7  38  ff  61  80
06       UID (NFCID1): 04  ed  55  39  ff  61  80
07       UID (NFCID1): 04  32  f0  38  ff  61  80
08       UID (NFCID1): 04  36  3f  39  ff  61  80
09       UID (NFCID1): 04  f4  03  39  ff  61  80
10       UID (NFCID1): 04  c5  f5  38  ff  61  80
11       UID (NFCID1): 04  1e  6e  38  ff  61  80
12       UID (NFCID1): 04  41  26  39  ff  61  81
13       UID (NFCID1): 04  2c  b9  38  ff  61  80
14       UID (NFCID1): 04  f7  63  39  ff  61  81
SKIP         -- 15       UID (NFCID1): 04  93  61  39  ff  61  81
Stop/Clear   -- 16       UID (NFCID1): 04  f9  b9  38  ff  61  80
"""


## State Machine

# a) There is no music playing, wait for a NFC read

# b) There is music currently playing, occasionally look for a new NFC read in case new request
# -- if its the same tag, do nothing
# -- else switch to the new album

MUSIC_DIR = "/home/cnelson/Music"
MAX_SONGS_QUEUE = 10
NFC_READ_DUTY_CYCLE = 10 #seconds


def add_songs_to_queue(nfc_uid, all_tracks, song_queue):
    """ Iterate thru tracks and add based on UID """

    match nfc_uid:
        case 1:
            """ True Shuffle -- 01       UID (NFCID1): 04  1c  a6  38  ff  61  81 """
            end_index = len(all_tracks)
            for i in range(MAX_SONGS_QUEUE):
                num = random.randint(0, end_index)
                song_queue.put(all_tracks[num])
        case 2:
            """ King Gizzard -- 02       UID (NFCID1): 04  c0  d9  38  ff  61  80 """
            for track in all_tracks:
                if "Polygondwanaland" in track.album:
                    song_queue.put(track)

        case 16:
            """ Stop/Clear   -- 16       UID (NFCID1): 04  f9  b9  38  ff  61  80 """
            #clear the queue
            while not song_queue.empty():
                try:
                    song_queue.get_nowait()
                except queue.Empty:
                    break
        case _:
            return "Error"


def poll_nfc_reader():
    """ Check if there is a new nfc tag placed """

    return 0

def play_next_song(song_queue):
    next_song = song_queue.get()
    #Get next in queue, play it
    song_path = Path(next_song.path).name
    song_duration = next_song.duration
    try:
        # Create a player and play the track
        player = vlc.MediaPlayer(song_path)
        player.play()
        #player.pause()
        #player.stop()
        #
        ## Sleep for the song duration
        time.sleep(song_duration)
    except Exception as ex:
        print(ex)

## Thread Tasks ##

def thread_nfc_worker(song_queue):
    """
    This thread will add to song_queue
    - Reads NFC reader to update song queue
    - Sleeps every 10 seconds
    """
    LAST_NFC_UID = 16 #Initialize to STOP/CLEAR UUID
    while True:
        # Read NFC on constant duty cycle
        nfc_read_uid = poll_nfc_reader()
        if nfc_read_uid != LAST_NFC_UID:
            #clear the queue
            while not song_queue.empty():
                try:
                    song_queue.get_nowait()
                except queue.Empty:
                    break
            #add new music to queue
            add_songs_to_queue(song_queue)
            #Update latest read
            LAST_NFC_UID = nfc_read_uid

        else:
            ## It is the same as before, do not update the song_queue
            print(f"Detected the same NFC read (or no read): {nfc_read_uid}")


        time.sleep(NFC_READ_DUTY_CYCLE)

def thread_play_music(song_queue):


if __name__ == "__main__":

    ## For now, just get every song by file glob. Eventually this will suck
    all_tracks = song.scan_library(MUSIC_DIR)

    song_queue = queue.Queue()
