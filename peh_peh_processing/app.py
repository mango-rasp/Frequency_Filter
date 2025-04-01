from flask import Flask, request, Response, send_file
from pydub import AudioSegment
import wave
import numpy as np
from IPython.display import Audio, display
import scipy as sp
import matplotlib.pyplot as plt
from scipy.io.wavfile import write
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/process-audio', methods=['POST'])

def process_audio():
    audio_file = request.files['audio']
    lower_hertz = int(float(request.form['low']))
    upper_hertz = int(float(request.form['upper']))

    temp_path = "temp_audio.wav"
    audio_file.save(temp_path)

    audio = wave.open(temp_path)
    aud_nframes = audio.getnframes()
    raw_data = audio.readframes(aud_nframes)
    aud_framerate = audio.getframerate()

    sig_int16 = np.frombuffer(raw_data, dtype=np.int16)
    sig = sig_int16.astype(np.float32) / 32768.0

    freq_3 = sig

    frequency_cutoff2 = upper_hertz
    frequency_cutoff3 = lower_hertz
    cutoff_index2 = int(frequency_cutoff2/(aud_framerate/2/len(sig)))
    cutoff_index3 = int(frequency_cutoff3/(aud_framerate/2/len(sig)))
    freq_3[cutoff_index2:] = 0
    freq_3[:cutoff_index3] = 0

    filtered_sig = np.fft.irfft(freq_3)
    filtered_sig = filtered_sig / np.max(np.abs(filtered_sig)) 
    filtered_sig_int16 = (filtered_sig * 32767).astype(np.int16)

    output_path = "filtered_audio.wav"
    write(output_path, aud_framerate, filtered_sig_int16)
    response = send_file(
        output_path, mimetype='audio/wav', as_attachment=True, conditional=True
    )
    @response.call_on_close
    def remove_files():
        try:
            os.remove(temp_path)
            os.remove(output_path)
        except:
            pass

    return response

if __name__ == '__main__':
    app.run(debug=True)
    


