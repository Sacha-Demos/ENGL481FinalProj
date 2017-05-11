from sklearn import tree
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier

import numpy as np
import random

def rotate_lists(data, reverse=False):
    return list(zip(*data[::-1 if not reverse else 1]))[::-1 if reverse else 1]

def filter_by(filt):
    return lambda x: [i for i, col in enumerate(x) if col.startswith(filt)]

class classifier(object):
    def __init__(self):
        self.classifiers = [
            [RandomForestClassifier(), filter_by("stat"), "Statistics"],
            [RandomForestClassifier(), filter_by("tfidf"), "TF IDF"],
            [RandomForestClassifier(), filter_by("tonality"), "Tonality"],
            [RandomForestClassifier(), None, "All In One"]
            ]
        self.final_class = tree.DecisionTreeClassifier()

    def train(self, data, labels, attributes):
        self.labels = list(set(labels))
        ilabels = [self.labels.index(label) for label in labels]
        predicts = []
        for class_data in self.classifiers:
            model = class_data[0]
            filt = class_data[1]
            if filt:
                filt_i = filt(attributes)
                filtered_data = [[row[i] for i in filt_i] for row in data]
                class_data[1] = filt_i
            else:
                filtered_data = data
            for i, row in enumerate(filtered_data[:]):
                if not np.all(np.isfinite(row)):
                   print("tossed"),
                   print(row)
                   filtered_data.remove(row)
            model.fit(filtered_data, ilabels)
            predicts.append(model.predict(filtered_data))
        predicts = rotate_lists(predicts)
        self.final_class.fit(predicts, labels)

    def predict(self, data, return_predicts = True):
        predicts = []
        for model, filt, name in self.classifiers:
            if filt:
                filtered_data = [[row[i] for i in filt] for row in data]
            else:
                filtered_data = data
            predicts.append(model.predict(filtered_data))
        predicts = rotate_lists(predicts)
        final_ans = self.final_class.predict(predicts)
        predicted_labels = []
        for predict in predicts:
            predicted_labels.append([self.labels[col] for col in predict])
        if not return_predicts:
            return final_ans
        else:
            return (final_ans, predicted_labels)

def test(model, data, labels):
    finals, predicts = model.predict(data, return_predicts = True)
    headers = ["Actual", "Final Prediction"]
    for classy, filt, name in model.classifiers:
        headers.append(type(classy).__name__)
    with open("results.csv", "w") as f:
        f.write(", ".join(headers) + "\n")
        for label, final, predict in zip(labels, finals, predicts):
            row = [label, final] + list(predict)
            f.write(", ".join(row) + "\n")
    print("Accuracy"),
    print(sum([1. if final==label else 0. for final, label in zip(finals, labels)])/ len(labels))
    print("Accuracies :")
    for i, m in enumerate(rotate_lists(predicts, reverse=True)):
        print(model.classifiers[i][2] + " : " + type(model.classifiers[i][0]).__name__),
        acc = sum([1. if final==label else 0. for final, label in zip(m, labels)])/ len(labels)
        print("\t" + ("" if acc==1. else " ")+ "%.2f perc" % (acc*100))

filename = "feats_region.csv"
data = []
labels = []
with open(filename) as f:
    headers = [tok.strip() for tok in f.readline().split(",")]
    for l in f:
        toks = [tok.strip() for tok in l.split(",")]
        data.append([float(tok) for tok in toks[1:]])
        labels.append(toks[0])


c = classifier()
train_data = []
train_labels = []

test_data = []
test_labels = []

size = len(data)
split_ind = int(float(size * 80) / 100)

splits = range(size)
random.shuffle(splits)
for i in splits[:split_ind]:
    train_data.append(data[i])
    train_labels.append(labels[i])
for i in splits[split_ind:]:
    test_data.append(data[i])
    test_labels.append(labels[i])

c.train(train_data, train_labels, headers[1:])
test(c, test_data, test_labels)
