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


class ParametricCircle:
    def __init__(self, res_w, res_h):
        self.res_w = float(res_w)
        self.res_h = float(res_h)
        
        self.vertices = np.array([
            [-0.1, 0.1, 0],
            [0.1, 0.1, 0],
            [0.1, -0.1, 0],
            [-0.1, -0.1, 0],
            [-0.1, 0.1, 0],
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
            join('shaders', 'parametric_vertices.glsl'),
            join('shaders', 'parametric_fragments.glsl')
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
        self.modelGL = glGetUniformLocation(self.shaders,'model')
        model_transform = pyrr.matrix44.create_from_translation(vec=np.array([0, 0, -1]), dtype=np.float32)        

        projection_matrix = pyrr.matrix44.create_perspective_projection(
            fovy=45,
            aspect=1,
            near=0.1,
            far=10,
            dtype=np.float32
        )

        glUniformMatrix4fv(self.projectionGL, 1, GL_FALSE, projection_matrix)

        glUniform2f(self.resGL, self.res_w, self.res_h)
        glUniformMatrix4fv(self.modelGL, 1, GL_FALSE, model_transform)
    
    def event_handler(self):
        for event in pg.event.get():
            if (event.type == pg.QUIT):
                return False
            
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                return False
        
        return True
    
    def execute(self):
        run = True
        start_time = time()
        while run:
            run = self.event_handler()

            current_time = time() - start_time

            glClear(GL_COLOR_BUFFER_BIT)

            glUniform1f(self.timeGL, current_time)

            glDrawArrays(GL_TRIANGLE_STRIP, 0, 5)

            pg.display.flip()

            self.clock.tick(60)

        glDeleteVertexArrays(1, [self.vao])
        glDeleteBuffers(1, [self.vbo])
            

if __name__ == '__main__':
    width=1920
    height=1080

    pc = ParametricCircle(width, height)
    pc.execute()
