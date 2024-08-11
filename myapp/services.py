#(roughly) working model using pytorch's WAV2VEC2_ASR_BASE_10M 
#(no kenlm), using ctc-decode
import torchaudio
import torch
from torchaudio.models.decoder import ctc_decoder
from .wav2.impl import WAV2VEC2_ASR_BASE_10M #remember to import wav2 folder
import os
from django.conf import settings
import pyaudio
import wave


bundle = WAV2VEC2_ASR_BASE_10M
model = bundle.get_model().to('cpu')

lexicon_path = os.path.join("myapp", "decoder", "lexicon.txt")
tokens_path = os.path.join("myapp", "decoder", "tokens.txt")

beam_search_decoder = ctc_decoder(
    lexicon=lexicon_path,
    tokens=tokens_path,
    lm=None,
    nbest=3,
    beam_size=1500,
    lm_weight=3.23,
    word_score=-0.26
)

def record_generate_response(length_milliseconds):
    tmp_file = os.path.join(settings.MEDIA_ROOT, "audio_temp.wav")
    rate=16000
    chunk=1024
    sec= length_milliseconds / 1000
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels = 1,
                    rate=rate,
                    input=True,
                    output=True,
                    frames_per_buffer=chunk)
    print("Recording...")
    frames=[]
    for _ in range(0, int(rate / chunk * sec)):
        data = stream.read(chunk)
        frames.append(data)
    stream.stop_stream()
    stream.close()
    p.terminate()
    print("Finished recording")
    with wave.open(tmp_file, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
        wf.close()
    print(f"Saved audio to {tmp_file}")

    waveform,sample_rate = torchaudio.load(tmp_file)
    print(waveform, waveform.size())
    
    waveform = waveform.to("cpu")

    if sample_rate != bundle.sample_rate:
        waveform = torchaudio.functional.resample(waveform, sample_rate, bundle.sample_rate)

    with torch.inference_mode():
        features,_=model.extract_features(waveform)
    with torch.inference_mode():
        emission,_=model(waveform)
    full_emission = emission

    #todo, add a greedy decoder. this is a new feature when you
    #can send it to your frontend to display the most likely letters
    #before you convert it to the most likely words

    beam_search_result = beam_search_decoder(emission)
    beam_search_transcript = " ".join(beam_search_result[0][0].words).strip()

    #to map letters to time-steps and the amplitude 
    #(needs waveform, emission, tokens, timesteps, sample_rate)
    #implemented using waveform[0] instead of waveform
    timesteps = beam_search_result[0][0].timesteps.cpu().numpy().tolist()
    predicted_tokens = beam_search_decoder.idxs_to_tokens(beam_search_result[0][0].tokens)

    feats = [] #convert features to list instead of tensors
    for t in features:
        feats.append(t.numpy().tolist())
    #make it return emission, timestep, predicted_tokens
    return beam_search_transcript, emission[0].cpu().T.numpy().tolist(), timesteps, predicted_tokens, feats, waveform.cpu().numpy().tolist(), full_emission.cpu().numpy().tolist()
