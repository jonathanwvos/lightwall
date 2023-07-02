from dep_colour_mask_2 import ColourMask
from utils import AudioStream, normalize
from math import ceil
from numpy import abs, frombuffer
from numpy.fft import fft as FFT
from os.path import isdir, join
from random import randint

import cv2
import numpy as np


class Circles(ColourMask):
    def __init__(self, no_bins, no_chunks, filename, masks_dir, outlines=False, radii=False):
        self.no_bins = no_bins
        self.no_chunks = no_chunks
        self.filename = filename
        (
            self.bass_mask, 
            self.bass_mask_gray,
            self.mid_mask, 
            self.mid_mask_gray,
            self.umid_mask,
            self.umid_mask_gray,
            self.treb_mask,
            self.treb_mask_gray
        ) = self.get_masks(masks_dir)
        self.bass_shape = self.bass_mask_gray.shape

        self.disp_arr = self.get_display_arr(outlines)

        if radii:
            self.radii = radii
        if not radii:
            self.radii = randint(1,10)

    def scintilate(self, idx, norm_fft, inc, shape, colour):
        raise NotImplementedError("scintilate is not used in the Circle's class.")

    def get_random_indices(self, mask, no_choices):
        raise NotImplementedError("get_random_indices is not used in the Circle's class.")

    def get_masks(self, dir):
        if not isdir(dir):
            raise FileNotFoundError(f'{dir} does not exist.')

        bass_mask = cv2.imread(join(dir, 'bass.png'))
        bass_mask_gray = cv2.cvtColor(bass_mask, cv2.COLOR_BGR2GRAY)
        bass_mask_gray[bass_mask_gray != 0] = 1
        mid_mask = cv2.imread(join(dir, 'midrange.png'))
        mid_mask_gray = cv2.cvtColor(mid_mask, cv2.COLOR_BGR2GRAY)
        mid_mask_gray[mid_mask_gray != 0] = 1
        umid_mask = cv2.imread(join(dir, 'upper midrange.png'))
        umid_mask_gray = cv2.cvtColor(umid_mask, cv2.COLOR_BGR2GRAY)
        umid_mask_gray[umid_mask_gray != 0] = 1
        treb_mask = cv2.imread(join(dir, 'treble.png'))
        treb_mask_gray = cv2.cvtColor(treb_mask, cv2.COLOR_BGR2GRAY)
        treb_mask_gray[treb_mask_gray != 0] = 1

        bass_shape = bass_mask.shape
        mid_shape = mid_mask.shape
        umid_shape = umid_mask.shape
        treb_shape = treb_mask.shape

        if bass_shape != mid_shape and bass_shape != umid_shape and bass_shape != treb_shape:
            raise Exception('Mask shapes do not match!')

        return bass_mask, bass_mask_gray, mid_mask, mid_mask_gray, umid_mask, umid_mask_gray, treb_mask, treb_mask_gray

    def get_display_arr(self, outlines=False):
        if outlines:
            disp_arr = cv2.imread(join(masks_dir, 'outlines.png'), cv2.IMREAD_GRAYSCALE)
            return disp_arr.astype(np.float32)
        else:
            return np.zeros(self.bass_mask_gray.shape, dtype=np.float32)

    def get_random_centroids(self, mask, no_choices):
        centroids = []
        y, x = np.where(mask == 1)
        coords = list(zip(y,x))
        coords_idx = np.arange(len(coords))

        idx = np.random.choice(coords_idx, size=no_choices, replace=False)

        centroids = [coords[id] for id in idx]

        return centroids
    
    def preprocess(self, no_bins):
        # FFT BASS, MID, UMID AND TREB INCREMENTS
        self.bass_inc = ceil(0.0125*no_bins)
        self.mid_inc = ceil(0.0095*no_bins)
        self.umid_inc = ceil(0.0875*no_bins)
        self.treb_inc = ceil(0.8*no_bins)

        # CENTROIDS
        self.b_centroids = self.get_random_centroids(self.bass_mask_gray, self.bass_inc)
        self.m_centroids = self.get_random_centroids(self.mid_mask_gray, self.mid_inc)
        self.um_centroids = self.get_random_centroids(self.umid_mask_gray, self.umid_inc)
        self.t_centroids = self.get_random_centroids(self.treb_mask_gray, self.treb_inc)

        # INTERVALS
        self.interval_0 = self.bass_inc
        self.interval_1 = self.bass_inc+self.mid_inc
        self.interval_2 = self.bass_inc+self.mid_inc+self.umid_inc
        self.interval_3 = self.bass_inc+self.mid_inc+self.umid_inc+self.treb_inc

    def postprocess(self, bass, mid=None, umid=None, treb=None):
        disp_arr = bass + mid + umid + treb

        disp_arr = cv2.resize(
            disp_arr,
            (1920, 1080),
            interpolation=cv2.INTER_NEAREST
        )

        return disp_arr

    def circles(self, centroids, norm_fft, shape, colour):
        arr = np.zeros(shape, dtype=np.float32)
        
        for id, (y,x) in enumerate(centroids):
            intensity = norm_fft[id]
            cv2.circle(arr, (x,y), self.radii, colour[y,x,:]*intensity, thickness=-1)
        
        return arr

    def execute(self):
        with AudioStream(self.filename) as (audio_file, stream):
            self.preprocess(self.no_bins)
            
            while len(data := audio_file.readframes(self.no_chunks)):
                stream.write(data) # Stream audio to speakers

                signal = frombuffer(data, dtype=np.int16)
                fft = abs(FFT(signal, n=self.no_bins))
                norm_fft = normalize(fft, dtype=np.float32)

                bass = self.circles(
                    self.b_centroids,
                    norm_fft,
                    self.bass_mask.shape,
                    self.bass_mask
                )

                mid = self.circles(
                    self.m_centroids,
                    norm_fft,
                    self.mid_mask.shape,
                    self.mid_mask
                )

                umid = self.circles(
                    self.um_centroids,
                    norm_fft,
                    self.umid_mask.shape,
                    self.umid_mask
                )

                treb = self.circles(
                    self.t_centroids,
                    norm_fft,
                    self.treb_mask.shape,
                    self.treb_mask
                )
            
                disp_arr = self.postprocess(bass, mid, umid, treb)

                cv2.imshow('Colour mask 2', disp_arr.astype('uint8'))
                cv2.waitKey(1)


if __name__ == '__main__':
    no_bins = 15000
    no_chunks = 1024
    filename = 'music/striker.wav'
    masks_dir = './masks/colours'
    outlines = 'outlines.png'
    radii = 1

    gm = Circles(no_bins, no_chunks, filename, masks_dir, radii)
    gm.execute()
