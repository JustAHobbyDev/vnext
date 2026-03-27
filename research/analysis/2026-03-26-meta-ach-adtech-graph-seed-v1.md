# META ACH / Adtech Graph Seed v1

- graph id: `meta_ach_adtech_seed_v1`
- stage: `seed_hypothesis`
- seed clue: `meta-ach-ad-funding-community-clue-v1`

## Seed Interpretation

The clue is not a supply-chain clue. It is a platform-monetization clue:

- Meta may be changing advertiser funding rails toward ACH
- the author reads this as near-term negative, long-term positive
- the most interesting branch is not generic AI capex
- the most interesting branch is advertiser onboarding, funding friction, and campaign velocity

## Nodes

- `meta` | `company` | `Meta Platforms, Inc.` | public=`True`
- `meta_ad_platform` | `platform` | `Meta Advertising Platform` | public=`False`
- `advertiser_onboarding` | `workflow` | `Advertiser Onboarding` | public=`False`
- `ach_ad_funding` | `payment_workflow` | `ACH Ad Funding` | public=`False`
- `smb_advertiser_liquidity` | `economic_driver` | `SMB Advertiser Liquidity` | public=`False`
- `campaign_launch_frequency` | `behavioral_metric` | `Campaign Launch Frequency` | public=`False`
- `measurement_attribution` | `service_layer` | `Measurement and Attribution` | public=`False`
- `marketing_automation` | `service_layer` | `Marketing Automation` | public=`False`
- `merchant_smb_software` | `software_layer` | `Merchant and SMB Software` | public=`False`
- `payment_rails` | `infrastructure_layer` | `Payment Rails` | public=`False`

## Edges

- `meta-owns-ad-platform` | `meta` -> `meta_ad_platform` | `capacity_for` | confidence=`0.95`
- `ad-platform-depends-on-onboarding` | `meta_ad_platform` -> `advertiser_onboarding` | `depends_on` | confidence=`0.81`
- `onboarding-enabled-by-ach-funding` | `advertiser_onboarding` -> `ach_ad_funding` | `depends_on` | confidence=`0.42`
- `ach-funding-improves-smb-liquidity` | `ach_ad_funding` -> `smb_advertiser_liquidity` | `capacity_for` | confidence=`0.37`
- `smb-liquidity-increases-campaign-frequency` | `smb_advertiser_liquidity` -> `campaign_launch_frequency` | `capacity_for` | confidence=`0.34`
- `campaign-frequency-drives-meta-ad-platform` | `campaign_launch_frequency` -> `meta_ad_platform` | `capacity_for` | confidence=`0.52`
- `meta-ad-platform-requires-measurement` | `meta_ad_platform` -> `measurement_attribution` | `depends_on` | confidence=`0.67`
- `meta-ad-platform-integrates-marketing-automation` | `meta_ad_platform` -> `marketing_automation` | `partner_of` | confidence=`0.64`
- `merchant-software-feeds-campaign-frequency` | `merchant_smb_software` -> `campaign_launch_frequency` | `capacity_for` | confidence=`0.48`
- `payment-rails-enable-ach-funding` | `payment_rails` -> `ach_ad_funding` | `depends_on` | confidence=`0.58`

## Candidate Classes

- `payment_infrastructure`
  - interesting if ACH funding is real and broad
- `marketing_automation`
  - interesting if easier funding increases campaign velocity
- `measurement_attribution`
  - interesting if more campaign activity drives more measurement demand
- `merchant_smb_software`
  - interesting if merchant workflow tools feed directly into Meta ad activation

## What Must Be Proven Next

1. Meta actually supports or is expanding ACH-based advertiser funding
2. The change is material enough to affect advertiser behavior
3. Named vendors, tools, or workflow layers can be tied to the funding/onboarding process
4. A non-obvious public beneficiary exists beyond Meta itself

## Current Read

This is a plausible differentiated graph, but it is still a hypothesis graph.

It should not be treated as grounded until the ACH claim and workflow dependencies are supported by real source artifacts.
