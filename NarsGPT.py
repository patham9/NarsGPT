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
import time
from Prompts import *
from Memory import *
from Control import *
import openai

openai.api_key = "YOUR_KEY"
relevantViewSize = 30      #how many relevant (judged by statement embedding) ONA memory items GPT can see
recentViewSize = 10        #how many recent (judged by lastUsed) ONA memory items GPT can see
eternalizationDistance = 3  #how long items are treated as events before contributing to generic belief evidence in long-term memory
filename = "mem.json" #the system's memory file
IncludeGPTKnowledge = False or "IncludeGPTKnowledge" in sys.argv #Whether it should be allowed to consider GPT's knowledge too
PrintInputSentence = True and "NoPrintInputSentence" not in sys.argv
PrintTruthValues = True and "NoPrintTruthValues" not in sys.argv
PrintMemoryUpdates = False or "PrintMemoryUpdates" in sys.argv
PrintGPTPrompt = False or "PrintGPTPrompt" in sys.argv
TimeHandling = True and "NoTimeHandling" not in sys.argv

for x in sys.argv:
    if x.startswith("API_KEY="):
        openai.api_key = x.split("API_KEY=")[1]
(memory, currentTime, evidentalBaseID) = Memory_load(filename) #the NARS-style long-term memory


def PromptProcess(inp, send_prompt, isQuestion):
    global evidentalBaseID
    if PrintGPTPrompt: print("vvvvSTART PROMPT", send_prompt, "\n^^^^END PROMPT")
    while True:
        try:
            response = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=[ {"role": "user", "content": send_prompt}], max_tokens=200, temperature=0)
            commands = response['choices'][0]['message']['content'].split("\n")
        except:
            print("Error: API call failed, will try repeating it in 10 seconds!")
            time.sleep(10) #wait 10 seconds
            continue
        break
    evidentalBaseID = Control_cycle(inp, memory, commands, isQuestion, currentTime, evidentalBaseID, PrintMemoryUpdates, PrintTruthValues, TimeHandling)
    return "\n".join(commands)

def NarsGPT_AddInput(inp):
    global currentTime
    RET_ANSWER = ""
    if PrintInputSentence: print("Input:", inp)
    if inp.startswith("*volume="): #TODO
        return RET_ANSWER
    if inp.startswith("*prompt"):
        if inp.endswith("?"):
            print(Memory_generate_prompt(currentTime, memory, "","", relevantViewSize, recentViewSize, inp[:-1].split("*prompt=")[1])[1])
        else:
            print(Memory_generate_prompt(currentTime, memory, "","", relevantViewSize, recentViewSize)[1])
        return RET_ANSWER
    if inp.startswith("*memory"):
        for x in memory.items():
            print(x[0], x[1][:-1])
        return RET_ANSWER
    if inp.startswith("*buffer"):
        if inp.endswith("?"):
            attention_buf = Memory_generate_prompt(currentTime, memory, "","", relevantViewSize, recentViewSize, inp[:-1].split("*buffer=")[1])[0]
            for x in attention_buf:
                print(x[0], x[1][:-1])
        else:
            attention_buf = Memory_generate_prompt(currentTime, memory, "","", relevantViewSize, recentViewSize)[0]
            for x in attention_buf:
                print(x[0], x[1][:-1])
        return RET_ANSWER
    if inp.startswith("//") or inp.startswith("*"):
        return RET_ANSWER
    if inp.endswith("?"):
        buf, text = Memory_generate_prompt(currentTime, memory, Prompts_question_start, "\nThe question: ", relevantViewSize, recentViewSize, inp)
        send_prompt = text + inp[:-1] + (Prompts_question_end_alternative if IncludeGPTKnowledge else Prompts_question_end)
        RET_ANSWER = PromptProcess(inp, send_prompt, True)
    else:
        if len(inp) > 0 and inp != "1":
            buf, text = Memory_generate_prompt(currentTime, memory, Prompts_belief_start, "\nThe sentence: ", relevantViewSize, recentViewSize)
            RET_ANSWER = PromptProcess(inp, text + inp + Prompts_belief_end, False)
        buf, text = Memory_generate_prompt(currentTime, memory, Prompts_inference_start, "\n", relevantViewSize, recentViewSize)
        PromptProcess(inp, text + Prompts_inference_end, False)
        currentTime += 1
        Memory_Eternalize(currentTime, memory)
        Memory_store(filename, memory, currentTime, evidentalBaseID)
    return RET_ANSWER

if __name__ == "__main__":
    while True:
        try:
            inp = input().rstrip("\n").strip().lower()
        except:
            exit(0)
        NarsGPT_AddInput(inp)
