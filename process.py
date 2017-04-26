import json
import re
import os

SONG_FILE_DIR = "songs"
SONG_DATA_DIR = "song_data"

MODULE_FILE = __file__

def process(text_data):
    stanzas = [ [] ]
    for line in text_data.split("\n"):
        line = line.strip()
        if "" == line:
            if len( stanzas[-1] ) > 0:
                stanzas.append(list())
            continue
        toks = line.lower().split(" ")
        stanzas[-1].append(toks)
    return {
        "len" : len(text_data),
        "stanzas" : stanzas
        }

def should_update(*args):
    if len(args) < 2:
        raise ValueError
    dest = args[-1]
    if not os.path.exists(dest):
        return True
    dest = os.path.getmtime(dest)
    source = max([os.path.getmtime(dep) for dep in args[:-1]])
    return dest < source

def maybe_process(source_path, dest_path):
    if should_update(MODULE_FILE, source_path, dest_path):
        print("Updating %s from %s." % (dest_path, source_path))
        with open(source_path) as source_file,\
             open(dest_path, "w") as dest_file:
            data = source_file.read()
            result = process(data)
            json.dump(result, dest_file)
            
file_pat = re.compile( "^(.*)\.txt$" )

def process_all(source_lst, dest_dir):
    for source in source_lst:
        m = file_pat.match(os.path.basename(source))
        if not m:
            continue
        dest = "%s.json" % m.group(1)
        dest_path = os.path.join(dest_dir, dest)
        maybe_process(source, dest_path)

if __name__ == "__main__":
    all_songs = [os.path.join(SONG_FILE_DIR, filename) for filename in os.listdir(SONG_FILE_DIR)]
    process_all(all_songs, SONG_DATA_DIR)
