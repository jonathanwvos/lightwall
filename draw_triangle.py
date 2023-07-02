import pygame as pg
from os.path import join
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

import numpy as np


class Shaders:
    def __init__(self, vertex_path, fragment_path):
        self.vertex_path = vertex_path
        self.fragment_path = fragment_path

        with open(self.vertex_path, 'r') as f:
            self.vertex_str = f.read()

        with open(self.fragment_path, 'r')as f:
            self.fragment_str = f.read()

    def compile(self):
        return compileProgram(
            compileShader(self.vertex_str, GL_VERTEX_SHADER),
            compileShader(self.fragment_str, GL_FRAGMENT_SHADER)
        )


class DrawTriangle:
    def __init__(self, vertices):
        self.res_w = 1920
        self.res_h = 1080

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
        self.vertices = np.array(vertices, dtype='float32')
        shaders = Shaders(
            join('shaders', 'triangle_vertices.glsl'),
            join('shaders', 'triangle_fragments.glsl')
        )
        self.shaders = shaders.compile()

    def event_handler(self):
        for event in pg.event.get():
            if (event.type == pg.QUIT):
                return False
            
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                return False
        
        return True

    def execute(self):

        offset = 3*np.dtype(np.float32).itemsize

        vbo = glGenBuffers(1)
        vao = glGenVertexArrays(1)
        
        glBindVertexArray(vao)
        
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, offset, ctypes.c_void_p(0))
        
        glUseProgram(self.shaders)

        run = True
        while(run):
            run = self.event_handler()

            glClear(GL_COLOR_BUFFER_BIT)

            glDrawArrays(GL_TRIANGLES, 0, 3)

            pg.display.flip()

            self.clock.tick(60)

        glDeleteVertexArrays(1, [vao])
        glDeleteBuffers(1, [vbo])
        pg.quit()


if __name__ == "__main__":
    # x, y, z
    vertices = [
        -0.5, -0.5, 0.0,
        0.0, 0.5, 0.0,
        0.5,  -0.5, 0.0,
    ]

    app = DrawTriangle(vertices)
    app.execute()
