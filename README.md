# sr-demo
Clone the repo, install the dependencies in the requirements.txt file, then run 'django manage.py runserver'.

Summary:
- Trained on 1,000 hours of speech data from CommonVoice (ran three epochs)
- Has ~8M parameters (~30mb file)
- $35 dollars to train (using cloud resource GPUs)
- Used a single A100 GPU for ~40 hours

Some things I learned:
- I learned a lot about working with audio in Python, recording it, parsing it, changing the frame-rate, buckets, quality, etc. I used pyaudio and pytorch.audio for most of the processing.
- I gained some experience with RNNs (used to predict likely sequences of letters)
- I also learned a lot about sending audio between the backend (harder than it sounds, in my opinion, because you have to figure out some specific media requirements for django)

  Here are some pictures:
Click 'record' to start recording:
![s1](https://github.com/user-attachments/assets/d80b65e6-7507-476d-aaee-5db4b1ba39b5)
Plot the classifications over time (28 classes: 26 letters, one space token, one silent token):
![s3](https://github.com/user-attachments/assets/1161bd0b-ad84-4c78-aeeb-c707587b22f8)
Helpful overlays to explain project ideas:
![s4](https://github.com/user-attachments/assets/fd3f9c14-7c8b-4604-8de1-873935d57e6b)
And at the end, it'll display the most likely word(s) in the audio clip (after showing the raw letters at first)!
![s5](https://github.com/user-attachments/assets/e5bf8f9c-a4b3-425e-be0f-4dc8216d62a5)

Note:
In order to run the demo, you need portaudio (a package that pyaudio depends on). If portaudio isn't installing correctly, try this:
```
pip install --global-option='build_ext' \
    --global-option='-I/usr/local/include' \
    --global-option='-L/usr/local/lib' \
    pyaudio
```
