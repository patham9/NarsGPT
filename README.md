# NarsGPT
A NARS implemented as a GPT model prompted to act like a Non-Axiomatic Logic reasoner, with NARS-based memory and control machinery implemented in Python.
This is the first reasoning system implementation which uses GPT for reasoning with long-term memory. Also it is following NARS principles regarding evidence tracking, memory management and attentional control which allow the system to operate in a long-term manner while being able to learn and apply new knowledge effectively.

Special features:
- Sentences are not stored in logical/structural form as in other NARS implementations, but in natural language sentences
- Accurate truth calculations are carried out via an inference machinery invoked by GPT.
- GPT uses the inference machinery based on its dynamic attention buffer content and a static part of the prompt which includes descriptions of NAL reasoning.
- Structures: Attention buffer and long-term sentence memory which can go far beyond GPT's context window.
- The attention buffer is a view of up to k relevant items in its memory decided based on recency, usefulness and relevance to other items in the attention buffer.
- Certainty values are a summary of NAL truth values (based on truth-expectation formula) which GPT does not (need to) see.

Compared to other projects such as AutoGPT:

- NarsGPT is a proper solution for reasoning and memory maintenance to build more effective adaptive systems which could operate autonomously.
- It builds on decades of knowledge about reasoning under uncertainty, evidence tracking and resource allocation in Non-Axiomatic Reasoning Systems.

Already supported in v0.1:
- NARS-like declarative inference and question answering with long-term memory storage

TODO for later:

- Episodic memory view as part of the attention buffer, introducing innate time notions as described in NAL-7 (occurrenceTime, temporal relations, anticipation).
- Goal and procedural memory view as part of the attention buffer and NARS-based decision making principles as described in NAL-8. This includes prompt encodings for executable operations, operation choice based on maximum truth expectation, etc.

