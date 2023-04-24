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

def Control_cycle(inp, buf, currentTime, memory, cmd, userQuestion, PrintMemoryUpdates, PrintTruthValues, QuestionPriming):
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
            x = x[7:].replace(",", " ").replace("  ", " ") #.replace('"', "").replace("'", "")
            truth = (0.0, 0.9)
        if x.startswith("RelationClaim") or x.startswith("PropertyClaim"):
            x = x.replace(",", " ").replace("  ", " ") #.replace('"', "").replace("'", "")
        isInput = x.startswith("RelationClaim(") or x.startswith("PropertyClaim(")
        if isInput and ")" in x:
            sentence = x.split("(")[1].split(")")[0].replace('"','').replace("'","").replace(".", "").lower()
            digested = Memory_digest_sentence(inp, currentTime, memory, sentence, truth, PrintMemoryUpdates)
            if digested:
                printsentence = sentence if isInput else x
                if PrintTruthValues:
                    print(f"{printsentence}. truth={truth}")
                else:
                    print(printsentence)
    if userQuestion and QuestionPriming:
        Memory_QuestionPriming(currentTime, "\n".join(cmd), memory, buf)
