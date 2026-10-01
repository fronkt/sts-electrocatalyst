# Public-source API pilot — October 1, 2026

Ten tier-1 NEEDS_SI records completed GPT-6 Luna route discovery. No new SI
candidate met the observed-URL, public-repository and exact-record gates. No
document was recovered or independently screened, and no scientific decision
changed. Unsuccessful discovery is not evidence that SI is absent.

The pinned records are S11549, S14704, S23135, S31137, S11392, S21177, S30575,
S29636, S23244 and S22690. They are outside the earlier 21-record recovery set.
The manifest retains 55 earlier public attempts rather than treating these as
previously unattempted records. Domain-restricted search often returned unrelated
pages; coverage is limited, not exhaustive. S11392 has a journal-version SI lead,
not verified SI for its supplied preprint version.

## Cost and controls

The conservative estimate is **$0.22567585** against the application-level $1
pilot limit. It uses long-context token rates, no cache discounts, and charges
every web-search event, including opens and the nonterminal event below. It is
not an invoice measurement or an account-wide hard budget. Pricing references:
[GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna) and
[tool pricing](https://developers.openai.com/api/docs/pricing).

Nine responses contain at most two tool events. S11392 contains two completed
events and a third, source-free event marked `searching`; its final response is
`completed` and echoes `max_tool_calls: 2`. The
[API reference](https://developers.openai.com/api/reference/cli/resources/responses/methods/create)
says attempts beyond the limit are ignored. An ignored attempt is a plausible
explanation, but a third processed or billed search is not established. All three
are charged in the conservative estimate. The strict verifier retains both
event-envelope/nonterminal flags, and the runner blocks further paid requests
when such saved-output anomalies exist. No further API calls are scheduled.

Ledger reservations precede requests; the exclusive lock covers re-reading the
ledger, duplicate checks and budget checks. Ledger updates use atomic replacement.
Ambiguous completion keeps the full $0.25 reservation and is not retried.
The request's output and tool settings are bounds requested from the API, not a
substitute for checking actual output. Only completed tool events can supply
observed candidate sources. Model output never changes screening state.

## Preservation and verification

Twenty-three unit tests and six asynchronous state-safety tests pass, including
concurrency, duplicate resumption, budget stop, failure cleanup and anomaly stop.
All eighteen existing scientific regression tests pass. The checklist rebuild is
byte-identical: 163 records, tiers 70/38/48/7 and 17 D10 checks. All six manifest
baseline hashes remain unchanged.

The scientific verifiers have zero errors: all 104 required third reads, 130 audit
targets, 109 historical outputs and 115 evidence files remain verified. Current
v5 stays 171 ELIGIBLE, 106 NEEDS_SI and 116 UNRESOLVED, with v3/v4 unchanged for
all 2,496 records. Seven policy choices remain unadopted.

`verification.json` records both strict API control flags separately from the
unchanged baseline checks; it is not an unqualified clean-control report.
`completed_round_recheck.json` retains the new scientific recheck without
overwriting the September 29 report. Request, response and receipt files retain
the pilot record; they contain no credential or authorization header.

## Access boundary and credential lifecycle

83 Sciences employer allowance is authorized. The account cannot create projects
or change project settings. Restricted `electro-public-si` is in the existing
`electrolyte-supercapacitor-dev` project, expiring October 8: model listing Read,
Responses Write; Files, Batch and other capabilities None. The secret is held
only in the local runtime, with the save-key browser dialog left for the entrant
to back it up in an approved credential manager. It is not in the repository,
chat or command arguments, and no permanent local key installation is claimed.

Cara is conferring with a colleague about Elsevier API access. That is pending
entitlement information, not permission for institutional/proxy automation.
Institutional retrieval remains paused; no publisher APIs, proxy sessions,
paywall bypass or CAPTCHA bypass were used in this pilot.

Next work should focus on exact public repository attachments, the versioned
S11392 lead, and the librarian's entitlement clarification. Do not expand paid
discovery or repeat completed scientific reads by default.
