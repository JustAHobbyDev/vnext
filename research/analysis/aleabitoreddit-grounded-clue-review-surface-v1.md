# Grounded Clue Review Surface v1

Generated at: 2026-03-25T11:45:00+00:00

## Purpose

This file records the first manual evidence-grounding pass for the highest-value
archive clue candidates. The goal is not to prove every archive inference. The
goal is to separate:

1. what the archive is clearly pointing at
2. what primary sources already support
3. what remains an inference that still needs evidence

## Grounding Packs

### grounded-pack-lite-cohr-ai-photonics-v1

- source queue item:
  - `grounding-queue-2003083807273152736`
- status:
  - `partially_grounded`
- focus:
  - `LITE`
  - `COHR`

Grounded:

- Lumentum publicly markets AI/cloud datacenter transceivers and states that its
  data-center optical portfolio is built on an indium phosphide platform.
- Coherent publicly markets datacom optical transceivers and InP optoelectronic
  devices for high-speed datacenter connectivity.

Still inference:

- the archive post's stronger `duopoly` framing
- the present-tense system-level supply-constraint claim

Primary sources:

- https://www.lumentum.com/en/products/data-center/datacom-transceivers
- https://www.lumentum.com/en/products/data-center
- https://investor.lumentum.com/financial-news-releases/news-details/2025/Lumentum-Showcases-Next-Generation-InP-Chip-Solutions-Enabling-Scalable-AI-Data-Centers-at-OFC-2025/default.aspx
- https://www.coherent.com/networking/transceivers/datacom.html
- https://www.coherent.com/news/press-releases/coherent-introduces-200g-indium-phosphile-electro-absorption-modulated-lasers
- https://www.coherent.com/networking/optoelectronic-devices/inp-optoelectronics

### grounded-pack-axti-inp-ai-interconnect-v1

- source queue item:
  - `grounding-queue-2014500318827168215`
- status:
  - `grounded_core_claim`
- focus:
  - `AXTI`

Grounded:

- AXT said in May 2024 that customers were using its indium phosphide
  substrates for high-speed optical components in AI interconnects.
- AXT said in August 2024 that indium phosphide would be required in optical
  transceivers for high-speed data transmission in AI applications.
- AXT raised capital in late 2025 to increase indium phosphide manufacturing
  capacity and described AI-infrastructure-driven growth again in February 2026.

Still inference:

- the archive's strongest bottleneck language around `entire AI industry`

Primary sources:

- https://investors.axt.com/Investors/news/news-details/2024/AXT-Inc.-Announces-First-Quarter-2024-Financial-Results/default.aspx
- https://investors.axt.com/Investors/news/news-details/2024/AXT-Inc.-Announces-Second-Quarter-2024-Financial-Results/
- https://investors.axt.com/Investors/news/news-details/2025/AXT-Announces-Closing-of-Public-Offering-of-Common-Stock-and-Full-Exercise-of-Underwriters-Option-to-Purchase-Additional-Shares/default.aspx
- https://investors.axt.com/Investors/news/news-details/2026/AXT-Inc--Announces-Fourth-Quarter-and-Fiscal-Year-2025-Financial-Results/default.aspx

### grounded-pack-iqe-lumentum-supplier-v1

- source queue item:
  - `grounding-queue-2032944164439208062`
- status:
  - `partially_grounded`
- focus:
  - `IQE`
  - `LITE`

Grounded:

- IQE announced a multi-year strategic supply agreement with Lumentum for
  epiwafers used across Lumentum laser products, explicitly including optical
  networking and data communications.
- IQE later reported photonics demand tied to AI and data-center markets.

Still inference:

- the stronger archive claim that IQE is itself a critical public bottleneck
  expression for AI photonics

Primary sources:

- https://www.iqep.com/media/press-releases/2022/iqe-announces-multi-year-strategic-supply-agreement-with-lumentum/
- https://www.iqep.com/media/press-releases/2026/trading-update/

### grounded-pack-aaoi-ai-transceiver-capacity-v1

- source queue item:
  - `grounding-queue-2029223044208832707`
- status:
  - `partially_grounded`
- focus:
  - `AAOI`

Grounded:

- AOI reported growing demand for 400G and 800G products and said it was
  building capacity to meet that demand.
- AOI later announced a first volume order for 800G datacenter transceivers
  from a major hyperscale customer tied to AI datacenter growth.

Still inference:

- the archive's specific claim about how many hyperscalers would absorb all
  available supply

Primary sources:

- https://newsroom.ao-inc.com/news-releases/applied-optoelectronics-reports-first-quarter-2025-results/
- https://newsroom.ao-inc.com/news-releases/aoi-receives-first-volume-order-of-800g-data-center-transceivers-from-major-hyperscale-customer/?hss_channel=lcp-744608

## Next Step

The next grounding pass should focus on collecting source artifacts for the top
`AXTI`, `LITE/COHR`, and `IQE/LITE` packs first, because they most directly
match the archive's clue-to-graph bottleneck logic.
