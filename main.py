
##
import vlc
import time
import os
import json
import queue
import threading
import random
import enum
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
NFC_READ_DUTY_CYCLE = 3 #seconds

class PlaybackControls(Enum):
    """
    ## Playback queue
    # 0: Request Pause/Stop current song
    # 1: Request Play current song
    # 2: Skip to next song
    """
    PLAY = 1
    STOP = 2
    SKIP = 3

def poll_nfc_reader():
    """ Check if there is a new nfc tag placed """
    return 1

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


def clear_queued_songs(song_queue):
    while not song_queue.empty():
        try:
            song_queue.get_nowait()
        except queue.Empty:
            break

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

def thread_nfc_worker(song_queue, playback_queue):
    """
    This thread will add to song_queue
    - Reads NFC reader to update song queue
    - Sleeps every 'N' seconds
    """
    NOREAD = 0
    previous_nfc_read = NOREAD #Initialize to NOREAD==0
    while True:
        # Read NFC on constant duty cycle
        nfc_read_uid = poll_nfc_reader()

        match nfc_read_uid:
            case NOREAD | previous_nfc_read:
                #No readback from NFC card / same as before > Do nothing
                previous_nfc_read = nfc_read_uid
            case x if 1 <= x < 15:
                # New songs
                add_songs_to_queue(nfc_uid, all_tracks, song_queue)
                playback_queue.put(PlaybackControls.PLAY)
            case 15:
                #Skip it
                playback_queue.put(PlaybackControls.SKIP)
            case 16:
                #Clear songs in queue & stop music
                # playback_semaphore =
                clear_queued_songs(song_queue)
                playback_queue.put(PlaybackControls.STOP)

            case _:
                print(f"!! Unhandled NF UID : {nfc_read_uid}")

        time.sleep(NFC_READ_DUTY_CYCLE)


def thread_play_music(song_queue,playback_queue):
    previous_playback_cmd = PlaybackControls.STOP #We start up in the STOP state

    while True:
        ## check playback status
        #
        # check playback queue
        #
        # check song queue
        #
        # repeat


if __name__ == "__main__":

    ## For now, just get every song by file glob. Eventually this will suck
    all_tracks = song.scan_library(MUSIC_DIR)

    song_queue = queue.Queue()
