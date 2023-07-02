from wave import open as open_wave

import numpy as np
import pyaudio


def normalize(arr, dtype=np.float16):
    _max = np.finfo(dtype).max
    _min = arr.min()

    return (_max-arr)/(_max-_min)


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
