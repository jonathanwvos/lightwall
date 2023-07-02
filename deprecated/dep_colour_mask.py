from utils import AudioStream, normalize
from math import ceil
from numpy import abs, frombuffer
from numpy.fft import fft as FFT
from os.path import isdir, join

import cv2
import numpy as np


class ColourMask:
    def __init__(self, no_bins, no_chunks, filename, masks_dir, outlines=False):
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

        self.disp_arr = self.get_display_arr()

        self.bass_inc = ceil(0.0125*no_bins)
        self.mid_inc = ceil(0.0095*no_bins)
        self.umid_inc = ceil(0.0875*no_bins)
        self.treb_inc = ceil(0.8*no_bins)

        # INDEXING
        # Bass
        self.random_b_idx = self.get_random_indices(self.bass_mask_gray, self.bass_inc)
        # Midrange
        self.random_m_idx = self.get_random_indices(self.mid_mask_gray, self.mid_inc)
        # Upper midrange
        self.random_um_idx = self.get_random_indices(self.umid_mask_gray, self.umid_inc)
        # Treble
        self.random_t_idx = self.get_random_indices(self.treb_mask_gray, self.treb_inc)

    def get_display_arr(self):
        if outlines:
            self.disp_arr = cv2.imread(join(masks_dir, 'outlines.png'), cv2.IMREAD_GRAYSCALE)
            return self.disp_arr.flatten()
        else:
            bass_size = self.bass_mask_gray.size
            return np.zeros(bass_size, dtype=np.float32)

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

    def get_random_indices(self, mask, no_choices):
        flat_mask = mask.flatten()
        indices = np.where(flat_mask == 1)[0]
        choices = np.random.choice(indices, size=no_choices, replace=False)

        return choices

    def preprocess(self):
        pass

    def process(self):
        pass

    def postprocess(self):
        pass

    def execute(self):
        with AudioStream(self.filename) as (audio_file, stream):
            while len(data := audio_file.readframes(no_chunks)):
                stream.write(data) # Stream audio to speakers

                signal = frombuffer(data, dtype=np.int16)
                fft = abs(FFT(signal, n=no_bins))
                norm_fft = normalize(fft)

                interval_0 = self.bass_inc
                interval_1 = self.bass_inc+self.mid_inc
                interval_2 = self.bass_inc+self.mid_inc+self.umid_inc
                interval_3 = self.bass_inc+self.mid_inc+self.umid_inc+self.treb_inc

                bass = np.zeros(self.get_display_arr().size, dtype=np.float32)
                bass[self.random_b_idx] = norm_fft[:self.bass_inc]
                bass = np.reshape(bass, self.bass_mask_gray.shape).astype('uint8')
                bass_colour = cv2.bitwise_and(self.bass_mask, self.bass_mask, mask=bass)
            
                mid = np.zeros(self.get_display_arr().size, dtype=np.float32)
                mid[self.random_m_idx] = norm_fft[interval_0:interval_1]
                mid = np.reshape(mid, self.mid_mask_gray.shape).astype('uint8')
                mid_colour = cv2.bitwise_and(self.mid_mask, self.mid_mask, mask=mid)

                umid = np.zeros(self.get_display_arr().size, dtype=np.float32)
                umid[self.random_um_idx] = norm_fft[interval_1:interval_2]
                umid = np.reshape(umid, self.umid_mask_gray.shape).astype('uint8')
                umid_colour = cv2.bitwise_and(self.umid_mask, self.umid_mask, mask=umid)

                treb = np.zeros(self.get_display_arr().size, dtype=np.float32)
                treb[self.random_t_idx] = norm_fft[interval_2:interval_3]
                treb = np.reshape(treb, self.treb_mask_gray.shape).astype('uint8')
                treb_colour = cv2.bitwise_and(self.treb_mask, self.treb_mask, mask=treb)

                disp_arr = bass_colour + mid_colour + umid_colour + treb_colour

                disp_arr = cv2.resize(
                    disp_arr,
                    (1920, 1080),
                    interpolation=cv2.INTER_NEAREST
                )

                cv2.imshow('Colour mask 1', disp_arr.astype('uint8'))
                cv2.waitKey(1)


if __name__ == '__main__':
    no_bins = 15000
    no_chunks = 1024
    filename = join('music', 'Amon Amarth - Masters of War.wav')
    masks_dir = './masks/colours'
    outlines = 'outlines.png'

    gm = ColourMask(no_bins, no_chunks, filename, masks_dir)
    gm.execute()
