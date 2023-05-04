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

from openai.embeddings_utils import get_embedding, cosine_similarity
from os.path import exists
import openai
import json
import time
import sys

openai.api_key = "YOUR_KEY"
relevantViewSize = 30
recentViewSize = 10
filename = "mem.json" #the system's memory file
PrintInputSentence = True and "NoPrintInputSentence" not in sys.argv
PrintGPTPrompt = False or "PrintGPTPrompt" in sys.argv

memory = []
recent = []
currentTime = 1
if exists(filename):
    with open(filename) as json_file:
        print("//Loaded memory content from", filename)
        (recent,memory,currentTime) = json.load(json_file)

for x in sys.argv:
    if x.startswith("API_KEY="):
        openai.api_key = x.split("API_KEY=")[1]

def get_embedding_robust(inp):
    while True:
        try:
            ret = get_embedding(inp)
        except:
            print("//Failed get embedding, will retry API call in 10s")
            time.sleep(10)
            continue
        break
    return ret

def RetrieveQuestionRelatedBeliefs(inp):
    global lastRetrieval
    primed = []
    qu_embed = get_embedding_robust(inp)
    for embedding, sentence in memory:
        if sentence not in recent:
            matchQuality = cosine_similarity(qu_embed, embedding)
            primed.append((matchQuality, sentence))
    primed.sort(key=lambda x: -x[0])
    primed = primed[:relevantViewSize]
    primed = [x[1] for x in primed]
    return list(reversed(primed))

def AddAnswer(answer):
    global memory, recent
    memory.append((get_embedding_robust(answer), answer))
    recent.append(answer)
    if len(recent) > recentViewSize:
        recent = recent[1:]

def NarsGPT_AddInput(inp): #use same name as in NarsGPT for easy wrapping in testing
    global view, currentTime
    RET_ANSWER = ""
    if len(inp.strip()) == 0:
        return RET_ANSWER
    #start debug command (same behavior as *prompt command in NarsGPT)
    if inp.startswith("*prompt"):
        if inp.endswith("?"):
            relevant = RetrieveQuestionRelatedBeliefs(inp.split("*prompt=")[1])
            for i,x in enumerate(relevant + recent):
                print(f"i={i}:", x)
        else:
            for i,x in enumerate(recent):
                print(f"i={i}:", x)
        return RET_ANSWER
    #end debug command
    if PrintInputSentence: print("Input:", inp)
    if inp.endswith("?"):
        relevant = RetrieveQuestionRelatedBeliefs(inp)
        view = relevant + recent
        viewstr = ""
        for i, x in enumerate(view):
            viewstr += f"\ni={i}: " + x
        viewstr = viewstr[1:]
        Prompts_question_end = " according to Memory and which memory item i? Answer in a probabilistic sense and within 15 words based on memory content only."
        send_prompt = "Memory:\n" + (viewstr if view else "EMPTY!") + "\n The question: " + inp[:-1] +  Prompts_question_end
        if PrintGPTPrompt: print("vvvv PROMPT\n" + send_prompt + "\n^^^^^")
        response = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=[ {"role": "user", "content": send_prompt}], max_tokens=200, temperature=0)
        RET_ANSWER = response['choices'][0]['message']['content']
        print(RET_ANSWER)
    else:
        AddAnswer(inp)
        currentTime += 1
        with open(filename, 'w') as f:
            json.dump((recent,memory,currentTime), f)
    return RET_ANSWER

if __name__ == "__main__":
    while True:
        try:
            inp = input().rstrip("\n").strip()
        except:
            exit(0)
        NarsGPT_AddInput(inp)
