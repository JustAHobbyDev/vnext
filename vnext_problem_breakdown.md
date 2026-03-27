# Problem Breakdown

The over-arching problem is:

> How do we go from real clue-like signals, especially in the AleaBito archive,
> to an evidence-backed graph that surfaces underappreciated public nodes early
> enough to matter?

The cleanest decomposition is into six smaller problems.

## 1. Signal capture
- What in the archive or real-world evidence stream should count as a clue
candidate at all?
- This includes detecting theme-bearing statements, unusual specificity,
supply-chain hints, bottleneck hints, and early demand signals.

2. Evidence grounding
- How do we trace each clue candidate to real artifacts with auditable
provenance?
- This is the boundary that prevents synthetic drift and hindsight laundering.

3. Clue formation
- Given grounded evidence, how do we convert it into a normalized `clue` object?
- This includes deciding clue type, confidence, theme hint, and whether the clue
is strong enough to justify expansion.

4. Graph expansion
- Starting from a clue, how do we discover and attach relevant nodes and edges?
- This is the core “reasoning recovery” problem: suppliers, customers,
chokepoints, dependencies, proxies, partners.

5. Node evaluation
- Once a graph exists, how do we distinguish obvious nodes from underappreciated
ones?
- This includes structural leverage, neglect, public-market accessibility, and
expression quality.

6. Replay and validation
- How do we check whether the system is actually recovering meaningful paths
similar to the archive’s implied reasoning?
- This should stay subordinate to discovery, but it still matters.

I’d split those further into practical workstreams:

- `archive understanding`
  - learn what kinds of clues actually appear in AleaBito’s posts
  - identify recurring reasoning patterns

- `evidence intake`
  - mirror, hash, store, and validate real artifacts
  - keep provenance strict

- `clue extraction`
  - create clue candidates from archive entries and supporting evidence
  - decide clue thresholds

- `graph construction`
  - define how clues trigger node/edge expansion
  - require evidence for edges

- `ranking`
  - score candidate nodes once graph quality is good enough

- `case replay`
  - compare recovered paths against known cases like photonics and memory

If we want the most useful near-term framing, I would say the project currently
has three primary unknowns:

1. What clue patterns in the archive are actually predictive of fruitful graph
expansion?
2. What is the minimum graph expansion logic needed to recover non-obvious
upstream or adjacent nodes?
3. What evidence threshold should be required before expansion continues versus
stops?

A practical next step would be to turn this into a problem tree with:
- core problem
- subproblems
- which are upstream dependencies
- which should be tackled first

If you want, I can draft that tree next in a compact, execution-oriented form.
