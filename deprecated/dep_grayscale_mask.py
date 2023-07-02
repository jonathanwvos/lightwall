from utils import AudioStream, normalize
from math import ceil
from numpy import abs, frombuffer
from numpy.fft import fft as FFT
from os.path import isdir, join

import cv2
import numpy as np


class GrayscaleMask:
    def __init__(self, no_bins, no_chunks, filename, masks_dir, outlines=False):
        self.no_bins = no_bins
        self.no_chunks = no_chunks
        self.filename = filename
        self.bass_mask, self.mid_mask, self.umid_mask, self.treb_mask = self.get_masks(masks_dir)
        self.bass_shape = self.bass_mask.shape

        if outlines:
            self.disp_arr = cv2.imread(join(masks_dir, 'outlines.png'), cv2.IMREAD_GRAYSCALE)
            self.disp_arr = self.disp_arr.flatten()
        else:
            bass_size = self.bass_mask.size
            self.disp_arr = np.zeros(bass_size, 'uint8')

        self.bass_inc = ceil(0.0125*no_bins)
        self.mid_inc = ceil(0.0095*no_bins)
        self.umid_inc = ceil(0.0875*no_bins)
        self.treb_inc = ceil(0.8*no_bins)

        # INDEXING
        # Bass
        self.random_b_idx = self.get_random_indices(self.bass_mask, self.bass_inc)
        # Midrange
        self.random_m_idx = self.get_random_indices(self.mid_mask, self.mid_inc)
        # Upper midrange
        self.random_um_idx = self.get_random_indices(self.umid_mask, self.umid_inc)
        # Treble
        self.random_t_idx = self.get_random_indices(self.treb_mask, self.treb_inc)

    def get_masks(self, dir):
        if not isdir(dir):
            raise FileNotFoundError(f'{dir} does not exist.')

        bass_mask = cv2.imread(join(dir, 'bass.png'), cv2.IMREAD_GRAYSCALE)
        mid_mask = cv2.imread(join(dir, 'midrange.png'), cv2.IMREAD_GRAYSCALE)
        umid_mask = cv2.imread(join(dir, 'upper midrange.png'), cv2.IMREAD_GRAYSCALE)
        treb_mask = cv2.imread(join(dir, 'treble.png'), cv2.IMREAD_GRAYSCALE)

        bass_shape = bass_mask.shape
        mid_shape = mid_mask.shape
        umid_shape = umid_mask.shape
        treb_shape = treb_mask.shape

        if bass_shape != mid_shape and bass_shape != umid_shape and bass_shape != treb_shape:
            raise Exception('Mask shapes do not match!')

        return bass_mask, mid_mask, umid_mask, treb_mask

    def get_random_indices(self, mask, no_choices):
        flat_mask = mask.flatten()
        indices = np.where(flat_mask == 255)[0]
        choices = np.random.choice(indices, size=no_choices, replace=False)

        return choices

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
                self.disp_arr[self.random_b_idx] = norm_fft[0:interval_0]
                self.disp_arr[self.random_m_idx] = norm_fft[interval_0:interval_1]
                self.disp_arr[self.random_um_idx] = norm_fft[interval_1:interval_2]
                self.disp_arr[self.random_t_idx] = norm_fft[interval_2:interval_3]

                arr = np.reshape(self.disp_arr, self.bass_shape)
                enlarged_disp_arr = cv2.resize(
                    arr,
                    (1920, 1080),
                    interpolation=cv2.INTER_NEAREST
                )

                cv2.imshow('Grayscale mask 1', enlarged_disp_arr)
                cv2.waitKey(1)


if __name__ == '__main__':
    no_bins = 10000
    no_chunks = 1024
    # filename = './music/striker.wav'
    filename = join('..', 'music', 'striker.wav')
    masks_dir = './masks'
    outlines = 'outlines.png'

    gm = GrayscaleMask(no_bins, no_chunks, filename, masks_dir)
    gm.execute()
