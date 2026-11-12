---
name: explore
description: Answer a bounded question about the code or the system, with evidence, and point to the next flow when the answer reveals work. Use when the user asks how something works, where something happens or what they think of an approach ("investiga cómo funciona", "dónde se calcula", "qué opinas de"), or when /dev routes a question here.
---

# explore

Answer one question. Reply to the user in the language they wrote in.

Read the code the question touches; dispatch `Explore` subagents for sweeps across many files and keep their conclusions. Questions about external docs or APIs go to `research`.

Done when the question has an answer backed by evidence: `file:line`, a command and its output, or a cited source. When it cannot be answered from what is reachable, say what is missing.

Answer first, then the evidence. When the answer reveals work, name the flow in one line and wait for the user: a bug → `/diagnose`, a change to make → `/build`, a design to settle → `/design`, something for later → `create-ticket`.
