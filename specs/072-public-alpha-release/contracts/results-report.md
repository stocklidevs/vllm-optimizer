# Contract: Results Report

The public results report is a Markdown document at `docs/RESULTS.md`.

Required sections:

- `# Optimization Results`
- `## Executive Summary`
- `## How To Read Tokens Per Second`
- `## Qwen3 Coder Next Results`
- `## Multi-Model Baselines`
- `## Why The Results Look Like This`
- `## Reproduction And Provenance`
- `## Limitations`

Required result rows:

- Qwen3 Coder Next single-user baseline and optimized result
- Qwen3 Coder Next C8 confirmed current and recommended result
- Qwen3 Coder Next best C8 sweep result
- Gemma 4 E4B IT baseline and safe-profile result
- GLM 4.7 Flash baseline and safe-profile result
- Qwen3.6 27B baseline and safe-profile result
- Qwen3.5 27B baseline and safe-profile result
- DeepSeek Coder V2 Lite Instruct baseline and safe-profile result

Required interpretation:

- State that C8 tokens/sec is aggregate throughput across concurrent requests.
- Provide the simple per-request average for C8 as aggregate tokens/sec divided by 8.
- State that single-user gains were modest while aggregate concurrent throughput improved sharply for Qwen.
- State that non-Qwen model safe-profile sweeps were first-pass conservative sweeps, not final promoted profiles.
