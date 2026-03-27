# Photonics Grounded Graph Review Surface v1

- graph id: `archive_photonics_grounded_v1`
- seed clue: `archive-clue-2003083807273152736`

## Nodes

- `lumentum` | `company` | `Lumentum Holdings Inc.` | public=`True`
- `coherent` | `company` | `Coherent Corp.` | public=`True`
- `axt` | `company` | `AXT, Inc.` | public=`True`
- `iqe` | `company` | `IQE plc` | public=`True`
- `aoi` | `company` | `Applied Optoelectronics, Inc.` | public=`True`
- `ai_data_center_photonics` | `theme` | `AI Data Center Photonics` | public=`False`
- `indium_phosphide` | `material` | `Indium Phosphide` | public=`False`

## Edges

- `lumentum-capacity-ai-photonics` | `lumentum` -> `ai_data_center_photonics` | `capacity_for` | confidence=`0.82` | evidence=`grounded-pack-lite-cohr-ai-photonics-v1`
- `coherent-capacity-ai-photonics` | `coherent` -> `ai_data_center_photonics` | `capacity_for` | confidence=`0.79` | evidence=`grounded-pack-lite-cohr-ai-photonics-v1`
- `aoi-capacity-ai-photonics` | `aoi` -> `ai_data_center_photonics` | `capacity_for` | confidence=`0.74` | evidence=`grounded-pack-aaoi-ai-transceiver-capacity-v1`
- `indium-phosphide-bottleneck-ai-photonics` | `indium_phosphide` -> `ai_data_center_photonics` | `bottleneck_to` | confidence=`0.85` | evidence=`grounded-pack-axti-inp-ai-interconnect-v1`
- `axt-proxy-indium-phosphide` | `axt` -> `indium_phosphide` | `proxy_for` | confidence=`0.82` | evidence=`grounded-pack-axti-inp-ai-interconnect-v1`
- `axt-supplier-lumentum` | `axt` -> `lumentum` | `supplier_of` | confidence=`0.73` | evidence=`grounded-pack-axti-inp-ai-interconnect-v1, grounded-pack-lite-cohr-ai-photonics-v1`
- `axt-supplier-coherent` | `axt` -> `coherent` | `supplier_of` | confidence=`0.71` | evidence=`grounded-pack-axti-inp-ai-interconnect-v1, grounded-pack-lite-cohr-ai-photonics-v1`
- `iqe-supplier-lumentum` | `iqe` -> `lumentum` | `supplier_of` | confidence=`0.86` | evidence=`grounded-pack-iqe-lumentum-supplier-v1`

## Ranked Public Nodes

- `axt` | composite=`0.783` | notes=`outgoing=3 leverage_edges=3 dependency_edges=0 public=True`
- `iqe` | composite=`0.621` | notes=`outgoing=1 leverage_edges=1 dependency_edges=0 public=True`
- `aoi` | composite=`0.616` | notes=`outgoing=1 leverage_edges=1 dependency_edges=0 public=True`
- `lumentum` | composite=`0.582` | notes=`outgoing=1 leverage_edges=1 dependency_edges=0 public=True`
- `coherent` | composite=`0.58` | notes=`outgoing=1 leverage_edges=1 dependency_edges=0 public=True`
