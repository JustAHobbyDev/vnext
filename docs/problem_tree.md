**Problem Tree**

**Core Problem**

Recover a real clue-to-graph discovery process, grounded in the AleaBito archive, that can surface underappreciated public nodes early enough to matter.

**1. Archive Signal Understanding**
Depends on: none

Questions:
- What clue patterns actually appear in the archive?
- Which clues seem to lead to graphable dependency chains?
- Which clues are noise, hindsight, or non-actionable commentary?

Outputs:
- small clue taxonomy
- examples of high-signal archive posts
- examples of non-expanding posts

**2. Evidence Intake**
Depends on: none

Questions:
- How do we mirror and store real artifacts safely?
- How do we preserve provenance and avoid synthetic contamination?
- How do we link archive observations to supporting real artifacts?

Outputs:
- mirrored artifact set
- strict provenance records
- validated artifact loader

**3. Clue Formation**
Depends on: 1, 2

Questions:
- What is the minimal normalized clue object?
- When is evidence strong enough to create a clue?
- How should clue confidence be assigned?

Outputs:
- clue schema
- clue creation rules
- initial clue packs from archive-driven cases

**4. Graph Expansion**
Depends on: 3

Questions:
- Given a clue, how do we discover relevant nodes?
- Which edge types matter first?
- What evidence is required before creating an edge?
- When should expansion stop?

Outputs:
- minimal expansion rules
- evidence-backed node/edge creation
- small explicit graphs from real clues

**5. Candidate Scoring**
Depends on: 4

Questions:
- Which graph properties best indicate underappreciation?
- How do we separate structural importance from obviousness?
- How do we limit scoring to public, actionable candidates?

Outputs:
- simple scoring model
- ranked candidate nodes
- score explanations tied to graph structure

**6. Replay / Validation**
Depends on: 3, 4, 5

Questions:
- Does the system recover meaningful paths on known cases?
- Does it find the right node for the right reason?
- How early in the path does useful signal appear?

Outputs:
- replay cases
- pass/fail review surfaces
- gap analysis

**Execution Order**

1. Archive Signal Understanding
2. Evidence Intake
3. Clue Formation
4. Graph Expansion
5. Candidate Scoring
6. Replay / Validation

**Near-Term Priority**

Focus now:
- 1. Archive Signal Understanding
- 2. Evidence Intake
- 3. Clue Formation
- 4. Graph Expansion

Defer until graph quality is real:
- 5. Candidate Scoring
- 6. Replay / Validation

**Immediate Working Question**

What clue types in the AleaBito archive most reliably justify graph expansion into non-obvious nodes?
