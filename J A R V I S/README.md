# J.A.R.V.I.S. One-Click Setup

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 15](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org/)

J.A.R.V.I.S. is a real-time voice assistant framework built around four core capabilities:
- persistent user memory,
- MDS-driven adaptive personalization,
- local document grounding over user-provided files,
- MCP-based tool orchestration for external workflows.

The current acronym used in the project documentation is:
`J.A.R.V.I.S. = Joint Adaptive Real-time Voice Intelligence System`

## Core Features

- Real-time voice interaction using LiveKit Agents and native audio-capable LLMs.
- Memory Depth Score (MDS) for quantifying personalization depth across sessions.
- Adaptive response behavior across `low`, `medium`, and `high` personalization tiers.
- Local document grounding over files placed in the project `knowledge_base/` folder.
- MCP-based tool integration for workflows such as Gmail, Google Drive, and n8n actions.
- Hybrid memory storage with cloud-backed Mem0 support and local JSON fallback.
- One-command bootstrap for local development and deployment.

## Project Structure

```text
.
├── backend/
│   ├── main.py                 # LiveKit worker entrypoint
│   ├── config.py               # user_config.json access layer
│   ├── prompts.py              # dynamic prompt builder
│   ├── memory.py               # cloud/local memory persistence
│   ├── memory_worker.py        # async memory extraction loop
│   ├── document_store.py       # local document grounding layer
│   ├── mcp_client/             # MCP server + tool adapter layer
│   └── tools/                  # utility tools (weather, search)
├── frontend/                   # Next.js application
├── knowledge_base/             # put your PDF/DOCX/TXT/CSV/JSON/MD files here
├── docs/                       # reports, paper draft, evaluation docs
├── scripts/
│   └── setup/bootstrap.py      # one-command environment bootstrap
├── assistant.bat               # Windows launcher
└── user_config.json            # runtime config (not committed)
```

## Quick Start

### Prerequisites
- Python `3.13+`
- Node.js `v20+`
- `pnpm` (bootstrap can install it if missing)

### Run

```bash
# Windows
assistant.bat start

# macOS / Linux
python3 scripts/setup/bootstrap.py start
```

This will:
1. validate runtime prerequisites,
2. create/install backend virtualenv dependencies,
3. install frontend dependencies,
4. start backend and frontend together.

## Configuration

Store runtime configuration in `user_config.json` at the repository root.
Use [user_config.example.json](./user_config.example.json) as the template.

Typical required fields:
- LiveKit: `livekit_url`, `livekit_key`, `livekit_secret`
- One LLM provider key: `google` or `openai`

Optional integrations:
- `mem0`
- `openweather`
- `google_search`
- `search_engine_id`
- `n8n_url`

Optional knowledge-base config:
- `knowledge_base.documents_dir`

If `knowledge_base.documents_dir` is not set, the project uses:
- [knowledge_base](./knowledge_base)

## Local Document Grounding

Place supported files in:
- [knowledge_base](./knowledge_base)

Supported file types:
- `.txt`
- `.md`
- `.json`
- `.csv`
- `.docx`
- `.pdf`

How it works:
1. The backend scans the folder at session startup.
2. It exposes local assistant tools:
   - `list_local_documents`
   - `search_local_documents`
3. When the user asks about a report, notes, PDF, or uploaded file, the assistant can retrieve matching passages and answer from them.

## Verified Benchmark Snapshot

From the current local 50-run benchmark:
- `MDS computation`: average `1.23 ms`, min `1.12 ms`, max `2.28 ms`, std dev `0.17 ms`, p95 `1.34 ms`
- `Datetime utility`: average `0.24 ms`, min `0.21 ms`, max `0.60 ms`, std dev `0.06 ms`, p95 `0.28 ms`

Results file:
- [local_benchmark_results_50_runs.json](./docs/results/local_benchmark_results_50_runs.json)

## Documentation

- [JARVIS_IEEE_Corrected_Draft.md](./docs/JARVIS_IEEE_Corrected_Draft.md)
- [Massive_Detailed_Project_Report_JARVIS.txt](./docs/Massive_Detailed_Project_Report_JARVIS.txt)
- [paper_ready_summary.md](./docs/results/paper_ready_summary.md)
- [MDS_Evaluation_Protocol.txt](./docs/MDS_Evaluation_Protocol.txt)

## Git Hygiene

The repository is configured to keep generated artifacts and secrets out of version control.

Do not commit:
- `user_config.json`
- local API keys
- `.env.local`
- generated build folders
- local memory dumps if they contain sensitive data

## License

MIT
