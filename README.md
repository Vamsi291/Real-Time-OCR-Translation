# Real-Time-OCR-Translation
Real Time Text Detection and Translation using Python, Google API and win32.


DESCRIPTION

Perform real time text detection and translation in applications such as video games. This uses Google's Vision and Translate API in order to detect text from your computer screen, translate it and overlay it on top of the detected text. 


REQUIREMENTS

See the requirements.txt
Google Credentials is needed in order to communicate with the Google API. 
Here's a link to get you started: https://cloud.google.com/docs/authentication/getting-started


USE

1. Change line 13 in real_time_OCR.py to the directory of which your Google Credentials .json file is located.

2. Run the script in cmd or your IDE console.

3. Set the dimensions of your monitor resolution.

In order to find out your resolution on windows 10, follow these instructions:

Select Start > Settings > System > Display.

Go to 'Display resolution', your monitor resolution is the 'Recommended' one.

Most common resolution is 1920 x 1080 (width x height).


4. Type in the window handle that you wish to perform OCR and translation.


VIDEO EXAMPLE

https://user-images.githubusercontent.com/56387677/126067842-05d8d4f6-6677-43b8-8458-b22aeda81579.mp4
