# Paper-Ready Experimental Summary

## Local Runtime Benchmarks

| Benchmark | Runs | Successes | Success Rate (%) | Avg Latency (ms) | Min (ms) | Max (ms) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| mds_calculation | 50 | 50 | 100.0 | 1.23 | 1.12 | 2.28 |
| get_current_datetime | 50 | 50 | 100.0 | 0.24 | 0.21 | 0.60 |
| get_current_city | 50 | 0 | 0.0 | N/A | N/A | N/A |
| get_weather | 50 | 0 | 0.0 | N/A | N/A | N/A |

## Implemented System Features

| Feature | Status | Notes |
| --- | --- | --- |
| MDS-driven adaptive personalization | Implemented | Low / medium / high personalization tiers |
| Local document grounding | Implemented | Searches user files from `knowledge_base/` |
| MCP tool orchestration | Implemented | Dynamic tool discovery and invocation |
| Hybrid memory layer | Implemented | Mem0 cloud with local JSON fallback |
| Adaptive response length | Implemented | Prompt-level verbosity control |

## Live Event Log Summary

| Metric | Value |
| --- | --- |
| Event log present | False |
| Total logged events | N/A |
| Tool event count | N/A |
| Tool success rate (%) | N/A |
| Tool avg latency (ms) | N/A |
| Tool p95 latency (ms) | N/A |

## Human Evaluation Summary

| Metric | Value |
| --- | --- |
| Baseline scored sessions | 0 |
| MDS scored sessions | 0 |
| Baseline average | N/A |
| MDS average | N/A |
| Absolute delta | N/A |
| Percent improvement | N/A |

## Notes

- Use only rows with real measurements in the paper.
- If human evaluation remains empty, do not claim user-rating improvements.
- If event logs are empty, do not claim live MCP tool success metrics.
- Local document grounding is implemented, but no separate retrieval-quality benchmark is claimed here.
