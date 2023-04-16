import sys
import openai

openai.api_key = "YOUR_KEY"

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
    return (min(1.0, (w1 * f1 + w2 * f2) / w), 
            min(0.99, max(max(Truth_w2c(w), c1), c2)))
#NAL truth functions end

belief_prompt_start = """
Commands:
Claim(sentence) ... this relation is claimed to be true in the sentence
NegatedClaim(sentence) ... the relation is claimed to be false in the sentence
Deduce(sentence) ... the sentence which can be deduced from memory items.
Remove(sentence) ... the duplicate sentence in memory which should be removed

Capture the complete sentence meaning with code that calls the two functions.
Please make sure that the word "not" is not included in your call, just use Claim and NegatedClaim.
Also generate Deduce calls for information which can be deductively generated from Memory items.

Memory:
"""
memory={}
belief_prompt_end = """

The sentence: """

question_prompt_start = """
Please mention what content of Memory, whereby only certainty values close to 1 are "yes", and close to 0 "no".

Memory:

The question: """

question_prompt_end = """

The question: """

def promptgen(prompt_start, prompt_end):
    prompt_memory = ""
    selectedItems=[]
    memorylist = list(memory.items())
    stmsize = 20
    #find 5 newest items:
    memorylist.sort(key=lambda x: -x[1][0])
    selectedItems += memorylist[0:int(stmsize/2)]
    #find additional 5 useful items which were not already part of the newest
    memorylist.sort(key=lambda x: -x[1][1])
    idx = 0
    while len(selectedItems) < stmsize and idx < len(memorylist):
        selectedItems.append(memorylist[idx])
        idx+=1
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
        isClaim = x.startswith("Claim(")
        isRemoval = x.startswith("Remove(")
        if (isDeduction or isClaim or isRemoval) and x.endswith(")"):
            if isDeduction:
                truth = (1.0, 0.81) #TODO truth function by letting it refer to memory indices in deduce calls
            arg = x.split("(")[1].split(")")[0].replace('"','').replace("'","")
            if isRemoval:
                if arg in memory:
                    del memory[arg]
                    print(x)
                    continue
            if arg in memory and isDeduction:
                continue #deduction cannot revise currently as stamp is yet to find a solution fo
            if isDeduction or isClaim:
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
    if inp.startswith("*mem"):
        print(memory)
        continue
    question = False
    if inp.endswith("?"):
        question = True
        inp=inp[:-1]+" according to Memory?"
        send_prompt = promptgen(question_prompt_start, question_prompt_end) + inp
    else:
        send_prompt = promptgen(belief_prompt_start, belief_prompt_end) + inp
        currentTime += 1
    #print("vvvvSTART PROMPT", send_prompt, "\n^^^^END PROMPT")
    response = openai.ChatCompletion.create(
    model='gpt-3.5-turbo',
      messages=[
        {"role": "user", "content": send_prompt}],
    max_tokens=50,
    temperature=0)
    commands = response['choices'][0]['message']['content'].split("\n")
    process_commands(commands, question)
@patham9
