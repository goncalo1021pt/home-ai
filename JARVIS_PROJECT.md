# Jarvis Project Brief

> Personal AI assistant inspired by Jarvis/Friday from the Marvel films.
> This document captures architecture decisions, scope, and build order
> from the planning phase. Read this first before starting any work.

---

## TL;DR

Build a voice-controlled personal AI assistant on PC first. Smart home
integration comes later, once family is on board. Architecture is
MCP-based so extending it is plug-and-play.

**Current scope: Phase 1 only — PC-based Jarvis, no smart home yet.**

---

## Project Goals

- Fun first, useful second. Should feel like a real personal AI, not a
  glorified chatbot.
- Voice-first interaction (wake word + natural conversation).
- Extensible via MCP so new capabilities drop in cleanly.
- Eventually controls smart home, but not yet.

---

## Architecture Decisions

### The brain
- **Model**: Claude Opus 4.7 via Anthropic API
- **Rationale**: Best agentic reasoning available. Worth the cost vs.
  Sonnet/Haiku for multi-step tool use and planning.
- **Cost mitigations**:
  - Use prompt caching for system prompt + tool definitions
  - Optionally route trivial queries (time, simple commands) to
    Haiku 4.5 later for cost optimization
  - Stream responses so TTS can start speaking before the model finishes

### Hosting strategy
- **Decision**: Cloud LLM (Anthropic API), local everything else
- **Rationale**: Local models can't match Opus for reasoning. STT/TTS
  run fine locally with privacy and latency wins.

### Pipeline
```
Wake word (local) → Mic capture → Whisper STT (local) → 
Claude Opus 4.7 (cloud) → Tool calls (MCP) → 
TTS (local or ElevenLabs) → Speaker output
```

### Stack
| Component | Choice | Notes |
|-----------|--------|-------|
| Agent framework | Anthropic SDK + MCP | Skip LangChain etc., too much magic |
| Wake word | openWakeWord | Free, local, custom "Hey Jarvis" trainable |
| STT | faster-whisper | Local, fast, free |
| TTS | Piper (local) or ElevenLabs (cinematic) | Start with Piper |
| Shell project | Fork of `isair/jarvis` | Solves audio pipeline + wake word boilerplate |

---

## Build Order (Phase 1: PC Only)

Each phase is roughly one weekend of work.

### Phase 1.1 — Agent loop (text only)
- [ ] Set up Python project with Anthropic SDK
- [ ] Build conversation loop with Claude Opus 4.7
- [ ] Define Jarvis personality in system prompt
- [ ] Implement 2–3 simple MCP tools (weather, web search, current time)
- [ ] Get tool calling working end-to-end
- [ ] Add conversation memory (rolling summary + recent turns)

### Phase 1.2 — Voice input
- [ ] Add push-to-talk hotkey (skip wake word for now)
- [ ] Integrate faster-whisper for STT
- [ ] Stream mic → STT → agent loop

### Phase 1.3 — Voice output
- [ ] Integrate Piper for local TTS
- [ ] Stream agent response → TTS → speakers
- [ ] (Optional) Add ElevenLabs as premium TTS option

### Phase 1.4 — Wake word
- [ ] Integrate openWakeWord
- [ ] Train or use pre-built "Hey Jarvis" model
- [ ] Replace hotkey with always-listening wake detection

### Phase 1.5 — Useful MCP tools
Pick from this list based on what's actually useful day-to-day:
- [ ] File search on local machine
- [ ] Calendar (Gmail/Outlook MCP)
- [ ] Email read/draft
- [ ] Spotify/music control
- [ ] Screen awareness (Claude can analyze screenshots)
- [ ] Shell command execution (sandboxed — be careful)
- [ ] Notes/reminders (Obsidian MCP or local file)
- [ ] Discord/Slack messaging
- [ ] Git/code helper (diff summaries, lint runs)

### Phase 1.6 — Polish
- [ ] Personality refinement (witty British AI vibe)
- [ ] Error handling for failed tool calls
- [ ] Logging for debugging
- [ ] Optional GUI or status indicator

---

## Phase 2 (Deferred — Pending Family Agreement)

Do not start until family discussion is resolved.

- Smart home integration via Home Assistant MCP
- Dell PowerEdge already in house — will run HA in VM/container
- MQTT expertise already in place (existing smart home 360 work)
- Hardware shopping list deferred to that conversation

---

## Hardware Context (For Future Phases)

- **Existing**: Dell PowerEdge server rack at home
- **Existing**: MQTT broker / smart home 360 experience
- **House**: ~1990s construction, no existing heating/AC, possible
  future renovation
- **Implication**: Clean slate for retrofits. Phase 2 hardware list
  will be tighter than typical because PowerEdge replaces dedicated
  hub + mini PC needs.

---

## Reference Repos

- **Primary shell to fork**: https://github.com/isair/jarvis
  - Voice-first, MCP-extensible, handles wake word + audio pipeline
  - Will need to swap LLM backend to Claude Opus 4.7
- **Architecture reference**: https://github.com/open-jarvis/OpenJarvis
  - Stanford Hazy Research, good preset architecture
- **For Phase 2**: Home Assistant has official MCP integration

---

## Open Questions for Implementation

- Which Python version? (Recommend 3.11+ for Anthropic SDK)
- Project layout — monolithic or split into agent / mcp-servers /
  voice-pipeline?
- Where to store conversation history (SQLite? JSON? Vector DB later?)
- How to handle the wake word "false positive" problem
- Streaming TTS strategy — sentence-by-sentence or token-buffered?

---

## What This Project Is NOT (Yet)

- Not a smart home controller (Phase 2)
- Not running on a Raspberry Pi (runs on dev PC for now)
- Not using a local LLM (cloud Claude Opus 4.7)
- Not multi-user
- Not voice-cloned (default TTS voice fine for now)

---

## Personality Direction

Aim for: witty, calm, slightly British, dry humor. Closer to Jarvis
than Friday. Should feel like a competent assistant who occasionally
makes a clever remark, not a chatbot trying to be funny.

System prompt will be iterated on heavily — treat it as a living
document inside the repo.

---

## First Concrete Task

Start with Phase 1.1. Open this file, then:

1. Create a Python project (`uv init` or `poetry new`)
2. Install `anthropic` SDK
3. Build the simplest possible loop: input → Claude Opus 4.7 → output
4. Add one MCP tool to prove the tool-calling path works
5. Then layer everything else on top

Keep it minimal until it works. Resist the urge to architect everything
upfront — the MCP pattern means you can add tools incrementally without
refactoring.
