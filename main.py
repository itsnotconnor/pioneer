
##
import vlc
import time
import os
import json

"""
01       UID (NFCID1): 04  1c  a6  38  ff  61  81
02       UID (NFCID1): 04  c0  d9  38  ff  61  80 
03       UID (NFCID1): 04  eb  2d  39  ff  61  80
04       UID (NFCID1): 04  05  95  39  ff  61  80
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
15       UID (NFCID1): 04  93  61  39  ff  61  81
16       UID (NFCID1): 04  f9  b9  38  ff  61  80
"""


if __name__ == "__main__":
    print("NFC Tag Test")
    # Create a player and play the track
    player = vlc.MediaPlayer("/home/cnelson/Music/King Gizzard & The Lizard Wizard - Loyalty.mp3")
    player.play()

    time.sleep(280)
