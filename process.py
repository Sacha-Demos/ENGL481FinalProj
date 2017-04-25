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

file_pat = re.compile( "^(.*)\.txt$" )

def process_all(source_dir, dest_dir):
    sources = os.listdir(source_dir)
    for source in sources:
        m = file_pat.match(source)
        if not m:
            continue
        source_path = os.path.join(source_dir, source)
        dest = "%s.json" % m.group(1)
        dest_path = os.path.join(dest_dir, dest)
        if should_update(MODULE_FILE, source_path, dest_path):
            print("Updating %s from %s." % (dest, source))
            with open(source_path) as source_file,\
                 open(dest_path, "w") as dest_file:
                data = source_file.read()
                result = process(data)
                json.dump(result, dest_file)

if __name__ == "__main__":
    process_all(SONG_FILE_DIR, SONG_DATA_DIR)
