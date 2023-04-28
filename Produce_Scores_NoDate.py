import json


with open("Correct.json") as json_file:
    DCorrect = json.load(json_file)
with open("Incorrect.json") as json_file:
    DIncorrect = json.load(json_file)

Correct = []
for D in DCorrect:
    if len(D["expectedOutput"].split("/")) <= 1:
        Correct.append(D)
Incorrect = []
for D in DIncorrect:
    if len(D["expectedOutput"].split("/")) <= 1:
        Incorrect.append(D)

All = len(Correct) + len(Incorrect)
scores = {"Correct": len(Correct), "Incorrect": len(Incorrect), "Ratio" : float(len(Correct)) / float(All)}
with open("scores_NoDate.json", 'w') as f:
    json.dump(scores, f)
