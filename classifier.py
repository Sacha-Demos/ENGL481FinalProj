from sklearn import tree
from sklearn.neural_network import MLPClassifier

def rotate_lists(data, reverse=False):
    return zip(*data[::-1 if not reverse else 1])[::-1 if reverse else 1]

class classifier(object):
    def __init__(self):
        self.classifiers = [
            tree.DecisionTreeClassifier()
            ]
        self.final_class = tree.DecisionTreeClassifier()

    def train(self, data, labels):
        self.labels = list(set(labels))
        ilabels = [self.labels.index(label) for label in labels]
        predicts = []
        for model in self.classifiers:
            model.fit(data, ilabels)
            predicts.append(model.predict(data))
        predicts = rotate_lists(predicts)
        self.final_class.fit(predicts, labels)

    def predict(self, data, return_predicts = True):
        predicts = []
        for model in self.classifiers:
            predicts.append(model.predict(data))
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
    for classy in model.classifiers:
        headers.append(type(classy).__name__)
    with open("results.csv", "w") as f:
        f.write(", ".join(headers) + "\n")
        for label, final, predict in zip(labels, finals, predicts):
            row = [label, final] + list(predict)
            f.write(", ".join(row) + "\n")
    print("Accuracy"),
    print(sum([1. if final==label else 0. for final, label in zip(finals, labels)])/ len(labels))
    print("Accuracies")
    for m in rotate_lists(predicts, reverse=True):
        print(sum([1. if final==label else 0. for final, label in zip(m, labels)])/ len(labels))
        

filename = "feats_region.csv"
data = []
labels = []
with open(filename) as f:
    f.readline()
    for l in f:
        toks = [tok.strip() for tok in l.split(",")]
        data.append(toks[1:])
        labels.append(toks[0])
c = classifier()
c.train(data, labels)
test(c, data, labels)
