import os

song_headers = ["Name", "Album", "Filename", "Url"]
album_headers = ["Name", "Artist", "ReleaseYear"]
artist_headers = ["Name", "Region", "Genre"]

final_headers = ["Artist","Region", "Genre", "Album", "ReleaseYear", "Song", "Filename", "Url"]

data_dir = "corpus_data"
artist_file = os.path.join(data_dir, "Artist.csv")
album_file = os.path.join(data_dir, "Album.csv")
song_file = os.path.join(data_dir, "Song.csv")

def load_file(filename):
    data = []
    with open(filename) as f:
        headers = f.readline()
        for l in f:
            row = l.strip().split(",", len(headers))
            row = [col.strip() for col in row]
            data.append(row)
    return data

def join_tables(left, right, right_key=1):
    ldata = {}
    for row in left:
        if row[0] in ldata:
            print("pk repition: %s" % row[0])
        ldata[row[0]] = row[1:]
    data = []
    for row in right:
        if not row[right_key] in ldata:
            print("No key for %s" % row[right_key])
            continue
        new_row = [row[right_key]] + ldata[row[right_key]] + [row[i] for i in range(len(row)) if i!=right_key]
        data.append(new_row)
    return data

def get_attributes():
    ar = load_file(artist_file)
    al = load_file(album_file)
    s = load_file(song_file)
    
    sal = join_tables(al, s)
    salar = join_tables(ar, sal)
    return salar

def check_songs(s):
    data = []
    for row in s:
        if not os.path.exists(row[2]):
            data.append(row)
    return data

def diag(attributes):
    regions = set()
    genres = set()
    print("%d Records" % len(attributes))
    for row in attributes:
        regions.add(row[1])
        genres.add(row[2])
        int(row[4])
    print("%d Regions" % len(regions))
    print(list(regions))
    print("%d Genres" % len(genres))
    print(list(genres))

if __name__ == "__main__":
    s = load_file(song_file)
    missing = check_songs(s)
    if missing:
        print("missing files:")
        for m in missing:
            print(m)
    print("\nSummary:")
    attrs = get_attributes()
    diag(attrs)
    print(final_headers)
    print(attrs[0])
