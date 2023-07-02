from os.path import join
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from OpenGL.GLUT import *
from time import time

import numpy as np
import pygame as pg
import pyrr


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


class DrawRotatingTriangle:
    def __init__(self, vertices):
        self.res_w = 1920.0
        self.res_h = 1080.0

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
            join('shaders', 'rotating_triangle_vertices.glsl'),
            join('shaders', 'rotating_triangle_fragments.glsl')
        )
        self.shaders = shaders.compile()

    def event_handler(self):
        for event in pg.event.get():
            if (event.type == pg.QUIT):
                return False
            
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                return False
        
        return True

    def render(self):
        offset = 3*np.dtype(np.float32).itemsize

        vbo = glGenBuffers(1)
        vao = glGenVertexArrays(1)
        
        glBindVertexArray(vao)
        
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_DYNAMIC_DRAW)
        
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, offset, ctypes.c_void_p(0))
        
        glUseProgram(self.shaders)
        angle = 0.01
        angle_inc = 0.03
        angleGL = glGetUniformLocation(self.shaders, 'angle')
        timeGL = glGetUniformLocation(self.shaders, 'time')
        resGL = glGetUniformLocation(self.shaders, 'resolution')
        projectionGL = glGetUniformLocation(self.shaders, 'projection')
        modelGL = glGetUniformLocation(self.shaders,'model')
        model_transform = pyrr.matrix44.create_from_translation(vec=np.array([0, 0, -2]), dtype=np.float32)        

        projection_matrix = pyrr.matrix44.create_perspective_projection(
            fovy=45,
            aspect=self.res_w/self.res_h,
            near=0.1,
            far=10,
            dtype=np.float32
        )

        glUniformMatrix4fv(projectionGL, 1, GL_FALSE, projection_matrix)

        glUniform2f(resGL, self.res_w, self.res_h)
        glUniformMatrix4fv(modelGL, 1, GL_FALSE, model_transform)


        start_time = time()
        run = True
        while(run):
            run = self.event_handler()

            current_time = time() - start_time

            glClear(GL_COLOR_BUFFER_BIT)

            glUniform1f(angleGL, angle)
            glUniform1f(timeGL, current_time)

            glDrawArrays(GL_TRIANGLES, 0, 3)

            pg.display.flip()

            angle += angle_inc
            self.clock.tick(60)

        glDeleteVertexArrays(1, [vao])
        glDeleteBuffers(1, [vbo])


if __name__ == "__main__":
    # x, y, z
    vertices = np.array([
        [-0.5, -0.5, 0],
        [0, 0.5, 0],
        [0.5, -0.5, 0]
    ])

    app = DrawRotatingTriangle(vertices)
    app.render()
