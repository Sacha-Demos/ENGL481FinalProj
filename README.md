# ENGL481FinalProj

# File Structure:

* corpus_data/ : Corpus data files.
* corpus_data.py : Python module for loading corpus data.

* song_text/ : Song lyric text files.
* song_data/ : Song JSON data files.
* process.py : Creates JSON files from song text files.

* rhyme.py, lang_util.py : Rhyme scoring functions. 
* feature_creation.py : Create feature set files from json files and corpus data.

* classifier.py : Trains and tests a classifier.

* anots/ : HTML with rhyme clusters highlighted.
* notes.py : generate HTML anotations.

* scape.py : HTML scraper.

* get_GtoP.sh : bash script to download CMU Grapheme to Phoneme and trained model.
* GtoP/ : folder generated from script.



# Install GtoP
Run get_GtoP.sh or install manually.

# To run train/test:
python feature_creation.py

python classifier.py