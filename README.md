# sevarG
<p align="center">
  <img width="512" height="512" alt="image" src="https://github.com/user-attachments/assets/14711087-0828-47ee-8c1d-64817750c58a" />
</p>
A web platform designed to provide structural improvement suggestions for architecture to strive toward accessibility for the disabled.
SevarG is inspired by Michael Graves, a disabled architect and designer whose work redefined accessibility and beauty in everyday life. His legacy reminds us that great design should empower everyone, regardless of ability.
SevarG is more than just a website that offers consulting to architects; it is also a strong example of modern technologies in community service and benefit. SevarG contains technologies such as AI Api integration and image processing models through Roboflow and Yolo.

## Process

Initially, an image is uploaded into the Api chat feature of the SevarG tab of the website. The image must be of an architecture, as the Gemini Api in SevarG has been programmed to observe the input and determine if it is disabled accessible or not. Based on the result that it outputs, the AI is prompted to display the strengths and liabilities visually with bounded boxes and is also designed to come up with design suggestions to make the situation displayed in the image more accessible for the disabled. Upon generating its design suggestions, the API is also prompted to prepare a shopping list for the user and specifically from Lowe's Home Improvements, providing links and insight into the different products that the buyer can purchase to implement the recommended design. 

## Image processing with Roboflow (Future Implementation) 

Throughout the course of designing SevarG, we also took the route of creating, training, and deploying our own training data for accessible architectural designs and certain patterns that they display. With this in mind, we compiled a vast set of images consisting of different variations of accessible architectural designs. We uploaded these images to Roboflow and manually annotated every image to prepare training data. While annotating the images, we included different object types and features such as stairs, ramps, slopes, and pavements. We later made different versions of this data to find the version that would best optimize the performance of the yolov8 model that would eventually be conducting scans on images upon being trained with our data. These augmentations included changing hue, exposure, greyscale, color contrast, cropping, and flipping images. Later, we deployed our training dataset for algorithmic use and API integration. This segment of the project is intended to be a feature added to SevarG, looking forward. 

## Sources

Some sources we used throughout our process are as follows: 

Google Gemini API: https://ai.google.dev/

30 Seconds of Code: https://www.30secondsofcode.org/

Claude: https://claude.ai/

Fast Api: https://fastapi.tiangolo.com/

Python-dotenv: https://pypi.org/project/python-dotenv/

Roboflow: https://roboflow.com/


 
