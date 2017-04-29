import os
from collections import defaultdict

from nltk import word_tokenize

from rhymes import Rhyme

source_folder = "example_songs"
dest_folder = "anots"

colors = ['white', 'red', 'green', 'blue', 'orange' , 'purple', 'grey', 'dark-grey']

CLUSTER_MIN = .6

def cluster(rhyme_list):
    rhyme_dists = []
    for i in range(len(rhyme_list)):
        for j in range(i + 1, len(rhyme_list)):
            score = rhyme_list[i].similarity(rhyme_list[j])
            rhyme_dists.append( (rhyme_list[i].word, rhyme_list[j].word, score) )
    rhyme_dists.sort(key = lambda x:0 - x[-1])
    clusts = []
    for one, two, score in rhyme_dists:
        if score <= CLUSTER_MIN:
            break
        onesets = [clust for clust in clusts if one in clust]
        oneset = onesets[0] if len(onesets)>0 else [one]
        twosets = [clust for clust in clusts if two in clust]
        twoset = twosets[0] if len(twosets)>0 else [two]
        if twoset in clusts:
            clusts.remove(twoset)
        if oneset in clusts:
            clusts.remove(oneset)
        clusts.append(list(set(oneset + twoset)))
    clusters = {}
    count = 1
    for clust in clusts:
        for word in clust:
            clusters[word] = count
        count += 1
    return clusters

def notes(data, f):
    tokens = []
    rhymes = {}
    for line in data.split("\n"):
        line=line.strip()
        line_toks = []
        for tok in word_tokenize(line):
            if len(tok) == 0:
                continue
            tok = tok.lower()
            if tok in rhymes:
                tokR = rhymes[tok]
            else:
                tokR = Rhyme(tok)
                rhymes[tok] = tokR
            line_toks.append([tok, tokR])
        tokens.append(line_toks)
    rhyme_list = rhymes.values()
    clusters = cluster(rhyme_list)
    write_html(tokens, f, clusters)

def write_html(data, f, clusters={}):
    f.write("<html>")
    f.write("<head>")
    f.write("</head>")
    f.write("<body>")
    for line in data:
        for tok in line:
            word, rhyme = tok
            if word in clusters:
                color = colors[clusters[word]]
                f.write("<span style='color:%s'>%s </span>"% (color,word))
            else:
                f.write("<span>%s </span>"% word)
        f.write("<br/>")
    f.write("<br/>")
    clust_rev = defaultdict(list)
    for word, clust in clusters.items():
        clust_rev[clust].append(word)
    for clust, words in clust_rev.items():
        color = colors[clust]
        words = " ".join(words)
        f.write("<span style='color:%s'>%s </span>" % (color, words))
        f.write("<br/>")
    f.write("</body>")
    f.write("</html>")

for filename in os.listdir(source_folder):
    destfilename = filename.replace(".","_")
    with open(os.path.join(source_folder, filename)) as f:
        data=f.read()
    destfilepath = os.path.join(dest_folder, destfilename+".html")
    with open(destfilepath, 'w') as f:
        notes(data, f)
