**Plan**

1. Build a normalized enrichment layer over `research/analysis/aleabitoreddit-daily-archive-v1.json`.
2. Add factual entity extraction first: links, mentions, cashtags, hashtags, reply/quote relationships.
3. Use the enriched archive for text-and-relationship clue extraction.
4. Ground promising clues in real linked evidence when available.

**Phase 1: Schema And Inventory**
Status: executed on March 25, 2026

Observed raw archive file:

- `research/analysis/aleabitoreddit-daily-archive-v1.json`

Observed top-level schema:

- `fetched_at`
- `mode`
- `username`
- `user`
- `start_date`
- `end_date`
- `days_completed`
- `posts`
- `stop_reason`
- `stopped_early`

Observed post count:

- `4002`

Observed per-post schema:

- `author_id`
- `bucket_date`
- `conversation_id`
- `created_at`
- `entities`
- `id`
- `lang`
- `public_metrics`
- `referenced_tweets`
- `text`

Observed nested schema:

- `entities.cashtags`
- `entities.hashtags`
- `entities.mentions`
- `entities.urls`
- `public_metrics.bookmark_count`
- `public_metrics.impression_count`
- `public_metrics.like_count`
- `public_metrics.quote_count`
- `public_metrics.reply_count`
- `public_metrics.retweet_count`
- `referenced_tweets[].id`
- `referenced_tweets[].type`

Observed coverage:

- posts with `entities`: `4002`
- posts with `entities.urls`: `1253`
- posts with `entities.mentions`: `3147`
- posts with `entities.cashtags`: `2847`
- posts with `entities.hashtags`: `1`
- posts with `referenced_tweets`: `3704`
- observed `referenced_tweets[].type` values:
  - `quoted`
  - `replied_to`
  - `retweeted`

Important Phase 1 finding:

- the archive already contains structured link and mention data
- the archive does not appear to contain explicit image, media, photo, or
  attachment fields
- however, some entries in `entities.urls` are image-adjacent X photo links such
  as `https://x.com/.../status/.../photo/1`
- therefore media discovery is still partially possible through deterministic URL
  classification
- however, image fetching and interpretation are now intentionally shelved
  because the expected cost is not justified by current value

Stable enriched-post schema to target in Phase 2:

- preserve raw fields unchanged:
  - `id`
  - `author_id`
  - `created_at`
  - `text`
  - `bucket_date`
  - `conversation_id`
  - `lang`
  - `public_metrics`
  - `entities`
  - `referenced_tweets`
- add deterministic normalized fields:
  - `post_id`
  - `urls`
  - `expanded_urls`
  - `domains`
  - `mentioned_users`
  - `cashtags`
  - `hashtags`
  - `reply_to_post_id`
  - `quoted_post_id`
  - `retweeted_post_id`
  - `conversation_root_id`
  - `external_link_count`
  - `mention_count`
  - `cashtag_count`
- reserve media fields for a later attachment-recovery path:
  - `attachments`
  - `attachment_ids`

Attachment inventory decision:

- do not fabricate attachment inventory from absent explicit media fields
- allow Phase 2 to classify probable media URLs from `entities.urls`
- do not pursue image recovery, mirroring, or interpretation in the active plan
- keep probable media URLs only as low-cost metadata

Phase 1 outputs now defined as:

- `PLAN.md` section updated with actual schema audit and inventory constraints
- no standalone `aleabitoreddit-attachment-inventory-v1.json` should be emitted
  yet because the source archive does not contain attachment metadata

**Phase 2: Deterministic Enrichment**
Status: executed on March 25, 2026

Implemented:

- deterministic enrichment module:
  - `src/vnext/archive/enrichment.py`
- runner script:
  - `scripts/enrich_aleabitoreddit_archive.py`
- targeted tests:
  - `tests/test_archive_enrichment.py`

Execution behavior:

- reads `research/analysis/aleabitoreddit-daily-archive-v1.json`
- normalizes URLs and domains
- extracts `mentioned_users`, `cashtags`, and `hashtags`
- derives `reply_to_post_id`, `quoted_post_id`, and `retweeted_post_id`
- classifies URLs into:
  - `x_post_photo`
  - `x_post`
  - `external_link`
  - `direct_image`
  - `short_media_link`
- records probable media URLs deterministically from URL patterns
- builds post-to-post, post-to-domain, post-to-url, post-to-user, and
  post-to-cashtag edges

Generated outputs:

- `research/analysis/aleabitoreddit-archive-enriched-v1.json`
- `research/analysis/aleabitoreddit-link-graph-v1.json`

Observed output summary:

- enriched post count: `4002`
- posts with URLs: `1253`
- posts with mentions: `3147`
- posts with cashtags: `2847`
- posts with probable media URLs: `1121`
- URL classification counts:
  - `x_post_photo`: `1121`
  - `x_post`: `502`
  - `external_link`: `4`
- referenced tweet type counts:
  - `replied_to`: `3258`
  - `quoted`: `491`
  - `retweeted`: `5`
- link-graph totals:
  - nodes: `10743`
  - edges: `18510`

Phase 2 conclusion:

- deterministic enrichment is working
- the archive is much more self-contained for clue-discovery work now
- probable image-bearing posts can already be identified through URL
  classification
- image-related processing is intentionally shelved from here forward unless the
  cost/value tradeoff changes

**Phase 3: Text And Relationship Clue Extraction**
Status: executed on March 25, 2026

Implemented:

- clue extraction module:
  - `src/vnext/archive/clue_extraction.py`
- runner script:
  - `scripts/extract_archive_clue_candidates.py`
- targeted tests:
  - `tests/test_clue_extraction.py`

Execution behavior:

- reads `research/analysis/aleabitoreddit-archive-enriched-v1.json`
- scores posts using deterministic heuristics over:
  - text language
  - cashtag density
  - mentions
  - reply/quote context
  - external links
- prioritizes signals such as:
  - dependency language
  - bottleneck or constraint language
  - comparative or relationship language
  - unusually specific numeric detail
- suppresses broad ratings-list shapes and ticker-dense posts without clear
  relational language
- emits review-oriented clue candidates rather than final scores

Generated outputs:

- `research/analysis/aleabitoreddit-clue-candidates-v1.json`
- `research/analysis/aleabitoreddit-discovery-review-surface-v1.md`

Observed output summary:

- candidate count: `449`
- high priority candidates: `185`
- medium priority candidates: `253`
- clue type counts:
  - `multi_entity_signal`: `378`
  - `conversation_signal`: `408`
  - `dependency_signal`: `138`
  - `bottleneck_signal`: `252`
  - `relationship_signal`: `92`
  - `specificity_signal`: `137`
  - `linked_evidence_signal`: `1`

Observed Phase 3 result:

- the archive now has a reviewable clue-candidate layer
- the top candidates include photonics-style supplier, bottleneck, and
  dependency language
- the output is intentionally heuristic and still noisy, but it is a useful
  discovery surface for graph-building work

**Phase 4: Evidence Grounding For Candidate Clues**
Status: partially executed on March 25, 2026

- implemented queue builder:
  - `src/vnext/archive/grounding_queue.py`
- implemented runner script:
  - `scripts/build_evidence_grounding_queue.py`
- added targeted tests:
  - `tests/test_grounding_queue.py`
- prioritize clue candidates that already contain external links
- map linked domains to source classes
- mirror and validate a small set of supporting real artifacts for the best clue
  candidates
- connect clue candidates to explicit evidence provenance

Outputs:
- `research/analysis/aleabitoreddit-evidence-grounding-queue-v1.json`
- `research/analysis/aleabitoreddit-evidence-grounding-review-surface-v1.md`
- `research/analysis/aleabitoreddit-grounded-clue-packs-v1.json`
- `research/analysis/aleabitoreddit-grounded-clue-review-surface-v1.md`
- `research/analysis/aleabitoreddit-photonics-grounded-graph-v1.json`
- `research/analysis/aleabitoreddit-photonics-grounded-graph-review-surface-v1.md`
- small grounded clue packs for selected cases

Observed queue summary:

- queue size: `30`
- theme counts:
  - `photonics`: `28`
  - `memory`: `2`
- evidence mode counts:
  - `manual_evidence_search`: `30`
- review priority:
  - `high`: `30`

Observed Phase 4 result so far:

- the broad clue set has been narrowed into a smaller evidence-grounding queue
- the queue is strongly biased toward photonics-style supplier, bottleneck, and
  capacity posts
- because external evidence links are rare in the archive, the immediate next
  step is manual evidence search for the top queue items rather than automated
  direct-link grounding
- a first manual grounding pass has now been completed for:
  - `LITE / COHR` AI photonics positioning
  - `AXTI` indium phosphide AI interconnect positioning
  - `IQE` as a `LITE` supplier
  - `AAOI` datacenter transceiver demand and capacity
- those grounded packs now support an explicit photonics graph with:
  - `7` nodes
  - `8` evidence-backed edges
- the current grounded graph ranks public nodes as:
  - `AXTI`
  - `IQE`
  - `AOI`
  - `LITE`
  - `COHR`

**Phase 5: Discovery-Oriented Views**
- Derive views optimized for clue discovery:
  - posts with external evidence links
  - posts with high-density mentions/cashtags
  - posts with multi-entity relationship structure
- Rank for review, not scoring.

Outputs:
- `aleabitoreddit-clue-candidates-v1.json`
- `aleabitoreddit-discovery-review-surface-v1.md`

**Guardrails**
- Keep raw archive separate from enriched outputs.
- Keep deterministic extraction separate from later interpretive layers.
- Preserve parent linkage from every enriched record back to raw post and mirrored attachment.
- Do not let missing linked evidence fail silently.
- Do not spend active effort on image fetching or image interpretation unless
  the cost/value tradeoff is revisited.

**Implementation Order**
1. Schema audit of the raw archive.
2. Deterministic link/mention extraction.
3. Text-and-relationship clue extraction.
4. Evidence grounding for selected clues.
5. Discovery-oriented review surface.

**Main Risks**
- Some mention/link data may be incomplete if the raw export is sparse.
- clue heuristics can become too broad and produce noisy review sets.
- linked evidence may still be sparse for some promising archive posts.

**Recommendation**
Keep the current deterministic enrichment outputs as the base layer and move
next into text-and-relationship clue extraction, not image handling.
