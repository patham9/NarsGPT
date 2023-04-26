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

from ast import literal_eval
from os.path import exists
import json
import sys
import os
cwd = os.getcwd()
sys.path.append(cwd + "/OpenNARS-for-Applications/misc/Python/")
os.chdir(cwd + "/OpenNARS-for-Applications/misc/Python/")
import NAR
os.chdir(cwd)
from Truth import *

def RetrieveQuestionContent(memory, attention_buf, inp, max_LTM_retrievals=5):
    primed = {}
    words = [x.strip().replace("?","") for x in inp.split(" ")]
    for x in words:
        n = Lemmatize(x, wordnet.NOUN)
        v = Lemmatize(x, wordnet.VERB)
        for m in list(memory.items()):
            padded = lambda w: " " + w.replace(">"," ").replace("<"," ").replace("("," ").replace(")"," ") + " "
            if padded(n) in padded(m[0][0]) or padded(v) in padded(m[0][0]):
                if m not in attention_buf:
                    matchQuality = 2 if (padded(n) in padded(m[0][0]) and padded(v) in padded(m[0][0])) else 1
                    if m[0] not in primed:
                        primed[m[0]] = (matchQuality, m[1])
                    else:
                        primed[m[0]] = (primed[m[0]][0] + matchQuality, primed[m[0]][1])
    primed = list(primed.items())
    primed.sort(key=lambda x: (-x[1][0], -Truth_Expectation(x[1][1][2]))) #sort by query match first then by truth expectation
    primed = primed[:max_LTM_retrievals]
    #for m in primed:
    #    print("//Retrieved from LTM:", m)
    primed = [(x[0],x[1][1]) for x in primed]
    return list(reversed(primed))

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
        attention_buf = RetrieveQuestionContent(memory, attention_buf, inpQuestion) + attention_buf
    return attention_buf

def ProductPrettify(term):
    if " --> " in term and " * " in term.split(" --> ")[0]:
        arg1 = term.split(" * ")[0].strip()
        arg2 = term.split(" * ")[1].split(" --> ")[0].strip()
        relarg = term.split(" --> ")[1].strip()
        term = arg1 + " " + relarg + " " + arg2
    return term.replace("(","").replace(")","")

def Memory_generate_prompt(currentTime, memory, prompt_start, prompt_end, attention_buffer_size, inpQuestion = None, TimeHandling = True):
    prompt_memory = ""
    buf = Memory_attention_buffer(memory, attention_buffer_size, inpQuestion)
    if len(buf) == 0:
        prompt_memory = "EMPTY!"
    for i,x in enumerate(buf):
        time = x[0][1]
        (f,c) = x[1][2]
        timeterm = ""
        if time != "eternal":
            timeterm = "time=" + str(time) + " "
            (f,c) = Truth_Projection((f,c), float(time), float(currentTime))
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
        term = x[0][0][1:-1] if "<" in x[0][0] else x[0][0]
        if "=/>" not in term:
            term = ProductPrettify(term)
        else:
            if " =/> " in term:
                prec_op = [ProductPrettify(p) for p in term.split(" =/> ")[0].split(" &/ ")]
                removeParentheses = lambda u: u.replace(" --> ["," hasproperty ").replace(" --> "," isa ").replace(" - ", " and not ").replace("(",""). \
                                                replace("<","").replace(")","").replace(">","").replace("  "," ").strip()
                precs = removeParentheses(" and when then ".join(prec_op[:-1]))
                op = prec_op[-1]
                if " --> " in op:
                    op = removeParentheses(prec_op[-1].split(" --> ")[1] + " " + prec_op[-1].split(" --> ")[0]).replace("{SELF} *", "")
                term = "When '" + precs + "' then '" + removeParentheses(op) + "' causes '" + removeParentheses(term.split(" =/> ")[1]) + "'"
        term = term.replace(" --> [", " hasproperty ").replace("]","").replace("[","").replace(" --> ", " isa ").replace(" &/ ", " then ").replace(" =/> ", " causes ")
        prompt_memory += f"i={i}: {term}. {timeterm}truthtype={truthtype} certainty={certainty}\n"
    return buf, prompt_start + prompt_memory + prompt_end

from nltk import WordNetLemmatizer
from nltk.corpus import wordnet
lemma = WordNetLemmatizer()
def Lemmatize(word, tag):
    global used_verbs
    word = word.lower().replace(" ", "_").replace("-","_")
    if word.endswith("encode") and len(word) > 6: #no idea why GPT adds Encode at the end for new words
        word = word[:-6]
    if "_" in word and tag == wordnet.NOUN:
        parts = word.split("_")
        lastpart = lemma.lemmatize(parts[-1], pos = tag).strip().lower().replace(" ","_").replace("-","_")
        ret = "_".join(parts[:-1]) + "_" + lastpart
    else:
        ret = lemma.lemmatize(word.lower(), pos = tag).strip().lower().replace(" ","_").replace("-","_")
        if tag == wordnet.VERB:
            if ret == "is" or ret == "isa" or ret == "is_a" or ret == "be" or ret == "are" or ret == "were" or ret == "arelike" or ret == "islike":
                return "isa"
    return ret

retrieved = set([])
def query(currentTime, memory, term, time):
    global retrieved
    if time != "eternal":
        return currentTime
    if (term, time) not in retrieved and (term, time) in memory:
        retrieved.add((term, time))
        (_, _, (f, c)) = memory[(term, time)]
        if time == "eternal":
            _, currentTime = ProcessInput(currentTime, memory, f"{term}. {{{f} {c}}}")
        if time == currentTime:
            _, currentTime = ProcessInput(currentTime, memory, f"{term}. :|: {{{f} {c}}}")
    if "?1" in term: #simple query matching
        parts = term.split("?1")
        bestTerm, bestTruth, bestTime = (None, (0.0, 0.5), "eternal")
        for (term2, time2) in memory:
            (_, _, (f2, c2)) = memory[(term2, time2)]
            if time2 == time and term2.startswith(parts[0]) and term2.endswith(parts[1]):
                if Truth_Expectation((f2, c2)) > Truth_Expectation((bestTruth[0], bestTruth[1])):
                    bestTerm = term2
                    bestTruth = (f2, c2)
                    bestTime = time2
        if bestTerm is not None:
            retrieved.add((bestTerm, bestTime))
            if bestTime == "eternal":
                _, currentTime = ProcessInput(currentTime, memory, f"{bestTerm}. {{{bestTruth[0]} {bestTruth[1]}}}")
            if bestTime == "currentTime":
                _, currentTime = ProcessInput(currentTime, memory, f"{bestTerm}. :|: {{{bestTruth[0]} {bestTruth[1]}}}")
    retrieved.add((term, time))
    return currentTime

def ProcessInput(currentTime, memory, inputforNAR, backups = ["input", "answers", "derivations"]):
    ret = NAR.AddInput(inputforNAR, Print=False)
    TestedCausalHypotheses = []
    for execution in ret["executions"]:
        print(execution, "expectation="+str(ret["reason"]["desire"]), ret["reason"]["hypothesis"])
        TestedCausalHypotheses.append(ret["reason"]["hypothesis"])
    for backup in backups:
        it = ret[backup] + TestedCausalHypotheses if backup == "input" else ret[backup] #append causal hypotheses to be added to memory!
        for derivation in it:
            if derivation["punctuation"] == "." and derivation["term"] != "None":
                term = derivation["term"]
                Continue = False
                for forbidden in [" /1 ", " \\1 ", " /2 ", " \\2 ", " & ", " | ", " ~ ", " - ", " <=> ", " && ", " || ", " ==> ", " <-> ", " =/> ", " . "]:
                    if forbidden in term and derivation not in TestedCausalHypotheses:
                        Continue = True
                if Continue:
                    continue
                if term.startswith("dt="): #we don't need to store time deltas
                    term = " ".join(term.split(" ")[1:])
                if term.startswith("<[") or (" --> " in term and " * " in term.split(" --> ")[1]):
                    continue
                time = derivation["occurrenceTime"]
                if time.isdigit():
                    time = int(time)
                currentTime = query(currentTime, memory, term, time)
                f2 = float(derivation["truth"]["frequency"])
                c2 = float(derivation["truth"]["confidence"])
                usefulnessAddition = 1000000 if "Priority" not in derivation or derivation["Priority"] == 1.0 else 1
                if (term, time) in memory:
                    (t, usefulness, (f, c)) = memory[(term, time)]
                    if c2 > c:
                        memory[(term, time)] = (currentTime, usefulness + usefulnessAddition, (f2, c2))
                else:
                    memory[(term, currentTime)] = (currentTime, usefulnessAddition, (f2, c2))
    if ">." in inputforNAR or "! :|:" in inputforNAR:
        currentTime += 1
    if inputforNAR.isdigit():
        currentTime += int(inputforNAR)
    return ret, currentTime

relations = set(["isa", "are", "hasproperty"])
def Relation(inp, currentTime, memory, s, v, p, punctuation_tv):
    global relations
    s = Lemmatize(s, wordnet.NOUN)
    p = Lemmatize(p, wordnet.NOUN)
    v = Lemmatize(v, wordnet.VERB)
    relations.add(v)
    if s.replace("_", " ") not in inp or p.replace("_", " ") not in inp:
        #print("//!!!! filtered out", s, v, p)
        return False, currentTime
    if s == "" or v == "" or p == "":
        return False, currentTime
    if v == "isa" or v == "are":
        if s == p:
            return False, currentTime
        _, currentTime = ProcessInput(currentTime, memory, f"<{s} --> {p}>" + punctuation_tv)
    else:
        _, currentTime = ProcessInput(currentTime, memory, f"<({s} * {p}) --> {v}>" + punctuation_tv)
    return True, currentTime

def Property(inp, currentTime, memory, s, p, punctuation_tv):
    if s.replace("_", " ") not in inp or p.replace("_", " ") not in inp:
        #print("//!!!! filtered out", s, "hasproperty", p)
        return False, currentTime
    s = Lemmatize(s, wordnet.NOUN)
    p = Lemmatize(p, wordnet.ADJ)
    if s == "" or p == "" or s == p:
        return False, currentTime
    _, currentTime = ProcessInput(currentTime, memory, f"<{s} --> [{p}]>" + punctuation_tv)
    return True, currentTime

lastTime = 0
hadRelation = set([])
def Memory_digest_sentence(inp, currentTime, memory, sentence, truth, PrintMemoryUpdates, TimeHandling):
    global lastTime, hadRelation
    if currentTime != lastTime:
        hadRelation = set([])
    if sentence in hadRelation:
        return False, currentTime
    lastTime = currentTime
    pieces = [x.strip().replace(" ","_") for x in sentence.split(",")]
    punctuation_tv = f". :|: {{{truth[0]} {truth[1]}}}" if TimeHandling else f". {{{truth[0]} {truth[1]}}}"
    if len(pieces) == 3:
        if pieces[1] == "hasproperty":
            return Property(inp, currentTime, memory, pieces[0], pieces[2], punctuation_tv)
        else:
            return Relation(inp, currentTime, memory, *pieces, punctuation_tv)
    else:
        #print("//!!!! Can't form relation:", pieces)
        return False, currentTime

def Memory_load(filename):
    memory = {} #the NARS-style long-term memory
    currentTime = 1
    if exists(filename):
        with open(filename) as json_file:
            print("//Loaded memory content from", filename)
            (mt, currentTime) = json.load(json_file)
            memory = {literal_eval(k): v for k, v in mt.items()}
    return (memory, currentTime)

def Memory_store(filename, memory, currentTime):
    with open(filename, 'w') as f:
        json.dump(({str(k): v for k, v in memory.items()}, currentTime), f)

def Memory_QuestionPriming(currentTime, cmd, memory, buf):
    #1. get all memory index references
    indexrefs = [x+" " for x in cmd.split("i=")]
    indices=[]
    for valstr in indexrefs:
        curdigits = ""
        i = 0
        while i<len(valstr):
            if valstr[i].isdigit():
                curdigits += valstr[i]
            else:
                if curdigits.isdigit():
                    indices.append(int(curdigits))
                    curdigits = ""
                if valstr[i] != ",":
                    break
            i += 1
    #2. check if they are in buf and prime ONA's memory with the question which will activate the concepts:
    for index in indices:
        if index >= 0 and index < len(buf):
            item = buf[index]
            query(currentTime, memory, item[0][0], item[0][1])
            
def Memory_Eternalize(currentTime, memory, eternalizationDistance = 3):
    deletes = []
    additions = []
    for (m, t) in memory:
        belief = memory[(m, t)]
        if t != "eternal" and currentTime - t > eternalizationDistance:
            deletes.append((m, t))
            additions.append(((m, "eternal"), (belief[0], belief[1], Truth_Eternalize(belief[2]))))
    for k in deletes:
        del memory[k]
    for (k, v) in additions:
        memory[k] = v
