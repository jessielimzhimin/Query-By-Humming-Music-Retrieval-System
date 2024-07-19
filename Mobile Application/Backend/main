from flask import Flask, request, jsonify
import torch
import torch.nn as nn
from model import CustomLSTMModel
import numpy as np
import torch.nn.functional as F
import os
from model import transform_data, get_prediction
from werkzeug.utils import secure_filename
from googleapiclient.discovery import build

app = Flask(__name__)

# Define the folder to save uploaded files
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

api_key = 'YOUR OWN API KEY HERE'

def youtube_search(query, max_results=1):
    youtube = build('youtube', 'v3', developerKey=api_key)
    search_response = youtube.search().list(
        q=query,
        part='snippet',
        maxResults=max_results
    ).execute()

    videos = []
    for search_result in search_response.get('items', []):
        if search_result['id']['kind'] == 'youtube#video':
            video_data = {
                'title': search_result['snippet']['title'],
                'videoId': search_result['id']['videoId'],
                'description': search_result['snippet']['description'],
                'thumbnail': search_result['snippet']['thumbnails']['default']['url']
            }
            videos.append(video_data)
    return videos


@app.route('/upload', methods=['PUT'])
def processing_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Perform feature extraction
        combined_features = transform_data(file_path)

        #Perform Prediction
        predictions = get_prediction(combined_features)

        youtube_results = []
        for prediction in predictions:
            search_results = youtube_search(prediction)
            youtube_results.extend(search_results)
        
        # Clean up the saved file
        os.remove(file_path)

        response_data = {'youtube_results': youtube_results, 'top_5_predictions': predictions}
        print(response_data)
        return jsonify(response_data)
