# NVIDIA & 运维技术文档

> 运维技术文档合集 — 孟希東

## 文档列表

| 文档 | 内容 |
|------|------|
| [数据中心供电架构详解](docs/数据中心供电架构详解.md) | 双路市电 / 双柴发 / UPS+电池 / 240V HVDC 直流 / 800V 演进趋势 |
| [数据中心制冷技术详解](docs/数据中心制冷技术详解.md) | CRAC/CRAH 传统风冷 / 房间行级机柜级 / 冷板式浸没式喷淋式液冷 / 风液混合 |
| [GPU 集群常见问题与故障排查手册](docs/GPU集群常见问题与故障排查手册.md) | XID 错误速查 · ECC/PCIe/NVLink 诊断 · 训练故障 · 推理问题 · 散热供电 · 预防性维护 |
| [Vera Rubin NVL72 技术全解](docs/Vera_Rubin_NVL72_技术全解.md) | 架构 / 六大芯片 / 45°C 液冷 / 供电 / 存储 / 网络 |
| [B300/GB300 NVL72 技术全解](docs/B300_GB300_NVL72_技术全解.md) | Blackwell Ultra 架构 / B300 vs B200 / 散热 / 供电 / 内存 / 网络 |
| [Aivres KR6288 (HGX H200) 训练节点网络结构 — s110-b7](docs/HGX_H200训练节点网络结构_s110-b7.md) | 铭牌解码 / 8:8:2 网络 / IBBZ 计算网 / 接线表 / 拓扑 SVG |
| [s110 集群网络架构 — 交换机与 CPU 服务器](docs/s110集群网络架构_交换机与CPU服务器.md) | 三张网分层 / 交换机清单(Quantum-2/Spectrum) / CPU 服务器角色 / pod 拓扑 SVG |
| [nvidia-smi 运维命令速查手册](docs/nvidia-smi运维命令速查手册.md) | GPU 监控 / 健康检查 / 性能调优 / NVLink 诊断 |
| [AIDC 机房运维流程](docs/AIDC机房运维流程.md) | 六大运维域 / AIOps / 典型工作流 / 与传统 DC 对比 |
| [AIDC 故障全生命周期管理流程](docs/AIDC故障全生命周期管理流程.md) | 7 阶段 29 步故障管理 SOP / 分级定义 / 时效要求 |
| [Dell RAID 故障恢复手册](docs/Dell_RAID故障恢复手册.md) | RAID 0/1/5/10 故障恢复 / perccli 命令 / 热插拔流程 |

关联仓库：[kubernetes](https://github.com/mengxidong-manager/kubernetes) · [network](https://github.com/mengxidong-manager/network)
