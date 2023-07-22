from collections import deque
from numpy import abs, frombuffer
from numpy.fft import fft as FFT
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader, glDeleteShader
from wave import open as open_wave

import numpy as np
import pyaudio


class AudioStream:
    '''
    Context manager to handle the overhead for loading audio files.
    '''
    
    def __init__(self, filename):
        self.filename = filename
        self.audio_file = None
        self.py_audio = None
        self.stream = None
    
    def __enter__(self):
        self.audio_file = open_wave(self.filename, 'rb')
        self.py_audio = pyaudio.PyAudio()

        self.stream = self.py_audio.open(
            format=self.py_audio.get_format_from_width(self.audio_file.getsampwidth()),
            channels=self.audio_file.getnchannels(),
            rate=self.audio_file.getframerate(),
            output=True
        )

        return self.audio_file, self.stream

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.stream.close()
        self.py_audio.terminate()


class Shaders:
    def __init__(self, vertex_path, fragment_path):
        self.vertex_path = vertex_path
        self.fragment_path = fragment_path

        with open(self.vertex_path, 'r') as f:
            self.vertex_str = f.read()

        with open(self.fragment_path, 'r') as f:
            self.fragment_str = f.read()

    def compile(self):
        return compileProgram(
            compileShader(self.vertex_str, GL_VERTEX_SHADER),
            compileShader(self.fragment_str, GL_FRAGMENT_SHADER)
        )
    
    # TODO: Delete Shaders


class DJ:
    def __init__(self):
        self.no_bins = 15000
        self.bass_inc = 188
        self.mid_inc = 143
        self.umid_inc = 1313
        self.treb_inc = 12000

        self.interval_0 = self.bass_inc
        self.interval_1 = self.bass_inc+self.mid_inc
        self.interval_2 = self.bass_inc+self.mid_inc+self.umid_inc
        self.interval_3 = self.bass_inc+self.mid_inc+self.umid_inc+self.treb_inc

        self.bass_queue = deque()
        self.bass_queue_size = 10
        self.bass_dampener = 0.9

        self.mid_queue = deque()
        self.mid_queue_size = 10
        self.mid_dampener = 0.9

        self.umid_queue = deque()
        self.umid_queue_size = 10
        self.umid_dampener = 0.9

        self.treb_queue = deque()
        self.treb_queue_size = 10
        self.treb_dampener = 0.9

    def audio_bands(self, data):
        signal = frombuffer(data, dtype=np.int16)
        fft = abs(FFT(signal, n=self.no_bins))
        log_fft = np.emath.logn(2, fft)

        return (
            log_fft[:self.bass_inc],
            log_fft[self.interval_0:self.interval_1],
            log_fft[self.interval_1:self.interval_2],
            log_fft[self.interval_2:self.interval_3]
        )

    def execute(self, data, execution_cycle):
        bass, mid, umid, treb = self.audio_bands(data)

        bass_mean = np.mean(bass)
        self.bass_queue.append(bass_mean)
        mid_mean = np.mean(mid)
        self.mid_queue.append(mid_mean)
        umid_mean = np.mean(umid)
        self.umid_queue.append(umid_mean)
        treb_mean = np.mean(treb)
        self.treb_queue.append(treb_mean)

        if execution_cycle >= self.bass_queue_size:
            self.bass_queue.popleft()
            self.mid_queue.popleft()
            self.umid_queue.popleft()
            self.treb_queue.popleft()

        bass_dampened = self.bass_dampener*(np.mean(self.bass_queue))
        mid_dampened = self.treb_dampener*(np.mean(self.mid_queue))
        umid_dampened = self.treb_dampener*(np.mean(self.umid_queue))
        treb_dampened = self.treb_dampener*(np.mean(self.treb_queue))

        return bass_dampened, mid_dampened, umid_dampened, treb_dampened