# gptONA (for [NarsGPT](https://github.com/patham9/NarsGPT) click here)

<img src="https://user-images.githubusercontent.com/8284677/234757994-5e8ad001-c5b1-4aa1-abe7-c56a4f7012dd.png" width="200px">

A GPT model prompted to build representations for a Non-Axiomatic Reasoning System ([OpenNARS for Applications](https://github.com/opennars/OpenNARS-for-Applications)). This is the first system implementation which uses GPT together with NARS for reasoning on natural language input. This system can learn in a long-term manner while being able to learn and apply new knowledge effectively.

**Features:**
- Natural open-ended Q&A interaction with the user
- System has no initial knowledge (unless IncludeGPTKnowledge flag is set) but you can simply teach it
- System will make inferences through ONA and will raise questions

**Architecture**

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

- Compared to NarsGPT (which is roughly equally capable in terms of incremental Q&A) this project translates language into the Narsese formal language via GPT and uses ONA for reasoning.

**Already supported:**
- NARS-style declarative inference and question answering with long-term memory storage
- Seamless interfacing with Narsese input and sensorimotor
