#!/bin/bash

DEST="GtoP"

echo "Clone GtoP repo"
git clone https://github.com/cmusphinx/g2p-seq2seq.git $DEST

echo "Setup"
cd $DEST
echo "Makeing it importable"
touch __init__.py
echo "Getting Model"
wget -O g2p-seq2seq-cmudict.tar.gz https://sourceforge.net/projects/cmusphinx/files/G2P%20Models/g2p-seq2seq-cmudict.tar.gz/download
echo "Extracting Model"
tar xf g2p-seq2seq-cmudict.tar.gz
cd ..
