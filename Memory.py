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
import json
import sys
import os
cwd = os.getcwd()
sys.path.append(cwd + "/OpenNARS-for-Applications/misc/Python/")
os.chdir(cwd + "/OpenNARS-for-Applications/misc/Python/")
import NAR
os.chdir(cwd)

def Memory_attention_buffer(memory, attention_buffer_size):
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
    return attention_buf

def Truth_Expectation(v):
    return (v[1] * (v[0] - 0.5) + 0.5)

def Memory_generate_prompt(memory, prompt_start, prompt_end, attention_buffer_size):
    prompt_memory = ""
    buf = Memory_attention_buffer(memory, attention_buffer_size)
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
        term = x[0][1:-1] if "<" in x[0] else x[0]
        if " * " in term and "=/>" not in term:
            arg1 = term.split("(")[1].split(" * ")[0].strip()
            arg2 = term.split(")")[0].split(" * ")[1].strip()
            relarg = term.split(" --> ")[1].strip()
            term = arg1 + " " + relarg + " " + arg2
        else:
            term = term.replace(" --> ", " isa ").replace(" &/ ", " then ").replace(" =/> ", " causes ")
        timeterm = ""
        if x[1][3] != "eternal":
            timeterm = "t=" + x[1][3] + " "
        prompt_memory += f"i={i}: {term}. {timeterm}truthtype={truthtype} certainty={certainty}\n"
    return prompt_start + prompt_memory + prompt_end

from nltk import WordNetLemmatizer
from nltk.corpus import wordnet
lemma = WordNetLemmatizer()
def Lemmatize(word, tag):
    global used_verbs
    ret = lemma.lemmatize(word.lower(), pos = tag).strip().lower().replace(" ","_").replace("-","_")
    if tag == wordnet.VERB:
        if ret == "is" or ret == "isa" or ret == "is_a" or ret == "be" or ret == "are" or ret == "were":
            return "isa"
    return ret

def ProcessInput(currentTime, memory, inputforNAR, backups = ["input", "answers", "derivations"]):
    ret = NAR.AddInput(inputforNAR, Print=False)
    for backup in backups:
        for derivation in ret[backup]:
            for forbidden in [" /1 ", " \1 ", " /2 ", " \2 ", " & ", " | ", " ~ ", " - ", " <=> ", " && ", " || ", " ==> ", " <-> "]:
                if forbidden in derivation["term"]:
                    return
            if derivation["punctuation"] == "." and derivation["term"] != "None":
                term = derivation["term"]
                if term.startswith("dt="): #we don't need to store time deltas
                    term = " ".join(term.split(" ")[1:])
                f2 = float(derivation["truth"]["frequency"])
                c2 = float(derivation["truth"]["confidence"])
                usefulnessAddition = 1000000 if "Priority" not in derivation or derivation["Priority"] == 1.0 else 1
                if term in memory:
                    (t, usefulness, (f, c), time) = memory[term]
                    if c2 >= c:
                        memory[term] = (currentTime, usefulness + usefulnessAddition, (f2, c2), time) #, #(f2, c2, usefulness + usefulnessAddition)
                else:
                    memory[term] = (currentTime, usefulnessAddition, (f2, c2), derivation["occurrenceTime"])

relations = set(["isa", "are", "hasproperty"])
def Relation(inp, currentTime, memory, s, v, p, punctuation_tv):
    global relations
    s = Lemmatize(s, wordnet.NOUN)
    p = Lemmatize(p, wordnet.NOUN)
    v = Lemmatize(v, wordnet.VERB)
    relations.add(v)
    if s not in inp or p not in inp:
        #print("//!!!! filtered out", s, v, p)
        return False
    if s == "" or v == "" or p == "":
        return False
    if v == "isa" or v == "are":
        ProcessInput(currentTime, memory, f"<{s} --> {p}>" + punctuation_tv)
    else:
        ProcessInput(currentTime, memory, f"<({s} * {p}) --> {v}>" + punctuation_tv)
    return True

def Property(inp, currentTime, memory, s, p, punctuation_tv):
    if s not in inp or p not in inp:
        #print("//!!!! filtered out", s, "hasproperty", p)
        return False
    s = Lemmatize(s, wordnet.NOUN)
    p = Lemmatize(p, wordnet.ADJ)
    if s == "" or p == "":
        return False
    ProcessInput(currentTime, memory, f"<{s} --> [{p}]>" + punctuation_tv)
    return True

lastTime = 0
hadRelation = set([])
def Memory_digest_sentence(inp, currentTime, memory, sentence, truth, PrintMemoryUpdates):
    global lastTime, hadRelation
    if currentTime != lastTime:
        hadRelation = set([])
    if sentence in hadRelation:
        return
    lastTime = currentTime
    pieces = sentence.split(" ")
    punctuation_tv = f". {{{truth[0]} {truth[1]}}}"
    if len(pieces) == 3:
        if pieces[1] == "hasproperty":
            return Property(inp, currentTime, memory, pieces[0], pieces[2], punctuation_tv)
        else:
            return Relation(inp, currentTime, memory, *pieces, punctuation_tv)
    else:
        #print("//!!!! Can't form relation:", pieces)
        return False
