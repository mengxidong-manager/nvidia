# nvidia-smi GPU 运维命令速查手册

> 覆盖基础监控、健康检查、故障排查、性能调优、NVLink 诊断等 AIDC 日常运维场景。
>
> 撰写人：孟希东（测试）

---

## 目录

- [基础信息查看](#1-基础信息查看)
- [GPU 详细信息](#2-gpu-详细信息)
- [显存与进程管理](#3-显存与进程管理)
- [健康检查与故障排查](#4-健康检查与故障排查)
- [功耗与性能管理](#5-功耗与性能管理)
- [NVLink 监控](#6-nvlink-监控)
- [拓扑与互联](#7-拓扑与互联)
- [常用运维脚本](#8-常用运维脚本)
- [速查表](#9-速查表)

---

## 1. 基础信息查看

### 查看 GPU 概览（最常用）

```bash
nvidia-smi
```

### 持续监控

```bash
nvidia-smi -l 1                    # 每 1 秒刷新
nvidia-smi dmon -s u -d 1          # dmon 精简模式
```

### 自定义查询字段，输出 CSV

```bash
nvidia-smi --query-gpu=index,name,temperature.gpu,utilization.gpu,utilization.memory,memory.used,memory.total,power.draw --format=csv,noheader,nounits
```

## 2. GPU 详细信息

```bash
nvidia-smi -q                      # 全量硬件信息
nvidia-smi -i 0 -q                 # 只看 GPU 0
nvidia-smi --query-gpu=driver_version,cuda_version --format=csv   # 驱动和 CUDA 版本
nvidia-smi --query-gpu=index,serial,uuid --format=csv             # 序列号和 UUID
```

## 3. 显存与进程管理

```bash
nvidia-smi pmon -i 0 -s um -d 1    # 实时监控 GPU 0 上的进程
nvidia-smi --query-compute-apps=pid,process_name,gpu_uuid,used_memory --format=csv  # 所有计算进程
```

### 强制终止占用 GPU 的进程

```bash
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv  # 先找 PID
kill -9 <PID>                       # 再终止（慎用，可能丢失 checkpoint）
```

## 4. 健康检查与故障排查

### ECC 错误（关键运维指标）

```bash
nvidia-smi --query-gpu=index,ecc.errors.corrected.volatile.total,ecc.errors.uncorrected.volatile.total --format=csv
```

> **corrected**：已纠正的错误，持续增长需关注。**uncorrected**：未纠正的错误，需立即排查。

### GPU 降频 / 退化状态

```bash
nvidia-smi -q -d PERFORMANCE       # SW Thermal Slowdown: Active = 过热降频
nvidia-smi --query-gpu=index,clocks_event_reasons.active --format=csv  # 时钟限制原因
```

### 温度与 PCIe

```bash
nvidia-smi --query-gpu=index,temperature.gpu,temperature.memory --format=csv
nvidia-smi -q -d PCIE              # PCIe 链路状态（排查带宽降级）
```

### 显存健康

```bash
nvidia-smi --query-retired-pages=gpu_uuid,address,cause --format=csv  # 退役页（坏块过多需换卡）
nvidia-smi --query-remapped-rows=gpu_uuid,remapped_rows.correctable,remapped_rows.uncorrectable,remapped_rows.pending,remapped_rows.failure --format=csv
```

## 5. 功耗与性能管理

### 查看 / 设置功耗

```bash
nvidia-smi --query-gpu=index,power.draw,power.limit,enforced.power.limit --format=csv
sudo nvidia-smi -i 0 -pl 300       # 限制 GPU 0 功耗为 300W（需 root）
```

### 锁定 / 解锁时钟频率

```bash
nvidia-smi -i 0 -q -d SUPPORTED_CLOCKS   # 查看支持的时钟
sudo nvidia-smi -i 0 -lgc 1400,1400      # 锁定 GPU 频率
sudo nvidia-smi -i 0 -lmc 1593           # 锁定显存频率
sudo nvidia-smi -i 0 -rgc                # 解锁 GPU 频率
sudo nvidia-smi -i 0 -rmc                # 解锁显存频率
```

### GPU 工作模式

```bash
sudo nvidia-smi -pm 1               # 开启持久模式（推荐生产环境）
sudo nvidia-smi -i 0 -c EXCLUSIVE_PROCESS  # 独占模式（每 GPU 仅允许一个进程）
sudo nvidia-smi -i 0 -c DEFAULT     # 恢复默认
```

## 6. NVLink 监控

```bash
nvidia-smi nvlink -s                # NVLink 状态
nvidia-smi nvlink -gt d             # NVLink 吞吐
nvidia-smi nvlink -e                # NVLink 错误计数（CRC 错误持续增长 = 硬件问题）
```

## 7. 拓扑与互联

```bash
nvidia-smi topo -m                  # GPU 互联拓扑
```

> **输出说明**：NV# = NVLink 直连，PHB = PCIe 同 Host Bridge，SYS = 跨 NUMA 节点。训练时应将通信密集的任务分配在 NVLink 直连的 GPU 上。

## 8. 常用运维脚本

### 快速健康巡检

```bash
nvidia-smi --query-gpu=index,name,temperature.gpu,utilization.gpu,memory.used,memory.total,power.draw,ecc.errors.uncorrected.volatile.total,clocks_event_reasons.active --format=csv
```

### 持续监控写日志

```bash
nvidia-smi --query-gpu=timestamp,index,temperature.gpu,utilization.gpu,memory.used,power.draw --format=csv -l 5 >> /var/log/gpu_monitor.csv
```

### GPU 重置（故障恢复，慎用）

```bash
sudo nvidia-smi -i 0 -r
```

> ⚠️ 此操作会强制重置 GPU 硬件，该 GPU 上的所有进程将被立即终止。仅在 GPU 完全无响应时使用。

## 9. 速查表

| 场景 | 命令 | 说明 |
|------|------|------|
| 快速查看所有 GPU | `nvidia-smi` | 最常用 |
| 持续监控 | `nvidia-smi -l 1` | 每秒刷新 |
| 查进程 | `nvidia-smi pmon -s um` | 按进程显示显存和利用率 |
| 查 ECC 错误 | `--query-gpu=ecc.errors.*` | 关键健康指标 |
| 查降频原因 | `-q -d PERFORMANCE` | 排查性能下降 |
| 查 NVLink 错误 | `nvlink -e` | 排查互联硬件问题 |
| 查拓扑 | `topo -m` | GPU 互联方式 |
| 设持久模式 | `-pm 1` | 生产环境推荐 |
| 限功耗 | `-pl <watts>` | 需 root |
| 锁频 | `-lgc <freq>` | 保持性能稳定 |
| 重置 GPU | `-i <id> -r` | 最后手段，慎用 |
