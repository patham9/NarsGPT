import sys
import openai

openai.api_key = "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"

#NAL truth functions
def Truth_w2c(w):
    return w / (w + 1.0)

def Truth_c2w(c):
    return c / (1.0 - c)

def Truth_Expectation(v):
    return (v[1] * (v[0] - 0.5) + 0.5)

def Truth_Negation(v):
    return (1-v[0], v[1])

def Truth_Revision(v1, v2):
    (f1, c1) = v1
    (f2, c2) = v2
    w1 = Truth_c2w(c1)
    w2 = Truth_c2w(c2)
    w = w1 + w2
    if w == 0:
        return (0.5, 0.0)
    return (min(1.0, (w1 * f1 + w2 * f2) / w), 
            min(0.99, max(max(Truth_w2c(w), c1), c2)))

def Truth_Deduction(v1, v2):
    (f1, c1) = v1
    (f2, c2) = v2
    return (f1*f2, f1*f2*c1*c2)
#NAL truth functions end

belief_prompt_start = """
Commands:
Input(sentence) ... this relation is true in the sentence
NegatedInput(sentence) ... the relation is claimed to be false in the sentence
Deduce(premise1,premise2,conclusion) ... the sentence which can be deduced from memory items.

Capture the complete sentence meaning with code that calls the two functions.
Please make sure that the word "not" is not included in your call, just use Claim and NegatedClaim.
Also generate Deduce calls for information which can be deductively generated from Memory items.

Memory:
"""
memory={}
belief_prompt_end = """

The sentence: """

question_prompt_start = """
Mention concrete memory contents with certainty values.
Use the minimum involved certainty value.

Memory:
"""

question_prompt_end = """

The question: """

def workingmemory():
    selectedItems=[]
    memory_candidates_list = [x for x in list(memory.items()) if Truth_Expectation(x[1][2]) > 0.6]
    stmsize = 20
    #find 5 newest items:
    memory_candidates_list.sort(key=lambda x: -x[1][0])
    selectedItems += memory_candidates_list[0:int(stmsize/2)]
    #find additional 5 useful items which were not already part of the newest
    memory_candidates_list.sort(key=lambda x: -x[1][1])
    for x in selectedItems:
        if x in memory_candidates_list:
            memory_candidates_list.remove(x) #so we won't select it as it is already part of mem
    idx = 0
    while len(selectedItems) < stmsize and idx < len(memory_candidates_list):
        selectedItems.append(memory_candidates_list[idx])
        idx+=1
    return selectedItems

def promptgen(prompt_start, prompt_end):
    prompt_memory = ""
    selectedItems = workingmemory()
    for i,x in enumerate(selectedItems):
        certainty = Truth_Expectation(x[1][2])
        prompt_memory += f"i={i}: {x[0]}. certainty={certainty}\n"
    return prompt_start + prompt_memory + prompt_end

currentTime = 0
def process_commands(cmd, question):
    global memory
    for x in cmd:
        truth = (1.0, 0.9)
        if question:
            print(x)
        isNegated = False
        if x.startswith("Negated"):
            isNegated = True
            x = x[7:]
            truth = (0.0, 0.9)
        isDeduction = x.startswith("Deduce(")
        isInput = x.startswith("Input(")
        if (isDeduction or isInput) and x.endswith(")"):
            arg = x.split("(")[1].split(")")[0].replace('"','').replace("'","").replace(".", "").lower()
            if isDeduction:
                statements = [x.strip().replace(".", "") for x in arg.split(", ")]
                if len(statements) != 3:
                    continue
                if statements[0] not in memory or statements[1] not in memory:
                    continue
                truth = Truth_Deduction(memory[statements[0]][2], memory[statements[1]][2])
                arg = statements[2] #the conclusion is to pbe put to memory
            if arg in memory and isDeduction:
                continue #deduction cannot revise currently as stamp is yet to find a solution fo
            if isDeduction or isInput:
                if isNegated:
                    print("Neg"+x)
                else:
                    print(x)
            if arg not in memory:
                memory[arg] = (0, 0, (0.5, 0.0))
            if arg in memory:
                lastUsed, useCount, TV = memory[arg]
                memory[arg] = (currentTime, useCount+1, Truth_Revision(TV, truth))

while True:
    try:
        inp = input().rstrip("\n")
    except:
        exit(0)
    if inp.startswith("*ltm"):
        for x in memory.items():
            print(x)
        continue
    if inp.startswith("*wm"):
        wm = workingmemory()
        for x in wm:
            print(x)
        continue
    question = False
    if inp.endswith("?"):
        question = True
        inp=inp[:-1]+" according to Memory?"
        send_prompt = promptgen(question_prompt_start, question_prompt_end) + inp
    else:
        send_prompt = promptgen(belief_prompt_start, belief_prompt_end) + inp + ". And deduce what you can!"
        currentTime += 1
    #print("vvvvSTART PROMPT", send_prompt, "\n^^^^END PROMPT")
    response = openai.ChatCompletion.create(
    model='gpt-3.5-turbo',
      messages=[
        {"role": "user", "content": send_prompt}],
    max_tokens=100,
    temperature=0)
    commands = response['choices'][0]['message']['content'].split("\n")
    process_commands(commands, question)
