# NARS-GPT

<img src="https://user-images.githubusercontent.com/8284677/232368549-5337cf02-63fd-43ae-bf15-6ba9935a5419.png" width="200px">

A GPT model as a language channel to build representations for a Non-Axiomatic Reasoning System ([OpenNARS for Applications](https://github.com/opennars/OpenNARS-for-Applications)). This is the first system implementation which uses GPT together with NARS for reasoning on natural language input. This system can learn in a long-term manner while being able to learn and apply new knowledge effectively.

[![NARS-GPT](https://img.youtube.com/vi/l4rklYGbcTo/0.jpg)](https://www.youtube.com/watch?v=l4rklYGbcTo "Integrating GPT and NARS (gptONA)")

**Features:**
- Natural open-ended Q&A interaction with the user
- System has no initial knowledge (unless IncludeGPTKnowledge flag is set) but you can simply teach it
- System will make inferences through ONA and will raise questions
- System can point out which memory items support a specific conclusion, and how certain it is

**Architecture:**

![gptONA Architecture](https://user-images.githubusercontent.com/8284677/234759143-0fc48767-68cd-44fc-800a-fc7023e11f37.png)

**Technical aspects:**
- Sentences are stored in logical/structural form as in other NARS implementations.
- Accurate reasoning with truth calculations are carried out via ONA.
- Structures: Attention buffer and long-term sentence memory which can go far beyond GPT's context window.
- The attention buffer is a view of up to k relevant items in ONA's memory decided based on recency, usefulness and relevance to other items in the attention buffer.
- The long-term memory can be set to be bounded, items with low use counter and last-used stamp the longest ago will be removed first.
- Certainty values provide a summary of NAL truth values (based on truth-expectation formula) which is relevant in Q&A and in decision making.

**Compared to other GPT with Long-term memory projects such as AutoGPT:**

- Having the AI maintain a useful and evidentally supported set of beliefs through reasoning is the goal in this project, invoking software tools will come later.
- gptONA is a proper solution for reasoning, truth maintenance and automated memory management, to build more effective adaptive systems which could operate autonomously.
- It builds on decades of knowledge about reasoning under uncertainty, evidence tracking and resource allocation in Non-Axiomatic Reasoning Systems.

**Compared to implementing a NARS via GPT:**

- This project translates language into the Narsese formal language via GPT and uses ONA for reasoning. This guarantees that conclusions are supported by the evidence and never faulty, and that representations are not ambiguous or redundant which makes belief revision easier when new evidence about a specific relation is presented to the system. Also this system can process Narsese events (dozens of events per second) in addition to the slow English input, which allows NARS sensorimotor capabilities to be utilized.

**Already supported:**
- NARS-style declarative inference and question answering with long-term memory storage
- Seamless interfacing with Narsese input and sensorimotor
