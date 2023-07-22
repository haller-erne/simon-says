#
# See https://www.waitingforfriday.com/?p=586
# and https://www.youtube.com/playlist?list=PLDnfaWhAwvwdrydaRuG8J8v8LQmrzIyXd
#
# The original Simon game has three game modes:
#
# Single Player – The game generates a sequence of lights and sounds which the player must follow, 
#   the sequence grows by one colour every turn and ends when the player makes a mistake or repeats 
#   the maximum number of colours in a sequence (which is dependent on the skill level setting)
# Multi Player (game 2) – The game begins with Simon displaying a colour, the first player must 
#   repeat the colour and then select another colour, subsequent players must enter the current 
#   sequence and then add one more, the next player then selects the sequence of colours entered so 
#   far and then one more and so on until a player makes a mistake (or a sequence of 31 colours is achieved).
# Multi Player (game 3) – This game is identical to game one, however each player owns one or more 
#   colours and is responsible for pressing it during the sequence. If a colour is incorrectly selected 
#   that colour is removed from the game and the game continues (with a new colour sequence) until only 
#   one colour is left (the winner)
#
# The game also features 4 skill levels:
#   1 - Repeat a sequence of 8 colours
#   2 - Repeat a sequence of 14 colours
#   3 - Repeat a sequence of 20 colours
#   4 - Repeat a sequence of 31 colours
# To play games 2 and 3 the skill level selector must be in position 4 or the game will end prematurely 
# (this is due to the ‘skill level’ performing the same function in all game modes; in the multi‐player 
# games the maximum sequence number Simon can handle gives the longest game play).
#
# The game hardware consists of 4 coloured lens which, when pressed, operate switches on the circuit board. 
# The colours from top‐left going clockwise are red, blue, yellow and green on the Pocket Simon and green, 
# red, blue and yellow on the full‐size version.
# 
# There are 3 push buttons on the game:
# - Last: Replays the sequence from the last game (only operates when the game is not in progress)
# - Start: Starts a new game (can be pressed at any time)
# - Longest: Replays the longest sequence successfully completed since the game was turned on (only 
#   operates when the game is not in progress)
#
# There are 2 sliding switches on the game (on the full‐sized game there is an additional on‐off switch 
# which in the pocket version is replaced by a two‐pole game switch):
# - Game: Off, 1, 2 and 3
# - Skill: 1, 2, 3 and 4
# 
import pygame
import os, sys
import simon_devices, simon_sounds
from time import sleep

hid = simon_devices.Devices()
sounds = simon_sounds.Sounds()
octave = 3

def play_note(note, duration):
    hid.led(note)
    sounds.play(note, octave)
    sleep(duration)
    sounds.stop()
    hid.led(0)

def victory_normal(key):
    # plays victory tone of six beeps (of the same frequency as the last colour in the sequence). 
    # The first beep is 0.02 seconds followed by 5 beeps of 0.07 seconds with a 0.02 second gap 
    # between tones the light of the last colour of the sequence is flashed on with each beep. 
    # The victory tone is played 0.8 seconds after the last colour of the sequence has been pressed and released.
    #sounds.play(key, octave)
    hid.led_all(hid.keycolors[key-1])
    hid.led_sw([0,1,1,0])
    sounds.music_play('tadaa.mp3', 1.0)
    sleep(0.2)
    hid.led_all([0,0,0])
    hid.led_sw([0,0,0,0])
    #sounds.stop()
    for i in range(2,13):
        sleep(0.1)
        hid.led_all(hid.keycolors[key-1])
        hid.led_sw([0,1,1,0])
        #sounds.play(key, octave)
        sleep(0.1)
        #sounds.stop()
        hid.led_all([0,0,0])
        hid.led_sw([0,0,0,0])
        hid.poll()
    while not sounds.music_is_done:
        hid.poll()
        sleep(0.1)

def play_sequence(tones, duration, gap):
    print("Sequence: ", end='')
    for i, v in enumerate(tones):
        if i != 0:
            sleep(gap)
        print(f" {v}", end='')
        play_note(v, duration)
        hid.poll()
    print("")

def victory_razz(key):
    razz = [ 2, 3, 4, 1, 1, 1, 2, 3 ]
    for i, v in enumerate(razz):
        hid.led(v)
        sounds.play(v, octave)
        sleep(0.1)
        sounds.stop()
        hid.led(0)
        hid.poll()
    
    sounds.play(0, octave)
    for i, v in enumerate(razz):
        hid.led(v)
        sleep(0.1)
        hid.led(0)
        hid.poll()
    sounds.stop()


class GameState:
    def __init__(self):
        self.mode = 0
        self.key = -1
        self.rnd = 0
        self.level = 10         # Soll-Anzahl
        self.sequence = []      # current list of tones
        self.cur_idx = 0        # current user index into tones
        self.tStart = 0         #


# cyclically called to implement the game logic
def game_loop(state, key):
    state.rnd = (state.rnd + 1) % 4         # random.

    if state.mode <= 0:         # startup
        #victory_normal(3)
        #victory_razz(3)
        sounds.music_play('bensound-summer_ogg_music.ogg')
        state.mode = 1
        hid.led_sw([0,0,0,0])

    elif state.mode == 1:       # idle, wait for start
        sounds.music_loop()     # loop the music
        keys = hid.get_keys()
        sw = hid.get_sw()
        if keys == [0,0,0,0]:
            hid.animate()           # show the idle animation
        if sw[1] != 0 or sw[2] != 0:
            state.mode = 2
            if sw[1] != 0:
                state.level = 6
                hid.led_sw([0,1,0,0])
            else:
                state.level = 8
                hid.led_sw([0,0,1,0])
            print(f'Starting level {state.level}')
            
        if key >= 0 and (key != state.key):
            # button pressed or released
            if key != 0:
                hid.led(key)
                sounds.play(key, octave)      # play the note associated to the key
            else:
                hid.led(0)
                sounds.stop()
            print(key)
            #if state.key > 0 and key > 0:
            #    # zwei tasten gedrückt --> start
            #    # setze Level: 1-4: 8 / 14 / 20 / 31 farben!
            #    state.mode = 2
            #    print(f'Starting level {state.level}')

            state.key = key

    elif state.mode == 2:         # startup
        hid.led(0)
        sounds.stop()
        sounds.music_stop()
        sleep(0.2)
        sounds.music_play('game-start-6104.mp3', 1.0)
        state.mode = 3

    elif state.mode == 3:         # startup
        sw = hid.get_sw()
        keys = hid.get_keys()
        if keys == [0,0,0,0] and sw[1] == 0 and sw[2] == 0 and sounds.music_is_done():            # wait for keys released and music done
            sounds.music_stop()
            sleep(0.2)
            state.mode = 100

    elif state.mode == 100:       # game starting
        print('---------- starting ----------')
        state.sequence = []
        state.mode = 102

    elif state.mode == 102:       # add tone and play the sequence
        state.sequence.append(state.rnd+1)        # zufälliger ton hinzu
        print(f"new: {state.rnd+1}")
        duration = 0.42                         # Länge der Töne - je länger umso schneller
        if len(state.sequence) >= 6 and len(state.sequence) < 14:
            duration = 0.32
        elif len(state.sequence) >= 14:
            duration = 0.22
        play_sequence(state.sequence, duration, 0.05)           # die gesamte sequenz nochmal abspielen
        state.mode = 103                        # wait for keys
        state.cur_idx = 0                       # es müssen nochmal alle Tasten gedrückt werden
        state.tStart = pygame.time.get_ticks()

    elif state.mode == 103:       # add tone and play the sequence
        if key >= 0 and (key != state.key):
            # button pressed or released
            if key != 0:
                print(f"key pressed: {key} ", end='')
                if key == state.sequence[state.cur_idx]:
                    ## richtige taste gedrückt
                    print("ok")
                    hid.led(key)
                    sounds.play(key, octave)      # play the note associated to the key
                else:
                    print("wrong!")
                    state.mode = 999               # verloren!
            else:
                hid.led(0)
                sounds.stop()
                state.tStart = pygame.time.get_ticks()
                state.cur_idx = state.cur_idx + 1
                if state.cur_idx >= state.level:
                    ## GEWONNEN!
                    state.mode = 1000
                else:
                    if state.cur_idx >= len(state.sequence):
                        # nächste note
                        state.mode = 102
                        sleep(0.8)
                    #else:
                        # warte auf nächste Note
            state.key = key
        else:
            # no key pressed, check timeout
            if pygame.time.get_ticks() - state.tStart > 3000:
                state.mode = 999               # verloren!
        
    elif state.mode == 999:       # verloren
        sounds.music_play('game-over.mp3', 1.0)
        state.mode = 1999

    elif state.mode == 1000:      # gewonnen
        victory_normal(state.sequence[len(state.sequence)-1])
        state.mode = 0           
  
    elif state.mode == 1999:       # 
        if sounds.music_is_done():
            play_note(0, 1.5)
            state.mode = 0           


# define a main function
def main():
    hid.init()

    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.display.init()
    #screen = pygame.display.set_mode((1,1))
    pygame.init()

    FPS = 60
    FramePerSec = pygame.time.Clock()

    game_state = GameState()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # read HID devices/buttons
        k = hid.poll()
        game_loop(game_state, k)

        #pygame.display.update()
        FramePerSec.tick(FPS)       # sleep a bit

# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
    # call the main function
    main()