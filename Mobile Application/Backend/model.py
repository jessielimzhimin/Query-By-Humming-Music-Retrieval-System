import torch
import torch.nn as nn
import torch.nn.functional as F
import librosa
import librosa.display
import numpy as np
import pandas as pd
from torch.utils.data import Dataset, DataLoader

class CustomLSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, num_classes):
        super(CustomLSTMModel, self).__init__()
        assert num_layers >= 2, "num_layers must be at least 2 for this architecture"
        
        # Define hidden sizes for each LSTM layer
        self.hidden_size1 = 1024  # Hidden size for the first LSTM layer
        self.hidden_size2 = hidden_size  # Hidden size for the second LSTM layer (512 as given)

        # Initialize the LSTM layers with different hidden sizes
        self.lstm1 = nn.LSTM(input_size, self.hidden_size1, batch_first=True)
        self.lstm2 = nn.LSTM(input_size + self.hidden_size1, self.hidden_size2, batch_first=True)

        # Fully connected layer to map the output of the last LSTM layer to class scores
        self.fc = nn.Linear(self.hidden_size2, num_classes)

    def forward(self, x):
        # Initialize hidden and cell states for both LSTMs
        h0_1 = torch.zeros(1, x.size(0), self.hidden_size1).to(x.device)
        c0_1 = torch.zeros(1, x.size(0), self.hidden_size1).to(x.device)
        h0_2 = torch.zeros(1, x.size(0), self.hidden_size2).to(x.device)
        c0_2 = torch.zeros(1, x.size(0), self.hidden_size2).to(x.device)

        out1, _ = self.lstm1(x, (h0_1, c0_1))
        combined_input = torch.cat((x, out1), dim=2)  

        out2, _ = self.lstm2(combined_input, (h0_2, c0_2))
        final_output = self.fc(out2[:, -1, :])

        final_output = F.softmax(final_output, dim=1)
        
        return final_output
    

# Model parameters
input_size = 443
hidden_size = 1024
num_layers = 2
num_classes = 80

# Initialize the model
model = CustomLSTMModel(input_size, hidden_size, num_layers, num_classes)

# Load the model state dictionary
model_path = r'E:\\new_training\\model_state_80songs.pth'
model.load_state_dict(torch.load(model_path))
model.eval()


def load_song_labels(labels_path):
    with open(labels_path, "r") as file:
        song_names = file.read().splitlines()
    song_labels = {i: song_names[i] for i in range(len(song_names))}
    return song_labels

# Load the song labels
song_labels = load_song_labels('E:\\new_training\\music\\song_names.txt')


# Apply padding to ensure every segment has consistent size
def pad_chroma_segments(chroma_data, target_length):
    current_length = chroma_data.shape[1]
    if current_length < target_length:
        padding_size = target_length - current_length
        padding = np.zeros((chroma_data.shape[0], padding_size))
        padded_chroma = np.hstack((chroma_data, padding))
    else:
        padded_chroma = chroma_data  
    return padded_chroma

# Chroma extraction of raw audio
def chroma_extraction(y, sr = 22050, hop_length = 512, segment_duration = 10):
    chromagram = librosa.feature.chroma_stft(y=y, sr=sr, hop_length=hop_length)
    
    target_length = int(segment_duration * sr / hop_length)
    
    chroma_segments = []
    for i in range(0, chromagram.shape[1], target_length):
        segment_chromagram = chromagram[:, i:i+target_length]
                
        padded_segment_chromagram = pad_chroma_segments(segment_chromagram, target_length)
        chroma_segments.append(padded_segment_chromagram)

    return chroma_segments

def mfcc_extraction(y, sr = 22050, hop_length = 512, n_mfcc=13, segment_duration = 10):
    # Compute the MFCC feature for the entire song
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc, hop_length=hop_length)
            
    # Determine the number of frames per segment
    frames_per_segment = int(segment_duration * sr / hop_length)  

    mfcc_segments = []
    for i in range(0, mfccs.shape[1], frames_per_segment):
        segment_mfccs = mfccs[:, i:i+frames_per_segment]
        segment_mfccs_transposed = segment_mfccs.T
        mfcc_segments.append(segment_mfccs_transposed)
    
    return mfcc_segments

def pad_sequences(data, max_length=260):
    time_steps, features = data.shape
    if time_steps < max_length:
        padding = np.zeros((max_length - time_steps, features))
        padded_data = np.vstack((data, padding))
    elif time_steps > max_length:
        padded_data = data[:max_length, :]
    else:
        padded_data = data
    return padded_data

def align_and_pad_features(chroma_data, mfcc_data, max_length=260):
    chroma_padded = pad_sequences(chroma_data, max_length=max_length)
    mfcc_padded = pad_sequences(mfcc_data, max_length=max_length)
    combined_features = np.concatenate((chroma_padded, mfcc_padded), axis=1)
    return combined_features

def transform_data(file_path):
    y, sr = librosa.load(file_path, sr = 22050)
    mfcc_segments = mfcc_extraction(y, sr=sr)
    chroma_segments = chroma_extraction(y, sr=sr)
    combined_features = [align_and_pad_features(chroma, mfcc)for chroma, mfcc in zip(chroma_segments, mfcc_segments)]
    combined_features = np.array(combined_features)
    combined_features = torch.tensor(combined_features, dtype=torch.float32)
    return combined_features

def get_prediction(data_tensor):
    outputs = model(data_tensor)
    _, top_k_predictions = outputs.topk(5, 1, True, True)
    
    top_k_song_names = []
    for pred in top_k_predictions[0]:
        song_name = song_labels[pred.item()]
        top_k_song_names.append(song_name)
        
    return top_k_song_names
