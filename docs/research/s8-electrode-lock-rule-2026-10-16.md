# S8 electrode data at the Oct 25 lock: what is reported if the measurements are partial (registered 2026-10-16)

**Decision of record.** Frank, 2026-10-16: "Go ahead". This approved the rule exactly as proposed to him that day:
- the comparison of Cu8 against Ni31 and Fe25 is reported only if those three alloys are complete;
- the "Cu22 is least active" test is reported only if all five alloys in that set are complete;
- otherwise one sentence says the measurements were not complete at the lock, with no partial means.

**Status.** No OER measurement is recorded in this repository as of this line. The last recorded status is "Nothing
measured yet" (Frank, 2026-10-12; freeze §1b).

**Why.** The freeze (`s8-stage1-freeze-proposal-2026-10-07.md` §6) says how many coupons make an alloy complete, but
not what is reported if only some alloys are complete at the data lock. Choosing that after seeing the numbers would
be an undisclosed analysis choice. This line fixes it first.

## Rule

1. **An alloy is complete** when it meets §6's replicate rule by the lock: at least 3 coupons measured over at least 2
   bench days, each day with IrO₂ and a blank. A coupon that fails a check §6 already requires does not count.
2. **A comparison is evaluated** only if every alloy it involves is complete:
   - **K1** (Cu8 against Ni31 and Fe25) needs Cu8, Ni31 and Fe25;
   - **K2** (Cu22 least active of the five K-set alloys) needs all five K-set alloys;
   - **the IrO₂ comparison** is made per alloy, for each complete alloy;
   - **each exploratory item** (an arm's leader, its full order and Spearman ρ, Ni34's position) needs every alloy
     it ranks.
3. **Anything not evaluated is reported as not evaluated.**
   - If nothing is evaluable, the report carries one sentence: the measurements were not complete at the data lock.
   - No means, error bars or orderings from incomplete alloys appear in the report. They are kept, dated, in the
     repository.
4. This rule adds no threshold and changes no criterion. K1, K2, the IrO₂ comparison and the twice-pooled-SD rule
   stand as frozen in §3 and §6.
