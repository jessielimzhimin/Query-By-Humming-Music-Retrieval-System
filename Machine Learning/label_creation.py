import os

files = 'E:\\new_training\\chroma_features'
new_files = 'E:\\new_training'
song_names = os.listdir(files)
song_names.sort()

txt_open = open(os.path.join(new_files, "song_names.txt"), "x")
o = open(os.path.join(new_files, "song_names.txt"), "a")
for i in song_names:
    o.write(i)
    o.write("\n")
o.close()
