from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader, glDeleteShader
from wave import open as open_wave

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