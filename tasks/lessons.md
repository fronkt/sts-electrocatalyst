# Lessons (corrections log)

## 2026-07-01 — Archive superseded planning docs explicitly, don't rely on git history
**What happened:** during the thermal pivot I rewrote `tasks/todo.md` in place,
counting on git history to preserve the old content. The user wanted the old plan
kept as a visible backup doc.
**Rule:** when a pivot/supersession replaces or rewrites a planning/status doc,
first copy the outgoing version to an explicit dated archive file (e.g.
`<name>-archive-YYYY-MM-DD-<reason>.md`) with a provenance header, and link it
from the replacement. Git history is provenance, not a browsable backup.
