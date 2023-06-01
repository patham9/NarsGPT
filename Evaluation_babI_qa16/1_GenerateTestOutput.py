import sys
import os
cwd = os.getcwd()
sys.path.append(cwd + "/../")
os.chdir(cwd + "/../")
from NarsGPT import *
os.chdir(cwd)
import json

lines = ""
with open("/home/tc/babI/tasks_1-20_v1-2/en-valid/qa16_train.txt") as f:
    lines = f.read().split("\n")

lastnum = -1
examples = []
example_cur = []
for line in lines:
    if line.strip() == "":
        continue
    words = line.split(" ")
    number, text = (int(words[0]), " ".join(words[1:]))
    if number < lastnum:
        examples.append(example_cur)
        example_cur = []
    example_cur.append(text)
    lastnum = number
examples.append(example_cur)

def question_and_expected_output(questionline):
    splitted = questionline.split("\t")
    return [splitted[0], splitted[1]]

examples = [[" ".join(example[0:-1])] + question_and_expected_output(example[-1]) for example in examples]

Line_Input_Output_ExpectedOutput = []
ExampleID = 1
for example in examples:
    BeliefInput, QuestionInput, expectedOutput = example
    expectedOutput = expectedOutput.strip()
    outputFromBeliefInput = AddInput(BeliefInput)
    actualOutput = AddInput(QuestionInput)
    Dic = {"ExampleID": ExampleID, "Input": BeliefInput + " " + QuestionInput, "OutputFromBeliefInput": outputFromBeliefInput,"actualOutput": actualOutput, "expectedOutput": expectedOutput}
    Line_Input_Output_ExpectedOutput.append(Dic)
    for k in Dic:
        print(k+":", Dic[k])
    print("\n")
    filename = "TestOutput.json"
    with open(filename, 'w') as f:
        json.dump(Line_Input_Output_ExpectedOutput, f)
    ExampleID += 1
    AddInput("*reset")


