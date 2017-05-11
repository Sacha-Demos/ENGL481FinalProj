import os

with open("corpus_data/song_data.csv") as f ,\
     open("corpus_data/Song.csv", "w") as w:
    for l in f:
        Name, Album, File, Url = [tok.strip() for tok in l.split(",")]
        txt_file = os.path.join("song_text", File)
        if os.path.exists(txt_file+".txt") or os.path.exists(txt_file+".html"):
            w.write(", ".join([Name, Album, File, Url]))
            w.write("\n")

with open("corpus_data/album_data.csv") as f ,\
     open("corpus_data/Album.csv", "w") as w:
    for l in f:
        Name, Artist, Release = [tok.strip() for tok in l.split(",")]
        w.write(", ".join([Name, Artist, Release]))
        w.write("\n")
