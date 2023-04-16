belief_prompt = """
Commands:
Input(sentence) ... this relation is true in the sentence
NegatedInput(sentence) ... this relation is false in the sentence
Deduce(premise1,premise2,conclusion) ... the sentence which can be deduced from memory items.
Induce(premise1,premise2,conclusion) ... the sentence which can be induced from memory items.
Abduce(premise1,premise2,conclusion) ... the sentence which can be abduced from memory items.

Syllogistic inferences should especially be made according to the cases:
Deduce("S is M", "M is P, "S is P"
Induce("A is B", "A is C", "C is B")
Abduce("A is C", "B is C", "B is A")

Capture the complete sentence meaning with code that calls the above functions.
Please make sure that the word "not" is not included in your call, just use Claim and NegatedClaim.

Memory:
"""

question_prompt = """
Mention concrete memory contents with certainty values.
Use the minimum involved certainty value.

Memory:
"""
