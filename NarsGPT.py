"""
 * The MIT License
 *
 * Copyright 2023 Patrick Hammer.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 * """

import sys
from Truth import *
from NAL import *
from Prompts import *
import json
from os.path import exists
import openai

openai.api_key = "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"
fname = "mem.json" #the system's memory file
IncludeGPTKnowledge = False or "IncludeGPTKnowledge" in sys.argv #Whether it should be allowed to consider GPT's knowledge too
PrintInputSentence = False or "PrintInputSentence" in sys.argv
PrintTruthValues = True or "PrintTruthValues" in sys.argv
PrintMemoryUpdates = False or "PrintMemoryUpdates" in sys.argv
PrintGPTPrompt = False or "PrintGPTPrompt" in sys.argv

memory = {} #the NARS-style long-term memory
currentTime = 0
evidentalBaseID = 1
if exists(fname):
    with open(fname) as json_file:
        print("//Loaded memory content from", fname)
        (memory, currentTime, evidentalBaseID) = json.load(json_file)

def attention_buffer(attention_buf_target_size = 20):
    attention_buf=[]
    relevant_item_list = list(memory.items())
    #find attention_buf_target_size/2 newest items:
    relevant_item_list.sort(key=lambda x: -x[1][0])
    attention_buf += reversed(relevant_item_list[0:int(attention_buf_target_size/2)]) #newer comes later in prompt
    #find additional attention_buf_target_size/2 useful items which were not already part of the newest
    relevant_item_list.sort(key=lambda x: -x[1][1])
    for x in attention_buf:
        if x in relevant_item_list:
            relevant_item_list.remove(x) #so we won't select it as it is already part of mem
    i = 0
    while len(attention_buf) < attention_buf_target_size and i < len(relevant_item_list):
        attention_buf = [relevant_item_list[i]] + attention_buf
        i += 1
    return attention_buf

def generate_prompt(prompt_start, prompt_end):
    prompt_memory = ""
    buf = attention_buffer()
    if len(buf) == 0:
        prompt_memory = "EMPTY!"
    for i,x in enumerate(buf):
        (f,c) = x[1][2]
        flags = []
        if c < 0.5:
            flags.append("hypothetically")
        else:
            flags.append("knowingly")
        if f < 0.3:
            flags.append("False")
        elif f > 0.7:
            flags.append("True")
        else:
            flags.append("Contradictory")
        certainty = Truth_Expectation((f,c))
        truthtype = '"' + " ".join(flags) + '"'
        prompt_memory += f"i={i}: {x[0]}. truthtype={truthtype} certainty={certainty}\n"
    return prompt_start + prompt_memory + prompt_end

def sentence_to_memory(sentence, truth, stamp):
    global memory
    if sentence not in memory:
        memory[sentence] = (0, 0, (0.5, 0.0), [])
    if sentence in memory:
        lastUsed, useCount, truth_existing, stamp_existing = memory[sentence]
        truth_updated, stamp_updated = NAL_Revision_And_Choice(truth, stamp, truth_existing, stamp_existing)
        memory[sentence] = (currentTime, useCount+1, truth_updated, stamp_updated)
        if PrintMemoryUpdates: print("//UPDATED", sentence, memory[sentence])

def invoke_commands(cmd, userQuestion):
    global evidentalBaseID
    for x in cmd:
        truth = (1.0, 0.9)
        systemQuestion = x.startswith("Question(")
        if userQuestion or systemQuestion:
            print(x)
        isNegated = False
        if x.startswith("Negated"):
            isNegated = True
            x = x[7:]
            truth = (0.0, 0.9)
        isDeduction = x.startswith("Deduce(")
        isInduction = x.startswith("Induce(")
        isAbduction = x.startswith("Abduce(")
        isInput = x.startswith("Claim(")
        if (isDeduction or isInduction or isAbduction or isInput) and ")" in x:
            sentence = x.split("(")[1].split(")")[0].replace('"','').replace("'","").replace(".", "").lower()
            if isInput:
                stamp = [evidentalBaseID]
                evidentalBaseID += 1
            else:
                InferenceResult = NAL_Inference(memory, [x.strip().replace(".", "") for x in sentence.split(", ")], isDeduction, isInduction, isAbduction)
                if InferenceResult is not None:
                    sentence, truth, stamp, Stamp_IsOverlapping = InferenceResult
                    if Stamp_IsOverlapping: #not valid to infer due to stamp overlap
                        continue
                else:
                    continue
            sentence_to_memory(sentence, truth, stamp)
            if PrintTruthValues:
                print(f"{x} truth={truth}")
            else:
                print(x)

while True:
    try:
        inp = input().rstrip("\n")
    except:
        exit(0)
    if PrintInputSentence: print("Input:", inp)
    if inp.startswith("*volume="):
        continue
    if inp.startswith("*prompt"):
        print(generate_prompt("",""))
        continue
    if inp.startswith("*memory"):
        for x in memory.items():
            print(x)
        continue
    if inp.startswith("*buffer"):
        attention_buf = attention_buffer()
        for x in attention_buf:
            print(x)
        continue
    if inp.endswith("?"):
        isQuestion = True
        send_prompt = generate_prompt(question_prompt_start, "\nThe question: ") + inp[:-1] + (question_prompt_end_alternative if IncludeGPTKnowledge else question_prompt_end)
    else:
        isQuestion = False
        send_prompt = generate_prompt(belief_prompt_start, "\nThe sentence: ") + inp + belief_prompt_end
        currentTime += 1
    if PrintGPTPrompt: print("vvvvSTART PROMPT", send_prompt, "\n^^^^END PROMPT")
    response = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=[ {"role": "user", "content": send_prompt}], max_tokens=200, temperature=0)
    invoke_commands(response['choices'][0]['message']['content'].split("\n"), isQuestion)
    with open(fname, 'w') as f:
        json.dump((memory, currentTime, evidentalBaseID), f)
