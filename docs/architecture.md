# Canglong Architecture

## Core Goal

Build an audit platform that behaves less like a rule dump and more like a senior reviewer:

- lower false positives through evidence fusion
- turn suspicious paths into reproducible runtime proof
- stage disposable docker ranges for verification
- support reverse-engineering inputs alongside source repositories

## System Shape

### 1. Ingestion Layer

- repository import: git, archive, mounted workspace
- binary intake: APK, JAR, WAR, ELF, PE
- metadata extraction: language, framework, build graph, entrypoints

### 2. Intermediate Knowledge Graph

- file graph
- symbol graph
- taint graph
- request-to-sink path graph
- evidence snapshots from runtime probes

This graph becomes the shared language between static audit, reverse engineering, and dynamic debugging.

### 3. Static Audit Engine

- parser adapters per language
- framework-aware source and sink packs
- semantic trace compression to keep analyst output readable
- confidence fusion to merge overlapping findings instead of flooding duplicates

### 4. Dynamic Verification Engine

- breakpoint recipes generated from static suspicion
- docker range provisioning with fixture data and mock dependencies
- replay capture for HTTP, MQ, RPC, and CLI flows
- verdict promotion only after proof or high-confidence contradiction handling

### 5. Reverse Engineering Lane

- decompiler adapters
- symbol recovery and endpoint recovery
- string/secret mining
- bridge decompiled call paths back into the same evidence graph

### 6. Mission Control UI

- one mission = one audit objective
- show path evidence, runtime plan, environment status, and proof trail together
- prioritize next best analyst action instead of only listing findings

### 7. Model Mesh And Research Agents

- provider adapters for OpenAI, Anthropic, Gemini, Qwen, DeepSeek, and self-hosted inference gateways
- routing policy based on task type: exploit reasoning, long-context review, multimodal artifact digestion, or low-cost batch triage
- research agents as first-class workers:
  - exploit chain researcher
  - false-positive reducer
  - docker range planner
  - decompiler recon agent
- prompt packs and tool permissions should be versioned per agent blueprint
- sensitive source code should support private routing to self-hosted inference lanes

## False-Positive Reduction Strategy

- require multi-signal agreement before promoting severity
- keep raw evidence attached to each claim
- rank by exploitability, preconditions, and runtime reachability
- demote paths invalidated by framework guards, type constraints, or container replay

## Suggested Next Implementation Order

1. real repository ingestion and language fingerprinting
2. persistent mission store and scan job queue
3. language adapters for Java, Go, Python, PHP, JavaScript/TypeScript
4. docker range templates and runtime probe agent
5. decompiler adapters and binary intake workflow
6. collaborative review features and exportable evidence reports
