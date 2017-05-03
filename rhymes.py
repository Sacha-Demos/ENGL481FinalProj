from collections import defaultdict
import itertools

import nltk
from nltk.corpus import cmudict

import lang_util


CLUSTER_MIN = .6
APPROX_MIN = 10

vowels = [u'A', u'E', u'I', u'O', u'U', u'Y']

phoneme_similarity = {}

stops = [('P', 'B'), ('T','D'), ('K', 'G')]
fricatives = [('F','V'), ('TH', 'DH'), ('S', 'Z', 'SH' , 'ZH')]
nasals = [('M', 'N'), ('NG',)]

for row in [stops, fricatives, nasals]:
    total = []
    for cross in itertools.product(*row):
        for combo in itertools.combinations(cross, 2):
            phoneme_similarity[combo] = .75
    for group in row:
        if len(group) <= 1:
            continue
        for combo in itertools.combinations(group, 2):
            phoneme_similarity[combo] = .25

phoneme_finals = {
    'S' : .25,
    'Z' : .5,
    }

cmu_dict  = cmudict.dict()

try:
    model = None
    
    def guess(word):
        global model
        if model is None:
            print("Attempting to load CMU G2P")
            import GtoP.g2p_seq2seq.g2p as g2p
            model = g2p.G2PModel("GtoP/g2p-seq2seq-cmudict")
            model.load_decode_model()
        toks = model.decode_word(word).split(" ")
        results = [[]]
        if len(toks) == 1:
            if toks[0] == '':
                return []
        for tok in toks:
            if tok[0] in vowels:
                new_res =[]
                for res in results:
                    new_res.append(res+[tok+"0"])
                    new_res.append(res+[tok+"1"])
                results = new_res
            else:
                for res in results:
                    res.append(tok)
        return results
except:
    print("Unable to find Grapheme to Phoneme CMU Library.")
    print("Try running get_GtoP.sh .")
    def guess(word):
        print("Default to null rhyme (%s)" % word)
        return []

def get_phones(word):
    if word in cmu_dict:
        return cmu_dict[word]
    return[]
    
class Rhyme(object):
    def __init__(self, word):
        self.word = word
        try:
            self.tails = get_tails(self.word)
        except:
            aprx = get_approx(self.word)
            if not aprx.keys() == []:
                item = max(aprx.items(), key=lambda x:x[1])
                if item[1] > APPROX_MIN:
                    self.tails = [item[0]]
                else:
                    print(self.word)
                    self.tails = get_tails(self.word, proncs=guess(self.word))
            else:
                self.tails = get_tails(self.word, proncs=guess(self.word))

    def __str__(self):
        lines =["Rhyme(%s){" % self.word]+ [" ".join(tail) for tail in self.tails]+["}"]
        return "\n".join(lines)
        
    def similarity(self, otherRhyme):
        if self.word == otherRhyme.word:
            return 1
        bestscore = 0
        for i in range(len(self.tails)):
            for j in range(len(otherRhyme.tails)):
                score = lang_util.similarity_score(self.tails[i],\
                                                   otherRhyme.tails[j],\
                                                   similarities=phoneme_similarity,\
                                                   finals = phoneme_finals,\
                                                   weight_func=lang_util.weight_func,\
                                                   power=2)
                if score == 1:
                    return 1
                elif score > bestscore:
                    bestscore = score
        return bestscore

tail_cache = {}
def get_tails(word, proncs=None):
    if word in tail_cache:
        return tail_cache[word]
    if proncs is None:
        try:
            proncs = cmu_dict[word]
        except:
            raise ValueError("Word(%s) not in CMUdict" % word)
    tails = set()
    for pronc in proncs:
        for i in range(1, len(pronc) + 1):
            if pronc[0 - i][0] in vowels:
                if i==1:
                    i+=1
                tails.add(tuple(pronc[0 - i:]))
                break
    tails = list(tails)
    tail_cache[word] = tails
    return tails

def get_approx(word):
    if word in cmu_dict:
        print("In dict")
    cutoff = 0
    for i in range(2, len(word) + 1):
        if word[0 - i].upper() in vowels:
            cutoff = i
            break
    while cutoff < len(word) and word[0 - cutoff].upper() in vowels:
        cutoff += 1
    word_end = word[0 - cutoff:]
    counts = defaultdict(float)
    for w in cmu_dict.keys():
        if w.endswith(word_end):
            tails = get_tails(w)
            for tail in tails:
                counts[tail] += (1/len(tails))
    return counts

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

def all_rhymes(word):
    word_scores = []
    wordR = Rhyme(word)
    for w in cmu_dict.keys():
        wR = Rhyme(w)
        score = wordR.similarity(wR)
        if score > 0:
            word_scores.append( (w, score, wR.tails) )
    return sorted(word_scores, key = lambda x:x[1])

if __name__ == "__main__":
    word = Rhyme("orange")
    print(word)


    print(Rhyme("medicine").similarity(Rhyme("medicines")))
    print(Rhyme("apple").similarity(Rhyme("banana")))

    o = Rhyme("eraser")
    l = Rhyme("stapler")
    print(o)
    print(l)
    print(o.similarity(l))
