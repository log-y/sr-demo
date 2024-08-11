document.getElementById('startRecording').addEventListener('click', async () => {
    const btn = document.getElementById('startRecording')

    // const status = document.getElementById('status');
    btn.textContent = 'Recording...';
    btn.classList.add('pulsate')

    let ms = 2000;

    let mediaRecorder;
    let audioChunks = [];
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    mediaRecorder = new MediaRecorder(stream, {
        audioBitsPerSecond: 16000 * 16, // Bitrate for 16-bit audio at 16 kHz
        mimeType: 'audio/webm'
    });
    mediaRecorder.ondataavailable = event => {
        audioChunks.push(event.data);
    };
    mediaRecorder.onstop = async () => {
    }
    mediaRecorder.start();

    setTimeout(() => {
        mediaRecorder.stop();
        btn.classList.remove('pulsate');
        btn.textContent = 'Processing...';
    }, ms);

    const response = await fetch('/api/start-recording/', {
        method: 'POST',
        body: JSON.stringify({ milliseconds: ms })
    });
    if (!response.ok) {
        console.error('Server returned an error', response.statusText);
        btn.textContent = 'Error occurred. Please try again.';
    } else {
        const data = await response.json();
        const transcript = data.transcript;
        // Clear previous images
        document.getElementById('imageContainer').innerHTML = '';
        document.getElementById('imageContainer1').innerHTML = '';
        document.getElementById('imageContainer2').innerHTML = '';
        document.getElementById('response').innerHTML = '';

        // First image
        const img0 = document.createElement('img');
        img0.src = 'data:image/png;base64,' + data.image;
        document.getElementById('imageContainer').appendChild(img0);

        // Second image
        const img1 = document.createElement('img');
        img1.src = 'data:image/png;base64,' + data.image1;
        document.getElementById('imageContainer1').appendChild(img1);

        // Third image
        const img2 = document.createElement('img');
        img2.src = 'data:image/png;base64,' + data.image2;
        // Make sure the image scales with the container
        document.getElementById('imageContainer2').appendChild(img2);
        btn.textContent = 'Processing complete';

        const responseDiv = document.getElementById("response");

        // Create and append the header
        const header = document.createElement('h3');
        header.innerText = "Transcript: ";
        responseDiv.appendChild(header);

        // Create a text node for the transcript and append it
        const transcriptText = document.createTextNode(transcript);
        responseDiv.appendChild(transcriptText);

        // Add the class last
        responseDiv.classList.add('response');
    }
});
// }
// catch(e){
//     console.error("Error accessing media device");
// }