import json
import re
import os
import numpy


from nltk import word_tokenize

from rhymes import Rhyme, get_phones, cluster

SONG_FILE_DIR = "song_text"
SONG_DATA_DIR = "song_data"

MODULE_FILE = __file__

def tonality(song_text):
    song_rhymes = []
    rhyme_clusters = []
    end_rhyme = []
    repeats = []
    for line in song_text:
        song_rhymes.append([Rhyme(word) for word in line if word.isalnum()])
        rhyme_clusters.append([None for word in line if word.isalnum()])
    for i in range(len(song_rhymes) - 2):
        line_one = song_rhymes[i]
        line_two = song_rhymes[i+1]
        line_three = song_rhymes[i+2]

        end_rhyme.append(max(line_one[-1].similarity(line_two[-1]),\
                             line_two[-1].similarity(line_three[-1]),\
                             line_one[-1].similarity(line_three[-1])))
        
        rhymes = list(set([w for w in line_one + line_two + line_three]))
        clusts = cluster(rhymes)

        rhyme_line_one = [clusts[w] if w in clusts else None for w in song_text[i]]
        rhyme_line_two = [clusts[w] if w in clusts else None for w in song_text[i+1]]
        rhyme_line_three = [clusts[w] if w in clusts else None for w in song_text[i+1]]

        counts = {}
        for clust in rhyme_line_one + rhyme_line_two + rhyme_line_three:
            if not clust in counts:
                counts[clust] = 0
            counts[clust] += 1

        repeat = 0
        if counts.keys() != [None]:
            ritem = max([item for item in counts.items() if not item[0] is None], key = lambda x:x[1])
            repeat = float(ritem[1]) / (len(line_one) + len(line_two) + len(line_three))
        repeats.append(repeat)
    data = {
        "end_rhyme_mean" : numpy.mean(end_rhyme),
        "end_rhyme_stdev" : numpy.std(end_rhyme),
        "repeat_rhyme_mean" : numpy.mean(repeats),
        "repeat_rhyme_stdev" : numpy.std(repeats)
        }
    return data

def process(text_data):
    song_text = []
    song_phones = []
    word_phone_lens = []
    for line in text_data.split("\n"):
        line = line.strip()
        if "" == line or line[0] == "[":
            continue
        line = line.lower().replace("'", "")
        toks = [tok.replace("-", "").lower() for tok in word_tokenize(line) if len(tok)!=0]
        phones = [get_phones(tok) for tok in toks]
        song_text.append(toks)
        song_phones.append(phones)
        for phone in phones:
            word_phone_lens.append(len(phone))
    tonality(song_text)
    return {
        "lines" : len(song_text),
        "line_lengths" : [len(line) for line in song_text],
        "song_text" : song_text,
        "avg_word_phones" : numpy.mean(word_phone_lens),
        "phones" : phones,
        "tonality" : tonality(song_text)
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
        try:
            os.makedirs(os.path.dirname(dest_path))
        except:
            pass
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
