# Canglong

<div align="right">

[English](./README.md) | [简体中文](./README.zh-CN.md)

</div>

<div align="center">

**Evidence-first code audit, Java exploit-chain recognition, Docker-oriented verification, and model-assisted security operations**

<p>
  <img src="https://img.shields.io/badge/Stage-Alpha-ff7a1a?style=for-the-badge" alt="Stage Alpha" />
  <img src="https://img.shields.io/badge/Frontend-Vue_3_%2B_TypeScript-00d4aa?style=for-the-badge" alt="Vue 3 and TypeScript" />
  <img src="https://img.shields.io/badge/Backend-FastAPI-0f172a?style=for-the-badge" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Analysis-Static_%2B_Chain_Aware-1f6feb?style=for-the-badge" alt="Static and Chain Aware" />
  <img src="https://img.shields.io/badge/AI-Multi--Model_Mesh-7c3aed?style=for-the-badge" alt="Multi-model Mesh" />
</p>

<p>
  <img src="https://img.shields.io/badge/OpenAI-Supported-111111?style=flat-square" alt="OpenAI Supported" />
  <img src="https://img.shields.io/badge/Anthropic-Supported-111111?style=flat-square" alt="Anthropic Supported" />
  <img src="https://img.shields.io/badge/Gemini-Supported-111111?style=flat-square" alt="Gemini Supported" />
  <img src="https://img.shields.io/badge/Qwen-Supported-111111?style=flat-square" alt="Qwen Supported" />
  <img src="https://img.shields.io/badge/DeepSeek-Supported-111111?style=flat-square" alt="DeepSeek Supported" />
  <img src="https://img.shields.io/badge/Self--Hosted-Supported-111111?style=flat-square" alt="Self-hosted Supported" />
</p>

</div>

> Canglong is designed to feel less like a noisy rule dump and more like a senior reviewer:
> correlate code evidence, reduce false positives, identify exploit paths, stage replay plans, and route model-assisted work to the right lane.

![img_5.png](img_5.png)
![img_3.png](img_3.png)
![img.png](img.png)
![img_4.png](img_4.png)

## Table Of Contents

- [Why Canglong](#why-canglong)
- [What Works Today](#what-works-today)
- [Java Audit Strategy](#java-audit-strategy)
- [Model Mesh](#model-mesh)
- [Quick Start](#quick-start)
- [Operator Flow](#operator-flow)
- [API Surface](#api-surface)
- [Repository Layout](#repository-layout)
- [Roadmap](#roadmap)
- [Notes](#notes)

## Why Canglong

Most security tooling is strong at one layer and weak at the handoff:

- static scanning without runtime context
- exploit research without clear code evidence
- reverse engineering without a unified operator workflow
- AI integration without routing discipline, privacy boundaries, or repeatability

Canglong is being shaped as one operator-facing workbench that combines:

- local and Git-based code intake
- evidence-ranked static audit
- Java-aware exploit-chain correlation
- Docker-oriented verification planning and runtime reachability checks
- bilingual UI for report-driven review
- multi-model routing for research agents and task-specific reasoning

## What Works Today

### Operator Experience

- Login-protected web command center built with Vue 3, TypeScript, and Vite
- English and Simplified Chinese switching
- Repository workspace for Git URLs and local source directories
- Model settings page for multi-provider configuration and default lane selection
- Audit progress tracking with stages, progress bars, and final report view

### Audit Engine

- Static repository fingerprinting for languages, frameworks, packaging, and manifests
- Endpoint discovery for Python, Java, JavaScript/TypeScript, and Go entry surfaces
- Dependency evidence extraction from `pom.xml`, Gradle, `requirements.txt`, `package.json`, and `go.mod`
- Finding promotion for command execution, unsafe deserialization, weak crypto, auth bypass, and language-specific risk markers
- False-positive controls to explain when findings are demoted or blocked
- Docker verification planning plus runtime reachability and login-required hinting

### Java-Focused Improvements Already Integrated

- `groupId:artifactId` dependency extraction for Maven and Gradle projects
- framework fingerprinting for Spring Boot, JAX-RS, Shiro, Dubbo, MyBatis, Struts, and Hessian
- automatic Java exploit-chain candidates with applicability checks
- runtime-aware demotion for modern JDK constraints
- dependency-backed reduction of noisy chain promotion

## Java Audit Strategy

The current Java strategy is intentionally chain-aware instead of pattern-only.

### Static Correlation Lanes

- JNDI lookup path recognition
- Fastjson AutoType risk detection
- Hessian and Dubbo deserialization path detection
- XStream XML deserialization detection
- generic gadget-style deserialization correlation
- Spring expression injection hints
- auth framework surface correlation for Spring Security, Shiro, and related stacks

### Applicability Logic

Each Java exploit-chain candidate is scored with explicit checks:

- ingress reachability
- dependency evidence
- code sink evidence
- runtime constraints

This is the main false-positive control borrowed from the `java-chains` style of thinking:
do not treat every suspicious sink as equally exploitable without matching dependency and environment evidence.

### Current Java Chain Outputs

Canglong can currently emit candidates such as:

- JNDI remote naming chain
- Fastjson AutoType gadget chain
- Hessian or Dubbo deserialization chain
- XStream XML deserialization chain
- Java gadget deserialization chain
- Spring expression injection chain

## Model Mesh

The product direction is not “show a long vendor list”. The goal is practical routing:

- use a strong general-purpose reasoning model as the default audit lane
- route long-context review to long-context models
- route reverse-engineering and diagram-heavy tasks to multimodal models
- support self-hosted or privacy-bound deployments when code cannot leave the boundary

### Current Provider Surface

- OpenAI
- Anthropic
- Gemini
- Qwen
- DeepSeek
- self-hosted / OpenAI-compatible gateways

### Planned Agent Roles

- Exploit Chain Researcher
- False-Positive Reducer
- Docker Range Planner
- Decompiler Recon Agent

## Quick Start

### 1. Run the web app

```bash
cd apps/web
npm install
npm run dev
```

### 2. Run the API

```bash
cd apps/api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 9000
```

### 3. Run with Docker Compose

```bash
docker compose up --build
```

### Demo access

- username: `admin`
- password: `Canglong123!`

## Operator Flow

1. Sign in at `/login`.
2. Open `/settings` if you want to configure provider lanes or a default model.
3. Go to `/workspace` and register either:
   - a Git repository URL
   - a local source directory
4. Sync the repository if it is Git-based.
5. Start an audit from the workspace card.
6. Open the report to inspect:
   - environment fingerprints
   - dependency evidence
   - discovered endpoints
   - exploit-chain candidates
   - false-positive controls
   - Docker verification status
   - login-required hints for runtime replay

## API Surface

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/healthz` | service health check |
| `POST` | `/api/auth/login` | authenticate and issue a bearer token |
| `GET` | `/api/auth/me` | validate the current session |
| `GET` | `/api/dashboard` | overview metrics and UI summary |
| `GET` | `/api/missions` | mission list |
| `POST` | `/api/missions` | create a mission |
| `GET` | `/api/llm/stack` | model-mesh strategy and agent templates |
| `POST` | `/api/llm/research-agents` | queue a model-assisted research agent |
| `GET` | `/api/settings/models` | fetch configured model lanes |
| `POST` | `/api/settings/models` | add a model lane |
| `PUT` | `/api/settings/models/{model_id}` | update a model lane |
| `POST` | `/api/settings/models/{model_id}/default` | mark the default lane |
| `GET` | `/api/repos` | list registered repositories |
| `POST` | `/api/repos` | register a Git or local repository |
| `POST` | `/api/repos/{repo_id}/sync` | clone/pull a Git repository or validate a local path |
| `GET` | `/api/audits` | list audit jobs |
| `POST` | `/api/audits` | start a new audit job |
| `GET` | `/api/audits/{job_id}` | fetch audit progress and stages |
| `GET` | `/api/audits/{job_id}/report` | fetch the completed audit report |

## Repository Layout

```text
.
|-- apps
|   |-- api
|   |   |-- app
|   |   |   |-- models
|   |   |   |-- routers
|   |   |   `-- services
|   |   |-- Dockerfile
|   |   `-- requirements.txt
|   `-- web
|       |-- src
|       |   |-- components
|       |   |-- router
|       |   |-- services
|       |   |-- styles
|       |   `-- views
|       |-- Dockerfile
|       `-- package.json
|-- docs
|   `-- architecture.md
|-- docker-compose.yml
`-- package.json
```

## Roadmap

- [x] Web and API monorepo skeleton
- [x] Login, session flow, and protected routes
- [x] Repository intake for Git and local directories
- [x] Background audit jobs and report generation
- [x] Model settings and multi-provider mesh surface
- [x] Java dependency fingerprinting and exploit-chain recognition
- [x] False-positive control reporting
- [x] Bilingual README and bilingual UI switching
- [ ] persistent repository and audit history storage
- [ ] deeper AST and dataflow engines across more languages
- [ ] breakpoint-oriented runtime executor
- [ ] full Docker deployment and replay orchestration per target stack
- [ ] reverse-engineering adapters for binary intake
- [ ] multi-user collaboration and evidence export

## Notes

### Positioning

Canglong is being built as a security operations workbench, not a single-purpose scanner.
The long-term direction is to merge:

- code audit
- exploit research
- runtime verification
- reverse engineering
- model-assisted analyst workflows

### GitHub Presentation

This README intentionally uses GitHub-native presentation elements:

- badges
- tables
- collapsible-friendly sections
- task-list roadmap
- bilingual switching

The goal is a repository front page that reads like a serious product surface instead of a placeholder.
