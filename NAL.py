"""
 * The MIT License
 *
 * Copyright 2023 The OpenNARS authors.
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

def Truth_w2c(w):
    return w / (w + 1.0)

def Truth_c2w(c):
    return c / (1.0 - c)

def Truth_Expectation(v):
    return (v[1] * (v[0] - 0.5) + 0.5)

def Truth_Negation(v):
    return (1-v[0], v[1])

def Truth_Revision(v1, v2):
    (f1, c1) = v1
    (f2, c2) = v2
    w1 = Truth_c2w(c1)
    w2 = Truth_c2w(c2)
    w = w1 + w2
    if w == 0:
        return (0.5, 0.0)
    return (min(1.0, (w1 * f1 + w2 * f2) / w), 
            min(0.99, max(max(Truth_w2c(w), c1), c2)))

def Truth_Deduction(v1, v2):
    (f1, c1) = v1
    (f2, c2) = v2
    return (f1*f2, f1*f2*c1*c2)

def Truth_Abduction(v1, v2):
    (f1, c1) = v1
    (f2, c2) = v2
    return (f2, Truth_w2c(f1 * c1 * c2))

def Truth_Induction(v1, v2):
    return Truth_Abduction(v2, v1)

def Truth_Choice(v1, v2):
    (f1, c1) = v1
    (f2, c2) = v2
    if c1 > c2:
        return v1
    return v2
