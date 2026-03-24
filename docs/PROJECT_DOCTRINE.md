# Project Doctrine

Date: March 23, 2026

## Purpose

This project exists to recover and operationalize the kind of reasoning implied
by `aleabitoreddit`'s stock research archive.

The central source artifact for that effort is:

- [aleabitoreddit-daily-archive-v1.json](/home/d/codex/vnext/research/analysis/aleabitoreddit-daily-archive-v1.json)

That archive is not incidental context. It is the empirical heart of the
project.

## North Star

The project is successful only if it improves the ability to:

1. observe a real clue
2. connect that clue to real supporting evidence
3. build a graph from that clue
4. surface connected candidate nodes
5. identify underappreciated nodes early enough to matter

## Core Belief

The value of this project does not come from building a generic market-research
pipeline.

It comes from learning how real clue-driven discovery paths emerge in the
AleaBito archive and turning those paths into explicit, evidence-backed graph
construction.

## Primary Corpus

`aleabitoreddit-daily-archive-v1.json` should be treated as a primary research
corpus.

It is important because it contains the closest available record of:

1. how clues first appear
2. how themes become legible
3. how dependency chains become visible
4. how candidate nodes emerge before broad recognition

## Product Focus

The active focus of the repository is:

1. `evidence`
2. `clues`
3. `graph`
4. `scoring`

`benchmarks` are useful only as replay and validation surfaces. They are not the
main product.

## Hard Rules

1. No synthetic evidence may enter discovery, graph-building, scoring, or
   evaluation paths.
2. The archive and mirrored real-world artifacts must remain separate from test
   fixtures.
3. Clues must be traceable to real artifacts through explicit provenance.
4. Graph edges should become more evidence-backed over time, not more inferred
   by unsupported convenience.
5. A module does not belong in this repo unless it improves evidence capture,
   clue formation, graph quality, node scoring, or replay against real cases.

## What To Avoid

Do not let the project drift into:

1. benchmark machinery as a substitute for discovery capability
2. formatting or handoff layers as a substitute for graph quality
3. workflow taxonomy expansion before the core loop works
4. broad infrastructure that is not clearly justified by better clue-to-graph
   performance

## Operational Question

Every substantial change should be judged against this question:

How does this help us go from an observed clue in the AleaBito archive to an
evidence-backed graph that surfaces the kind of underappreciated node he was
finding?

If the answer is weak, the change is probably off-track.
