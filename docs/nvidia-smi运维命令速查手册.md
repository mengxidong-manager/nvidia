# nvidia-smi GPU 运维命令速查手册

> 覆盖基础监控、健康检查、故障排查、性能调优、NVLink 诊断等 AIDC 日常运维场景。
>
> 撰写人：孟希東

---

## 1. 基础信息查看

```bash
nvidia-smi                          # GPU 概览
nvidia-smi -l 1                     # 每秒刷新
nvidia-smi dmon -s u -d 1           # dmon 精简模式
nvidia-smi --query-gpu=index,name,temperature.gpu,utilization.gpu,memory.used,memory.total,power.draw --format=csv,noheader,nounits
```

## 2. GPU 详细信息

```bash
nvidia-smi -q                       # 全量信息
nvidia-smi -i 0 -q                  # 只看 GPU 0
nvidia-smi --query-gpu=driver_version,cuda_version --format=csv
nvidia-smi --query-gpu=index,serial,uuid --format=csv
```

## 3. 显存与进程管理

```bash
nvidia-smi pmon -i 0 -s um -d 1     # 监控 GPU 0 进程
nvidia-smi --query-compute-apps=pid,process_name,gpu_uuid,used_memory --format=csv
kill -9 <PID>                        # 强制终止（慎用）
```

## 4. 健康检查

```bash
nvidia-smi --query-gpu=index,ecc.errors.corrected.volatile.total,ecc.errors.uncorrected.volatile.total --format=csv
nvidia-smi -q -d PERFORMANCE        # 降频状态
nvidia-smi --query-gpu=index,temperature.gpu,temperature.memory --format=csv
nvidia-smi -q -d PCIE               # PCIe 链路
nvidia-smi --query-retired-pages=gpu_uuid,address,cause --format=csv
nvidia-smi --query-remapped-rows=gpu_uuid,remapped_rows.correctable,remapped_rows.uncorrectable,remapped_rows.pending,remapped_rows.failure --format=csv
```

## 5. 功耗与性能

```bash
nvidia-smi --query-gpu=index,power.draw,power.limit --format=csv
sudo nvidia-smi -i 0 -pl 300        # 限功耗
sudo nvidia-smi -i 0 -lgc 1400,1400 # 锁频
sudo nvidia-smi -i 0 -rgc           # 解锁
sudo nvidia-smi -pm 1               # 持久模式
sudo nvidia-smi -i 0 -c EXCLUSIVE_PROCESS  # 独占模式
```

## 6. NVLink

```bash
nvidia-smi nvlink -s                # 状态
nvidia-smi nvlink -gt d             # 吞吐
nvidia-smi nvlink -e                # 错误计数
```

## 7. 拓扑

```bash
nvidia-smi topo -m                  # GPU 互联拓扑
```

## 8. 运维脚本

```bash
# 快速巡检
nvidia-smi --query-gpu=index,name,temperature.gpu,utilization.gpu,memory.used,memory.total,power.draw,ecc.errors.uncorrected.volatile.total --format=csv
# 持续监控写日志
nvidia-smi --query-gpu=timestamp,index,temperature.gpu,utilization.gpu,memory.used,power.draw --format=csv -l 5 >> /var/log/gpu_monitor.csv
# GPU 重置（慎用）
sudo nvidia-smi -i 0 -r
```

## 9. 速查表

| 场景 | 命令 | 说明 |
|------|------|------|
| 查看 GPU | `nvidia-smi` | 最常用 |
| 持续监控 | `-l 1` | 每秒刷新 |
| 查进程 | `pmon -s um` | 显存和利用率 |
| 查 ECC | `--query-gpu=ecc.errors.*` | 关键指标 |
| 查降频 | `-q -d PERFORMANCE` | 排查性能 |
| 查 NVLink | `nvlink -e` | 硬件问题 |
| 查拓扑 | `topo -m` | 互联方式 |
| 持久模式 | `-pm 1` | 生产推荐 |
| 限功耗 | `-pl <W>` | 需 root |
| 重置 | `-i <id> -r` | 慎用 |
