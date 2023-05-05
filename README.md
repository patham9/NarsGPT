# Comparison baseline (for [NarsGPT](https://github.com/patham9/NarsGPT) and [gptONA](https://github.com/patham9/NarsGPT/tree/gptONA) click here)

A baseline for NarsGPT and gptONA comparison. This baseline uses a combination of recent user input (FIFO buffer as short-term memory) and sentence embeddings for long-term memory. Differently than NarsGPT and gptONA it does not extract relation and property claims but stores the full sentences.

Most obvious shortcoming: it cannot revise relationships, so the user cannot correct a previous information input by himself or another user unless the user would be allowed to directly delete a memory item ("brain surgery").

Other shortcomings related to not supporting other NAL reasoning types are yet to be worked out in detail.

Most obvious benefit: it keeps all the information as the full sentences are stored in long-term memory.
So in question-answering settings where the system should just remember a set of input facts, this baseline might be hard to beat.

TODO: extend it with the text summarization idea, and port over this branch and the others to using Langchain.
