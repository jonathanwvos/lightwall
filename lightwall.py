from collections import deque
from numpy import abs, frombuffer
from numpy.fft import fft as FFT
from os.path import join
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader, glDeleteShader
from OpenGL.GLUT import *
from utils import AudioStream, Shaders
from time import time

import numpy as np
import pygame as pg
import pyrr


class Canvas:
    def __init__(self, res_w, res_h):
        self.res_w = float(res_w)
        self.res_h = float(res_h)
        
        self.vertices = np.array([
            [-1.7, 1, 0],
            [1.7, 1, 0],
            [1.7, -1, 0],
            [-1.7, -1, 0],
            [-1.7, 1, 0],
        ], dtype='float32')

        # Pygame configurations
        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK,
                                    pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.set_mode((self.res_w, self.res_h), pg.OPENGL|pg.DOUBLEBUF)
        self.clock = pg.time.Clock()

        # OpenGL configurations
        glClearColor(0.0, 0.0, 0.0, 1)

        # Shader configurations
        shaders = Shaders(
            join('shaders', 'lightwall_vertices.glsl'),
            join('shaders', 'lightwall_fragments.glsl')
        )
        self.shaders = shaders.compile()
        self.init_GL()

    def init_GL(self):
        offset = 3*np.dtype(np.float32).itemsize

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, offset, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        glUseProgram(self.shaders)
        self.timeGL = glGetUniformLocation(self.shaders, 'time')
        self.resGL = glGetUniformLocation(self.shaders, 'resolution')
        self.projectionGL = glGetUniformLocation(self.shaders, 'projection')
        self.bassDampGL = glGetUniformLocation(self.shaders, 'bassDampened')
        self.midDampGL = glGetUniformLocation(self.shaders, 'midDampened')
        self.umidDampGL = glGetUniformLocation(self.shaders, 'umidDampened')
        self.trebDampGL = glGetUniformLocation(self.shaders, 'trebDampened')
        self.modelGL = glGetUniformLocation(self.shaders,'model')
        model_transform = pyrr.matrix44.create_from_translation(vec=np.array([0, 0, -3]), dtype=np.float32)        

        projection_matrix = pyrr.matrix44.create_perspective_projection(
            fovy=45,
            aspect=self.res_w/self.res_h,
            near=0.1,
            far=10,
            dtype=np.float32
        )

        glUniformMatrix4fv(self.projectionGL, 1, GL_FALSE, projection_matrix)

        glUniform2f(self.resGL, self.res_w, self.res_h)
        glUniformMatrix4fv(self.modelGL, 1, GL_FALSE, model_transform)

    def render(self, current_time, bass, mid, umid, treb):
        glClear(GL_COLOR_BUFFER_BIT)

        glUniform1f(self.timeGL, current_time)
        glUniform1f(self.bassDampGL, bass)
        glUniform1f(self.midDampGL, mid)
        glUniform1f(self.umidDampGL, umid)
        glUniform1f(self.trebDampGL, treb)

        glDrawArrays(GL_TRIANGLE_STRIP, 0, 5)

        pg.display.flip()

        self.clock.tick(60)

    def destroy(self):
        glDeleteVertexArrays(1, [self.vao])
        glDeleteBuffers(1, [self.vbo])


class DJ:
    def __init__(self, no_bins):
        self.no_bins = no_bins
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


class Lightwall:
    def __init__(
            self,
            no_chunks: int,
            filename: str,
            width: int,
            height: int
        ):
        
        self.no_bins = 15000
        self.no_chunks = no_chunks
        self.filename = filename
        self.res_w = width
        self.res_h = height
        self.canvas = Canvas(self.res_w, self.res_w)
        self.dj = DJ(self.no_bins)
    
    def event_handler(self):
        for event in pg.event.get():
            if (event.type == pg.QUIT):
                return False
            
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                return False
        
        return True
    
    def execute(self):
        with AudioStream(self.filename) as (audio_file, stream):

            run = True
            execution_cycle = 1
            start_time = time()
            while len(data := audio_file.readframes(self.no_chunks)) and run:
                run = self.event_handler()

                stream.write(data) # Stream audio to speakers
                bass_dampened, mid_dampened, umid_dampened, treb_dampened = self.dj.execute(data, execution_cycle)
                current_time = time() - start_time

                self.canvas.render(
                    current_time,
                    bass_dampened,
                    mid_dampened,
                    umid_dampened,
                    treb_dampened
                )
                execution_cycle += 1

            self.canvas.destroy()


if __name__ == '__main__':
    no_chunks=1024
    filename=join('music', 'striker.wav')
    width=1920
    height=1080

    lightwall = Lightwall(no_chunks, filename, width, height)
    lightwall.execute()
