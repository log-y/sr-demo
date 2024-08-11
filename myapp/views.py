import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse
from .services import record_generate_response
import io
import json
import torch
import base64

@csrf_exempt
def start_recording(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            sec = data.get('milliseconds', '')
            transcript, emission, timesteps, tokens, features, waveform, full_emission = record_generate_response(sec)
            rate = 16000

            #first pic
            fig, ax = plt.subplots(len(features), 1, figsize=(16, 4.3 * len(features)))
            
            for i, feats in enumerate(features):
                ax[i].imshow(feats[0], interpolation="nearest") #removed a .cpu()
                ax[i].set_title(f"Feature from transformer layer {i+1}")
                ax[i].set_xlabel("Feature dimension")
                ax[i].set_ylabel("Frame (time-axis)")
            fig.tight_layout()

            buf1 = io.BytesIO()
            fig.savefig(buf1, format='png')
            buf1.seek(0)
            plt.close(fig)
            img_base64 = base64.b64encode(buf1.read()).decode('utf-8')

            # Return the base64 string in the JSON response
            # return JsonResponse({'here': "here"})


            #second pic
            plt.imshow(emission, interpolation="nearest")
            plt.title("Classification result")
            plt.xlabel("Frame (time-axis)")
            plt.ylabel("Class")
            plt.tight_layout()

            buf2 = io.BytesIO()
            plt.savefig(buf2, format='png')
            buf2.seek(0)
            plt.close()
            img2_base64 = base64.b64encode(buf2.read()).decode('utf-8')
            
            waveform = torch.tensor(waveform)
            # emission = torch.tensor(emission) #2d array
            full_emission = torch.tensor(full_emission)
            timesteps = torch.tensor(timesteps)
            # waveform = waveform[0]
            print(waveform)
            
            #third pic
            def plot_alignments(waveform, emission, tokens, timesteps, sample_rate):
                t = torch.arange(waveform.size(0)) / sample_rate
                ratio = waveform.size(0) / emission.size(1) / sample_rate

                chars = []
                words = []
                word_start = None
                for token, timestep in zip(tokens, timesteps * ratio):
                    if token == "|":
                        if word_start is not None:
                            words.append((word_start, timestep))
                        word_start = None
                    else:
                        chars.append((token, timestep))
                        if word_start is None:
                            word_start = timestep

                fig1, axes = plt.subplots(3, 1)

                def _plot(ax, xlim):
                    ax.plot(t, waveform)
                    for token, timestep in chars:
                        ax.annotate(token.upper(), (timestep, 0.5))
                    for word_start, word_end in words:
                        ax.axvspan(word_start, word_end, alpha=0.1, color="red")
                    ax.set_ylim(-0.6, 0.7)
                    ax.set_yticks([0])
                    ax.grid(True, axis="y")
                    ax.set_xlim(xlim)


                _plot(axes[0], (0.3, 2.5))
                # _plot(axes[1], (2.5, 4.7))
                # _plot(axes[2], (4.7, 6.9))
                axes[0].set_xlabel("time (sec)")
                fig1.delaxes(axes[2])
                fig1.delaxes(axes[1])
                fig1.tight_layout()

                buf3 = io.BytesIO()
                fig1.savefig(buf3, format='png')
                buf3.seek(0)
                plt.close(fig1)

                img3_base64 = base64.b64encode(buf3.read()).decode('utf-8')
                return img3_base64

            img3_base64 = plot_alignments(waveform[0], full_emission, tokens, timesteps, rate)


            

            
            return JsonResponse({"image": img_base64,
                                 "image1": img2_base64,
                                 'image2': img3_base64,
                                 'transcript': transcript})

            

            return JsonResponse({'transcript': transcript,
                                 'emission': emission,
                                 'timesteps': timesteps,
                                 'predicted_tokens': tokens,
                                 'feats': features
                                 })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
            
def index(request):
    return render(request,'index.html')

#for features and layers:
'''
fig, ax = plt.subplots(len(features), 1, figsize=(16, 4.3 * len(features)))
for i, feats in enumerate(features):
    ax[i].imshow(feats[0].cpu(), interpolation="nearest")
    ax[i].set_title(f"Feature from transformer layer {i+1}")
    ax[i].set_xlabel("Feature dimension")
    ax[i].set_ylabel("Frame (time-axis)")
fig.tight_layout()
'''
#for classes and timeframe:
'''
plt.imshow(emission[0].cpu().T, interpolation="nearest")
plt.title("Classification result")
plt.xlabel("Frame (time-axis)")
plt.ylabel("Class")
plt.tight_layout()
'''
#for waveform, tokens, and timesteps 
'''
def plot_alignments(waveform, emission, tokens, timesteps, sample_rate):

    t = torch.arange(waveform.size(0)) / sample_rate
    ratio = waveform.size(0) / emission.size(1) / sample_rate

    chars = []
    words = []
    word_start = None
    for token, timestep in zip(tokens, timesteps * ratio):
        if token == "|":
            if word_start is not None:
                words.append((word_start, timestep))
            word_start = None
        else:
            chars.append((token, timestep))
            if word_start is None:
                word_start = timestep

    fig, axes = plt.subplots(3, 1)

    def _plot(ax, xlim):
        ax.plot(t, waveform)
        for token, timestep in chars:
            ax.annotate(token.upper(), (timestep, 0.5))
        for word_start, word_end in words:
            ax.axvspan(word_start, word_end, alpha=0.1, color="red")
        ax.set_ylim(-0.6, 0.7)
        ax.set_yticks([0])
        ax.grid(True, axis="y")
        ax.set_xlim(xlim)

    _plot(axes[0], (0.3, 2.5))
    _plot(axes[1], (2.5, 4.7))
    _plot(axes[2], (4.7, 6.9))
    axes[2].set_xlabel("time (sec)")
    fig.tight_layout()

plot_alignments(waveform[0], emission, predicted_tokens, timesteps, bundle.sample_rate)
'''