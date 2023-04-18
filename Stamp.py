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

def Stamp_make(stamp1, stamp2, stamp_size_max = 10):
    ret = []
    processStamp1, processStamp2 = (True, True)
    j,i = (0,0)
    while i<stamp_size_max:
        if processStamp1:
            if i < len(stamp1):
                ret.append(stamp1[i])
                if len(ret) >= stamp_size_max:
                    break;
            else:
                processStamp1 = False
        if processStamp2:
            if i < len(stamp2):
                ret.append(stamp2[i])
                if len(ret) >= stamp_size_max:
                    break
        if not processStamp1 and not processStamp2:
            break
        i += 1
    return ret

def Stamp_hasOverlap(a, b):
    return len(set(a) & set(b)) > 0
