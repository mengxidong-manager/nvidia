# Documentation Index (English)

English index for this repository. Document bodies are written in Chinese; all links below are percent-encoded and work in any client.

> 中文目录请见 [README.md](README.md)

---

## AI Cluster Architecture

| Document | Contents |
|---|---|
| [HGX B300 Training Cluster — As-Built Architecture v1.0](docs/HGX_B300%E8%AE%AD%E7%BB%83%E9%9B%86%E7%BE%A4%E8%AE%BE%E8%AE%A1%E6%96%B9%E6%A1%88_1024GPU.md) | 127 nodes / 1016 GPUs, dual-plane RoCEv2, 76 H3C switches, WEKA, native K8s, capacity ledger |
| [HGX H200 Training Node Network — s110-b7](docs/HGX_H200%E8%AE%AD%E7%BB%83%E8%8A%82%E7%82%B9%E7%BD%91%E7%BB%9C%E7%BB%93%E6%9E%84_s110-b7.md) | Nameplate decoding, 8:8:2 topology, IBBZ compute fabric, cabling table |
| [s110 Cluster Network — Switches & CPU Servers](docs/s110%E9%9B%86%E7%BE%A4%E7%BD%91%E7%BB%9C%E6%9E%B6%E6%9E%84_%E4%BA%A4%E6%8D%A2%E6%9C%BA%E4%B8%8ECPU%E6%9C%8D%E5%8A%A1%E5%99%A8.md) | Three-plane layering, switch inventory, CPU server roles, pod topology |
| [800G Optics & Leaf Switch Connection Guide](docs/800G%E5%85%89%E6%A8%A1%E5%9D%97%E4%B8%8ELeaf%E4%BA%A4%E6%8D%A2%E6%9C%BA%E8%BF%9E%E6%8E%A5%E6%96%B9%E5%BC%8F%E8%AF%A6%E8%A7%A3.md) | 800G optical module types, breakout modes, Leaf switch port mapping |

## Hardware Deep Dives

| Document | Contents |
|---|---|
| [B300 / GB300 NVL72 Deep Dive](docs/B300_GB300_NVL72_%E6%8A%80%E6%9C%AF%E5%85%A8%E8%A7%A3.md) | Blackwell Ultra architecture, B300 vs B200, cooling, power, memory, networking |
| [Vera Rubin NVL72 Deep Dive](docs/Vera_Rubin_NVL72_%E6%8A%80%E6%9C%AF%E5%85%A8%E8%A7%A3.md) | Architecture, six chips, 45°C liquid cooling, power, storage, networking |
| [Gigabyte HGX B300 Server Operations Manual](docs/Gigabyte_HGX_B300_%E6%9C%8D%E5%8A%A1%E5%99%A8%E8%BF%90%E7%BB%B4%E6%89%8B%E5%86%8C.md) | G894-ZD3-AAX7 hardware ops and maintenance procedures |

## Operations & Troubleshooting

| Document | Contents |
|---|---|
| [GPU Cluster Troubleshooting Handbook](docs/GPU%E9%9B%86%E7%BE%A4%E5%B8%B8%E8%A7%81%E9%97%AE%E9%A2%98%E4%B8%8E%E6%95%85%E9%9A%9C%E6%8E%92%E6%9F%A5%E6%89%8B%E5%86%8C.md) | XID error reference, ECC/PCIe/NVLink diagnostics, training & inference issues |
| [GPU Fallen-Off-Bus Incident Handbook](docs/GPU%E9%9B%86%E7%BE%A4%E6%8E%89%E5%8D%A1%E6%95%85%E9%9A%9C%E5%A4%84%E7%90%86%E6%89%8B%E5%86%8C.md) | Inference vs. training SOP, zero-downtime techniques, checkpoint strategy, YAML snippets |
| [nvidia-smi Command Reference](docs/nvidia-smi%E8%BF%90%E7%BB%B4%E5%91%BD%E4%BB%A4%E9%80%9F%E6%9F%A5%E6%89%8B%E5%86%8C.md) | GPU monitoring, health checks, performance tuning, NVLink diagnostics |
| [Dell RAID Recovery Handbook](docs/Dell_RAID%E6%95%85%E9%9A%9C%E6%81%A2%E5%A4%8D%E6%89%8B%E5%86%8C.md) | RAID 0/1/5/10 recovery, perccli commands, hot-swap procedures |

## Data Center Facilities

| Document | Contents |
|---|---|
| [Data Center Power Architecture](docs/%E6%95%B0%E6%8D%AE%E4%B8%AD%E5%BF%83%E4%BE%9B%E7%94%B5%E6%9E%B6%E6%9E%84%E8%AF%A6%E8%A7%A3.md) | Dual utility feeds, generators, UPS, 240V HVDC, 800V roadmap |
| [Data Center Cooling Technologies](docs/%E6%95%B0%E6%8D%AE%E4%B8%AD%E5%BF%83%E5%88%B6%E5%86%B7%E6%8A%80%E6%9C%AF%E8%AF%A6%E8%A7%A3.md) | CRAC/CRAH air cooling, row/rack level, cold plate / immersion / spray, hybrid |
| [AIDC Data Center Operations Workflow](docs/AIDC%E6%9C%BA%E6%88%BF%E8%BF%90%E7%BB%B4%E6%B5%81%E7%A8%8B.md) | Six operational domains, AIOps, typical workflows, vs. traditional DC |
| [AIDC Incident Lifecycle Management](docs/AIDC%E6%95%85%E9%9A%9C%E5%85%A8%E7%94%9F%E5%91%BD%E5%91%A8%E6%9C%9F%E7%AE%A1%E7%90%86%E6%B5%81%E7%A8%8B.md) | 7-phase / 29-step incident SOP, severity levels, SLA targets |

---

## Diagrams

| Diagram | Document |
|---|---|
| [B300 cluster network architecture](docs/images/b300-network-arch-127.svg) | As-built, 127 nodes |
| [Dual-plane fabric](docs/images/b300-dualplane.svg) | B300 cluster |
| [Rack layout](docs/images/b300-rack-layout.svg) | B300 cluster |
| [Fault handling flow](docs/images/gpu-fault-flow.svg) | Fallen-off-bus handbook |
| [s110-b7 node topology](docs/images/s110-b7-topology.svg) | H200 node |
| [s110 pod topology](docs/images/s110-pod-topology.svg) | s110 cluster |

---

## Related Repositories

- [network](https://github.com/mengxidong-manager/network) — networking protocols and AI cluster communication patterns ([English index](https://github.com/mengxidong-manager/network/blob/main/INDEX-EN.md))
- [kubernetes](https://github.com/mengxidong-manager/kubernetes)
