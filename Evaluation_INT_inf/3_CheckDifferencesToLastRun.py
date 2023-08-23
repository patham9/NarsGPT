import json

with open("CorrectBefore.json") as json_file:
    Before = json.load(json_file)

with open("Correct.json") as json_file:
    Now = json.load(json_file)
    
with open("IncorrectBefore.json") as json_file:
    Before += json.load(json_file)

with open("Incorrect.json") as json_file:
    Now += json.load(json_file)
    
for answer in Before:
    for answer2 in Now:
        if answer["Line"] == answer2["Line"]:
            if answer["Correct"] and answer2["Correct"] and answer["actualOutput"] != answer2["actualOutput"]:
                print("BOTH CORRECT BUT DIFFERENT:\n", answer, "\n", answer2)

for answer in Before:
    for answer2 in Now:
        if answer["Line"] == answer2["Line"]:
            if answer["Correct"] and not answer2["Correct"]:
                print("NOT CORRECT ANYMORE:\n", answer, "\n", answer2)

for answer in Before:
    for answer2 in Now:
        if answer["Line"] == answer2["Line"]:
            if not answer["Correct"] and answer2["Correct"]:
                print("CORRECT NOW:\n", answer, "\n", answer2)
