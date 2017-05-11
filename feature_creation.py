import json
import os
import process
import math
from nltk import FreqDist, RegexpTokenizer
from nltk.corpus import stopwords

import corpus_data

stop = set(stopwords.words('english'))

TF_IDF_COUNT = 100

class FeatureSet(object):
    def __init__(self):
        self.headers = ["stat_length", "stat_line_length", "stat_line_avg_phones",\
                        "stat_word_phones", "stat_word_avg_chars", "tonality_end_rhyme_mean",\
                        "tonality_end_rhyme_stdev", "tonality_repeat_rhyme_mean", "tonality_repeat_rhyme_stdev"
        ]
        self.distributions = {}
        self.total_distribution = {}
        self.number_of_files = 0
        self.document_frequencies = {}

    def get_freq(self, data):
        tokens = []
        for line in data['stemmed']:
            tokens += line

        # Hack to get rid of punctuation tokens
        tokenizer = RegexpTokenizer(r'\w+')
        tokens = tokenizer.tokenize((' ').join(tokens))

        return FreqDist(tokens)
    def prescan(self, data, label):
        dist = self.get_freq(data)

        if label not in self.distributions.keys():
            self.distributions[label] = {}
        
        for key in dist.keys():
            if key in stop:
                continue
            if key not in self.distributions[label].keys():
                self.distributions[label][key] = 0
            if key not in self.document_frequencies.keys():
                self.document_frequencies[key] = 0
            self.distributions[label][key] += dist[key]
            self.document_frequencies[key] += 1

        self.number_of_files += 1

    def pack(self):
        # Make overall distribution
        for dist in self.distributions.keys():
            for key in self.distributions[dist].keys():
                if key not in self.total_distribution:
                    self.total_distribution[key] = 0
                self.total_distribution[key] += self.distributions[dist][key]

        # Find top word for each tag
        for dist in self.distributions.keys():
            dist_word_count = sum(self.distributions[dist].values())
            idf_values = {}
            for key in self.distributions[dist].keys():
                tf = float(self.distributions[dist][key])/dist_word_count
                idf = math.log(float(self.number_of_files)/(1 + self.document_frequencies[key]))
                idf_values[key] = tf * idf

            print("Top words for " + dist)
            for key in sorted(idf_values, key=idf_values.get, reverse=True)[:TF_IDF_COUNT]:
                print(key + " - " + str(idf_values[key]))

        good_words = set()
        for label in self.distributions.keys():
            topwords = sorted(self.distributions[label], key=self.distributions[label].get, reverse=True)[:TF_IDF_COUNT]
            for w in topwords:
                good_words.add(w)
        self.tf_idf_features = list(good_words)
        for w in self.tf_idf_features:
            self.headers.append("tfidf_"+w)
    
    def create_row(self, data):
        stat_length = data["lines"]
        stat_line_length = float(sum(data["line_lengths"])) / max(len(data["line_lengths"]), 1)
        phones = []
        phones_line = []
        for line in data["phones"]:
            sum_line = 0.
            for word in line:
                if len(word) > 0:
                    w_avg_phone = float(sum([len(pronc) for pronc in word])) / len(word)
                    sum_line += w_avg_phone
                    phones.append(w_avg_phone)
            phones_line.append((sum_line / len(line)) if len(line) else 0)
        word_avg_phones = (sum(phones) / len(phones)) if len(phones) else 0
        line_avg_phones = (sum(phones_line) / len(phones_line)) if len(phones_line) else 0
        word_chars = []
        for line in data["song_text"]:
            for tok in line:
                word_chars.append(len(tok))
        word_avg_chars = (float(sum(word_chars)) / len(word_chars)) if len(word_chars) else 0

        stats = [stat_length, stat_line_length, line_avg_phones, word_avg_phones, word_avg_chars]
        
        tonality = [data["tonality"][key] for key in ["end_rhyme_mean", "end_rhyme_stdev", "repeat_rhyme_mean", "repeat_rhyme_stdev"]]
        
        dist = self.get_freq(data)
        tfidf = [dist[w] for w in self.tf_idf_features]
        return stats  + tonality + tfidf

class FeatureFile(object):
    def __init__(self, filename, headers):
        self.filename = filename
        self.headers = headers
        self.data = []
    def add_row(self, row):
        self.data.append(row)
    def save(self):
        with open(self.filename, 'w') as f:
            line = ", ".join([str(col) for col in self.headers])+"\n"
            f.write(line)
            for row in self.data:
                line = ", ".join([str(col) for col in row])+"\n"
                f.write(line)

def files_to_table(file_list, file_dir, data_file, target):
    fs = FeatureSet()
    source_files = []
    dest_files = []

    target_ind = corpus_data.final_headers.index(target)

    print("Updating Files:")
    for file_info in file_list:
        source_file = os.path.join(process.SONG_FILE_DIR, file_info[-2]+".txt")
        if not os.path.exists(source_file):
            source_file = os.path.join(process.SONG_FILE_DIR, file_info[-2]+".html")
        source_files.append( source_file )
        dest_file = os.path.join(file_dir, file_info[-2]+".json")
        process.maybe_process(source_file, dest_file)
        if not os.path.exists(dest_file):
            continue
        with open(dest_file) as f:
            data = json.load(f)
            fs.prescan(data, file_info[target_ind])
        dest_files.append(dest_file)
    fs.pack()
    feature_file = FeatureFile("feats_%s.csv" % target.lower(), [target] + fs.headers)

    print("Vectorizing")
    for file_info in file_list:
        dest_file = os.path.join(file_dir, file_info[-2]+".json")
        if not os.path.exists(dest_file):
            continue
        with open(dest_file) as f:
            data = json.load(f)
            row = fs.create_row(data)
            feature_file.add_row([ file_info[target_ind] ] + row)

    feature_file.save()

if __name__ == "__main__":
    file_dir = "song_data"
    file_list = corpus_data.get_attributes()
    files_to_table(file_list, file_dir, "feature_data.csv", "Region")
