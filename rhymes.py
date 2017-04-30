from collections import defaultdict

import nltk
from nltk.corpus import cmudict

import lang_util

vowels = [u'A', u'E', u'I', u'O', u'U', u'Y']

phoneme_similarity = {
    (u'S', u'Z') : .5,
    (u'Z', u'ZH') : .5,
    (u'S', u'ZH') : .25,
    (u'T', u'D') : .25,
    (u'D', u'V') : .5,
    (u'JH', u'G') : .5,
    (u'T', u'K') : .5,
    (u'M', u'N') : .25,
    }

phoneme_finals = {
    'S' : .25,
    'Z' : .5,
    }

cmu_dict  = cmudict.dict()

try:
    print("Attempting to load CMU G2P")
    import GtoP.g2p_seq2seq.g2p as g2p

    model = g2p.G2PModel("GtoP/g2p-seq2seq-cmudict")
    model.load_decode_model()
    def guess(word):
        toks = model.decode_word(word).split(" ")
        results = [[]]
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

class Rhyme(object):
    def __init__(self, word):
        self.word = word
        try:
            self.tails = get_tails(self.word)
        except:
            aprx = get_approx(self.word)
            if not aprx.keys() == []:
                self.tails = [max(aprx.items(), key=lambda x:x[1])[0]]
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

def normalize(word):
    return word.lower()

tail_cache = {}
def get_tails(word, proncs=None):
    word = normalize(word)
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

if __name__ == "__main__":
    word = "orange"
    wordR = Rhyme(word)
    print(wordR)
    word_scores = []
    for w in cmu_dict.keys():
        wR = Rhyme(w)
        score = wordR.similarity(wR)
        if score > 0:
            word_scores.append( (w, score, wR.tails) )
    res = sorted(word_scores, key = lambda x:x[1])[-100:]
    for l in res:
        print(l)


    print(Rhyme("medicine").similarity(Rhyme("medicines")))
    print(Rhyme("apple").similarity(Rhyme("banana")))

    o = Rhyme("sicko")
    l = Rhyme("psycho")
    print(o)
    print(l)
    print(o.similarity(l))

    print(guess("boo"))
