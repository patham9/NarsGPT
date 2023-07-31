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
import time
import nltk
from nltk import WordNetLemmatizer
from nltk.corpus import wordnet
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)

Print = False
def SetPrint(Flag):
    global Print
    Print = Flag
def GetPrint():
    return Print

def ReplaceEncode(word):
    if word.endswith("encode") and len(word) > 6: #no idea why GPT adds Encode at the end for new words
            word = word[:-6]
    return word

def MergeInto(RET_DICT, ret):
    for key in ret:
        if key in RET_DICT and key != "reason": #list (only last reason is returned, consistent with NAR.py)
            RET_DICT[key] = RET_DICT[key] + ret[key]
        else:
            RET_DICT[key] = ret[key]

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

def ProductPrettify(term):
    if " --> " in term and " * " in term.split(" --> ")[0]:
        arg1 = term.split(" * ")[0].strip()
        arg2 = term.split(" * ")[1].split(" --> ")[0].strip()
        relarg = term.split(" --> ")[1].strip()
        term = arg1 + " " + relarg + " " + arg2
    return term.replace("(","").replace(")","")

def Term_AsSentence(T):
    term = T[1:-1] if "<" in T else T
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
    return term.replace(" + ", " ")

def Term_Embedded(T):
    return get_embedding_robust(Term_AsSentence(T).replace("-"," ").replace("_"," "))

def RetrieveQuestionRelatedBeliefs(memory, view, inp, max_LTM_retrievals=30):
    primed = {}
    qu_embed = get_embedding_robust(inp)
    for m in list(memory.items()):
        if m not in view:
            matchQuality = cosine_similarity(qu_embed, m[1][4])
            primed[m[0]] = (matchQuality, m[1])
    primed = list(primed.items())
    primed.sort(key=lambda x: (-x[1][0], -Truth_Expectation(x[1][1][2]))) #sort by query match first then by truth expectation
    primed = primed[:max_LTM_retrievals]
    #for m in primed:
    #    print("//Retrieved from LTM:", m[0], m[1][:-1])
    primed = [(x[0],x[1][1]) for x in primed]
    return list(reversed(primed))

def Memory_view(memory, relevantViewSize, recentViewSize, inpQuestion = None):
    view=[]
    recent_item_list = list(memory.items())
    #find recentViewSize items:
    recent_item_list.sort(key=lambda x: -x[1][0])
    view += reversed(recent_item_list[0:recentViewSize]) #newer comes later in prompt
    if inpQuestion is not None:
        view = RetrieveQuestionRelatedBeliefs(memory, view, inpQuestion, relevantViewSize) + view
    return view

def Memory_generate_prompt(currentTime, memory, prompt_start, prompt_end, relevantViewSize, recentViewSize, inpQuestion = None):
    prompt_memory = ""
    buf = Memory_view(memory, relevantViewSize, recentViewSize, inpQuestion)
    if len(buf) == 0:
        prompt_memory = "EMPTY!"
    for i,x in enumerate(buf):
        time = x[0][1]
        (f,c) = x[1][2]
        timeterm = ""
        if time != "eternal":
            timeterm = "time=" + str(time) + " "
            (f,c) = Truth_Projection((f,c), float(time), float(currentTime))
        term = Term_AsSentence(x[0][0])
        if f < 0.5:
            words = term.split(" ")
            term = (words[0] + " not " + " ".join(words[1:])).replace(" not isa ", " is not a ").replace(" isa ", " is a ")
        prompt_memory += f"i={i}: {term}. {timeterm}confidence={c}\n"
    return buf, prompt_start + prompt_memory + prompt_end

lemma = WordNetLemmatizer()
def Lemmatize(word, tag):
    global used_verbs
    word = ReplaceEncode(word.lower().replace(" ", "_").replace("-","_"))
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

def Atomize(atom, atoms, pos, atomCreationThreshold):
    splitter = ";;"
    key = atom + splitter + str(pos)
    atomembedding = atoms[key] if key in atoms else get_embedding_robust(atom)
    closest_atom = None
    closest_quality = None
    for key2 in atoms:
        atom2, pos2 = key2.split(splitter)
        if pos2 == pos:
            embedding = atoms[key2]
            matchQuality = cosine_similarity(atomembedding, embedding)
            #print("!!!", atom2, atom, matchQuality)
            if closest_atom is None or matchQuality > closest_quality:
                closest_atom = atom2
                closest_quality = matchQuality
    if closest_quality is None or closest_quality < atomCreationThreshold:
        ret = atom
        atoms[key] = atomembedding
    else:
        #print(f"REPLACED {atom} with {closest_atom} matchVal={matchQuality}")
        ret = closest_atom
    return ret

retrieved = set([])
def Allow_requery_if_not_in_ONA(RET_DICT, term, time):
    #check if previously queried item is not in ONA memory anymore else we need
    #to set it up for re-query by removing it from retrieved
    if (term, time) in retrieved:
        ret = NAR.AddInput(term + "?", Print=Print)
        MergeInto(RET_DICT, ret)
        if "answers" in ret and ret["answers"]:
            answer = ret["answers"][0]
            if "truth" not in answer and answer["term"] == "None":
                retrieved.remove(term, time)

def query(RET_DICT, currentTime, memory, term, time):
    global retrieved
    if time != "eternal":
        return currentTime
    Allow_requery_if_not_in_ONA(RET_DICT, term, time)
    if (term, time) not in retrieved and (term, time) in memory:
        retrieved.add((term, time))
        (_, _, (f, c), stamp, _) = memory[(term, time)]
        NAR.AddInput("*stampimport=" + str(stamp), Print=Print)
        if time == "eternal":
            _, currentTime = ProcessInput(RET_DICT, currentTime, memory, f"{term}. {{{f} {c}}}")
    if "?1" in term: #simple query matching
        parts = term.split("?1")
        bestTerm, bestTruth, bestTime, bestStamp = (None, (0.0, 0.5), "eternal", [])
        for (term2, time2) in memory:
            (_, _, (f2, c2), stamp, _) = memory[(term2, time2)]
            if time2 == "eternal" and term2.startswith(parts[0]) and term2.endswith(parts[1]):
                if Truth_Expectation((f2, c2)) > Truth_Expectation((bestTruth[0], bestTruth[1])):
                    bestTerm = term2
                    bestTruth = (f2, c2)
                    bestTime = time2
                    bestStamp = stamp
        if bestTerm is not None:
            Allow_requery_if_not_in_ONA(bestTerm, time)
        if bestTerm is not None and (bestTerm, bestTime) not in retrieved:
            retrieved.add((bestTerm, bestTime))
            NAR.AddInput("*stampimport=" + str(bestStamp), Print=Print)
            if bestTime == "eternal":
                _, currentTime = ProcessInput(RET_DICT, currentTime, memory, f"{bestTerm}. {{{bestTruth[0]} {bestTruth[1]}}}")
    retrieved.add((term, time))
    return currentTime

def ProcessInput(RET_DICT, currentTime, memory, inputforNAR, backups = ["input", "answers", "derivations"]):
    ret = NAR.AddInput(inputforNAR, Print=Print)
    MergeInto(RET_DICT, ret)
    TestedCausalHypotheses = []
    for execution in ret["executions"]:
        reason = ""
        desire = 0.0
        if "reason" in ret and ret["reason"] is not None:
            reason = ret["reason"]["hypothesis"]
            desire = ret["reason"]["desire"]
            TestedCausalHypotheses.append(ret["reason"]["hypothesis"])
        print(execution, "expectation="+str(desire), reason)
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
                stamp = derivation["Stamp"]
                if str(time).isdigit():
                    time = int(time)
                currentTime = query(RET_DICT, currentTime, memory, term, time)
                f2 = float(derivation["truth"]["frequency"])
                c2 = float(derivation["truth"]["confidence"])
                usefulnessAddition = 1000000 if "Priority" not in derivation or derivation["Priority"] == 1.0 else 1
                if (term, time) in memory:
                    (t, usefulness, (f, c), _, embedding) = memory[(term, time)]
                    if c2 > c:
                        memory[(term, time)] = (currentTime, usefulness + usefulnessAddition, (f2, c2), stamp, embedding)
                else:
                    #optimization: if there is already an eternalized version with the same term, use that embedding:
                    if (term, "eternal") in memory:
                        embedding = memory[(term, "eternal")][4]
                    else:
                        embedding = Term_Embedded(term)
                    #now where we got the embedding too, make entry to memory:
                    memory[(term, time)] = (currentTime, usefulnessAddition, (f2, c2), stamp, embedding)
    if ">." in inputforNAR or "! :|:" in inputforNAR or ". :|:" in inputforNAR:
        currentTime += 1
    if inputforNAR.isdigit():
        currentTime += int(inputforNAR)
    return ret, currentTime

def notIncluded(word, inp):
    word = ReplaceEncode(word)
    return word.replace("_", " ") not in inp.replace(". "," ").replace("'","")

relations = set(["isa", "are", "hasproperty"])
def Relation(RET_DICT, inp, currentTime, memory, atoms, s, v, p, punctuation_tv, ImportGPTKnowledge, atomCreationThreshold):
    global relations
    sentence = ""
    if not ImportGPTKnowledge and (notIncluded(s, inp) or notIncluded(p, inp)):
        #print("//!!!! filtered out", s, v, p)
        return False, currentTime, sentence
    s = Atomize(Lemmatize(s, wordnet.NOUN), atoms, "NOUN", atomCreationThreshold)
    p = Atomize(Lemmatize(p, wordnet.NOUN), atoms, "NOUN", atomCreationThreshold)
    v = Atomize(Lemmatize(v, wordnet.VERB), atoms, "VERB", atomCreationThreshold)
    relations.add(v)
    if s == "" or v == "" or p == "":
        return False, currentTime, sentence
    if v == "isa" or v == "are":
        if s == p:
            return False, currentTime, sentence
        sentence = f"<{s} --> {p}>" + punctuation_tv
        _, currentTime = ProcessInput(RET_DICT, currentTime, memory, sentence)
    else:
        sentence = f"<({s} * {p}) --> {v}>" + punctuation_tv
        _, currentTime = ProcessInput(RET_DICT, currentTime, memory, sentence)
    return True, currentTime, sentence

def Property(RET_DICT, inp, currentTime, memory, atoms, s, p, punctuation_tv, ImportGPTKnowledge, atomCreationThreshold):
    sentence = ""
    if not ImportGPTKnowledge and (notIncluded(s, inp) or notIncluded(p, inp)):
        #print("//!!!! filtered out", s, "hasproperty", p)
        return False, currentTime, sentence
    s = Atomize(Lemmatize(s, wordnet.NOUN), atoms, "NOUN", atomCreationThreshold)
    p = Atomize(Lemmatize(p, wordnet.ADJ), atoms, "ADJ", atomCreationThreshold)
    if s == "" or p == "" or s == p:
        return False, currentTime, sentence
    sentence = f"<{s} --> [{p}]>" + punctuation_tv
    _, currentTime = ProcessInput(RET_DICT, currentTime, memory, sentence)
    return True, currentTime, sentence

lastTime = 0
hadRelation = set([])
def Memory_digest_sentence(RET_DICT, inp, currentTime, memory, atoms, sentence, truth, userGoal, PrintMemoryUpdates, TimeHandling, ImportGPTKnowledge, atomCreationThreshold):
    global lastTime, hadRelation
    #print(">>>>", sentence)
    if currentTime != lastTime:
        hadRelation = set([])
    if sentence in hadRelation:
        return False, currentTime, ""
    lastTime = currentTime
    pieces = [x.strip().replace(" ","_") for x in sentence.split(",")]
    punctuation = "!" if userGoal else "."
    punctuation_tv = f"{punctuation} :|: {{{truth[0]} {truth[1]}}}" if TimeHandling else f"{punctuation} {{{truth[0]} {truth[1]}}}"
    if len(pieces) == 3:
        if pieces[1] == "hasproperty":
            return Property(RET_DICT, inp, currentTime, memory, atoms, pieces[0], pieces[2], punctuation_tv, ImportGPTKnowledge, atomCreationThreshold)
        else:
            return Relation(RET_DICT, inp, currentTime, memory, atoms, *pieces, punctuation_tv, ImportGPTKnowledge, atomCreationThreshold)
    else:
        #print("//!!!! Can't form relation:", pieces)
        return False, currentTime, ""

def Memory_load(filename):
    memory = {} #the NARS-style long-term memory
    atoms = dict({}) #atom to embedding mapping
    currentTime = 1
    if exists(filename):
        with open(filename) as json_file:
            print("//Loaded memory content from", filename)
            (mt, currentTime) = json.load(json_file)
            memory = {literal_eval(k): v for k, v in mt.items()}
        atomfile = filename.replace(".json", "_atoms.json")
        with open(atomfile) as json_file:
            print("//Loaded atoms with embeddings from", filename)
            atoms = json.load(json_file)
    maxBaseId = 0
    for key in memory:
        maxBaseId = max([maxBaseId] + memory[key][3])
    return (memory, atoms, currentTime, maxBaseId)

def Memory_store(filename, memory, atoms, currentTime):
    with open(filename, 'w') as f:
        json.dump(({str(k): v for k, v in memory.items()}, currentTime), f)
    atomfile = filename.replace(".json", "_atoms.json")
    with open(atomfile, 'w') as f:
        json.dump(atoms, f)

def Memory_QuestionPriming(RET_DICT, currentTime, cmd, memory, buf):
    #1. get all memory index references
    indexrefs = [x+" " for x in cmd.replace("i=", "item ").split("item ")]
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
                if valstr[i] != "," and valstr[i] != "-":
                    break
            i += 1
    #2. check if they are in buf and prime ONA's memory with the question which will activate the concepts:
    for index in indices:
        if index >= 0 and index < len(buf):
            item = buf[index]
            query(RET_DICT, currentTime, memory, item[0][0], item[0][1])
            
def Memory_Eternalize(currentTime, memory, eternalizationDistance):
    deletes = []
    additions = []
    for (m, t) in memory:
        belief = memory[(m, t)]
        if t != "eternal" and currentTime - t > eternalizationDistance:
            previous_lastUsed = 0
            previous_useCount = 0
            if (m, "eternal") in memory:
                belief_old = memory[(m, "eternal")]
                previous_lastUsed = belief_old[0]
                previous_useCount = belief_old[1]
            deletes.append((m, t))
            #Get belief truth from ONA
            answers = NAR.AddInput(m + "?", Print=Print)["answers"]
            if answers and "truth" in answers[0]:
                f,c = float(answers[0]["truth"]["frequency"]), float(answers[0]["truth"]["confidence"])
                stamp = answers[0]["Stamp"]
                additions.append(((m, "eternal"), (max(previous_lastUsed, belief[0]), previous_useCount + belief[1], (f,c), stamp, belief[4])))
    for k in deletes:
        del memory[k]
    for (k, v) in additions:
        memory[k] = v

def Memory_inject_commands(RET_DICT, inp, buf, currentTime, memory, atoms, cmd, userQuestion, userGoal, PrintAnswer, PrintMemoryUpdates, PrintTruthValues, QuestionPriming, TimeHandling, ImportGPTKnowledge, atomCreationThreshold):
    AlreadyExecuted = set([])
    for x in cmd:
        if len(x) < 3:
            continue
        if x[1] == "." and x[2] == " ": #1. Deduce( (it often outputs in a list like that)
            x = " ".join(x.split(" ")[1:])
        if "#" in x:
            x = x.split("#")[0].strip()
        if x in AlreadyExecuted or "hasproperty none" in x.lower() or "isa none" in x.lower() \
                                or "none hasproperty" in x.lower() or "none isa" in x.lower(): #avoids some none calls
            continue
        AlreadyExecuted.add(x)
        truth = (1.0, 0.9)
        systemQuestion = x.startswith("Question(")
        if userQuestion or systemQuestion:
            if PrintAnswer:
                print(x)
        isNegated = False
        if x.startswith("NegatedRelationClaim") or x.startswith("NegatedPropertyClaim"):
            isNegated = True
            x = x[7:].replace("  ", " ") #.replace('"', "").replace("'", "")
            truth = (0.0, 0.9)
        if x.startswith("RelationClaim") or x.startswith("PropertyClaim"):
            x = x.replace("  ", " ") #.replace('"', "").replace("'", "")
        isInput = x.startswith("RelationClaim(") or x.startswith("PropertyClaim(")
        if isInput and ")" in x:
            sentence = x.split("(")[1].split(")")[0].replace('"','').replace("'","").replace(".", "").lower()
            digested, currentTime, retsentence = Memory_digest_sentence(RET_DICT, inp, currentTime, memory, atoms, sentence, truth, userGoal, PrintMemoryUpdates, TimeHandling, ImportGPTKnowledge, atomCreationThreshold) #currentTime updated
            if digested and PrintAnswer:
                printsentence = retsentence if isInput else x
                print(printsentence)
    if userQuestion and QuestionPriming:
        Memory_QuestionPriming(RET_DICT, currentTime, "\n".join(cmd), memory, buf)
    return currentTime
