belief_prompt_start = """
Commands:
Claim(sentence) ... this relation is claimed to be true in the sentence
NegatedClaim(sentence) ... this relation is claimed to be false in the sentence with an explicit 'not' word
Deduce(premise1,premise2,conclusion) ... the sentence which can be deduced from memory items.
Induce(premise1,premise2,conclusion) ... the sentence which can be induced from memory items.
Abduce(premise1,premise2,conclusion) ... the sentence which can be abduced from memory items.

Syllogistic inferences should especially be made according to the cases:
Deduce("S is M", "M is P", "S is P")
Induce("A is B", "A is C", "C is B")
Abduce("A is C", "B is C", "B is A")

Capture the complete sentence meaning with code that calls the above functions.
Please make sure that the word "not" is not included in your call, just use Input and NegatedInput.

Memory:
"""

belief_prompt_end = ". Do not forget to make inferences but only involve memory items as arguments!"

question_prompt_start = """
Mention concrete memory contents with certainty values.
Use the minimum involved certainty value.

Memory:
"""

question_prompt_end = " according to Memory? Answer in a probabilistic sense and within 10 words based on memory content only."
