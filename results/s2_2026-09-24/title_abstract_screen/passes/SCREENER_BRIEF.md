# Screener brief (identical for every batch; your pass letter P and batch name are given in your task)

Root: `C:/Users/frank/sts-electrocatalyst/results/s2_2026-09-24/title_abstract_screen/`

1. Read `screening_instructions.md` in the root and follow it exactly.
2. Input: `passes/session_pass_<P>/batches/<batch>.in.jsonl` (200 records or fewer, one JSON object per line). Read EVERY record in full. Lines are long, so do not rely on the Read tool (it can cut long lines). Print the records in slices of 15:
   `PYTHONIOENCODING=utf-8 python -c "import sys;L=open(r'<input>',encoding='utf-8').read().splitlines();[print(l) for l in L[int(sys.argv[1]):int(sys.argv[1])+15]]" 0`
   then 15, 30, and so on to the end.
   - **Pass A** works forwards from slice 0.
   - **Pass B** works backwards from the last slice to slice 0.
3. Output: `passes/session_pass_<P>/batches/<batch>.out.jsonl`.
   - One JSON line per input record, in the ORIGINAL input order.
   - Fields exactly `{"screen_id","doi","label","reason"}`.
   - Copy screen_id and doi exactly; doi may be null.
4. Judge every record yourself from its title, abstract and metadata. Do NOT write a keyword script or any code that assigns labels.
5. Open only `screening_instructions.md`, this brief and your one input file.
   - Do not open any other batch, any `.out.jsonl` of any pass, or anything under `pilot/`.
   - Do not touch git.
6. When done, check that the output has one line per input record in the input's screen_id order. A short Python check is allowed for that only. Fix any gap.
7. Reply with ONE line: the counts per label.
