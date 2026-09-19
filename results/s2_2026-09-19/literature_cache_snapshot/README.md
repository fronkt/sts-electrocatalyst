# P-LIT cache snapshot, 2026-09-19

This snapshot preserves the 20,000 retrieved source occurrences and 19,813 deduplicated metadata candidates at the API-budget stop. All four streams remain incomplete; changing query-1 counts and duplicate provider IDs remain in the readout. No eligibility or method decisions are contained here.

`manifest.json` lists every archived raw response, receipt, failed response, search specification and candidate export with its original path and SHA-256. The SQLite index is reconstructible and excluded. Each ZIP member was compared byte-for-byte with the unchanged local source after compression; successful-page receipt hashes were also verified. Restore only into an empty directory and validate every member against the manifest before reuse. The archived specifications retain their original pinned-code identity.
