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

belief_prompt_start = """
Commands:
Claim(sentence) ... this relation is claimed to be true in the sentence
NegatedClaim(sentence) ... this relation is claimed to be false in the sentence with an explicit 'not' word
Deduce(premise1,premise2,conclusion) ... the sentence which can be deduced from memory items.
Induce(premise1,premise2,conclusion) ... the sentence which can be induced from memory items.
Abduce(premise1,premise2,conclusion) ... the sentence which can be abduced from memory items.
Question(question) ... raise a question regarding the sentence and other memory items.

Syllogistic inferences should especially be made according to the cases:
Deduce("S is M", "M is P", "S is P")
Induce("A is B", "A is C", "C is B")
Abduce("A is C", "B is C", "B is A")

Capture the complete sentence meaning with code that calls the above functions.
Please make sure that the word "not" is not included in your call, just use Input and NegatedInput.

Memory:
"""

belief_prompt_end = ". Do not forget to make inferences but only involve memory items as arguments, and raise one question!"

question_prompt_start = """
Mention concrete memory contents with certainty values.
Use the minimum involved certainty value.

Memory:
"""

question_prompt_end = " according to Memory? Answer in a probabilistic sense and within 10 words based on memory content only."
#If it should be allowed to consider GPT's 'weight-based' knowledge too, set IncludeGPTKnowledge=True, then the following is utilized:
question_prompt_end_alternative = "? Answer in a probabilistic sense and within 10 words."
