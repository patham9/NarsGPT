# NarsGPT

<img src="https://user-images.githubusercontent.com/8284677/232368549-5337cf02-63fd-43ae-bf15-6ba9935a5419.png" width="200px">

A NARS implemented as a GPT model prompted to act like a Non-Axiomatic Logic reasoner, with NARS-based memory and control machinery implemented in Python.
This is the first reasoning system implementation which uses GPT for reasoning with long-term memory. Also it is following NARS principles regarding evidence tracking, memory management and attentional control which allow the system to operate in a long-term manner while being able to learn and apply new knowledge effectively.

**Features:**
- Natural Q&A interaction with the user
- System has no initial knowledge (unless IncludeGPTKnowledge flag is set) but you can simply teach it
- System will make NAL inferences and will raise questions

**Architecture**

![NarsGPT Architecture](https://user-images.githubusercontent.com/8284677/232365471-faa3ccaf-5078-4830-905f-e8d7d520dde6.png)

**Technical aspects:**
- Sentences are not stored in logical/structural form as in other NARS implementations, but in natural language sentences
- Accurate truth calculations are carried out via an inference machinery invoked by GPT.
- GPT uses the inference machinery based on its dynamic attention buffer content and a static part of the prompt which includes descriptions of NAL reasoning.
- Structures: Attention buffer and long-term sentence memory which can go far beyond GPT's context window.
- The attention buffer is a view of up to k relevant items in its memory decided based on recency, usefulness and relevance to other items in the attention buffer.
- The long-term memory can be set to be bounded, items with low use counter and last-used stamp the longest ago will be removed first.
- Certainty values provide a summary of NAL truth values (based on truth-expectation formula) which is relevant in Q&A and later also in decision making.

**Compared to other GPT with Long-term memory projects such as AutoGPT:**

- Having the AI maintain a useful and evidentally supported set of beliefs through reasoning is the goal in this project, invoking software tools will come later.
- NarsGPT is a proper solution for reasoning, truth maintenance and automated memory management, to build more effective adaptive systems which could operate autonomously.
- It builds on decades of knowledge about reasoning under uncertainty, evidence tracking and resource allocation in Non-Axiomatic Reasoning Systems.

**Compared to NARS with GPT as natural language channel:**

- Compared to the quite successful https://github.com/opennars/OpenNARS-for-Applications/blob/master/misc/Python/english_to_narsese_gpt3.py approach ( which is shown in https://www.youtube.com/watch?v=cpu6TooJ0Dk ) this project makes no attempt to translate language into the Narsese formal language, no formal representations are used in this project but crucial evidence collection principles which support hypotheses formation in uncertain conditions are applied.

**Already supported:**
- NARS-like declarative inference and question answering with long-term memory storage

**Additionally:**

- There is also the option to use ONA for reliable reasoning (GPT models sometimes propose faulty inference steps) and for a tighter connection to sensorimotor with grounded representations. There is a branch https://github.com/patham9/NarsGPT/tree/gptONA for this purpose, check it out in case you need greater reliability and combination with efficienty event processing for sensorimotor and control purposes.
