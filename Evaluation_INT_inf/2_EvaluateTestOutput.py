import json
import openai
import time
import sys

for x in sys.argv:
    if x.startswith("API_KEY="):
        openai.api_key = x.split("API_KEY=")[1]

with open("../TestOutput.json") as json_file:
    ListOfDicts, _ = json.load(json_file)

# {"Line": Line, "Input": Input, "actualOutput": actualOutput, "expectedOutput": expectedOutput}
Questions = []
for D in ListOfDicts:
    Line = D["Line"]
    Input = D["Input"]
    actualOutput = D["actualOutput"]
    expectedOutput = D["expectedOutput"]
    if expectedOutput != "" and len(D["expectedOutput"].split("/")) <= 1: #no questions about Aigo's innate time handling
        Questions.append(D)
    
PROMPT = """Does the actual output contain the asked information answered in the expected output?
The question: _QUESTION_
The actual output: _ACTUAL_OUTPUT_
The expected output: _EXPECTED_OUTPUT_
Please answer yes/no only!"""

Correct = []
Incorrect = []
for D in Questions:
    Line = D["Line"]
    Input = D["Input"]
    actualOutput = D["actualOutput"]
    expectedOutput = D["expectedOutput"]
    send_prompt = PROMPT.replace("_QUESTION_", Input).replace("_ACTUAL_OUTPUT_",actualOutput).replace("_EXPECTED_OUTPUT_",expectedOutput)
    print(send_prompt)
    while True:
        try:                                            #'gpt-4'
            response = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=[ {"role": "user", "content": send_prompt}], max_tokens=200, temperature=0)
            ret = response['choices'][0]['message']['content']
        except:
            print("Error: API call failed, will try repeating it in 10 seconds!")
            time.sleep(10) #wait 10 seconds
            continue
        break
    YES = "yes" in ret.lower()
    D["Correct"] = YES
    print("Correct?", YES)
    if YES:
        Correct.append(D)
    else:
        Incorrect.append(D)
    scores = {"Correct": len(Correct), "Incorrect": len(Incorrect), "Ratio" : float(len(Correct)) / float(len(Correct)+len(Incorrect))}
    print("So far:", scores)
    with open("Correct.json", 'w') as f:
        json.dump(Correct, f)
    with open("Incorrect.json", 'w') as f:
        json.dump(Incorrect, f)
    with open("Scores.json", 'w') as f:
        json.dump(scores, f)
