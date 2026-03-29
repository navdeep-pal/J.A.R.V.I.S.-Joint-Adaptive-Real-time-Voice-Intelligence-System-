# J.A.R.V.I.S.: A Real-Time Voice Assistant Framework with MDS-Driven Adaptive Personalization, Local Document Grounding, and MCP-Based Tool Integration

Dev Agarwal
Department of Computer Science and Engineering
Graphic Era University, Dehradun, India
[devagarwal2468@gmail.com]

Prof Dr Durgaprasad Gangodkar
Department of Computer Science and Engineering
Graphic Era University, Dehradun, India
[durgaprasad@gmail.com]

Navdeep Pal
Department of Computer Science and Engineering
Graphic Era University, Dehradun, India
[Navdeepal@gmail.com]

## Abstract
This paper presents J.A.R.V.I.S., a real-time voice assistant framework that unifies persistent memory, adaptive personalization, local document grounding, and tool-augmented interaction within a single deployable architecture. The system integrates a LiveKit-based real-time audio backend, configurable large language model providers with automatic fallback, a hybrid memory layer supporting local JSON and cloud-backed persistence, a local document knowledge base for grounded responses over user-provided files, and MCP-enabled tool orchestration for external workflow execution. The primary contribution is the Memory Depth Score (MDS), a bounded 0-100 personalization metric computed as a weighted combination of memory density (50%), session continuity (30%), and topic breadth (20%). Unlike conventional systems that treat stored memory as passive retrieval context, J.A.R.V.I.S. operationalizes MDS as an active control signal that dynamically modulates assistant response strategy across three progressive adaptation tiers: low, medium, and high personalization. Local benchmarking over 50 runs shows that MDS computation incurs an average latency of 1.23 ms, with a minimum of 1.12 ms, a maximum of 2.28 ms, a standard deviation of 0.17 ms, and a p95 latency of 1.34 ms. These results establish MDS-driven adaptation as a computationally lightweight and practically deployable mechanism for long-term personalized real-time voice interaction.

**Index Terms** - Voice AI, Real-time Agent, Memory Depth Score, Adaptive Personalization, LiveKit, Model Context Protocol, Persistent Memory, Agentic AI

## I. INTRODUCTION
Voice-based AI assistants have transitioned from novelty to utility, yet the dominant architecture of widely deployed systems remains largely session-bounded. In many production assistants, each interaction begins with limited carryover of user-specific history, preferences, or prior contextual patterns. As a result, personalization is often shallow, inconsistent, or restricted to short-term conversational context. This limitation has been recognized in the broader literature on conversational memory and retrieval-augmented systems, but its integration into deployable real-time voice assistants remains limited.

At the same time, several technological developments have made advanced voice AI systems increasingly practical: (a) native audio large language models that unify speech understanding and generation in a single streaming pipeline, (b) production-grade real-time session orchestration frameworks such as LiveKit Agents, (c) the Model Context Protocol (MCP), which enables structured and extensible external tool integration, and (d) lightweight local document-grounding pipelines that allow assistants to respond from user-provided files without requiring a full external retrieval stack. Together, these developments provide the systems foundation for voice assistants that are not only conversational, but also adaptive, persistent, grounded, and action-capable.

This paper presents J.A.R.V.I.S. (Joint Adaptive Real-time Voice Intelligence System), a real-time voice assistant framework built on these foundations. Its central contribution is the Memory Depth Score (MDS), a bounded metric that quantifies the depth of user-specific memory accumulated across sessions and uses this signal to modulate assistant response strategy. In contrast to architectures where memory is stored only for passive retrieval, J.A.R.V.I.S. closes the loop between measured memory state and active behavioral adaptation. The framework further extends assistant grounding through a local document knowledge base that allows runtime retrieval over user-provided files.

The main contributions of this paper are as follows:
- A Memory Depth Score (MDS), defined as a bounded 0-100 composite metric for quantifying multi-session personalization depth using memory density, session continuity, and topic breadth.
- A memory-conditioned behavioral adaptation mechanism that uses MDS to dynamically modulate assistant response strategy across three personalization tiers, thereby forming a closed memory-behavior feedback loop.
- A lightweight local document-grounding module that allows the assistant to inspect and search user-provided PDF, DOCX, TXT, CSV, JSON, and Markdown files from a dedicated knowledge-base folder.
- A reusable MCP-to-LiveKit integration layer that enables dynamic tool discovery and invocation within a real-time voice assistant pipeline.
- A deployable full-stack assistant architecture that combines real-time audio interaction, persistent memory, adaptive personalization, grounded document access, and external workflow execution.
- A local benchmark demonstrating that MDS-driven adaptation introduces negligible computational overhead, with an average MDS computation latency of 1.23 ms over 50 runs.

## II. RELATED WORK
### A. Memory in Conversational Agents
Memory management in conversational AI has been explored through dialogue state tracking, retrieval-augmented generation, and long-term memory retrieval mechanisms. Prior work has shown that structured memory can improve coherence and long-horizon consistency in interactive agents. However, existing approaches primarily treat memory as stored context for retrieval. To the best of our knowledge, prior work has not operationalized personalization depth as a bounded metric directly coupled to response-strategy modulation in a real-time voice assistant setting.

### B. Agentic Tool Use
Tool-augmented reasoning has been studied through agent frameworks such as ReAct and Toolformer, which demonstrate that language models can selectively invoke external functions. MCP extends this direction by standardizing tool schema definition and transport, enabling heterogeneous tools to be consumed through a consistent interface. J.A.R.V.I.S. adopts MCP as its tool integration standard and extends its use into real-time voice sessions through a custom adapter layer.

### C. LLM-Based Voice Assistants
Recent large language model systems have advanced from text-only reasoning to native multimodal and audio-capable interaction. These developments reduce reliance on fragmented ASR-NLU-TTS pipelines and support lower-latency, more natural conversational flows. J.A.R.V.I.S. builds on this trend by combining real-time voice interaction with persistent memory, adaptive personalization, local document grounding, and extensible external tool use.

## III. SYSTEM ARCHITECTURE
J.A.R.V.I.S. follows a layered architecture with six principal components: (1) a Next.js frontend providing the browser-accessible voice interface via the LiveKit JavaScript SDK, (2) a LiveKit media layer handling real-time audio transport, (3) a Python 3.13 agent worker hosting the AI pipeline, MDS computation, MCP client, and local document tools, (4) a configurable LLM provider layer with fallback handling, (5) a hybrid memory layer using cloud-backed storage when configured and local JSON persistence as a fallback, and (6) a local document knowledge base that indexes user-provided files from a dedicated folder for grounded retrieval.

### A. Session Lifecycle
On session initiation, the frontend requests connection details and joins the LiveKit session. The backend worker initializes session state, retrieves prior memory, computes the user's MDS score, inspects the local document knowledge base, and constructs the system prompt before starting the agent session. The computed personalization tier and document-availability context are injected into the prompt so that response behavior is conditioned from the beginning of the interaction.

### B. LLM Fallback Strategy
The framework supports configurable provider selection and fallback handling. In the current implementation, supported model variants are attempted in priority order until a valid session-capable configuration is established. This reduces operational fragility in the presence of model deprecations, provider-side changes, or configuration mismatch.

### C. Hybrid Memory Layer
The memory subsystem supports both cloud-backed persistence and local JSON storage. When cloud credentials are available, the assistant can use the external memory service; otherwise, it continues in local mode without disabling the broader voice pipeline. This dual-path design improves deployability and fault tolerance while preserving a consistent personalization interface.

### D. Local Document Knowledge Base
The framework includes a dedicated knowledge-base folder for user-provided files. At startup, the backend scans supported formats including PDF, DOCX, TXT, CSV, JSON, and Markdown, extracts textual content, segments it into compact chunks, and exposes two runtime tools to the assistant: one for listing available local documents and one for searching relevant passages. This enables grounded responses over user-supplied files without requiring an external vector database dependency.

## IV. MEMORY DEPTH SCORE (MDS)
The Memory Depth Score is the central contribution of this work. It quantifies how thoroughly the assistant has built a model of a specific user across sessions, producing a single bounded scalar that can be tracked, compared, and acted upon.

### A. Metric Definition
MDS is computed as a weighted composite of three sub-metrics:

MDS = 0.50 Md + 0.30 Ms + 0.20 Mt

where Md is memory density, Ms is session continuity, and Mt is topic breadth. Memory density reflects the normalized count of retained memory items, session continuity estimates repeated engagement across interaction history, and topic breadth captures the diversity of recurring user-specific themes derived from stored memory. The final score is bounded to the interval [0, 100].

### B. Component Weights
- Memory Density (Md): 50%  
  Rationale: emphasizes the retained volume of user-specific facts.
- Session Continuity (Ms): 30%  
  Rationale: reflects repeated multi-session engagement.
- Topic Breadth (Mt): 20%  
  Rationale: captures diversity in the modeled user context.

### C. Personalization Tiers
The computed MDS maps to one of three behavioral tiers that govern the assistant's response strategy:
- Low (0-33): exploratory behavior that prioritizes preference discovery and clarification.
- Medium (34-66): reinforcing behavior that selectively references known preferences and prior context.
- High (67-100): proactive behavior that anticipates likely user needs and offers more personalized continuity.

### D. Memory-Behavior Feedback Loop
The central systems insight is that MDS is not merely descriptive. It is used as an active control signal during session initialization and response conditioning. As user interactions accumulate across sessions, memory depth increases, the MDS value changes, and the assistant's response policy moves across the defined personalization tiers. This creates a closed loop between memory accumulation and behavioral adaptation.

## V. MCP TOOL INTEGRATION
J.A.R.V.I.S. implements an adapter layer that enables a LiveKit-based voice agent to discover and invoke tools exposed by MCP-compatible servers.

### A. MCP Server Connectivity
The backend establishes a session with the configured MCP server using an SSE-based client flow. Tool metadata can be cached at session scope to avoid repeated discovery overhead within a single interaction.

### B. Schema-to-Function Adaptation
MCP tool schemas are translated into callable function interfaces compatible with the voice agent runtime. Tool arguments are serialized in JSON form, passed to the remote tool endpoint, and normalized into string outputs consumable by the LLM layer.

### C. Runtime Tool Binding
Tool signatures are generated dynamically from MCP schemas and exposed to the assistant through the function-calling interface. This allows the framework to remain extensible without hardcoding every external action into the assistant core. If the MCP endpoint is unavailable, the session can continue without tool support rather than terminating abruptly.

## VI. IMPLEMENTATION
### A. Adaptive Response Length
The system prompt encodes a query-aware verbosity policy: simple factual queries are constrained to one sentence, complex or task-oriented queries to three sentences, emotional or personal queries to two sentences with a warmer tone, and ambiguous queries to concise two-sentence responses. A user may still request more detail explicitly. This mechanism is implemented entirely through prompt design and does not require model fine-tuning.

### B. Local Document Grounding
A lightweight local retrieval layer enables grounded answers over project or personal documents placed in a dedicated knowledge-base folder. The current implementation performs format-aware text extraction, chunking, and keyword-overlap retrieval. Rather than treating documents as a static prompt appendix, the assistant receives callable local tools that can enumerate files and retrieve relevant passages at runtime when the user asks about uploaded material.

### C. Asynchronous Memory Extraction
A background memory extraction coroutine periodically reviews newly added session messages and persists them to the memory backend without blocking the live interaction path. This allows memory accumulation to proceed concurrently with voice interaction while minimizing impact on response latency.

### D. Bootstrap and Deployment
The project includes a bootstrap utility that validates runtime prerequisites, initializes the Python environment, installs dependencies, and launches the application stack. This simplifies reproduction and reduces setup friction for local deployment.

## VII. EVALUATION
### A. MDS Computational Benchmark
To evaluate the computational feasibility of introducing MDS computation into a real-time assistant pipeline, we conducted a controlled 50-run local benchmark. Table I summarizes the resulting latency statistics.

| Metric | MDS (ms) | Datetime Baseline (ms) |
|---|---:|---:|
| Average Latency | 1.23 | 0.24 |
| Minimum Latency | 1.12 | 0.21 |
| Maximum Latency | 2.28 | 0.60 |
| Standard Deviation | 0.17 | 0.06 |
| p95 Latency | 1.34 | 0.28 |
| Success Rate | 100% | 100% |

MDS evaluation completed successfully in all 50 runs. The average latency of 1.23 ms, compared with 0.24 ms for a lightweight datetime baseline, indicates that the personalization score introduces only a small local computational overhead. This supports the practical inclusion of MDS within a real-time voice assistant pipeline.

### B. Evaluation Scope
The present evaluation is focused on computational feasibility and deployability of the implemented personalization mechanism. Specifically, it establishes that MDS can be computed reliably with negligible overhead in the current implementation. The local document-grounding and MCP integration modules are described at the systems level in accordance with the implemented runtime architecture; however, this paper reports only the measured benchmark results that were directly collected for the MDS computation path.

## VIII. DISCUSSION
The proposed MDS framework introduces a useful systems abstraction for voice assistants: memory as a quantified behavioral driver rather than a passive retrieval store. Because the score is bounded and derived from interpretable sub-components, it can be inspected, logged, and adapted without dependence on a single model provider or memory backend.

The three-tier adaptation model is intentionally simple. Real-world personalization likely exists on a continuum; however, discrete tiers provide predictable and testable behavioral boundaries that are practical for deployable systems.

The local document knowledge base addresses grounded access to user-supplied files, while the MCP adapter layer addresses extensible actionability across external services. Together, MDS-driven personalization, local document grounding, and MCP-based tool orchestration allow the assistant to evolve beyond a stateless conversational interface into a persistent, grounded, tool-augmented interaction system. The novelty of the framework lies not in storing memory alone, but in converting accumulated memory depth into a runtime control signal while unifying that adaptation with grounded document access and external tool invocation inside one real-time voice pipeline.

## IX. CONCLUSION
This paper presented J.A.R.V.I.S., a real-time voice assistant framework centered on persistent memory, adaptive personalization, local document grounding, and extensible tool use. Its primary technical contribution is the Memory Depth Score, a bounded metric that quantifies multi-session personalization depth and drives a three-tier behavioral adaptation policy. The framework further demonstrates how local document retrieval, MCP-based tool integration, and real-time voice orchestration can be combined within a single deployable architecture. Local benchmarking shows that MDS computation adds negligible overhead, with an average latency of 1.23 ms over 50 runs. Collectively, these results support MDS-driven adaptation as a practical mechanism for long-term personalized real-time voice interaction.

## REFERENCES
[1] A. Vaswani et al., "Attention Is All You Need," in *Proc. NeurIPS*, 2017.  
[2] P. Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," in *Proc. NeurIPS*, 2020.  
[3] J. D. Williams, A. Raux, and M. Henderson, "The Dialog State Tracking Challenge Series," *Dialogue and Discourse*, vol. 7, no. 3, 2016.  
[4] J. Kaplan et al., "Scaling Laws for Neural Language Models," arXiv:2001.08361, 2020.  
[5] Google DeepMind, "Gemini: A Family of Highly Capable Multimodal Models," Technical Report, 2023.  
[6] OpenAI, "GPT-4 Technical Report," arXiv:2303.08774, 2023.  
[7] S. Yao et al., "ReAct: Synergizing Reasoning and Acting in Language Models," in *Proc. ICLR*, 2023.  
[8] T. Schick et al., "Toolformer: Language Models Can Teach Themselves to Use Tools," in *Proc. NeurIPS*, 2023.  
[9] J. S. Park et al., "Generative Agents: Interactive Simulacra of Human Behavior," in *Proc. ACM UIST*, 2023.  
[10] LiveKit, Inc., "LiveKit Agents SDK Documentation," 2024. [Online]. Available: https://docs.livekit.io/agents  
[11] Anthropic, "Model Context Protocol Specification," 2024. [Online]. Available: https://modelcontextprotocol.io/  
[12] Mem0, Inc., "Mem0 Memory Layer for AI Agents," 2024. [Online]. Available: https://docs.mem0.ai/  
