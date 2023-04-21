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
RelationClaim(noun,verb,noun)
RelationClaim(noun,"IsA",noun)
PropertyClaim(noun,"HasProperty", adjective)
NegatedRelationClaim(noun,verb,noun) ... this relation is claimed to be false in the sentence with an explicit 'not' word
NegatedRelationClaim(noun,"IsA",noun) ... this relation is claimed to be false in the sentence with an explicit 'not' word
NegatedPropertyClaim(noun,"HasProperty",adjective) ... this relation is claimed to be false in the sentence with an explicit 'not' word
Question(question) ... raise a question regarding the sentence and other memory items.

Capture the complete sentence meaning with code that calls the four functions, and only use a single word per argument.
Please make sure that the word "not" is not included in your call, just use the functions and Negated functions instead.
And use verbs for comparative relations!

Memory:
"""

Prompts_belief_end = "Encode all relations in the sentence, also raising one question!"

Prompts_inference_start = """
Commands:
Deduce(premise1,premise2,conclusion) ... the sentence which can be deduced from memory items.
Induce(premise1,premise2,conclusion) ... the hypothesis which can be induced from memory items.
Abduce(premise1,premise2,conclusion) ... the hypothesis which can be abduced from memory items.

Rules: #Syllogistic inferences should especially be made according to the cases:

Deduce("A isa B", "B isa C", "A isa C") #the last word of the first premise is required to be the same as the first word of the second premise!!!
Induce("A isa B", "A isa C", "C isa B") #speculative conclusion, very important to use instead of Deduce when it matches!!!
Abduce("A isa C", "B isa C", "B isa A") #speculative conclusion, very important to use instead of Deduce when it matches!!!

Deduce("A isa B", "B HasProperty C", "A HasProperty C") #the last word of the first premise is required to be the same as the first word of the second premise!!!
Induce("A hasproperty B", "A hasproperty C", "C isa B") #speculative conclusion, very important to use instead of Deduce when it matches!!!
Abduce("A hasproperty C", "B hasproperty C", "B isa A") #speculative conclusion, very important to use instead of Deduce when it matches!!!

Deduce("A isa B", "B verb C", "A verb C") #the last word of the first premise is required to be the same as the first word of the second premise!!!
Induce("A verb B", "A verb C", "C isa B") #speculative conclusion, very important to use instead of Deduce when it matches!!!
Abduce("A verb C", "B verb C", "B isa A") #speculative conclusion, very important to use instead of Deduce when it matches!!!

Memory:
"""

Prompts_inference_end = ". Do not forget to make inferences according to the rules but only involve memory items as arguments and do not create new words!"

Prompts_question_start = """
Mention concrete memory contents with certainty values.
Use the minimum involved certainty value.

Memory:
"""

Prompts_question_end = " according to Memory? Answer in a probabilistic sense and within 15 words based on memory content only."
#If it should be allowed to consider GPT's 'weight-based' knowledge too, set IncludeGPTKnowledge=True, then the following is utilized:
Prompts_question_end_alternative = "? Answer in a probabilistic sense and within 10 words."
