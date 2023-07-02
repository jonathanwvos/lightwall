from numpy import abs, frombuffer
from numpy.fft import fft as FFT
from utils import normalize

import cv2
import pyaudio
import numpy as np
import wave


def display_array(arr, disp_shape):
    arr = arr.reshape(disp_shape)
    arr = arr*255
    return arr.astype('uint8')


def main(filename, no_chunks, no_bins, disp_shape, disp_sf):
    indices = np.arange(no_bins)
    index_map = np.arange(no_bins)
    np.random.shuffle(index_map)

    with wave.open(filename, 'rb') as audio_file:
        p = pyaudio.PyAudio()

        stream = p.open(
            format=p.get_format_from_width(audio_file.getsampwidth()),
            channels=audio_file.getnchannels(),
            rate=audio_file.getframerate(),
            output=True
        )

        # Play wave file and render FFT
        mapped_disp_arr = np.zeros(no_bins, np.int16)
        while len(data := audio_file.readframes(no_chunks)):
            stream.write(data)

            signal = frombuffer(data, dtype=np.int16)
            fft = abs(FFT(signal, n=no_bins))
            norm_fft = normalize(fft)
            mapped_disp_arr[indices] = norm_fft[index_map]
            disp_arr = display_array(mapped_disp_arr, disp_shape)
            enlarged_disp_arry = cv2.resize(
                disp_arr,
                disp_shape*disp_sf
                )
            # smoothed_disp_arr = cv2.blur(enlarged_disp_arry, (5,5))

            cv2.imshow('', enlarged_disp_arry)
            cv2.waitKey(1)

        stream.close()

        p.terminate()


if __name__ == '__main__':
    filename = 'music/striker.wav'
    no_chunks = 1024
    no_bins = 20000
    display_shape = np.array([200, 100])
    display_scaling_factor = 4

    main(
        filename,
        no_chunks,
        no_bins,
        display_shape,
        display_scaling_factor
    )
