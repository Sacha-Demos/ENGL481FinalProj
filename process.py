import json
import re
import os
import numpy
import traceback

from nltk import word_tokenize
from nltk.stem.snowball import SnowballStemmer

from rhymes import Rhyme, get_phones, cluster

SONG_FILE_DIR = "song_text"
SONG_DATA_DIR = "song_data"

MODULE_FILE = __file__

stemmer = SnowballStemmer("english", ignore_stopwords=True)

def tonality(song_text):
    song_rhymes = []
    rhyme_clusters = []
    end_rhyme = []
    repeats = []
    for line in song_text:
        if len(line) == 0:
            print(line)
        if True in [w.isalnum() for w in line]:
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
    song_stems = []
    word_phone_lens = []
    text_data = text_data.decode('utf8', 'ignore')
    for line in text_data.splitlines(True):
        line = line.strip()
        if "" == line or line[0] == "[":
            continue
        line = line.lower().replace("'", "")
        toks = [tok.replace("-", "").lower() for tok in word_tokenize(line) if len(tok)!=0 and tok.isalnum()]
        if len(toks) == 0:
            continue
        phones = [get_phones(tok) for tok in toks]
        stems = [stemmer.stem(tok) for tok in toks]
        song_text.append(toks)
        song_phones.append(phones)
        song_stems.append(stems)
        for phone in phones:
            word_phone_lens.append(len(phone))
    tonality(song_text)
    return {
        "lines" : len(song_text),
        "line_lengths" : [len(line) for line in song_text],
        "song_text" : song_text,
        "avg_word_phones" : numpy.mean(word_phone_lens),
        "phones" : song_phones,
        "stemmed" : song_stems,
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

files_p = 0
files_u = 0
def maybe_process(source_path, dest_path):
    global files_p
    global files_u
    try:
        if should_update(MODULE_FILE, source_path, dest_path):
            print("Updating %s from %s. (%d / %d)" % (dest_path, source_path, files_p, files_p-files_u ))
            files_p += 1
            try:
                os.makedirs(os.path.dirname(dest_path))
            except:
                pass
            with open(source_path) as source_file,\
                 open(dest_path, "w") as dest_file:
                data = source_file.read()
                result = process(data)
                json.dump(result, dest_file)
            files_u += 1
    except Exception as e:
        traceback.print_exc()
        if os.path.exists(dest_path):
            os.remove(dest_path)
    except KeyboardInterrupt:
        if os.path.exists(dest_path):
            os.remove(dest_path)
        exit(1)
            
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
