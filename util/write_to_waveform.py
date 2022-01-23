import wave, os, shutil, threading
from inspect import getsourcefile
class WAVutil:
    def __init__(self, default_rate=16000):
        self.curr_dir = os.path.abspath(getsourcefile(lambda:0)+ '/..')
        self.wf = wave
        self.blob = None

    def set_wave(self, blob):
        self.blob = blob

    def write_wav(self, filepath):
        self.pd


if __name__ == "__main__":
    pass