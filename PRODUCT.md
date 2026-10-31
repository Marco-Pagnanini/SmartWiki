# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users
Primary audience: students and attendees of a lecture where SmartWiki is projected live. They watch the presenter type requests into the chat and need to understand how a request travels through a multi-agent system. Company employees searching/adding wiki documents are a possible future audience, not the current one.

## Product Purpose
SmartWiki is a company wiki of documents driven by AI agents. A chat sends the user's message to an orchestrator agent, which delegates to sub agents (researcher: find a document by exact name; archivist: add a document). Sub agents reach the database only through MCP tools that wrap the service layer. Success: the audience sees and understands that path, and the chat answers correctly.

## Positioning
A teaching demo of agent architecture (orchestrator → sub agent → MCP tool gateway → service → database), not a generic chatbot. Making the request's journey visible is the point.

## Operating Context
Projected in a lecture room from the presenter's laptop. Backend: FastAPI + MCP server + Anthropic API (Haiku, low effort); responses take several seconds. Frontend talks only to `POST /api/chat` (`{message, history}` → `{reply}`).

## Capabilities and Constraints
- Find a document by exact file name; add a document (unique name, group number ≥ 1, optional summary).
- Not yet: search by topic/group/partial name, update, delete, chat persistence.
- All code, comments and UI copy in English.

## Brand Commitments
- Look: classic shadcn/ui, arranged like ChatGPT. Only shadcn components, customised in the project's components folder.
- No mascot/logo: a simple icon identifies the app.
- Loading is a purely illustrative animation of a packet travelling orchestrator → sub agent → tool gateway → service and back to the user, shown for at least one full cycle even if the answer is ready earlier.

## Evidence on Hand
One real document in the database: `manuale-ferie.pdf` (group 2). No other content.

## Product Principles
1. Show the mechanism: the request's path is the lesson.
2. Familiar first: a chat everyone already knows how to use.
3. Honest about limits: the agents say what they cannot do yet.
