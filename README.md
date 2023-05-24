# NarsGPT (for [gptONA](https://github.com/patham9/NarsGPT/tree/gptONA), the recommended branch click here)

<img src="https://user-images.githubusercontent.com/8284677/232368549-5337cf02-63fd-43ae-bf15-6ba9935a5419.png" width="200px">

A NARS implemented as a GPT model prompted to act like a Non-Axiomatic Logic reasoner, with NARS-based memory and control machinery implemented in Python.
This is the first reasoning system implementation which uses GPT for reasoning with long-term memory. Also it is following NARS principles regarding evidence tracking, memory management and attentional control which allows the system to operate in a long-term manner while being able to learn and apply new knowledge effectively.

**Features:**
- Natural open-ended Q&A interaction with the user
- System has no initial knowledge (unless IncludeGPTKnowledge flag is set) but you can simply teach it
- System will make NAL inferences and will raise questions
- System can point out which memory items support a specific conclusion, and how certain it is

**Architecture:**

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

**Compared to NARS with GPT for translating English to Narsese:**

- Compared to gptONA (which is more capable in terms of incremental Q&A) this project makes no attempt to translate language into the Narsese formal language. No formal representations are used in this project but crucial evidence collection principles which support hypotheses formation in uncertain conditions are applied. The benefit is that the overall system is simpler, and that the representations can be more flexible. But they also tend to be more ambiguous and redundant, and both can cause issues in belief revision. Additionally not all inferences GPT suggests are valid, which can cause problems in incremental learning settings as more faulty conclusions can be drawn from unsupported conclusions.
However we believe both projects represent two key alternative directions on the crossroads to AGI and are hence explored in parallel in this 2-branched repository.

![Project Venn Diagram](https://user-images.githubusercontent.com/8284677/234832807-f26aaa18-afb9-4f6e-91ea-c667b74f1a5d.png)

**Already supported:**
- NARS-like declarative inference and question answering with long-term memory storage

**Additionally:**

- There is also the option to use ONA for reliable reasoning (GPT models sometimes propose faulty inference steps) and for a tighter connection to sensorimotor with grounded representations. There is a branch https://github.com/patham9/NarsGPT/tree/gptONA for this purpose, check it out in case you need greater reliability and combination with efficienty event processing for sensorimotor and control purposes.
