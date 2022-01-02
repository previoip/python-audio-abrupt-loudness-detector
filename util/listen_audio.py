import pyaudio, math, struct, audioop, wave

class listenAudioHandler:
    # author: previoip
    # reference: https://github.com/xSparfuchs/clap-detection/blob/master/clap-detection.py
    # wrapper-util for pyaudio-pydub

    def __init__(self, verbose=False):
        self.pa = pyaudio.PyAudio()
        self.format = pyaudio.paInt16
        self.device_id = None
        self.stream = None
        self.__verbose = verbose
        self.quietcount = 0 
        self.noisycount = 0
        self.errorcount = 0
        self.tapcount = 0
        self.waveform_queue = [None for _ in range(10)]

        # defaults
        self.set_opt(
            channels = 1,
            tap_threshold = 1,
            sample_rate = 16000,
            input_block_time = 0.05
        )

        self.select_device()

    def set_opt(self, **kwargs):
        opts = {'channels', 'tap_threshold', 'sample_rate', 'input_block_time',}
        self.__dict__.update((k, v) for k, v in kwargs.items() if k in opts)
        self.input_frame_blocksize = int(self.input_block_time * self.sample_rate)
        self.__const_oversensitive = 15.0 / self.input_block_time
        self.__const_undersensitive = 120.0 / self.input_block_time
        self.__max_tap_block = 0.15 / self.input_block_time

    # static methods
        # get rms of audio stream block
    def __get_rms(self, block):
        # get rms of the waveform block https://stackoverflow.com/questions/25868428/pyaudio-how-to-check-volume
        # RMS amplitude is defined as the square root of the 
        # mean over time of the square of the amplitude.
        # so we need to convert this string of bytes into 
        # a string of 16-bit samples...

        # we will get one short out for each 
        # two chars in the string.
        count = len(block)/2
        _format = "%dh"%(count)
        shorts = struct.unpack( _format, block )

        # iterate over the block.
        sum_squares = 0.0
        for sample in shorts:
            # sample is a signed short in +/- 32768. 
            # normalize it to 1.0
            n = sample / 32768
            sum_squares += n*n

        return math.sqrt( sum_squares / count )
        # or unnormalized rms:
        # return audioop.rms(block, 2)
    
    # public methods
        # prompt device selector
    def select_device(self):
        info = self.pa.get_default_host_api_info()
        num_devices = info.get('deviceCount')

        # iterate for all possible device instances
        for i in range(0, num_devices):
            if(self.pa.get_device_info_by_host_api_device_index(0,i).get('maxInputChannels')):
                dname = self.pa.get_device_info_by_host_api_device_index(0, i).get('name')
                print(f'input device: {i} - {dname}')

        # prompt for device index
        index = int(input('Enter device index: '))

    
        print("recording via index", str(index), self.pa.get_device_info_by_host_api_device_index(0, index).get('name'))

        # sets device index
        self.device_id = index

        # audio-io listening handler
        # opens stream
    def open_stream(self):
        self.stream = self.pa.open(
            format = self.format,
            channels = self.channels,
            rate = self.sample_rate,
            input = True,
            input_device_index = self.device_id,
        )
        return True

        # begin listening input
    def listen(self):
        try:
            block = self.stream.read(self.input_frame_blocksize)
            self.waveform_queue.append(block)
            self.waveform_queue.pop(0)
        except IOError as e:
            self.errorcount += 1
            print( "(%d) Error recording: %s"%(self.errorcount,e) )
            self.noisycount = 1
            return

        amp = self.__get_rms(block)

        if amp > self.tap_threshold:
            # noisy input
            self.quietcount = 0
            self.noisycount += 1
            if self.noisycount > self.__const_oversensitive:
                self.tap_threshold *= 1.1
        else:            
            if 1 <= self.noisycount <= self.__max_tap_block:
                self.tapcount += 1
                self.get_waveform_from_queue()
            self.quietcount += 1
            self.noisycount = 0
            if self.quietcount > self.__const_undersensitive:
                self.tap_threshold *= 0.9
        
        if self.__verbose: 
            str_amp = f"amplitude: {'{:.4f}'.format(amp)}"
            str_nquiet = f"n_quiet:{self.quietcount}{' '*(4-len(str(self.quietcount)))}"
            str_nnoise = f"n_noisy:{self.noisycount}{' '*(4-len(str(self.noisycount)))}"
            str_ntap = f"tap:{self.tapcount}"
            str_queueLen = f"cache: {len(self.waveform_queue)}"
            str_volume = f"|| {'#'*int(amp*100/2)}"
            print(str_amp, str_nquiet, str_nnoise, str_ntap, str_queueLen, str_volume)

    def get_waveform_from_queue(self):
        for _ in range(3):
            block = self.stream.read(self.input_frame_blocksize)
            self.waveform_queue.append(block)
        data_frame = b''.join(self.waveform_queue)
        wf = wave.open('cache/cache.wav', 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.pa.get_sample_size(self.format))
        wf.setframerate(self.sample_rate)
        wf.writeframes(data_frame)
        wf.close()
        return

        # abrupt stop handler
    def abort(self):
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()
        print('aborted')



if __name__ == "__main__":
    pass