from os.path import join
from OpenGL.GL import *
from OpenGL.GLUT import *
from utils import AudioStream, DJ, Shaders
from time import time

import numpy as np
import pygame as pg
import pyrr


class Canvas:
    def __init__(self, res_w, res_h, frame_rate):
        self.res_w = float(res_w)
        self.res_h = float(res_h)
        self.frame_rate = frame_rate
        
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
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_DYNAMIC_DRAW)

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
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glUniform1f(self.timeGL, current_time)
        glUniform1f(self.bassDampGL, bass)
        glUniform1f(self.midDampGL, mid)
        glUniform1f(self.umidDampGL, umid)
        glUniform1f(self.trebDampGL, treb)

        glDrawArrays(GL_TRIANGLE_STRIP, 0, 5)

        pg.display.flip()

        self.clock.tick(self.frame_rate)

    def destroy(self):
        glDeleteVertexArrays(1, [self.vao])
        glDeleteBuffers(1, [self.vbo])


class Lightwall:
    def __init__(
            self,
            no_chunks: int,
            filename: str,
            width: int,
            height: int
        ):
        
        self.no_chunks = no_chunks
        self.filename = filename
        self.res_w = width
        self.res_h = height
        self.frame_rate = 240
        self.canvas = Canvas(self.res_w, self.res_w, self.frame_rate)
        self.dj = DJ()
    
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
                bass_dampened, mid_dampened, umid_dampened, treb_dampened = self.dj.extract_bands(data, execution_cycle)
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
