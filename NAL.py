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

from Truth import *
from Stamp import *

def NAL_Syllogisms(memory, statements, isDeduction, isInduction, isAbduction):
    if statements[0] not in memory or statements[1] not in memory:
        return None
    premise1, premise2 = memory[statements[0]], memory[statements[1]]
    if isDeduction or isInduction or isAbduction:
        if len(statements) != 3:
            return None
        if statements[0] not in memory or statements[1] not in memory:
            return None
        if isDeduction:
            #start additional guards for deductions:
            if isDeduction and " isa " not in statements[0] + " " + statements[1] and \
                               " are " not in statements[0] + " " + statements[1]:
                return None
            if len(statements[0].split(" ")) != 3 and len(statements[1].split(" ")) != 3:
                return None
            lastword_st0 = statements[0].split(" ")[-1]
            firstword_st0 = statements[0].split(" ")[0]
            lastword_st1 = statements[1].split(" ")[-1]
            firstword_st1 = statements[1].split(" ")[0]
            if lastword_st0 not in firstword_st1 and firstword_st1 not in lastword_st0 and \
               lastword_st1 not in firstword_st0 and firstword_st0 not in lastword_st1:
                   return None
            #end deduction guards
            truth = Truth_Deduction(premise1[2], premise2[2])
        elif isInduction:
            truth = Truth_Induction(premise1[2], premise2[2])
        elif isAbduction:
            truth = Truth_Abduction(premise1[2], premise2[2])
        stamp = Stamp_make(premise1[3], premise2[3])
        Stamp_IsOverlapping = Stamp_hasOverlap(premise1[3], premise2[3])
        conclusion = statements[2]
        return conclusion, truth, stamp, Stamp_IsOverlapping
    return None

def NAL_Revision_And_Choice(truth1, stamp1, truth2, stamp2):
    if not Stamp_hasOverlap(stamp1, stamp2):
        return Truth_Revision(truth1, truth2), Stamp_make(stamp1, stamp2)
    else:
        if truth1[1] > truth2[1]:
            return truth1, stamp1
        else:
            return truth2, stamp2
