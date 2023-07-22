# see https://stackoverflow.com/questions/56592522/python-simple-audio-tone-generator
import pygame, pygame.sndarray
import numpy
import scipy.signal

class Sounds:
    def __init__(self):
        self._sample_rate = 48000
        self._sound = None
        self.notes = [      # these are the Simon notes...
            42,             # bad
            415,            # green G4 391.995Hz
            310,            # red E4 329.628Hz
            252,            # yellow C4 261.626Hz
            209,            # blue G3 195.998Hz
        ]
        pygame.mixer.pre_init(self._sample_rate, -16, 1, 1024)
        self._tones = None
        self._octave = 3

    def set_octave(self, octave):
        self._tones = []
        self._octave = octave
        for i, freq in enumerate(self.notes):
            s = self.audio_freq(freq*self._octave)     # green G4 391.995Hz
            self._tones.append(s)

    def square_wave(self, hz, peak, n_samples, duty_cycle=.5):
        samples = 500 * 440/hz
        t = numpy.linspace(0, 1, int(samples), endpoint=False)
        wave = scipy.signal.square(2 * numpy.pi * 5 * t, duty=duty_cycle)
        wave = numpy.resize(wave, (n_samples,))
        return (peak / 2 * wave.astype(numpy.int16))

    def audio_freq(self, freq = 800):
        sample_wave = self.square_wave(freq, 4096, self._sample_rate)
        #sound = pygame.sndarray.make_sound(sample_wave)
        return pygame.mixer.Sound(sample_wave)

    # use 1..4 for the tone associated to the color buttons 1..4
    def play(self, tone, octave = 3):
        if self._tones == None or self._octave != octave:
            self.set_octave(octave)

        if tone < 0 or tone > 4:
            return
        if self._sound != None:
            self._sound.stop()

        #self._sound = self.audio_freq(self.notes[tone]*octave)     # green G4 391.995Hz
        self._sound =  self._tones[tone]
        self._sound.play(-1)

    def music_play(self, file, volume = 0.1):
        pygame.mixer.music.load('/home/pi/prj/simon/src/sounds/' + file)
        pygame.mixer.music.play()
        pygame.mixer.music.set_volume(volume)

    def music_loop(self):
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play()

    def music_is_done(self):
        return not pygame.mixer.music.get_busy()

    def music_stop(self):
        pygame.mixer.music.stop()
        
    # stop playing the tone
    def stop(self):
        if self._sound != None:
            self._sound.stop()

    def test(self):
        from time import sleep
        # pygame.init()

        # TEST
        octave = 4
        length = 0.22              # 0.42 / 0.32 / 0.22

        notes = [
            415,            # green G4 391.995Hz
            310,            # red E4 329.628Hz
            252,            # yellow C4 261.626Hz
            209,            # blue G3 195.998Hz
            42              # bad
        ]

        for freq in notes:
            sound = self.audio_freq(freq*octave)     # green G4 391.995Hz
            sound.play(-1)
            sleep(length)
            sound.stop()
            sleep(0.05)

