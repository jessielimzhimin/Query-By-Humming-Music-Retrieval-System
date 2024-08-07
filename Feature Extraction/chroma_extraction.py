import librosa
import librosa.display
import numpy as np
import os
import pandas as pd

# Add paddings to the chroma segments to ensure same size
def pad_chroma_segments(chroma_data, target_length):
    current_length = chroma_data.shape[1]
    if current_length < target_length:
        padding_size = target_length - current_length
        padding = np.zeros((chroma_data.shape[0], padding_size))
        padded_chroma = np.hstack((chroma_data, padding))
    else:
        padded_chroma = chroma_data  # No padding needed if current_length >= target_length
    return padded_chroma
    
def extract_and_save_chroma_features(base_folder_path, output_base_path, sr=22050, hop_length=512, segment_duration=10):
    if not os.path.exists(base_folder_path):
        print(f"Base folder {base_folder_path} does not exist.")
        return
    
    os.makedirs(output_base_path, exist_ok=True)
    
    song_folders = [d for d in os.listdir(base_folder_path) if os.path.isdir(os.path.join(base_folder_path, d))]
    
    # Determine the target length for padding based on the segment duration
    target_length = int(segment_duration * sr / hop_length)
    
    for song_folder in song_folders:
        song_folder_path = os.path.join(base_folder_path, song_folder)
        song_output_dir = os.path.join(output_base_path, song_folder)
        os.makedirs(song_output_dir, exist_ok=True)
        
        audio_files = [f for f in os.listdir(song_folder_path) if os.path.isfile(os.path.join(song_folder_path, f))]
        
        for audio_file in audio_files:
            audio_path = os.path.join(song_folder_path, audio_file)
            y, sr = librosa.load(audio_path, sr=sr)
            chromagram = librosa.feature.chroma_stft(y=y, sr=sr, hop_length=hop_length)
            
            for i in range(0, chromagram.shape[1], target_length):
                segment_chromagram = chromagram[:, i:i+target_length]
                
                # Apply padding to each segment to ensure consistent size
                padded_segment_chromagram = pad_chroma_segments(segment_chromagram, target_length)

                # Save to CSV
                csv_filename = f"{os.path.splitext(audio_file)[0]}_segment_h_{i//target_length}.csv"
                np.savetxt(os.path.join(song_output_dir, csv_filename), padded_segment_chromagram, delimiter=",")
                

base_folder_path = 'E:\\new_training\\temp'  # Path to the directory containing song folders
output_base_path = 'E:\\new_training\\temp\\chroma_features'  # Path to the base directory where you want to store all Chroma features
extract_and_save_chroma_features(base_folder_path, output_base_path)
