import json
import os
import process

import corpus_data

class FeatureSet(object):
    def __init__(self):
        self.headers = ["stat_length", "stat_line_length", "stat_line_avg_phones",\
                        "stat_word_phones", "stat_word_avg_chars"]
        
    def prescan(self, data, label):
        print(label)
    def pack(self):
        pass
    def create_row(self, data):
        stat_length = data["lines"]
        stat_line_length = float(sum(data["line_lengths"]))/len(data["line_lengths"])
        phones = []
        phones_line = []
        for line in data["phones"]:
            sum_line = 0.
            for word in line:
                w_avg_phone = float(sum([len(pronc) for pronc in word])) / len(word)
                sum_line += w_avg_phone
                phones.append(w_avg_phone)
            phones_line.append(sum_line / len(line))
        word_avg_phones = sum(phones) / len(phones)
        line_avg_phones = sum(phones_line) / len(phones_line)
        word_chars = []
        for line in data["song_text"]:
            for tok in line:
                word_chars.append(len(tok))
        word_avg_chars = float(sum(word_chars)) / len(word_chars)
        return [stat_length, stat_line_length, line_avg_phones, word_avg_phones, word_avg_chars]

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

    for file_info in file_list:
        source_file = os.path.join(process.SONG_FILE_DIR, file_info[-2]+".txt")
        source_files.append( source_file )
        dest_file = os.path.join(file_dir, file_info[-2]+".json")
        process.maybe_process(source_file, dest_file)
        with open(dest_file) as f:
            data = json.load(f)
            fs.prescan(f, file_info[target_ind])
        dest_files.append(dest_file)
    fs.pack()
    feature_file = FeatureFile("feats_%s.csv" % target.lower(), [target] + fs.headers)

    for file_info in file_list:
        with open(dest_file) as f:
            data = json.load(f)
            row = fs.create_row(data)
            feature_file.add_row([ file_info[target_ind] ] + row)

    feature_file.save()

if __name__ == "__main__":
    file_dir = "song_data"
    file_list = corpus_data.get_attributes()
    files_to_table(file_list, file_dir, "feature_data.csv", "Region")
