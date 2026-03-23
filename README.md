# vNext Seed

This directory is the clean proof-path seed for the next project.

## Goal

Prove that vNext can:

1. capture a real clue
2. build a graph from that clue
3. surface connected nodes
4. rank the most underappreciated node early enough to matter

## Scope

The active vNext loop is:

1. `clues`
2. `graph`
3. `scoring`
4. `benchmarks`

## Not In Scope

1. execution policy
2. options expression logic
3. lane taxonomy growth
4. large downstream formatting layers

## Layout

- `docs/`
- `src/vnext/`
- `benchmarks/`

## Rule

If a change does not improve clue capture, graph quality, node scoring, or
benchmark evaluation, it should not land here.

## Evidence Guardrail

Discovery and benchmark inputs must come from local mirrored artifacts whose
provenance resolves to real-world sources.

Synthetic inputs are allowed only in `tests/` for code-mechanics coverage and
must not be used by the strict clue/evidence loader.
