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

def NAL_Syllogisms(memory, premises, conclusion, isDeduction, isInduction, isAbduction):
    if premises is None:
        return None
    premise1, premise2, conclusionTime = premises
    if isDeduction or isInduction or isAbduction:
        if isDeduction:
            #start additional guards for deductions:
            if " isa " not in premise1[0][0] + " " + premise2[0][0] and \
               " are " not in premise1[0][0] + " " + premise2[0][0]:
                return None
            if len(premise1[0][0].split(" ")) != 3 and len(premise2[0][0].split(" ")) != 3:
                return None
            lastword_st0 = premise1[0][0].split(" ")[-1]
            firstword_st0 = premise1[0][0].split(" ")[0]
            lastword_st1 = premise2[0][0].split(" ")[-1]
            firstword_st1 = premise2[0][0].split(" ")[0]
            if lastword_st0 not in firstword_st1 and firstword_st1 not in lastword_st0 and \
               lastword_st1 not in firstword_st0 and firstword_st0 not in lastword_st1:
                   return None
            #end deduction guards
            truth = Truth_Deduction(premise1[1][2], premise2[1][2])
        elif isInduction:
            truth = Truth_Induction(premise1[1][2], premise2[1][2])
        elif isAbduction:
            truth = Truth_Abduction(premise1[1][2], premise2[1][2])
        stamp = Stamp_make(premise1[1][3], premise2[1][3])
        Stamp_IsOverlapping = Stamp_hasOverlap(premise1[1][3], premise2[1][3])
        return conclusion, conclusionTime, truth, stamp, Stamp_IsOverlapping
    return None

def NAL_Revision_And_Choice(truth1, stamp1, truth2, stamp2):
    if not Stamp_hasOverlap(stamp1, stamp2):
        return Truth_Revision(truth1, truth2), Stamp_make(stamp1, stamp2)
    else:
        if truth1[1] > truth2[1]:
            return truth1, stamp1
        else:
            return truth2, stamp2

def NAL_Projection(premise, conclusionTime):
    ((term, time), (lastUsed, useCount, TV, stamp, embedding)) = premise
    return ((term, conclusionTime), (lastUsed, useCount, Truth_Projection(TV, time, conclusionTime), stamp))
