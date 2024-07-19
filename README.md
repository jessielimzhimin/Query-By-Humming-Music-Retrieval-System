# Query By Humming Music Retrieval System

## Description

Query By Humming Music Retrieval System is a mobile application that allows users to record a humming input and predict songs based on the hummed melody. The system utilizes machine learning techniques for music retrieval and integrates YouTube API for playing the predicted songs.

## Features

- **Humming Input:** Record and process hummed melodies to identify songs.
- **Machine Learning Model:** Utilizes an LSTM-based model for accurate song prediction.
- **YouTube Integration:** Plays predicted songs directly from YouTube.
- **User Interface:** Built with Flutter for a smooth and responsive user experience.
- **Backend Processing:** Flask-based backend to handle feature extraction and model inference.

## Technologies Used

- **Frontend:** Flutter
- **Backend:** Flask
- **Machine Learning Model:** LSTM
- **API Integration:** YouTube API

## Folder Structure

### 1. Feature Extraction

This folder contains code for extracting audio features such as MFCC and chroma, which are used in the machine learning model to predict songs.

- `mfcc_extraction.py`: Code for extracting Mel-Frequency Cepstral Coefficients (MFCC) from audio files.
- `chroma_extraction.py`: Code for extracting chroma features from audio files.

### 2. Machine Learning

This folder contains code for dataset creation, label generation, and the training and evaluation of the LSTM model.

- `dataset_creation.py`: Jupyter notebook for creating the dataset from audio files.
- `label_creation.py`: Script for generating labels for the dataset.
- `lstm_training_evaluation.ipynb`: Jupyter notebook for training and evaluating the LSTM model.

### 3. UI (User Interface)

This folder contains the code for the mobile application's user interface, built using Flutter.

- `ui_code.dart`: Main UI code for the Flutter application. Contains the logic for the recording page, processing page, and results page.

### 4. Backend

This folder contains the backend code for handling feature extraction, model inference, and serving the API.

- `model.py`: Contains the machine learning model implementation, including loading the trained model and making predictions.
- `main.py`: Main Flask application code that sets up the API endpoints for recording, processing, and predicting songs.

## UI of Recording and Uploading Humming Inputs Page
![image](https://github.com/user-attachments/assets/768e6437-249a-40ae-81ff-c0cbfcae83c3)

## UI of Processing Page
![image](https://github.com/user-attachments/assets/a1aab353-f334-434b-bf96-9e39b69721ee)

## UI of Results Page
![image](https://github.com/user-attachments/assets/0df2fb06-9b07-45f1-b4fd-81363cfeb26a)

## Dataset
Kaggle: https://www.kaggle.com/datasets/limzhiminjessie/query-by-humming-qbh-audio-dataset/data

## Contributors
- [Jessie Lim Zhi Min](https://github.com/jessielimzhimin)
