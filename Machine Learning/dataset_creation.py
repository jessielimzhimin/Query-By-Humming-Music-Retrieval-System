import torch
import numpy as np
import pandas as pd
import os
from torch.utils.data import Dataset, DataLoader

class HybridFeaturesDataset(Dataset):
    def __init__(self, base_path_chroma, base_path_mfcc, transform=None, split='train', split_ratio=0.8):
        songs_txt = 'E:\\new_training\\song_names.txt'
        read = open(songs_txt, "r")
        names = read.read()
        song_names = names.split("\n")
        read.close
        self.base_path_chroma = base_path_chroma
        self.base_path_mfcc = base_path_mfcc
        self.transform = transform
        self.samples = []
        self.labels = {}
        for i, item in enumerate(song_names):
            self.labels[item] = i
            
        for song_name, label in self.labels.items():
            chroma_dir = os.path.join(base_path_chroma, song_name)
            mfcc_dir = os.path.join(base_path_mfcc, song_name)
            chroma_files = [f for f in os.listdir(chroma_dir) if f.endswith('.csv')]
            mfcc_files = [f for f in os.listdir(mfcc_dir) if f.endswith('.csv')]
            chroma_files.sort()
            mfcc_files.sort()
            split_index = int(len(chroma_files) * split_ratio)
            
            if split == 'train':
                selected_chroma = chroma_files[:split_index]
                selected_mfcc = mfcc_files[:split_index]
            else:  # 'valid'
                selected_chroma = chroma_files[split_index:]
                selected_mfcc = mfcc_files[split_index:]

            for chroma_file, mfcc_file in zip(selected_chroma, selected_mfcc):
                chroma_path = os.path.join(chroma_dir, chroma_file)
                mfcc_path = os.path.join(mfcc_dir, mfcc_file)
                self.samples.append((chroma_path, mfcc_path, label))

    def __len__(self):
        return len(self.samples)
  
    def __getitem__(self, idx):
        chroma_path, mfcc_path, label = self.samples[idx]
        chroma_data = pd.read_csv(chroma_path, header=None).to_numpy()
        mfcc_data = pd.read_csv(mfcc_path, header=None).to_numpy()

        # Align and pad features before concatenating
        combined_features = align_and_pad_features(chroma_data, mfcc_data)

        if self.transform:
            combined_features = self.transform(combined_features)

        return torch.tensor(combined_features, dtype=torch.float32), torch.tensor(label, dtype=torch.long)

def align_and_pad_features(chroma_data, mfcc_data, max_length=260):
    # Pad or truncate each feature array to ensure they have the same time dimension length
    chroma_padded = pad_sequences(chroma_data, max_length=max_length)
    mfcc_padded = pad_sequences(mfcc_data, max_length=max_length)
    
    # Concatenate along the feature dimension
    combined_features = np.concatenate((chroma_padded, mfcc_padded), axis=1)
    
    return combined_features

def pad_sequences(data, max_length=260):
    time_steps, features = data.shape
    
    if time_steps < max_length:
        # Pad the sequence
        padding = np.zeros((max_length - time_steps, features))
        padded_data = np.vstack((data, padding))
    elif time_steps > max_length:
        # Truncate the sequence
        padded_data = data[:max_length, :]
    else:
        padded_data = data
        
    return padded_data


# Create the training dataset
train_dataset = HybridFeaturesDataset(
    base_path_chroma='C:\\Users\\jessi\\OneDrive\\Desktop\\chroma_features,
    base_path_mfcc='C:\\Users\\jessi\\OneDrive\\Desktop\\mfcc_features',
    transform=pad_sequences,  
    split='train',
    split_ratio=0.8
)

# Create the validation dataset
valid_dataset = HybridFeaturesDataset(
    base_path_chroma='C:\\Users\\jessi\\OneDrive\\Desktop\\chroma_features',
    base_path_mfcc='C:\\Users\\jessi\\OneDrive\\Desktop\\mfcc_features',
    transform=pad_sequences,  
    split='valid',  
    split_ratio=0.8
)

# DataLoader for the training dataset
train_dataloader = DataLoader(
    train_dataset,
    batch_size=32,
    shuffle=True
)

# DataLoader for the validation dataset
valid_dataloader = DataLoader(
    valid_dataset,
    batch_size=32,
    shuffle=False
)


