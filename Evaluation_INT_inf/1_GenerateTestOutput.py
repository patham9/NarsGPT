import sys
import os
with open("INT_Inf_benchmarkTest.csv") as f:
    lines = f.read().split("\n")
cwd = os.getcwd()
sys.path.append(cwd + "/../")
os.chdir(cwd + "/../")
from NarsGPT import *
os.chdir(cwd)
import json

Line_Input_Output_ExpectedOutput = []
Line = 1
for line in lines:
    parts = ",".join(line.split(",")[1:]).split(",,,,,,")
    try:
        Input, expectedOutput = parts
    except:
        continue
    Input = Input.strip()
    expectedOutput = expectedOutput.strip()
    if expectedOutput != "":
        if not Input.endswith("?"):
            Input += "?"
    actualOutput = AddInput(Input, Print=False, PrintInputSentenceOverride=True, PrintInputSentenceOverrideValue=True)["GPT_Answer"]
    Dic = {"Line": Line, "Input": Input, "actualOutput": actualOutput, "expectedOutput": expectedOutput}
    Line_Input_Output_ExpectedOutput.append(Dic)
    for k in Dic:
        print(k+":", Dic[k])
    print("\n")
    filename = "TestOutput.json"
    with open(filename, 'w') as f:
        json.dump((Line_Input_Output_ExpectedOutput, currentTime), f)
    Line += 1


