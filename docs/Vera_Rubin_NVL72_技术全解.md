# NVIDIA Vera Rubin NVL72 技术全解

> 六芯协同设计、机架级统一计算、45°C 温水液冷、五级存储分层、双模 Scale-out 网络
>
> 撰写人：孟希东（测试）

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
| NVLink 全互联 | **260 TB/s** |
| Scale-out / GPU | 1.6 Tb/s（2 × 800G） |
| 机架功耗 | 120-130 kW |
| 冷却 | **100% 液冷，45°C 温水，无需冷水机** |
| 供电 | 8 × 电源架（54V DC），97% 效率 |
| 架构 | 第三代 MGX，无线缆模块化托盘 |
| vs Blackwell 推理 | **5× 性能，10× 成本效率** |
| 上市 | 2026 H2 |

---

## 1. 架构总览

### 基本计算单元：Vera Rubin Superchip

每个 Superchip 将 1 颗 Vera CPU 与 2 颗 Rubin GPU 通过 NVLink-C2C 封装在一起，LPDDR5X 和 HBM4 可视为统一内存池。整个机架由 36 个 Superchip 组成。

### 机架物理设计

- **无线缆模块化**：板对板连接器，组装时间从 2 小时缩短到 5 分钟
- **第三代 MGX 架构**：支持从 Blackwell 无缝升级
- **第二代 RAS 引擎**：不停机预防性维护，软件定义 NVLink 路由
- **机密计算**：第三代全系统加密，每条总线传输中加密

---

## 2. 六大协同设计芯片

### Rubin GPU（R100）

- 台积电 3nm，双芯片，3360 亿晶体管（Blackwell 1.6×）
- HBM4：288 GB / 卡，带宽 22 TB/s
- NVLink：3.6 TB/s 双向
- TDP：2,300W

### Vera CPU

- 自研 88 核 Arm Olympus（v9.2），空间多线程 176 线程
- 最高 1.5 TB LPDDR5X
- NVLink-C2C：1.8 TB/s → GPU（比 PCIe Gen6 快 7×）

### NVLink 6 Switch

- 每 GPU 3.6 TB/s 双向，机架全互联 260 TB/s
- Scale-up 带宽比上一代翻倍
- 支持零停机维护，可运行中移除或部分填充

### ConnectX-9 SuperNIC

- 1.6 Tb/s / GPU（2 × 800G）
- 支持 800G Ethernet + InfiniBand 双模
- PCIe Gen6 48-lane

### BlueField-4 DPU

- 双芯片：64 核 Grace CPU + ConnectX-9
- 负责网络/存储/安全卸载
- 支持 ICMS 推理上下文存储
- ASTRA 多租户隔离

### Spectrum-6 Switch

- 102 TB/s 交换容量，集成硅光（CPO）
- 能效 5×、可靠性 10×、正常运行 5×

---

## 3. 散热系统

### 三环路架构

```
Dry Cooler（室外） → CDU（冷却液分配） → 45°C → Cold Plate（直接接触芯片） → 65°C → CDU → Dry Cooler
```

| 环路 | 组件 | 作用 |
|------|------|------|
| Loop 1 - FWS | 室外干冷器 | 自然环境散热，无需冷水机 |
| Loop 2 - CDU | 冷却液分配单元 | 泵组+歧管，45°C 供水 / 65°C 回水，ΔT=20°C |
| Loop 3 - DLC | 冷板直接液冷 | GPU/CPU/NVLink 交换托盘全部液冷 |

> **为什么不需要冷水机？** 45°C 供水温度在全球绝大多数气候下高于室外环境温度，用简单的干冷器即可散热。冷水机通常占数据中心总能耗的 30-40%。

---

## 4. 供电架构

### 供电链路

```
电网(10-35kV AC) → 变压器(→480V AC) → UPS → PDU → 电源架(→54V DC, η97%) → 铜母线(2500A+) → VRM(→~0.7V) → GPU核心
```

- **电源架**：8 个，各含 6×5.5kW PSU，总供电 264kW
- **铜母线**：54V DC 垂直贯穿机架背板，满载 2500A+
- **废热**：97% 效率下仍有 ~3.6kW 转换废热（液冷排出）

### 功率路线图

| 机架型号 | 功耗 | 配电 | 上市 |
|----------|------|------|------|
| VR NVL72 | 120-130 kW | 54V DC | 2026 H2 |
| VR NVL144 | 190 kW | 800V→54V 混合 | 2026 H2 |
| NVL144 CPX | 370 kW | 800V HVDC | 2026-2027 |
| Rubin Ultra Kyber | 600 kW | 800V HVDC | 2027 H2 |

> **800V HVDC**：电流降低 15×，铜材减少，I²R 损耗降低 278×，端到端效率 >92%。

---

## 5. 存储体系

### 五级存储分层

| 层级 | 介质 | 容量 | 用途 |
|------|------|------|------|
| G1 | GPU HBM4 | 288 GB/卡, 22 TB/s | 热 KV Cache，当前推理窗口 |
| G2 | CPU LPDDR5X | 最高 1.5 TB/CPU | 温 KV Cache，预加载上下文 |
| G3 | 本地 NVMe SSD | 节点级 | 本地溢出，毫秒级延迟 |
| G3.5 | ICMS（BlueField-4） | 最高 16 TB/GPU | Pod 级共享 KV Cache |
| G4 | 网络存储 | PB 级 | 训练数据集、Checkpoint |

### ICMS：推理上下文内存存储

- 每个 Pod（1,152 GPU）包含专用 BF4 机架：16 机箱 × 4 BF4 = 64 颗
- 每颗 BF4 后端 150 TB NVMe，Pod 总容量 ~9,600 TB
- 通过 NIXL 传输库在存储层级间调度 KV 块
- 相比传统存储：推理 token/s 提升 5×，TCO 提升 5×

---

## 6. 网络互联

### Scale-Up：NVLink 6（机架内）

- 每 GPU 3.6 TB/s 双向，72 GPU 全互联 260 TB/s
- 交换托盘支持零停机维护
- 软件定义路由，链路故障自动绕行

### Scale-Out（跨机架，双模可选）

| 方案 | 协议 | 特色 | 适用场景 |
|------|------|------|----------|
| Spectrum-X | Ethernet (RoCE) | 102 TB/s 交换，CPO 硅光，支持 ICMS | 推理为主，Agentic AI |
| Quantum-X800 | InfiniBand | 集合通信硬件卸载 | 大规模分布式训练 |

每 GPU 均 1.6 Tb/s（2×800G），由 ConnectX-9 SuperNIC 提供。

---

## 7. Pod / 集群扩展

| 配置 | GPU 数 | 机架数 | FP4 算力 | HBM4 |
|------|--------|--------|----------|------|
| NVL72（单机架） | 72 | 1 | 3.6 EFLOPS | ~20.7 TB |
| Scalable Unit | 1,152 | 16+ | ~57.6 EFLOPS | ~331 TB |
| Rubin Ultra Kyber | 144 | 1 | 15 EFLOPS | — |
