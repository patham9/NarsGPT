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
from Memory import *
import openai

openai.api_key = "YOUR_KEY"
attention_buffer_size = 20 #how large the system's attention buffer should be
filename = "mem.json" #the system's memory file
IncludeGPTKnowledge = False or "IncludeGPTKnowledge" in sys.argv #Whether it should be allowed to consider GPT's knowledge too
PrintInputSentence = False or "PrintInputSentence" in sys.argv
PrintTruthValues = True or "PrintTruthValues" in sys.argv
PrintMemoryUpdates = False or "PrintMemoryUpdates" in sys.argv
PrintGPTPrompt = False or "PrintGPTPrompt" in sys.argv

for x in sys.argv:
    if x.startswith("API_KEY="):
        openai.api_key = x.split("API_KEY=")[1]
(memory, currentTime, evidentalBaseID) = Memory_load(filename) #the NARS-style long-term memory

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
            Memory_digest_sentence(memory, sentence, truth, stamp, currentTime, PrintMemoryUpdates)
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
    if inp.startswith("*volume="): #TODO
        continue
    if inp.startswith("*prompt"):
        print(Memory_generate_prompt(memory, "","", attention_buffer_size))
        continue
    if inp.startswith("*memory"):
        for x in memory.items():
            print(x)
        continue
    if inp.startswith("*buffer"):
        attention_buf = Memory_attention_buffer(memory, attention_buffer_size)
        for x in attention_buf:
            print(x)
        continue
    if inp.endswith("?"):
        isQuestion = True
        send_prompt = Memory_generate_prompt(memory, question_prompt_start, "\nThe question: ", attention_buffer_size) + inp[:-1] + \
                                            (question_prompt_end_alternative if IncludeGPTKnowledge else question_prompt_end)
    else:
        isQuestion = False
        send_prompt = Memory_generate_prompt(memory, belief_prompt_start, "\nThe sentence: ", attention_buffer_size) + inp + belief_prompt_end
        currentTime += 1
    if PrintGPTPrompt: print("vvvvSTART PROMPT", send_prompt, "\n^^^^END PROMPT")
    response = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=[ {"role": "user", "content": send_prompt}], max_tokens=200, temperature=0)
    invoke_commands(response['choices'][0]['message']['content'].split("\n"), isQuestion)
    Memory_store(filename, memory, currentTime, evidentalBaseID)
