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

Prompts_belief_start = """
RelationClaim(noun,verb,noun) ... this relation is claimed to be true in the sentence
RelationClaim(noun,"IsA",noun) ... this relation is claimed to be true in the sentence
PropertyClaim(noun,"HasProperty", adjective) ... this relation is claimed to be true in the sentence
NegatedRelationClaim(noun,verb,noun) ... this relation is claimed to be false in the sentence with an explicit 'not' word
NegatedRelationClaim(noun,"IsA",noun) ... this relation is claimed to be false in the sentence with an explicit 'not' word
NegatedPropertyClaim(noun,"HasProperty",adjective) ... this relation is claimed to be false in the sentence with an explicit 'not' word

Capture the complete sentence meaning with code that calls the four functions.
Please make sure that the word "not" is not included in your call, just use the functions and Negated functions instead.
And use verbs for comparative relations!

Memory:
"""

Prompts_belief_end = "Encode all relations in the sentence, and the sentence has to be believed!"

Prompts_question_start = """
Mention concrete memory contents with certainty values.
Use the minimum involved certainty value.

Memory:
"""

Prompts_question_end = " according to Memory and which memory item i? Answer in a probabilistic sense and within 15 words based on memory content only."
#If it should be allowed to consider GPT's 'weight-based' knowledge too, set IncludeGPTKnowledge=True, then the following is utilized:
Prompts_question_end_alternative = " and which memory item i? Answer in a probabilistic sense and within 15 words."
