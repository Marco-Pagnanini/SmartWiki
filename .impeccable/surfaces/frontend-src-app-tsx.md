---
version: 1
slug: "frontend-src-app-tsx"
primary_target: "frontend/src/App.tsx"
related_targets: []
---

Scope: frontend chat (single screen). Mode: Operate.
Audience/job: lecture attendees watch the presenter ask the wiki agents; they must follow the request's path. Task: type a request, watch the packet travel, read the answer.
Constraints: shadcn/ui only (customised under src/components), ChatGPT arrangement, simple icon instead of logo, English copy, POST /api/chat {message, history} -> {reply}.

## Direction contract
THESIS: A familiar ChatGPT-style chat whose waiting time becomes the lesson; refuses the skeleton/shimmer loader.
OWN-WORLD: shadcn neutral tokens, Geist, rounded-3xl composer, grey user bubbles, plain assistant text; primary (near-black / white in dark) marks the active node.
STORY: attendee sees a request leave "You", hop through Orchestrator, Sub agent, Tool gateway (MCP), Service, and come back; then the answer appears.
FIRST VIEWPORT: slim top bar (icon + SmartWiki left, theme toggle and New chat right); centered "What can I help with?" with composer and three suggestion pills; after first message, thread in a 768px column with composer docked bottom.
FORM: canon (user-pinned category standard: ChatGPT on shadcn). seed: none (unavailable — direction pinned by user).
SIGNATURE: packet-flow card in the assistant slot: five nodes, forward lane top and return lane bottom, a Package icon travelling hop by hop and disappearing into each node, which lights up; minimum one full cycle.
