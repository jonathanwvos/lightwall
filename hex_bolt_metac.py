from multiprocessing import Process, Queue, Event
from bolts import hex_bolt
from numpy import abs, frombuffer, mean
from numpy import float32 as FLOAT32
from numpy import int16 as INT16
from numpy import pi as PI
from numpy.fft import fft as FFT
from os.path import join
from OpenGL.GL import *
from OpenGL.GLUT import *
from polytopes import truncated_octahedron, truncated_octahedron_edges
from utils import AudioStream, Shaders
from time import time
from collections import deque

import numpy as np
import pygame as pg
import pyrr


class DJ:
    def __init__(self, filename, no_chunks, event):
        self.filename = filename
        self.no_chunks = no_chunks
        self.no_bins = 15000
        self.bass_inc = 188
        self.mid_inc = 143
        self.umid_inc = 1313
        self.treb_inc = 12000
        self.terminate_loop = False
        self.event = event
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
        
        self.beat_queue = deque()
        self.beat_queue_size = 10
        self.beat_dampener = 0.9

    def audio_bands(self, data, log=True):
        signal = frombuffer(data, dtype=INT16)
        fft = abs(FFT(signal, n=self.no_bins))
        if log:
            fft = np.emath.logn(2, fft)

        return (
            fft[:self.bass_inc],
            fft[self.interval_0:self.interval_1],
            fft[self.interval_1:self.interval_2],
            fft[self.interval_2:self.interval_3]
        )
        
    def extract_bands(self, data, execution_cycle):
        bass, mid, umid, treb = self.audio_bands(data)

        bass_mean = mean(bass)
        self.bass_queue.append(bass_mean)
        mid_mean = mean(mid)
        self.mid_queue.append(mid_mean)
        umid_mean = mean(umid)
        self.umid_queue.append(umid_mean)
        treb_mean = mean(treb)
        self.treb_queue.append(treb_mean)

        if execution_cycle >= self.bass_queue_size:
            self.bass_queue.popleft()
            self.mid_queue.popleft()
            self.umid_queue.popleft()
            self.treb_queue.popleft()

        bass_dampened = self.bass_dampener*(mean(self.bass_queue))
        mid_dampened = self.treb_dampener*(mean(self.mid_queue))
        umid_dampened = self.treb_dampener*(mean(self.umid_queue))
        treb_dampened = self.treb_dampener*(mean(self.treb_queue))

        return bass_dampened, mid_dampened, umid_dampened, treb_dampened

    def execute(self, queue):
        with AudioStream(self.filename) as (audio_file, stream):
            execution_cycle = 1
            self.event.set()
            while len(data := audio_file.readframes(self.no_chunks)) and not self.terminate_loop:
                stream.write(data) # Stream audio to speakers
                bass_dampened, mid_dampened, umid_dampened, treb_dampened = self.extract_bands(data, execution_cycle)
                queue.put([bass_dampened, mid_dampened, umid_dampened, treb_dampened])
                execution_cycle += 1


class Canvas:
    def __init__(
        self,
        res_w,
        res_h,
        frame_rate,
        bolt_color_start,
        bolt_color_end,
        bolt_len
    ):
        self.res_w = float(res_w)
        self.res_h = float(res_h)
        self.frame_rate = frame_rate
        self.bolt_color_start = bolt_color_start
        self.bolt_color_end = bolt_color_end
        self.bolt_len = bolt_len
        
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
        
        hex_grid_shaders = Shaders(
            join('shaders', 'hex_grid_vertices.glsl'),
            join('shaders', 'hex_grid_fragments.glsl')
        )
        self.hex_grid_shaders = hex_grid_shaders.compile()
    
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
        
    def set_grid_GL(self):
        glUseProgram(self.hex_grid_shaders)
        self.set_projection_matrices(self.hex_grid_shaders)
        self.bolt_vao = glGenVertexArrays(1)
        self.bolt_vbo = glGenBuffers(1)

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

    # def render_hex_grid(self, points, point_width):
        

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
        
    def render_hex_bolt(self, pure_bolt, alpha, line_width):
        bolt_lines = self.bolt_lines(pure_bolt)
        color_bl = self.add_bolt_color(bolt_lines, alpha)
        color_bp = self.add_bolt_color(pure_bolt, alpha*0.7)
        
        self.set_bolt_GL()
        self.render_bolt_points(color_bp, line_width)
        self.render_bolt_lines(color_bl, line_width)

    def render_metac_body(self, trunc_oct, current_time, angleX, angleY, angleZ):
        offset = 12
        
        glBindVertexArray(self.eye_vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.eye_vbo)
        glGetAttribLocation(self.hex_eye_shaders, 'position')
        glBufferData(GL_ARRAY_BUFFER, trunc_oct.nbytes, trunc_oct, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, False, offset, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        
        glUniform1f(self.angleXGL, angleX)
        glUniform1f(self.angleYGL, angleY)
        glUniform1f(self.angleZGL, angleZ)
        for i in range(len(trunc_oct)):
            glDrawArrays(GL_TRIANGLES, i*3, 3)
        
        glUniform1f(self.timeGL, current_time)

    def render_metac_wireframes(self, edges, angleX, angleY, angleZ):
        offset = 12
        
        glBindVertexArray(self.eye_wireframe_vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.eye_wireframe_vbo)
        glGetAttribLocation(self.hex_eye_wireframe_shaders, 'position')
        glBufferData(GL_ARRAY_BUFFER, edges.nbytes, edges, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, False, offset, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        
        glUniform1f(self.angleXGL, angleX)
        glUniform1f(self.angleYGL, angleY)
        glUniform1f(self.angleZGL, angleZ)
        for i in range(len(edges)):
            glDrawArrays(GL_LINES, i*2, 2)
        
    def render_metac(self, trunc_oct, trunc_oct_edges, current_time, angleX, angleY, angleZ):
        self.set_eye_GL()
        self.render_metac_body(trunc_oct, current_time, angleX, angleY, angleZ)
        self.set_eye_wireframes_GL()
        self.render_metac_wireframes(trunc_oct_edges, angleX, angleY, angleZ)
        
    def clear_display(self):
        glEnable(GL_DEPTH_TEST)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
    def flush_and_flip(self):
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

    def event_handler(self):
        for event in pg.event.get():
            if (event.type == pg.QUIT):
                return False
            
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                return False
        
        return True
    
    def execute(self, queue):
        
        # while(count):
        #     print(count)
            
        #     count = queue.get()
            
        start_time = time()
        angleX_inc = 0.0
        angleY_inc = 0.0
        angleZ_inc = 0.0
        angleX = 0.0
        angleY = 0.01
        angleZ = 0.0
        pace = 10
        execution_cycle = 1
        oct_edge_len = 0.05
        
        run = True
        count = queue.get()
        while count and run:
            run = self.event_handler()
            
            # bass_dampened, mid_dampened, umid_dampened, treb_dampened = self.dj.extract_bands(data, execution_cycle)
            current_time = time() - start_time
            
            angleY = 0.3*np.sin(pace*current_time)
            angleX = -0.3*(np.sin(pace*2*current_time)+0.7)

            origin = np.array([0,0,0], FLOAT32)
            pure_bolt = hex_bolt(self.bolt_len, 0.05, origin, 0)
            trunc_oct = truncated_octahedron(origin, oct_edge_len)
            trunc_oct_edges = truncated_octahedron_edges(origin, oct_edge_len)
            
            print(round(current_time,1)/4)
            # if np.isclose(round(current_time,0)%2, 0.0):
            limit = 2
            for i in range(limit):
                self.clear_display()
                self.render_hex_bolt(pure_bolt, 1-i/limit, 2)
                self.render_metac(
                    trunc_oct=trunc_oct,
                    trunc_oct_edges=trunc_oct_edges,
                    current_time=current_time,
                    angleX=angleX,
                    angleY=angleY,
                    angleZ=angleZ
                )
                self.flush_and_flip()
            
            angleX += angleX_inc
            angleY += angleY_inc
            angleZ += angleZ_inc
            execution_cycle += 1
            
            count = queue.get()
        
        self.destroy()


class HexBoltMETAC:
    def __init__(self, filename, no_chunks, width, height, bolt_len, bolt_color_start, bolt_color_end, frame_rate):
        self.filename = filename
        self.no_chunks = no_chunks
        self.res_w = width
        self.res_h = height
        self.frame_rate = frame_rate
        self.bolt_len = bolt_len
        self.bolt_color_start = bolt_color_start
        self.bolt_color_end = bolt_color_end
        
        self.canvas = Canvas(self.res_w,
            self.res_h,
            self.frame_rate,
            self.bolt_color_start,
            self.bolt_color_end,
            self.bolt_len
        )
        self.music_event = Event()
        self.dj = DJ(filename, no_chunks, self.music_event)
    
    def event_handler(self):
        for event in pg.event.get():
            if (event.type == pg.QUIT):
                return False
            
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                return False
        
        return True
        
    def execute(self):
        queue = Queue()
        dj_process = Process(target=self.dj.execute, args=(queue,))
        
        start_time = time()
        angleX_inc = 0.0
        angleY_inc = 0.0
        angleZ_inc = 0.0
        angleX = 0.0
        angleY = 0.01
        angleZ = 0.0
        pace = 10
        execution_cycle = 1
        oct_edge_len = 0.05
        
        run = True
        dj_process.start()
        
        while not self.music_event.is_set():
            pass
        
        while run:
            run = self.event_handler()
            
            print(queue.get())
            current_time = time() - start_time
            
            angleY = 0.3*np.sin(pace*current_time)
            angleX = -0.3*(np.sin(pace*2*current_time)+0.7)

            origin = np.array([0,0,0], FLOAT32)
            pure_bolt = hex_bolt(self.bolt_len, 0.05, origin, 0)
            trunc_oct = truncated_octahedron(origin, oct_edge_len)
            trunc_oct_edges = truncated_octahedron_edges(origin, oct_edge_len)
            
            limit = 5
            for i in range(limit):
                self.canvas.clear_display()
                self.canvas.render_hex_bolt(pure_bolt, 1-i/limit, 2)
                self.canvas.render_metac(
                    trunc_oct=trunc_oct,
                    trunc_oct_edges=trunc_oct_edges,
                    current_time=current_time,
                    angleX=angleX,
                    angleY=angleY,
                    angleZ=angleZ
                )
                self.canvas.flush_and_flip()
            
            angleX += angleX_inc
            angleY += angleY_inc
            angleZ += angleZ_inc
            execution_cycle += 1
        
        dj_process.terminate()
        self.canvas.destroy()
        queue.close()
        queue.join_thread()


if __name__ == '__main__':
    filename = join('music', 'Scissors.wav')
    no_chunks = 1024
    width = 1920
    height = 1080
    bolt_len = 200
    bolt_color_start = np.array([69, 0, 156], FLOAT32)/255.
    bolt_color_end = np.array([207, 170, 255], FLOAT32)/255.
    frame_rate = 240
    metac = HexBoltMETAC(filename, no_chunks, width, height, bolt_len, bolt_color_start, bolt_color_end, frame_rate)
    metac.execute()
