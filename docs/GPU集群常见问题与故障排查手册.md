# GPU 集群常见问题与故障排查手册

> 覆盖硬件故障、XID 错误、ECC 内存、驱动异常、容器/K8s 调度、分布式训练、推理服务、散热供电等全场景
>
> 撰写人：孟希東

---

## 目录

- [1. 快速诊断流程](#1-快速诊断流程)
- [2. 硬件故障（XID 错误）](#2-硬件故障xid-错误)
- [3. 显存 ECC 错误](#3-显存-ecc-错误)
- [4. PCIe 与 NVLink 故障](#4-pcie-与-nvlink-故障)
- [5. 驱动与软件问题](#5-驱动与软件问题)
- [6. 容器与 K8s GPU 调度问题](#6-容器与-k8s-gpu-调度问题)
- [7. 分布式训练故障](#7-分布式训练故障)
- [8. 推理服务问题](#8-推理服务问题)
- [9. 散热与供电问题](#9-散热与供电问题)
- [10. 诊断工具速查](#10-诊断工具速查)
- [11. 预防性维护](#11-预防性维护)

---

## 1. 快速诊断流程

遇到 GPU 问题时，按此顺序排查：

```
1. dmesg | grep -i "nvrm\|xid\|nvidia"     ← 内核日志，查 XID 错误码
2. nvidia-smi                                ← GPU 是否可见、温度、利用率
3. nvidia-smi -q -d ECC                      ← ECC 错误计数
4. nvidia-smi -q -d PERFORMANCE              ← 是否降频
5. nvidia-smi nvlink -e                      ← NVLink 错误
6. dcgmi diag -r 3                           ← DCGM 深度诊断（12 分钟）
7. kubectl describe node / kubectl get pods  ← K8s 调度层面
```

---

## 2. 硬件故障（XID 错误）

### 什么是 XID？

XID 是 NVIDIA 驱动写入内核日志的错误报告，每个 XID 码对应一种特定的 GPU 故障类型。

```bash
# 查看 XID 错误
dmesg | grep -i "xid"
# 示例输出：NVRM: Xid (PCI:0000:5a:00): 79, GPU has fallen off the bus.
```

### 常见 XID 错误速查表

| XID | 含义 | 严重性 | 处理方法 |
|-----|------|--------|----------|
| **13** | GR 引擎异常 | ⚠️ 警告 | 通常是应用 bug（非法内存访问），检查 CUDA 代码。重启应用，复发则升级驱动 |
| **31** | GPU 内存页错误 | 🔴 严重 | 非法内存访问。检查应用代码。如非代码问题，可能是显存物理故障，跑 `dcgmi diag -r 3` |
| **43** | GPU 初始化失败 | 🔴 严重 | 重启驱动 `nvidia-smi -r`。复发则重装驱动。仍复发需 RMA |
| **45** | 预装系统测试失败 | 🔴 严重 | GPU 硬件故障，需要 RMA 更换 |
| **48** | 双比特 ECC 错误（DBE） | 🔴 严重 | 显存物理损坏。重启 GPU 触发 Row Remap。反复出现需更换 GPU |
| **61** | InfoROM 损坏 | ⚠️ 警告 | 固件损坏。`nvidia-smi -r` 重置。持续则需 RMA |
| **63** | 页退役/行重映射 | ℹ️ 信息 | 自动修复机制，ECC 坏块被隔离。单独出现可忽略，频繁出现说明显存退化 |
| **64** | 页退役失败 | 🔴 严重 | 坏块太多无法退役。GPU 需要更换 |
| **79** | GPU 从总线掉落 | 🔴 致命 | GPU 物理上与 PCIe 总线断开。检查物理连接、电源线、PCIe 插槽。重启服务器。复发需 RMA |
| **92** | 高 SBE 计数 | ⚠️ 警告 | 单比特错误率过高（ECC 可纠正但频率异常）。预示显存退化，计划更换 |
| **94** | 单比特 ECC 已纠正 | ℹ️ 信息 | **正常现象**。宇宙射线等导致，ECC 已自动纠正。每月几次可忽略 |
| **95** | 不可遏制的 ECC 错误 | 🔴 严重 | 错误扩散到其他进程。隔离 GPU，重启节点，跑诊断 |
| **119** | GSP 固件异常 | 🔴 严重 | GPU 系统处理器错误。重启节点，升级驱动到最新版 |

### XID 处理原则

- **信息级（94, 63）**：记录但不行动，关注频率趋势
- **警告级（13, 61, 92）**：调查原因，安排维护窗口处理
- **严重级（31, 48, 79, 95）**：立即隔离 GPU，迁移工作负载，启动更换流程

---

## 3. 显存 ECC 错误

### 问题分类

| 类型 | 说明 | 影响 | 处理 |
|------|------|------|------|
| **SBE（单比特）** | 单个比特翻转，ECC 可纠正 | 无影响 | 监控频率。少量正常 |
| **DBE（双比特）** | 两个比特翻转，ECC 不可纠正 | 数据损坏，进程崩溃 | 重启 GPU 触发 Row Remap |
| **Row Remap** | 自动将坏行映射到备用行 | 透明修复 | A100+ 支持。查看 Pending 状态 |
| **Page Retirement** | 旧 GPU 的坏页隔离机制 | 透明修复 | V100 等旧型号 |

### 诊断命令

```bash
# 查看 ECC 错误计数
nvidia-smi -q -d ECC

# 关键字段解读
# Volatile（驱动加载后计数）
#   SRAM Correctable: 0      ← SBE，少量正常
#   SRAM Uncorrectable: 0    ← DBE，>0 需关注
#   DRAM Correctable: 0      ← HBM SBE
#   DRAM Uncorrectable: 0    ← HBM DBE，>0 需立即处理
# Aggregate（GPU 生命周期计数）

# 查看 Row Remap 状态（A100+）
nvidia-smi -q -d REMAPPED_ROWS
# Pending: Yes → 需要重启 GPU 完成重映射
# Remapping Failure: Yes → GPU 需要更换

# 查看退役页（旧 GPU）
nvidia-smi --query-retired-pages=gpu_uuid,address,cause --format=csv
```

### 处理流程

```
发现 ECC 错误
  ├── SBE 且频率正常（<10/月） → 记录，继续监控
  ├── SBE 频率持续上升 → 计划维护窗口更换 GPU
  ├── DBE 出现
  │     ├── Row Remap Pending: Yes → 重启节点完成重映射
  │     ├── Remapping Failure: Yes → 立即更换 GPU
  │     └── 重映射后 DBE 复发 → 更换 GPU
  └── Retired Pages > 40 → GPU 寿命接近终点，计划更换
```

---

## 4. PCIe 与 NVLink 故障

### PCIe 问题

| 症状 | 可能原因 | 诊断 | 处理 |
|------|----------|------|------|
| GPU 不可见 | PCIe 线缆松动 / 接触不良 | `lspci \| grep -i nvidia` | 重新插拔 GPU，检查 PCIe 插槽 |
| 带宽降级 | 链路训练到低速 | `nvidia-smi -q -d PCIE` 查看链路速度和宽度 | BIOS 设置 PCIe Gen4/Gen5，重新插拔 |
| XID 79 | GPU 从总线掉落 | `dmesg \| grep xid` | 检查电源线、散热、PCIe 插槽。重启服务器 |
| 吞吐异常低 | IOMMU / ACS 配置 | `nvidia-smi topo -m` | BIOS 关闭 IOMMU（如不需要虚拟化）|

```bash
# 检查 PCIe 链路速度
nvidia-smi -q -d PCIE
# 期望：Link Speed: 16 GT/s (Gen4), Width: x16
# 异常：降级到 x8 或 Gen3 表示有问题

# PCIe 带宽测试
# 使用 CUDA samples
./bandwidthTest --device=0
```

### NVLink 问题

| 症状 | 诊断 | 处理 |
|------|------|------|
| 训练吞吐突然下降 | `nvidia-smi nvlink -e` 查看错误计数 | CRC 错误持续增长 → NVLink 线缆或 GPU 硬件问题 |
| NCCL AllReduce 超时 | `nvidia-smi nvlink -s` 查看链路状态 | Inactive 链路 → 检查 NVSwitch 和线缆 |
| 多卡通信带宽低 | `nvidia-smi nvlink -gt d` 查看吞吐 | 低于预期 → 检查 NVLink 拓扑配置 |

```bash
# NVLink 状态
nvidia-smi nvlink -s

# NVLink 错误计数（CRC 错误最关键）
nvidia-smi nvlink -e
# replay_errors / recovery_errors 持续增长 = 硬件问题

# NVLink 吞吐测试
# 使用 NCCL 测试
./all_reduce_perf -b 512M -e 8G -g 8
```

---

## 5. 驱动与软件问题

| 问题 | 症状 | 诊断 | 处理 |
|------|------|------|------|
| **驱动未加载** | `nvidia-smi` 报 "driver not loaded" | `lsmod \| grep nvidia`，`dmesg \| grep nvidia` | `sudo modprobe nvidia`。失败则重装驱动 |
| **驱动版本不兼容** | CUDA 程序报错 | `nvidia-smi` 查驱动版本，`nvcc --version` 查 CUDA 版本 | [兼容性矩阵](https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/) 对照，升级驱动 |
| **持久模式未开** | 首次 GPU 操作延迟高 | `nvidia-smi -q \| grep Persistence` | `sudo nvidia-smi -pm 1` |
| **Fabric Manager 未运行** | 多 GPU 系统 NVLink 不可用 | `systemctl status nvidia-fabricmanager` | `sudo systemctl enable --now nvidia-fabricmanager` |
| **GPU 重置后状态异常** | nvidia-smi 显示异常 | `nvidia-smi -r` | 重启节点。仍异常则检查硬件 |

---

## 6. 容器与 K8s GPU 调度问题

| 问题 | 症状 | 诊断 | 处理 |
|------|------|------|------|
| **节点无 nvidia.com/gpu** | `kubectl describe node` 看不到 GPU 资源 | 检查 GPU Operator Pod 状态 | Device Plugin Pod 是否 Running？驱动是否安装？ |
| **Pod 一直 Pending** | Insufficient nvidia.com/gpu | `kubectl describe pod` 看 Events | 集群 GPU 已用满。释放资源或扩容 |
| **Pod 内 nvidia-smi 失败** | "Failed to initialize NVML" | 检查 Container Toolkit | containerd 配置中 nvidia runtime 是否注册 |
| **GPU 分配后容器看不到** | `torch.cuda.device_count()` 返回 0 | 检查 Pod YAML resources.limits | 必须在 `limits` 中指定 `nvidia.com/gpu` |
| **GPU 类型不匹配** | Pod 被调度到错误的 GPU 节点 | `kubectl describe node` 看 GPU 标签 | 使用 `nodeSelector: nvidia.com/gpu.product` |

```bash
# K8s GPU 排查命令
kubectl get pods -n gpu-operator                          # GPU Operator 组件状态
kubectl logs -n gpu-operator -l app=nvidia-driver-daemonset  # 驱动安装日志
kubectl logs -n gpu-operator -l app=nvidia-device-plugin-daemonset  # Device Plugin 日志
kubectl describe node <gpu-node> | grep -A10 "Allocatable"  # GPU 资源是否注册
kubectl describe node <gpu-node> | grep -A10 "Allocated"    # GPU 已分配情况
```

---

## 7. 分布式训练故障

### NCCL 通信问题（最常见）

| 问题 | 症状 | 原因 | 处理 |
|------|------|------|------|
| **NCCL Timeout** | 训练挂起后报 Watchdog timeout | 某个 GPU 掉队，网络拥塞，某节点故障 | 开启 `NCCL_DEBUG=INFO` 定位哪个 rank 卡住 |
| **NCCL Init 失败** | 启动时报 unhandled system error | 网络不通，防火墙阻断 | 检查节点间网络，开放 NCCL 端口范围 |
| **AllReduce 极慢** | 训练吞吐远低于预期 | 跨机走以太网而非 IB | `NCCL_SOCKET_IFNAME` 指定正确网卡 |
| **Rank 不一致** | 部分节点报 rank mismatch | 环境变量错误 | 检查 MASTER_ADDR/PORT/WORLD_SIZE/RANK |

```bash
# 调试 NCCL
export NCCL_DEBUG=INFO
export NCCL_DEBUG_SUBSYS=ALL

# 定位问题 Rank
# 日志会显示每个 rank 的初始化、通信状态
# 如果某个 rank 没有 "Connected" 日志 → 该节点有问题

# NCCL 性能测试（排除应用因素）
./all_reduce_perf -b 512M -e 8G -g 8 -n 50
# 期望带宽：NVLink ~400GB/s, IB ~300Gbps, 以太网 ~10Gbps
```

### GPU OOM（显存溢出）

| 症状 | 原因 | 处理 |
|------|------|------|
| CUDA out of memory | batch size 太大 | 减小 batch size |
| OOM 在训练中途出现 | KV Cache / 激活值累积 | 开启 gradient checkpointing |
| 显存碎片化 | 长时间训练后碎片 | `torch.cuda.empty_cache()`，或设置 `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` |

```bash
# 实时监控显存
watch -n 1 'nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu --format=csv'
```

### 训练 Loss 异常

| 症状 | 可能原因 | 排查 |
|------|----------|------|
| Loss NaN / Inf | 梯度爆炸，或 ECC 错误导致数据损坏 | 先查 ECC，排除硬件后检查学习率、数据 |
| Loss 不下降 | 学习率、数据管道、权重初始化问题 | 非 GPU 硬件问题，检查训练代码 |
| 不同 GPU 训练结果不一致 | ECC 错误、GPU 降频 | 比较各 GPU 的 ECC 计数和时钟频率 |

### 训练挂起（Hang）

```bash
# 1. 检查 GPU 利用率
nvidia-smi
# 全部 0% 但进程存在 → 可能是 NCCL 死锁或某个 rank 卡住

# 2. 检查是否有 XID 错误
dmesg | grep -i xid

# 3. 检查 NCCL 日志（如已开启 DEBUG）
# 找到最后一条正常通信日志，定位卡住的 rank

# 4. py-spy 抓取 Python 堆栈（不中断进程）
pip install py-spy
py-spy dump --pid <PID>

# 5. 如果确认死锁，kill 后从 checkpoint 恢复
```

---

## 8. 推理服务问题

| 问题 | 症状 | 原因 | 处理 |
|------|------|------|------|
| **首次请求延迟高** | 第一个请求几十秒 | 模型冷加载到 GPU | 配置模型预加载/预热。开启持久模式 |
| **吞吐突然下降** | tokens/s 骤降 | GPU 降频（过热或功耗限制） | 检查温度和功耗。`nvidia-smi -q -d PERFORMANCE` |
| **KV Cache OOM** | 长上下文请求报 OOM | KV Cache 占满显存 | 减小 `max-model-len`，或增加 GPU 数量 |
| **推理结果不一致** | 相同输入不同输出 | ECC 错误导致权重损坏 | 检查 ECC，重新加载模型 |
| **vLLM 启动失败** | 模型加载报错 | 显存不足放不下模型 | 增加 `tensor-parallel-size`（更多卡），或降低 `gpu-memory-utilization` |

```bash
# vLLM 性能监控
curl http://localhost:8000/metrics | grep -E "vllm:(num_requests|avg_generation|gpu_cache)"

# 关键指标
# vllm:num_requests_running      ← 正在处理的请求数
# vllm:avg_generation_throughput  ← 平均生成吞吐
# vllm:gpu_cache_usage_perc       ← KV Cache 使用率（>90% 需关注）
```

---

## 9. 散热与供电问题

### 温度问题

| 状态 | 温度范围 | 影响 | 处理 |
|------|----------|------|------|
| 正常 | < 75°C | 无 | — |
| 警告 | 75-83°C | 可能开始降频 | 检查散热系统 |
| 降频 | 83-90°C | SW Thermal Slowdown 触发 | 立即检查液冷/风扇 |
| 危险 | > 90°C | HW Thermal Slowdown，严重降频 | 停止工作负载，排查散热故障 |
| 关机 | > 100°C | GPU 自动关机保护 | 立即断电排查 |

```bash
# 查看温度和降频状态
nvidia-smi -q -d TEMPERATURE,PERFORMANCE

# 关键字段
# GPU Current Temp:          72 C
# GPU T.Limit Temp:          83 C
# SW Thermal Slowdown:       Not Active   ← Active = 降频中！
# HW Thermal Slowdown:       Not Active   ← Active = 严重降频！
```

### 液冷故障

| 症状 | 可能原因 | 处理 |
|------|----------|------|
| 温度异常升高 | CDU 泵故障 / 冷却液流量不足 | 检查 CDU 运行状态和流量 |
| 温度不均匀 | 管路气锁（Air Lock） | 排气操作 |
| 泄漏告警 | 快接头 / 管路接头漏液 | 立即关闭阀门，断电，清理 |
| 水质异常 | 冷却液降解 / 污染 | 检测 pH 和电导率，更换冷却液 |

### 供电问题

| 症状 | 可能原因 | 处理 |
|------|----------|------|
| XID 79（GPU 掉总线） | 供电不稳导致 PCIe 瞬断 | 检查 PSU 模块和母线 |
| GPU 功耗被限制 | Power Limit 设置太低 | `nvidia-smi -q -d POWER` 查看 |
| XID 54 | 电源线未插好 | 检查 GPU 辅助供电线缆 |

---

## 10. 诊断工具速查

| 工具 | 命令 | 用途 |
|------|------|------|
| nvidia-smi | `nvidia-smi` | 基础 GPU 状态一览 |
| nvidia-smi 详查 | `nvidia-smi -q` | 全量硬件信息 |
| ECC 检查 | `nvidia-smi -q -d ECC` | 内存错误计数 |
| 降频检查 | `nvidia-smi -q -d PERFORMANCE` | 时钟限制原因 |
| PCIe 检查 | `nvidia-smi -q -d PCIE` | 链路速度和宽度 |
| NVLink 错误 | `nvidia-smi nvlink -e` | NVLink CRC 错误 |
| NVLink 吞吐 | `nvidia-smi nvlink -gt d` | NVLink 带宽 |
| 拓扑 | `nvidia-smi topo -m` | GPU 互联关系 |
| Row Remap | `nvidia-smi -q -d REMAPPED_ROWS` | 显存行重映射状态 |
| GPU 重置 | `sudo nvidia-smi -i <id> -r` | 重置 GPU（慎用） |
| **DCGM 快速诊断** | `dcgmi diag -r 1` | 快速检查（< 1分钟） |
| **DCGM 中度诊断** | `dcgmi diag -r 2` | 中度检查（~2分钟） |
| **DCGM 深度诊断** | `dcgmi diag -r 3` | 深度检查（~12分钟，含压力测试） |
| DCGM 健康监控 | `dcgmi health -s a` | 设置全项监控 |
| 内核日志 | `dmesg \| grep -i "xid\|nvrm\|nvidia"` | XID 错误和驱动消息 |
| NCCL 调试 | `NCCL_DEBUG=INFO` | 分布式训练通信诊断 |

### 一键巡检脚本

```bash
#!/bin/bash
echo "=== GPU 概览 ==="
nvidia-smi

echo -e "\n=== ECC 错误 ==="
nvidia-smi --query-gpu=index,ecc.errors.corrected.volatile.total,ecc.errors.uncorrected.volatile.total --format=csv

echo -e "\n=== 降频状态 ==="
nvidia-smi --query-gpu=index,clocks_event_reasons.active --format=csv

echo -e "\n=== Row Remap ==="
nvidia-smi -q -d REMAPPED_ROWS 2>/dev/null || echo "此 GPU 不支持 Row Remap"

echo -e "\n=== NVLink 错误 ==="
nvidia-smi nvlink -e 2>/dev/null || echo "无 NVLink"

echo -e "\n=== XID 错误（最近 24h）==="
journalctl --since "24 hours ago" -k | grep -i xid || echo "无 XID 错误"

echo -e "\n=== PCIe 链路 ==="
nvidia-smi --query-gpu=index,pcie.link.gen.current,pcie.link.width.current --format=csv
```

---

## 11. 预防性维护

### 日常巡检（每日）

- [ ] nvidia-smi 确认所有 GPU 可见且温度正常
- [ ] ECC 错误计数无异常增长
- [ ] 无 XID 错误（`dmesg` 或 Prometheus 告警）
- [ ] GPU 利用率与业务负载匹配

### 周期维护（每月）

- [ ] 跑 `dcgmi diag -r 3` 深度诊断
- [ ] 检查 NVLink 错误计数趋势
- [ ] 检查 Row Remap / Page Retirement 计数
- [ ] 液冷系统水质检测
- [ ] 驱动版本是否有安全更新

### 告警阈值建议

| 指标 | 阈值 | 动作 |
|------|------|------|
| GPU 温度 | > 83°C 持续 5 分钟 | 告警，检查散热 |
| ECC Uncorrectable（DBE） | > 0 | 立即告警，隔离 GPU |
| ECC Correctable（SBE）增长率 | > 100/天 | 告警，计划更换 |
| Row Remap Pending | Yes | 告警，安排重启 |
| Row Remap Failure | Yes | 立即告警，更换 GPU |
| NVLink CRC 错误增长 | 持续增长 | 告警，检查线缆/硬件 |
| GPU 利用率 | 0% 持续 30 分钟（有任务时） | 告警，可能挂起 |
| 功耗 | 超过 Power Limit | 告警，检查供电 |
