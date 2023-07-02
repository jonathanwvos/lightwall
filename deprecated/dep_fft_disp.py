import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt

# Parameters for audio processing
CHUNK = 1024  # Number of audio frames per buffer
FORMAT = 'float32'  # Audio format
CHANNELS = 1  # Mono audio
RATE = 44100  # Sampling rate (Hz)

# Create the figure and axes for the FFT plot
fig, ax = plt.subplots()

# Create a buffer to store audio data for computing FFT
audio_buffer = np.zeros(CHUNK, dtype=np.float32)

# Callback function for audio stream
def audio_callback(indata, frames, time, status):
    # Store the audio data in the buffer
    audio_buffer[:frames] = indata[:, 0]  # Use only the first channel if stereo

    # Compute the FFT
    fft = np.abs(np.fft.fft(audio_buffer))

    # Update the FFT plot
    ax.clear()
    ax.plot(fft)

    # Set plot limits and labels
    ax.set_xlim(0, CHUNK // 2)
    ax.set_ylim(0, 2000)  # Adjust the y-axis limit as needed
    ax.set_xlabel('Frequency (bins)')
    ax.set_ylabel('Magnitude')

    # Update the plot
    plt.pause(0.001)

# Open the audio stream and start playing
stream = sd.InputStream(callback=audio_callback,
                        channels=CHANNELS,
                        samplerate=RATE,
                        dtype=FORMAT,
                        blocksize=CHUNK)
stream.start()

# Wait for the user to stop the program
input("Press enter to stop...")

# Stop the audio stream
stream.stop()
stream.close()

# Close the plot window
plt.close(fig)
