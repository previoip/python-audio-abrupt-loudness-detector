from util.listen_audio import listenAudioHandler as LAh
from util.get_time_interval import TimeHandler
import signal, threading, wave, os, shutil
from inspect import getsourcefile

export_file_name = 'audio'
export_file_ext = '.wav'
export_max_num = 1000



if __name__ == "__main__":
    # instantiate timer class
    thread_timer = TimeHandler()
    timer = TimeHandler()
    timer.cls()
    curr_folder_dir = os.path.abspath(getsourcefile(lambda:0) + '/..')

    # instantiate audio handler
    stream = LAh(verbose=True)
    stream.set_opt(
        channels = 2,
        sample_rate = 16000,    # leave as is
        tap_threshold = 0.05,   # adjust threshold if no tap/click sound is detected
        input_block_time = 0.08  # leave as is
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

    # write waveform
    wf_param = {
        'n_channels': stream.channels,
        'sample_width': stream.pa.get_sample_size(stream.format),
        'frame_rate': stream.sample_rate
    }

    def write_waveform(blob):
        thread_timer.begin(show_header=False)

        cache_path = os.path.join(curr_folder_dir ,'cache/cache.wav')
        wf = wave.open(cache_path, 'wb')
        wf.setnchannels(wf_param['n_channels'])
        wf.setsampwidth(wf_param['sample_width'])
        wf.setframerate(wf_param['frame_rate'])
        wf.writeframes(blob)
        wf.close()

        export_path = os.path.join(curr_folder_dir, 'export')
        export_path_list = os.listdir(export_path)

        if not export_path_list:
            shutil.copyfile(cache_path, os.path.join(export_path, export_file_name + '_0' + export_file_ext))
        else:
            # export_path_list = [i[len(export_file_name):len(export_file_ext)-1] for i in export_path_list]
            export_path_list = [int(i[len(export_file_name) + 1 : -1 * len(export_file_ext)]) for i in export_path_list]
            index = 0
            while True:
                if index >= export_max_num:
                    print('max num of file exceeded: ', str(export_max_num))
                    break

                elif index not in export_path_list:
                    shutil.copyfile(cache_path, os.path.join(export_path, export_file_name + '_' + str(index) + export_file_ext))
                    print('new audio file created: ', export_file_name + '_' + str(index), ' eta: ', thread_timer.secondsToStr(thread_timer.get()))
                    break
                index += 1


    while True:
        is_detected, blob = stream.listen()
        if is_detected:
            threading.Thread(target=write_waveform(blob))
