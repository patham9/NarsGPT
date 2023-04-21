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
from Prompts import *
from Memory import *
from Control import *
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
memory = {} #the NARS-style long-term memory
currentTime = 1

def PromptProcess(send_prompt, isQuestion):
    if PrintGPTPrompt: print("vvvvSTART PROMPT", send_prompt, "\n^^^^END PROMPT")
    response = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=[ {"role": "user", "content": send_prompt}], max_tokens=200, temperature=0)
    commands = response['choices'][0]['message']['content'].split("\n")
    Control_cycle(currentTime, memory, commands, isQuestion, PrintMemoryUpdates, PrintTruthValues)

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
        send_prompt = Memory_generate_prompt(memory, Prompts_question_start, "\nThe question: ", attention_buffer_size) + inp[:-1] + \
                                            (Prompts_question_end_alternative if IncludeGPTKnowledge else Prompts_question_end)
        PromptProcess(send_prompt, True)
    else:
        if len(inp) > 0 and inp != "1":
            PromptProcess(Memory_generate_prompt(memory, Prompts_belief_start, "\nThe sentence: ", attention_buffer_size) + inp + Prompts_belief_end, False)
        #PromptProcess(Memory_generate_prompt(memory, Prompts_inference_start, "\n", attention_buffer_size) + Prompts_inference_end, False)
        currentTime += 1
    #Memory_store(filename, memory, currentTime, evidentalBaseID)
