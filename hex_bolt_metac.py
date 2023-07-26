from bolts import hex_bolt
from numpy import float32 as FLOAT32
from numpy import pi as PI
from os.path import join
from OpenGL.GL import *
from OpenGL.GLUT import *
from polytopes import hexagon, truncated_octahedron, truncated_octahedron_edges
from utils import AudioStream, DJ, Shaders
from time import time

import numpy as np
import pygame as pg
import pyrr


class Canvas:
    def __init__(
        self,
        res_w,
        res_h,
        frame_rate,
        bolt_color_start,
        bolt_color_end
    ):
        self.res_w = float(res_w)
        self.res_h = float(res_h)
        self.frame_rate = frame_rate
        self.bolt_color_start = bolt_color_start
        self.bolt_color_end = bolt_color_end
        
        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 4)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 4)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.set_mode((self.res_w, self.res_h), pg.OPENGL|pg.DOUBLEBUF)
        self.clock = pg.time.Clock()
        
        glClearColor(0.0, 0.0, 0.0, 0.0)
        
        bolt_shaders = Shaders(
            join('shaders', 'bolt_vertices.glsl'),
            join('shaders', 'bolt_fragments.glsl')
        )
        self.bolt_shaders = bolt_shaders.compile()
        
        hex_eye_shaders = Shaders(
            join('shaders', 'metac_hex_eye_vertices.glsl'),
            join('shaders', 'metac_hex_eye_fragments.glsl')
        )
        self.hex_eye_shaders = hex_eye_shaders.compile()
        
        hex_eye_wireframe_shaders = Shaders(
            join('shaders', 'metac_hex_eye_vertices.glsl'),
            join('shaders', 'metac_hex_eye_wireframe_fragments.glsl')
        )
        self.hex_eye_wireframe_shaders = hex_eye_wireframe_shaders.compile()
    
    def set_projection_matrices(self, shaders):
        projectionGL = glGetUniformLocation(shaders, 'projection')
        modelGL = glGetUniformLocation(shaders, 'model')
        
        projection_matrix = pyrr.matrix44.create_perspective_projection(
            fovy=45,
            aspect=self.res_w/self.res_h,
            near=0.1,
            far=10,
            dtype=np.float32
        )
        model_transform = pyrr.matrix44.create_from_translation(vec=np.array([0,0,-1]), dtype=np.float32)
        
        glUniformMatrix4fv(projectionGL, 1, False, projection_matrix)
        glUniformMatrix4fv(modelGL, 1, False, model_transform)
    
    def set_bolt_GL(self):
        glUseProgram(self.bolt_shaders)
        self.set_projection_matrices(self.bolt_shaders)
        self.bolt_vao = glGenVertexArrays(2)
        self.bolt_vbo = glGenBuffers(2)

    def set_eye_GL(self):
        glUseProgram(self.hex_eye_shaders)
        self.set_projection_matrices(self.hex_eye_shaders)
        self.eye_vao = glGenVertexArrays(1)
        self.eye_vbo = glGenBuffers(1)
        self.resGL = glGetUniformLocation(self.hex_eye_shaders, 'resolution')
        glUniform2f(self.resGL, self.res_w, self.res_h)
        self.timeGL = glGetUniformLocation(self.hex_eye_shaders, 'time')
        
        self.angleXGL = glGetUniformLocation(self.hex_eye_shaders, 'angleX')
        self.angleYGL = glGetUniformLocation(self.hex_eye_shaders, 'angleY')
        self.angleZGL = glGetUniformLocation(self.hex_eye_shaders, 'angleZ')

    def set_eye_wireframes_GL(self):
        glUseProgram(self.hex_eye_wireframe_shaders)
        self.set_projection_matrices(self.hex_eye_wireframe_shaders)
        self.eye_wireframe_vao = glGenVertexArrays(1)
        self.eye_wireframe_vbo = glGenBuffers(1)
        self.resGL = glGetUniformLocation(self.hex_eye_wireframe_shaders, 'resolution')
        glUniform2f(self.resGL, self.res_w, self.res_h)
        self.timeGL = glGetUniformLocation(self.hex_eye_wireframe_shaders, 'time')
        
        self.angleXGL = glGetUniformLocation(self.hex_eye_wireframe_shaders, 'angleX')
        self.angleYGL = glGetUniformLocation(self.hex_eye_wireframe_shaders, 'angleY')
        self.angleZGL = glGetUniformLocation(self.hex_eye_wireframe_shaders, 'angleZ')

    def bolt_lines(self, pure_bolt):
        bolt = [pure_bolt[0]]
        
        for i in range(len(pure_bolt)-1):
            bolt.append(pure_bolt[i])
            bolt.append(pure_bolt[i])
        
        bolt.append(pure_bolt[-1])
        
        return np.array(bolt, FLOAT32)
    
    def add_bolt_color(self, bolt, alpha):
        color_inc = (self.bolt_color_end-self.bolt_color_start)/len(bolt-1)
        color_bolt = []
        for i, p in enumerate(bolt):
            col_line = np.append(p, self.bolt_color_start+color_inc*i)
            col_line = np.append(col_line, alpha)
            color_bolt.append(col_line)
            
        return np.array(color_bolt, FLOAT32)

    def configure_bolt_arrays_and_buffers(self, vao, vbo, vertices):
        offset = 28
        
        glBindVertexArray(vao)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glGetAttribLocation(self.bolt_shaders, 'position')
        glEnableVertexAttribArray(0)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, False, offset, ctypes.c_void_p(0))
        
        glGetAttribLocation(self.bolt_shaders, 'color')
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 4, GL_FLOAT, False, offset, ctypes.c_void_p(12))
        
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def render_bolt_points(self, points, point_width):
        self.configure_bolt_arrays_and_buffers(
            self.bolt_vao[0],
            self.bolt_vbo[0],
            points
        )
        glPointSize(point_width)
        glDrawArrays(GL_POINTS, 0, len(points))
    
    def render_bolt_lines(self, lines, line_width):
        self.configure_bolt_arrays_and_buffers(
            self.bolt_vao[1],
            self.bolt_vbo[1],
            lines
        )
        glLineWidth(line_width)
        glDrawArrays(GL_LINES, 0, len(lines))

    def render_metac(self, trunc_oct, current_time, angle):
        offset = 12
        
        glBindVertexArray(self.eye_vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.eye_vbo)
        glGetAttribLocation(self.hex_eye_shaders, 'position')
        glBufferData(GL_ARRAY_BUFFER, trunc_oct.nbytes, trunc_oct, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, False, offset, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        
        glUniform1f(self.angleXGL, angle)
        glUniform1f(self.angleYGL, angle)
        glUniform1f(self.angleZGL, angle)
        for i in range(len(trunc_oct)):
            glDrawArrays(GL_TRIANGLES, i*3, 3)
        
        glUniform1f(self.timeGL, current_time)

    def render_metac_wireframes(self, edges, angle):
        offset = 12
        
        glBindVertexArray(self.eye_wireframe_vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.eye_wireframe_vbo)
        glGetAttribLocation(self.hex_eye_wireframe_shaders, 'position')
        glBufferData(GL_ARRAY_BUFFER, edges.nbytes, edges, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, False, offset, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        
        glUniform1f(self.angleXGL, angle)
        glUniform1f(self.angleYGL, angle)
        glUniform1f(self.angleZGL, angle)
        for i in range(len(edges)):
            glDrawArrays(GL_LINES, i*2, 2)
        
    def render(self, trunc_oct, trunc_oct_edges, pure_bolt, line_width, alpha, current_time, angle):
        glEnable(GL_DEPTH_TEST)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        bolt_lines = self.bolt_lines(pure_bolt)
        color_bl = self.add_bolt_color(bolt_lines, alpha)
        color_bp = self.add_bolt_color(pure_bolt, alpha*0.7)
        
        self.set_bolt_GL()
        self.render_bolt_points(color_bp, line_width)
        self.render_bolt_lines(color_bl, line_width)
        self.set_eye_GL()
        self.render_metac(trunc_oct, current_time, angle)
        self.set_eye_wireframes_GL()
        self.render_metac_wireframes(trunc_oct_edges, angle)
        
        glFlush()
        
        pg.display.flip()
        self.clock.tick(self.frame_rate)
        
    def destroy(self):
        glDeleteVertexArrays(2, self.bolt_vao)
        glDeleteBuffers(2, self.bolt_vbo)
        glDeleteVertexArrays(1, [self.eye_vao])
        glDeleteBuffers(1, [self.eye_vbo])
        glDeleteVertexArrays(1, [self.eye_wireframe_vao])
        glDeleteBuffers(1, [self.eye_wireframe_vbo])

class HexBoltMETAC:
    def __init__(self, width, height, bolt_len, bolt_color_start, bolt_color_end):
        self.res_w = width
        self.res_h = height
        self.frame_rate = 240
        self.bolt_len = bolt_len
        self.bolt_color_start = bolt_color_start
        self.bolt_color_end = bolt_color_end
        
        self.canvas = Canvas(self.res_w,
            self.res_h,
            self.frame_rate,
            self.bolt_color_start,
            self.bolt_color_end
        )
        self.dj = DJ()
 
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
        angle_inc = 0.03
        angle = 0.01
        while run:
            current_time = time() - start_time
            run = self.event_handler()

            origin = np.array([0,0,0], FLOAT32)
            pure_bolt = hex_bolt(self.bolt_len, 0.05, origin, 0)
            oct_edge_len = 0.05
            trunc_oct = truncated_octahedron(origin, oct_edge_len)
            trunc_oct_edges = truncated_octahedron_edges(origin, oct_edge_len)
            
            limit = 10
            for i in range(limit):
                self.canvas.render(
                    trunc_oct=trunc_oct,
                    trunc_oct_edges=trunc_oct_edges,
                    pure_bolt=pure_bolt,
                    line_width=2,
                    alpha=1-i/limit,
                    current_time=current_time,
                    angle=angle
                )
                
            angle += angle_inc
        self.canvas.destroy()

   
if __name__ == '__main__':
    width = 1920
    height = 1080
    bolt_len = 200
    bolt_color_start = np.array([69, 0, 156], FLOAT32)/255.
    bolt_color_end = np.array([207, 170, 255], FLOAT32)/255.
    hl = HexBoltMETAC(width, height, bolt_len, bolt_color_start, bolt_color_end)
    hl.execute()
