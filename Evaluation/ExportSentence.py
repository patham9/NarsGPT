from NarsGPT import *
import json

Line_Input_Output_ExpectedOutput = []
Line = 1
while True:
    try:
        line = input()
    except EOFError:
        #print(NarsGPT_AddInput("where is the cat?"))
        exit(0)
    parts = ",".join(line.split(",")[1:]).split(",,,,,,")
    Input, expectedOutput = parts
    Input = Input.strip()
    expectedOutput = expectedOutput.strip()
    if expectedOutput != "":
        if not Input.endswith("?"):
            Input += "?"
    actualOutput = NarsGPT_AddInput(Input)
    Dic = {"Line": Line, "Input": Input, "actualOutput": actualOutput, "expectedOutput": expectedOutput}
    Line_Input_Output_ExpectedOutput.append(Dic)
    for k in Dic:
        print(k+":", Dic[k])
    print("\n")
    filename = "OUT.json"
    with open(filename, 'w') as f:
        json.dump((Line_Input_Output_ExpectedOutput, currentTime), f)
    Line += 1


