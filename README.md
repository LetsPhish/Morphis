# Morphis DeepFake Project

## Overview
**Morphis** is an advanced video conferencing application that demonstrates real-time face swapping using deepfake technology. This project utilizes InsightFace for face detection and face swapping, offering a GPU-optimized experience where available, or fallback to CPU processing. Built with PyQt5, the application provides a clean, user-friendly interface that displays the live video feed, with an option to toggle face swapping in real-time.

## Key Features
- **Real-time Face Swapping**: Use deepfake technology to swap faces in a live video feed.
- **GPU Support**: Automatically detects GPU availability and utilizes it for faster processing when possible.
- **Intuitive UI**: Built with PyQt5, offering easy controls for toggling face swap and GPU status.
- **Default Face Detection**: Preloads a default image for face swapping, with verification to ensure the image contains a detectable face.

## Future Enhancements
We are actively working on adding more advanced features, including:
- **Live Voice Cloning**: In addition to face-swapping, future versions will support real-time voice cloning, allowing for more immersive deepfake experiences.
- **Enhanced UI and Controls**: Improved usability and additional settings for fine-tuning the deepfake output.
- **Additional Model Support**: Experimenting with different face and voice models to expand compatibility and enhance output quality.

## Requirements
- Python 3.x
- [InsightFace](https://github.com/deepinsight/insightface)
- PyQt5
- OpenCV
- ONNX Runtime (for GPU support)

## Installation
Clone the repository and install the dependencies:

```bash
git clone https://github.com/yourusername/Morphis-Ultimate-DeepFake-Project.git
cd Morphis-Ultimate-DeepFake-Project
pip install -r requirements.txt
```

## Model Download
This project requires the `inswapper_128.onnx` model file for face swapping. Please download the model and place it in the following directory:

```plaintext
src/inswapper_128.onnx
```

## Changing the Deepfake Face
You can customize the target face used for deepfake swapping by replacing the default image at:

```plaintext
assets/face.jpg
```
