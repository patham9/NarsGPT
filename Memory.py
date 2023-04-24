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

from os.path import exists
from NAL import *
import json

retrieved_content = []
def RetrieveQuestionContent(memory, attention_buf, inp, max_LTM_retrievals=5):
    global retrieved_content
    primed = {}
    words = [x.strip().replace("?","") for x in inp.split(" ")]
    for x in words:
        for m in list(memory.items()):
            padded = lambda w: " " + w + " "
            if padded(x) in padded(m[0]):
                if m not in attention_buf:
                    if m[0] not in primed:
                        primed[m[0]] = (1, m[1])
                    else:
                        primed[m[0]] = (primed[m[0]][0] + 1, primed[m[0]][1])
    primed = list(primed.items())
    primed.sort(key=lambda x: (-x[1][0], -Truth_Expectation(x[1][1][2]))) #sort by query match first then by truth expectation
    primed = primed[:max_LTM_retrievals]
    #for m in primed:
    #    print("//Retrieved from LTM:", m)
    primed = [(x[0],x[1][1]) for x in primed]
    retrieved_content = list(reversed(primed))

def Memory_attention_buffer(memory, attention_buffer_size, inpQuestion = None):
    attention_buf=[]
    relevant_item_list = list(memory.items())
    #find attention_buffer_size/2 newest items:
    relevant_item_list.sort(key=lambda x: -x[1][0])
    attention_buf += reversed(relevant_item_list[0:int(attention_buffer_size/2)]) #newer comes later in prompt
    #find additional attention_buffer_size/2 useful items which were not already part of the newest
    relevant_item_list.sort(key=lambda x: -x[1][1])
    for x in attention_buf:
        if x in relevant_item_list:
            relevant_item_list.remove(x) #so we won't select it as it is already part of mem
    i = 0
    while len(attention_buf) < attention_buffer_size and i < len(relevant_item_list):
        attention_buf = [relevant_item_list[i]] + attention_buf
        i += 1
    #pull in question content that is not already included
    if inpQuestion is not None:
        RetrieveQuestionContent(memory, attention_buf, inpQuestion)
    attention_buf = attention_buf + retrieved_content
    return attention_buf

def Memory_generate_prompt(memory, prompt_start, prompt_end, attention_buffer_size, inpQuestion = None):
    prompt_memory = ""
    buf = Memory_attention_buffer(memory, attention_buffer_size, inpQuestion)
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

def Memory_digest_sentence(memory, sentence, truth, stamp, currentTime, PrintMemoryUpdates):
    if sentence not in memory:
        memory[sentence] = (0, 0, (0.5, 0.0), [])
    if sentence in memory:
        lastUsed, useCount, truth_existing, stamp_existing = memory[sentence]
        truth_updated, stamp_updated = NAL_Revision_And_Choice(truth, stamp, truth_existing, stamp_existing)
        memory[sentence] = (currentTime, useCount+1, truth_updated, stamp_updated)
        if PrintMemoryUpdates: print("//UPDATED", sentence, memory[sentence])

def Memory_load(filename):
    memory = {} #the NARS-style long-term memory
    currentTime = 0
    evidentalBaseID = 1
    if exists(filename):
        with open(filename) as json_file:
            print("//Loaded memory content from", filename)
            (memory, currentTime, evidentalBaseID) = json.load(json_file)
    return (memory, currentTime, evidentalBaseID)

def Memory_store(filename, memory, currentTime, evidentalBaseID):
    with open(filename, 'w') as f:
        json.dump((memory, currentTime, evidentalBaseID), f)
