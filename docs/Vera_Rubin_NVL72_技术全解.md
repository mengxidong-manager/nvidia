# NVIDIA Vera Rubin NVL72 技术全解

> 六芯协同设计、机架级统一计算、45°C 温水液冷、五级存储分层、双模 Scale-out 网络——Vera Rubin NVL72 是 NVIDIA 为 Agentic AI 时代打造的下一代 AI 工厂基础单元。
>
> 撰写人：孟希東

---

## 机架核心指标

| 指标 | 规格 |
|------|------|
| GPU | 72 × Rubin R100（3nm，双芯片，3360 亿晶体管） |
| CPU | 36 × Vera（88 核 Arm Olympus，176 线程） |
| NVFP4 推理算力 | **3.6 EFLOPS** |
| 训练算力 | 2.5 EFLOPS |
| HBM4 总容量 | ~20.7 TB（288 GB × 72） |
| HBM4 总带宽 | 1.6 PB/s |
| LPDDR5X 总容量 | 最高 54 TB（1.5 TB × 36） |
| NVLink 全互联 | **260 TB/s** |
| Scale-out / GPU | 1.6 Tb/s（2 × 800G） |
| ICMS 容量 / GPU | 最高 16 TB（Pod 级） |
| ICMS Pod 总容量 | ~9,600 TB |
| 机架功耗 | 120-130 kW |
| 冷却 | **100% 液冷，45°C 温水，无需冷水机** |
| 供电 | 8 × 电源架（54V DC），97% 效率 |
| 架构 | 第三代 MGX，无线缆模块化托盘 |
| 组装时间 | ~5 分钟（计算托盘） |
| 机密计算 | 第三代，全系统加密 |
| vs Blackwell 推理 | **5× 性能，10× 成本效率** |
| vs Blackwell 训练 | 3.5× 性能，4× GPU 效率 |
| 上市 | 2026 H2 |

---

## 1. 架构总览

VR NVL72 是 NVIDIA 第二代机架级 Oberon 架构，将六种协同设计的芯片整合为一个统一的分布式加速器。整个机架就是一个计算单元。

### 基本计算单元：Vera Rubin Superchip

每个 Superchip 将 1 颗 Vera CPU 与 2 颗 Rubin GPU 通过 NVLink-C2C 封装在一起，应用可将 LPDDR5X 和 HBM4 视为统一内存池。整个机架由 36 个 Superchip 组成（36 CPU + 72 GPU）。

### 机架物理组成

- 72× Rubin GPU
- 36× Vera CPU
- NVLink 6 Switch
- ConnectX-9 SuperNIC
- BlueField-4 DPU
- Spectrum-6 Switch

### 机架物理设计

**无线缆模块化**：计算托盘通过板对板连接器连接，无线缆设计将组装时间从 2 小时缩短到 5 分钟。基于第三代 MGX 机架架构，支持从 Blackwell 无缝升级。

**可靠性设计**：第二代 RAS 引擎覆盖 GPU、CPU 和 NVLink，支持不停机预防性维护。NVLink 交换托盘支持零停机维护，可在运行中移除或部分填充。

**机密计算**：NVL72 是首个在整个系统范围内提供 NVIDIA 机密计算的机架级平台。第三代机密计算确保 CPU、GPU 和整个 NVLink 域的数据安全，每条总线在传输中加密。

---

## 2. 六大协同设计芯片

通过"极致协同设计"作为统一系统运行，每颗芯片各司其职。

### Rubin GPU（R100）

台积电 3nm 双芯片设计，3360 亿晶体管（Blackwell 的 1.6 倍）。

- HBM4：288 GB / 卡
- 带宽：22 TB/s / 卡
- TDP：2,300W
- NVLink：3.6 TB/s 双向

### Vera CPU（ARM）

自研 88 核 Arm Olympus 架构（v9.2），空间多线程支持 176 线程。

- 内存：最高 1.5 TB LPDDR5X
- C2C：1.8 TB/s → GPU
- vs PCIe 6：快 7 倍

### NVLink 6 Switch

第六代 NVLink，72 颗 GPU 全互联。Scale-up 带宽比上一代翻倍。

- 每 GPU：3.6 TB/s 双向
- 机架全互联：260 TB/s

### ConnectX-9 SuperNIC

高吞吐、低延迟端点网络接口，负责 scale-out AI 通信。

- 带宽：1.6 Tb/s / GPU
- 协议：800G Ethernet + IB
- PCIe：Gen6 48-lane

### BlueField-4 DPU

双芯片封装，集成 64 核 Grace CPU + ConnectX-9，负责基础设施卸载和安全。

- 功能：网络 / 存储 / 安全
- ICMS：推理上下文存储
- 隔离：ASTRA 多租户

### Spectrum-6 Switch

Scale-out 网络交换机，集成硅光（CPO），200G SerDes。

- 交换容量：102 TB/s
- 能效：5× 传统
- 可靠性：10× 传统

---

## 3. 散热系统

100% 液冷，45°C 温水直接冷却，无需冷水机组。从"制冷"转向"管道工程"。

### 三环路架构（冷却液循环链路）

```
Dry Cooler（室外散热） → CDU（冷却液分配） → 45°C → Cold Plate（直接接触芯片） → 65°C → CDU → Dry Cooler
```

**Loop 1 · FWS 设施水系统**：室外干冷器利用自然环境散热。45°C 在大多数地区高于环境温度，因此不需要耗电的冷水机组（chiller）。直接省去数据中心最大的电力开销之一。

**Loop 2 · CDU 冷却液分配**：系统的核心枢纽。泵组和歧管将 45°C 冷却液分配到机架，回收 65°C 热水送回室外。ΔT = 20°C 的大温差意味着更低的泵功耗。

**Loop 3 · DLC 直接液冷**：机架内 72 颗 Rubin GPU、36 颗 Vera CPU、NVLink 交换托盘全部通过冷板直接接触液冷。芯片硅结温约 100°C 时降频，45°C 供水仍有约 55°C 的散热裕量，足以高效冷却。电源架也采用水冷设计。

> **为什么不需要冷水机？** 45°C 的供水温度在全球绝大多数气候下高于室外环境温度，这意味着可以用简单的干冷器（风扇 + 散热片）将热量排到室外，无需消耗大量电力制冷。冷水机通常占数据中心总能耗的 30-40%，去掉后 PUE 大幅降低。

---

## 4. 供电架构

单机柜 130kW，从电网到 GPU 核心经历五级降压。当前 54V DC，未来演进至 800V HVDC。

### 供电链路：从电网到 GPU 核心

```
电网(10-35kV AC) → 变压器(→480V AC) → UPS(480V AC) → PDU(配电分发)
  → 电源架 PSU(→54V DC, η97%) → 铜母线(54V DC, 2500A+) → VRM(→~0.7V DC) → GPU核心
```

**电源架（Power Shelf）**：位于机架顶/底部，8 个电源架各含 6 × 5.5kW PSU（共 48 个 PSU），总供电能力 264kW。将 480V 三相 AC 转换为 54V DC，效率 97%，废热约 3.6kW（液冷排出）。

**铜母线（Busbar）**：沿机架背板垂直贯穿，将 54V DC 配电到各计算托盘。满载电流超过 2500A，发热显著。这是未来 800V HVDC 要解决的核心瓶颈。

**VRM 降压**：计算托盘上的电压调节模块将 54V DC 最终降到 GPU 核心所需的约 0.7-1.0V。这是整个链路中转换比最大的一级。

### 功率路线图

| 机架型号 | 功耗 | 配电 | 上市 |
|----------|------|------|------|
| VR NVL72 | 120-130 kW | 54V DC | 2026 H2 |
| VR NVL144 | 190 kW | 800V→54V 混合 | 2026 H2 |
| NVL144 CPX | 370 kW | 800V HVDC | 2026-2027 |
| Rubin Ultra Kyber | 600 kW | 800V HVDC | 2027 H2 |

> **800V HVDC 的意义**：将电压提高到 800V 可以将母线电流降低约 15 倍，大幅减少铜材用量和 I²R 热损耗。使用宽禁带半导体（GaN/SiC），端到端效率从 87% 提升到 92% 以上。这是支撑未来 600kW-1MW 机架的物理前提条件。

---

## 5. 存储体系

Vera Rubin 引入 ICMS（推理上下文内存存储），在 GPU HBM 与传统网络存储之间建立了全新的存储分层体系，专为 Agentic AI 的长上下文推理而设计。

### 五级存储分层

从最快（纳秒级）到最大（PB 级），KV Cache 在不同层级之间按需流动：

| 层级 | 介质 | 容量 | 用途 |
|------|------|------|------|
| G1 | GPU HBM4 | 288 GB/卡 · 22 TB/s | 热 KV Cache，当前推理窗口 |
| G2 | CPU LPDDR5X | 最高 1.5 TB/CPU | 温 KV Cache，预加载上下文 |
| G3 | 本地 NVMe SSD | 节点级快速缓存 | 本地溢出，毫秒级延迟 |
| G3.5 | ICMS（BlueField-4） | 每 GPU 最高 16 TB | Pod 级共享 KV Cache 存储 |
| G4 | 网络存储 | PB 级 | 训练数据集、Checkpoint、冷数据 |

### ICMS：推理上下文内存存储

这是 Vera Rubin 平台最重要的存储创新。随着 Agentic AI 的上下文窗口扩展到百万级 token，KV Cache 会迅速超出单机 GPU + CPU 内存容量。ICMS 将 KV Cache 提升为一等系统资源，在 Pod 范围内（1,152 颗 GPU）提供高速共享访问。

**架构设计**：每个 Vera Rubin Pod 包含一个专用 BlueField-4 机架，内含 16 个存储机箱，每个机箱 4 颗 BlueField-4 DPU，共 64 颗。每颗 BF4 后端连接 150 TB NVMe 闪存，Pod 总容量约 9,600 TB。

**工作原理**：推理框架（如 NVIDIA Dynamo）通过 NIXL 传输库在存储层级间调度 KV 块。ICMS 在 decode 阶段之前将 KV 块预加载到 G2/G1 内存中，减少推理中断。BlueField-4 上直接运行存储软件（如 VAST CNode），无需额外 x86 服务器。

**性能指标**：相比传统网络存储用于推理场景：每秒推理 token 数提升 5 倍，TCO 性能比提升 5 倍，能效提升 5 倍。通过 RDMA 加速，延迟远低于传统存储方案。

> **为什么 ICMS 如此重要？** Agentic AI 的推理会话远超单次 GPU 执行窗口——多轮对话、工具调用、长文档分析都需要保持巨大的 KV Cache。没有 ICMS，这些上下文要么被丢弃后重新计算（增加延迟），要么全部放在昂贵的 HBM 中（成本爆炸）。ICMS 用闪存级的成本提供了接近内存级的性能。

---

## 6. 网络互联

双层网络架构：NVLink 6 负责机架内 72 颗 GPU 全互联（scale-up），Spectrum-X Ethernet 或 Quantum-X InfiniBand 负责跨机架通信（scale-out）。

### Scale-Up：NVLink 6（机架内全互联，260 TB/s）

第六代 NVLink 为每颗 GPU 提供 3.6 TB/s 双向带宽，比 Blackwell 翻倍。72 颗 GPU 通过 NVLink 交换机实现全互联，整个机架的 bisection 带宽达到 260 TB/s。NVLink 交换托盘支持零停机维护——可在运行中移除或部分填充，机架仍可正常工作。软件定义的 NVLink 路由可在链路故障时自动绕行。

### Scale-Out：双模可选

每颗 GPU 通过 ConnectX-9 SuperNIC 提供 2 × 800 Gb/s（共 1.6 Tb/s）的 scale-out 带宽，支持两种网络方案：

**Spectrum-X Ethernet**：NVIDIA 自研的 AI 优化以太网方案。Spectrum-6 交换机集成硅光（CPO），102 TB/s 交换容量。CoreWeave 部署了多轨多平面 RoCE 架构，实现每 GPU 1.6 Tb/s 后端带宽，两层网络可扩展至数十万 GPU。

- 能效：5× 传统
- 可靠性：10× 传统
- 正常运行：5× 传统
- 特色：支持 ICMS 存储方案

**Quantum-X800 InfiniBand**：传统 HPC/AI 训练的首选网络。提供与 Spectrum-X 相同的每 GPU 带宽（2 × 800 Gb/s），但使用 InfiniBand 协议，在集合通信（AllReduce 等）场景下有独特的硬件加速优势。

- 协议：InfiniBand HDR/NDR
- 优势：集合通信硬件卸载
- 场景：大规模分布式训练
- 生态：成熟的 HPC 生态

> **如何选择 Spectrum-X vs Quantum-X？** Spectrum-X Ethernet 适合推理为主的工作负载，特别是需要 ICMS 存储扩展的 Agentic AI 场景，且运维团队熟悉以太网。Quantum-X InfiniBand 适合大规模训练集群，对集合通信性能要求极高的场景。两者提供相同的 GPU 侧带宽，选择取决于工作负载类型和运维偏好。

### ConnectX-9 SuperNIC（GPU 的网络接口，1.6 Tb/s）

每颗 GPU 配备 ConnectX-9 SuperNIC，提供可编程 RDMA 能力，实现低延迟、GPU-Direct 网络通信。支持 800G Ethernet（4×200G PAM4 SerDes）和 InfiniBand 双模。PCIe Gen6 48 通道，是 CX-8 的迭代升级，新增 800G 以太网支持。VR NVL72 每个计算托盘包含 4 颗 CX-9，为 4 颗 Rubin GPU 各提供独立网络路径。

---

## 7. 规格汇总

NVL72 机架核心参数一览：

| 指标 | 规格 |
|------|------|
| GPU | 72 × Rubin R100（3nm，双芯片，3360 亿晶体管） |
| CPU | 36 × Vera（88 核 Arm Olympus，176 线程） |
| HBM4 总容量 | ~20.7 TB（288 GB × 72） |
| HBM4 总带宽 | 1.6 PB/s |
| LPDDR5X 总容量 | 最高 54 TB（1.5 TB × 36） |
| NVFP4 推理算力 | 3.6 EFLOPS |
| 训练算力 | 2.5 EFLOPS |
| NVLink 全互联带宽 | 260 TB/s |
| Scale-out 带宽 / GPU | 1.6 Tb/s（2 × 800G） |
| ICMS 容量 / GPU | 最高 16 TB（Pod 级） |
| ICMS Pod 总容量 | ~9,600 TB |
| 机架功耗 | 120-130 kW |
| 冷却方式 | 100% 液冷，45°C 温水，无需冷水机 |
| 供电 | 8 × 电源架（54V DC），97% 效率 |
| 机架架构 | 第三代 MGX，无线缆模块化托盘 |
| 组装时间 | ~5 分钟（计算托盘） |
| 机密计算 | 第三代，全系统加密 |
| vs Blackwell 推理 | 5× 性能，10× 成本效率 |
| vs Blackwell 训练 | 3.5× 性能，4× GPU 效率 |
| 上市时间 | 2026 H2 |

### Pod / 集群扩展

| 配置 | GPU 数 | 机架数 | FP4 算力 | HBM4 |
|------|--------|--------|----------|------|
| NVL72（单机架） | 72 | 1 | 3.6 EFLOPS | ~20.7 TB |
| Scalable Unit | 1,152 | 16 + 网络/存储 | ~57.6 EFLOPS | ~331 TB |
| Rubin Ultra Kyber | 144 | 1 | 15 EFLOPS | — |
