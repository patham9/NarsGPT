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
from openai.embeddings_utils import get_embedding, cosine_similarity
from Prompts import *
from Memory import *
from Control import *
import openai
import time

openai.api_key = "YOUR_KEY"
relevantViewSize = 30      #how many relevant (judged by statement embedding) ONA memory items GPT can see
recentViewSize = 10        #how many recent (judged by lastUsed) ONA memory items GPT can see
eternalizationDistance = 3  #how long items are treated as events before contributing to generic belief evidence in long-term memory
filename = "mem.json" #the system's memory file
IYouExchange = True or "NoIYouExchange" in sys.argv #whether I and you, my and your is exchanged in communication
ConsiderGPTKnowledge = False or "ConsiderGPTKnowledge" in sys.argv #Whether it should be allowed to consider GPT's knowledge too for answering a question
ImportGPTKnowledge = False or "ImportGPTKnowledge" in sys.argv #Whether it should be allowed to encode GPT's knowledge too when receiving new user input
PrintInputSentence = True and "NoPrintInputSentence" not in sys.argv
PrintTruthValues = True and "NoPrintTruthValues" not in sys.argv
PrintMemoryUpdates = False or "PrintMemoryUpdates" in sys.argv
PrintGPTPrompt = False or "PrintGPTPrompt" in sys.argv
NarseseByONA = True and "NarseseByGPT" not in sys.argv
QuestionPriming = True and "NoQuestionPriming" not in sys.argv
TimeHandling = True and "NoTimeHandling" not in sys.argv

for x in sys.argv:
    if x.startswith("API_KEY="):
        openai.api_key = x.split("API_KEY=")[1]
(memory, currentTime, maxBaseId) = Memory_load(filename) #the ONA memory
NAR.AddInput("*currenttime=" + str(currentTime))
NAR.AddInput("*stampid=" + str(maxBaseId + 1))

def PromptProcess(RET_DICT, inp, buf, send_prompt, isQuestion, isGoal=False):
    if PrintGPTPrompt: print("vvvvSTART PROMPT", send_prompt, "\n^^^^END PROMPT")
    while True:
        try:
            response = openai.ChatCompletion.create(model='gpt-3.5-turbo', messages=[ {"role": "user", "content": send_prompt}], max_tokens=200, temperature=0)
            commands = response['choices'][0]['message']['content'].split("\n")
        except Exception as e:
            print("Error: API call failed, will try repeating it in 10 seconds!", str(e))
            time.sleep(10) #wait 10 seconds
            continue
        break
    curTime = Control_cycle(RET_DICT, inp, buf, currentTime, memory, commands, isQuestion, isGoal, PrintMemoryUpdates, PrintTruthValues, QuestionPriming, TimeHandling, ImportGPTKnowledge)
    RET_DICT["GPT_Answer"] = "\n".join(commands)
    return curTime

def I_You_Exchange(RET_DICT):
    if "GPT_Answer" in RET_DICT:
        answer = (" " + RET_DICT["GPT_Answer"] + " ").replace("\"", " \" ").replace("?", " ?")
        if " you " in answer or " your " in answer or " You " in answer or " Your " in answer:
            answer = answer.replace(" you ", " I ").replace(" You ", " I ").replace(" your ", " my ").replace(" Your ", " my ").replace(" yours ", " my ").replace(" Yours ", " my ").strip() #replace you/your with i/my
        else:
            answer = answer.replace(" i ", " you ").replace(" I ", " you ").replace(" My ", " your ").replace(" my ", " your ").strip() #replace i/my with you/your
        RET_DICT["GPT_Answer"] = answer.replace("  \" ", " \"").replace(" \"  ", "\" ").replace(" ?", "?")

groundings = []
lastGoal = ""
def AddInput(inp, Print=True, PrintInputSentenceOverride=True, PrintInputSentenceOverrideValue=False):
    global currentTime, lastGoal, memory, PrintInputSentence
    SetPrint(Print)
    if PrintInputSentenceOverride:
        PrintInputSentence = PrintInputSentenceOverrideValue
    RET_DICT = {"GPT_Answer" : ""}
    if inp == "*step" and lastGoal != "":
        inp = lastGoal
    if PrintInputSentence: print("Input:", inp)
    if inp.startswith("//"):
        return RET_DICT
    if inp.startswith("*volume="): #TODO
        return RET_DICT
    if inp.startswith("*prompt"):
        if inp.endswith("?"):
            print(Memory_generate_prompt(currentTime, memory, "","", relevantViewSize, recentViewSize, inp[:-1].split("*prompt=")[1])[1])
        else:
            print(Memory_generate_prompt(currentTime, memory, "","", relevantViewSize, recentViewSize)[1])
        return RET_DICT
    if NarseseByONA and (inp.startswith("<") or inp.startswith("(") or " :|:" in inp):
        if QuestionPriming:
            if inp.endswith("?"): #query first
                query(RET_DICT, currentTime, memory, inp[:-1].strip(), "eternal")
        ret, currentTime = ProcessInput(RET_DICT, currentTime, memory, inp)
        if "answers" in ret and ret["answers"]:
            answer = ret["answers"][0]
            if Print == False:
                if "truth" not in answer:
                    print("Answer: None.")
                else:
                    occurrenceTimeInfo = "" if answer["occurrenceTime"] == "eternal" else " t="+answer["occurrenceTime"]
                    print("Answer: " + answer["term"] + answer["punctuation"] + " {" + str(answer["truth"]["frequency"]) + " " + str(answer["truth"]["confidence"]) + "}" + occurrenceTimeInfo)
        if not inp.endswith("?"):
            Memory_Eternalize(currentTime, memory, eternalizationDistance)
            Memory_store(filename, memory, currentTime)
        return RET_DICT
    if inp.startswith("*memory"):
        for x in memory.items():
            print(x[0], x[1][:-1])
        return RET_DICT
    if inp.startswith("*ground="):
        narsese = inp.split("ground=")[1]
        sentence = Term_AsSentence(narsese)
        print("//Grounded:", narsese," <= ", sentence)
        embedding = get_embedding_robust(sentence)
        groundings.append((sentence, embedding))
        return RET_DICT
    if inp.startswith("*time"):
        print(currentTime)
        return RET_DICT
    if inp.startswith("*reset"):
        memory = {}
        currentTime = 1
        maxBaseId = 1
        NAR.AddInput("*reset")
        return RET_DICT
    if inp.startswith("*buffer"):
        if inp.endswith("?"):
            memory_view = Memory_generate_prompt(currentTime, memory, "","", relevantViewSize, recentViewSize, inp[:-1].split("*buffer=")[1])[0]
            for x in memory_view:
                print(x[0], x[1][:-1])
        else:
            memory_view = Memory_generate_prompt(currentTime, memory, "","", relevantViewSize, recentViewSize)[0]
            for x in memory_view:
                print(x[0], x[1][:-1])
        return RET_DICT
    if inp.startswith("*"):
        NAR.AddInput(inp)
        return RET_DICT
    inp = inp.lower()
    if inp.endswith("?"):
        buf, text = Memory_generate_prompt(currentTime, memory, Prompts_question_start, "\nThe question: ", relevantViewSize, recentViewSize, inp)
        send_prompt = text + inp[:-1] + (Prompts_question_end_alternative if ConsiderGPTKnowledge else Prompts_question_end)
        currentTime = PromptProcess(RET_DICT, inp, buf, send_prompt, True)
        I_You_Exchange(RET_DICT)
    else:
        if len(inp) > 0 and not inp.isdigit():
            buf, text = Memory_generate_prompt(currentTime, memory, Prompts_belief_start, "\nThe sentence: ", relevantViewSize, recentViewSize)
            isGoal = inp.endswith("!")
            if isGoal:
                lastGoal = inp
            else:
                lastGoal = ""
            if isGoal:
                inp_embedding = get_embedding_robust(inp)
                bestQual = 0.0
                bestsentence = ""
                for (sentence, embedding) in groundings:
                    matchQuality = cosine_similarity(inp_embedding, embedding)
                    if matchQuality > bestQual:
                        bestsentence = sentence
                        bestQual = matchQuality
                if bestsentence == "":
                    print("//Goal isn't grounded, rejected")
                    return RET_DICT
                inp = bestsentence
                print("//Reinterpreted as grounded goal:", inp)
            currentTime = PromptProcess(RET_DICT, inp, buf, text + inp + Prompts_belief_end, False, isGoal)
        else:
            _, currentTime = ProcessInput(RET_DICT, currentTime, memory, "1" if len(inp) == 0 else inp)
        Memory_Eternalize(currentTime, memory, eternalizationDistance)
        Memory_store(filename, memory, currentTime)
    return RET_DICT

def getNAR():
    return NAR.getNAR()

def setNAR(proc):
    NAR.setNAR(proc)

def terminateNAR(proc=None):
    if proc is None:
        proc = getNAR()
    NAR.terminateNAR(proc)

def spawnNAR():
    NAR.spawnNAR()
def Shell():
    while True:
        try:
            inp = input().rstrip("\n").strip()
        except:
            exit(0)
        AddInput(inp, Print=False, PrintInputSentenceOverride=True, PrintInputSentenceOverrideValue=PrintInputSentence)

if __name__ == "__main__":
    Shell()
