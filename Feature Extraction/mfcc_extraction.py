import librosa
import librosa.display
import numpy as np
import os
import pandas as pd

def extract_and_save_mfcc_features(base_folder_path, output_base_path, sr=22050, hop_length=512, n_mfcc=13, segment_duration=10):
    # Check if the base folder exists
    if not os.path.exists(base_folder_path):
        print(f"Base folder {base_folder_path} does not exist.")
        return
    
    # Create a base output directory for MFCC features
    os.makedirs(output_base_path, exist_ok=True)
    
    # List all subfolders (each subfolder represents a song)
    song_folders = [d for d in os.listdir(base_folder_path) if os.path.isdir(os.path.join(base_folder_path, d))]
    
    for song_folder in song_folders:
        song_folder_path = os.path.join(base_folder_path, song_folder)
        
        # Output directory for the current song's MFCC features
        song_output_dir = os.path.join(output_base_path, song_folder)
        
        os.makedirs(song_output_dir, exist_ok=True)
        
        # Get all audio files in the song folder
        audio_files = [f for f in os.listdir(song_folder_path) if os.path.isfile(os.path.join(song_folder_path, f))]
        
        for audio_file in audio_files:
            audio_path = os.path.join(song_folder_path, audio_file)
            
            # Load the audio file
            y, sr = librosa.load(audio_path, sr=sr)
            
            # Compute the MFCC feature for the entire song
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc, hop_length=hop_length)
            
            # Determine the number of frames per segment
            frames_per_segment = int(segment_duration * sr / hop_length)
            
            # Process each segment
            for i in range(0, mfccs.shape[1], frames_per_segment):
                segment_mfccs = mfccs[:, i:i+frames_per_segment]
                
                # Transpose the MFCC segment to save coefficients in columns
                segment_mfccs_transposed = segment_mfccs.T
                
                # Save to CSV
                csv_filename = f"{os.path.splitext(audio_file)[0]}_segment_h_{i//frames_per_segment}.csv"
                np.savetxt(os.path.join(song_output_dir, csv_filename), segment_mfccs_transposed, delimiter=",")

base_folder_path = 'E:\\new_training\\temp'
output_base_path = 'E:\\new_training\\temp\\mfcc_features'
extract_and_save_mfcc_features(base_folder_path, output_base_path)
