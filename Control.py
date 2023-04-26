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

from Memory import *

def Control_cycle(inp, memory, cmd, userQuestion, currentTime, evidentalBaseID, PrintMemoryUpdates, PrintTruthValues, TimeHandling):
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
            print(x)
        isNegated = False
        if x.startswith("NegatedRelationClaim") or x.startswith("NegatedPropertyClaim"):
            isNegated = True
            x = x[7:].replace("  ", " ") #.replace('"', "").replace("'", "")
            truth = (0.0, 0.9)
        if x.startswith("RelationClaim") or x.startswith("PropertyClaim"):
            x = x.replace("  ", " ") #.replace('"', "").replace("'", "")
        isDeduction = x.startswith("Deduce(")
        isInduction = x.startswith("Induce(")
        isAbduction = x.startswith("Abduce(")
        isInput = x.startswith("RelationClaim(") or x.startswith("PropertyClaim(")
        if (isDeduction or isInduction or isAbduction or isInput) and ")" in x:
            sentence = x.split("(")[1].split(")")[0].replace('"','').replace("'","").replace(".", "").lower()
            if isInput:
                taskTime = currentTime
                pieces = [x.strip().replace(" ", "_") for x in sentence.split(",")]
                sentence = " ".join(pieces)
                if len(pieces) == 3:
                    if pieces[0].replace("_", " ") not in inp or pieces[2].replace("_", " ") not in inp:
                        continue
                stamp = [evidentalBaseID]
                evidentalBaseID += 1
            else:
                statements = [x.strip() for x in sentence.split(",")]
                if len(statements) != 3:
                    continue
                InferenceResult = NAL_Syllogisms(memory, Memory_retrievePremises(memory, [statements[0], statements[1]]), statements[2], isDeduction, isInduction, isAbduction)
                if InferenceResult is not None:
                    sentence, taskTime, truth, stamp, Stamp_IsOverlapping = InferenceResult
                    if Stamp_IsOverlapping: #not valid to infer due to stamp overlap
                        continue
                else:
                    continue
            sentence = " ".join([x.strip() for x in sentence.split(",")])
            Memory_digest_sentence(currentTime, memory, sentence, truth, stamp, taskTime, PrintMemoryUpdates, TimeHandling)
            printsentence = sentence if isInput else x
            printsentence = printsentence.replace(", ",",").replace(","," ").replace("_"," ")
            if PrintTruthValues:
                print(f"{printsentence}. truth={truth}")
            else:
                print(printsentence)
    return evidentalBaseID
