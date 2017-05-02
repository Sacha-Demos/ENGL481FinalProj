import json
import os
import process

import corpus_data

class FeatureSet(object):
    def __init__(self):
        self.headers = ["length", "line_lengths"]

    def prescan(self, data):
        pass
    def pack(self):
        pass
    def create_row(self, data):
        return [ data["lines"], float(sum(data["line_lengths"]))/len(data["line_lengths"]) ]

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
            
def files_to_table(file_list, file_dir, data_file, targets=["Region", "Genre"]):
    fs = FeatureSet()
    source_files = []
    dest_files = []

    for file_info in file_list:
        source_file = os.path.join(process.SONG_FILE_DIR, file_info[-2]+".txt")
        source_files.append( source_file )
        dest_file = os.path.join(file_dir, file_info[-2]+".json")
        process.maybe_process(source_file, dest_file)
        with open(dest_file) as f:
            data = json.load(f)
            fs.prescan(f)
        dest_files.append(dest_file)
    fs.pack()
    feature_files = []
    target_ind = []
    for target in targets:
        target_ind.append( corpus_data.final_headers.index(target) )
        feature_files.append( FeatureFile("feats_%s.csv" % target.lower(), [target] + fs.headers) )

    for file_info in file_list:
        with open(dest_file) as f:
            data = json.load(f)
            row = fs.create_row(data)
        for i in range(len(target_ind)):
            feature_files[i].add_row([ file_info[target_ind[i]] ] + row)

    for f in feature_files:
        f.save()

if __name__ == "__main__":
    file_dir = "song_data"
    file_list = corpus_data.get_attributes()
    files_to_table(file_list, file_dir, "feature_data.csv")
