import json
import os
import sqlite3 as lite
import process
from collections import namedtuple

DB_FILE = "song_info.sqlite"

table_headers = ["Name", "Artist", "Region", "Genre", "Album", "Releaseyear"]
data_headers = ["len"]
headers = table_headers + data_headers

def create_row(file_info, data):
    file_row = [getattr(file_info, header) for header in table_headers]
    data_row = [data[header] for header in data_headers]
    return file_row + data_row

def files_to_table(file_list, file_dir, data_file):
    with open(data_file, 'w') as csv:
        csv.write(",".join(headers))
        csv.write("\n")

        for file_info in file_list:
            source_file = os.path.join(process.SONG_FILE_DIR, file_info[-1]+".txt")
            dest_file = os.path.join(file_dir, file_info[-1]+".json")
            process.maybe_process(source_file, dest_file)
            with open(dest_file) as f:
                data = json.load(f)
            row = create_row(file_info, data)
            csv.write(",".join([str(val) for val in row]))
            csv.write("\n")

def get_file_info(dbfile = DB_FILE):
    con = lite.connect(dbfile)
    
    cur = con.cursor()
    cur.execute('SELECT * FROM Complete;')
    
    Row = namedtuple('row', [col[0] for col in cur.description])
    rows = [Row(*record) for record in cur.fetchall()]
    return rows
    
if __name__ == "__main__":
    file_dir = "song_data"
    file_list = get_file_info()
    files_to_table(file_list, file_dir, "feature_data.csv")
