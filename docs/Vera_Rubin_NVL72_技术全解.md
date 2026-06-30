# NVIDIA Vera Rubin NVL72 技术全解

> 六芯协同设计、机架级统一计算、45°C 温水液冷、五级存储分层、双模 Scale-out 网络
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

每个 Superchip 将 1 颗 Vera CPU 与 2 颗 Rubin GPU 通过 NVLink-C2C 封装在一起。无线缆模块化设计，组装 5 分钟。第二代 RAS 引擎 + 第三代机密计算。

## 2. 六大芯片

Rubin GPU (3nm, 288GB HBM4, 22TB/s, 2300W) · Vera CPU (88核 Arm, 1.5TB LPDDR5X) · NVLink 6 (3.6TB/s/GPU, 260TB/s) · ConnectX-9 (1.6Tb/s) · BlueField-4 DPU · Spectrum-6 (102TB/s)

## 3. 散热系统

三环路：FWS(室外干冷器) → CDU(45°C供/65°C回, ΔT=20°C) → DLC(冷板直接液冷)。无需冷水机。

## 4. 供电

电网→54V DC(8×电源架, η97%) → 铜母线(2500A+) → VRM(−0.7V)。未来路线：800V HVDC。

## 5. 存储

五级分层：G1(HBM4) → G2(LPDDR5X) → G3(NVMe) → G3.5(ICMS, Pod级~9600TB) → G4(网络存储)

## 6. 网络

Scale-up: NVLink 6 (260TB/s) · Scale-out: Spectrum-X 或 Quantum-X800 (1.6Tb/s/GPU)

## 7. 扩展

NVL72(72GPU) → Scalable Unit(1152GPU) → Rubin Ultra Kyber(144GPU, 15 EFLOPS)

*完整版请参考仓库历史版本或 HTML 文档*
