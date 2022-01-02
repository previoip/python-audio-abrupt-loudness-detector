class WAVutil:
    def __init__(self, default_rate=16000):
        import pydub
        self.pd = pydub
        self.rate = default_rate
        self.waveform = None
    
    def write_wav(self, filepath):
        self.pd


if __name__ == "__main__":
    pass