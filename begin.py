from util.write_to_waveform import WAVutil
from util.listen_audio import listenAudioHandler as LAh
from util.get_time_interval import TimeHandler
import time, signal

if __name__ == "__main__":
    # instantiate timer class
    timer = TimeHandler()
    timer.cls()

    # instantiate audio handler
    stream = LAh(verbose=True)
    stream.set_opt(
        sample_rate = 16000,    # leave as is
        tap_threshold = 0.05,   # adjust threshold if no tap/click sound is detected
        input_block_time = 0.1  # leave as is
    )

    timer.begin()
    # opens audio-io stream
    stream.open_stream()
    def interruptHandler(signal, frame):
        _, _ = signal, frame
        timer.get()
        timer.log()
        stream.abort()
        exit()
    signal.signal(signal.SIGINT, interruptHandler)

    while True:
        stream.listen()

# print(f'program ran for {time.time() - begin_time} seconds')
