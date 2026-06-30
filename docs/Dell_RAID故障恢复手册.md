# Dell 服务器 RAID 故障恢复操作手册

> 覆盖 RAID 0/1/5/10 四种级别的故障识别、硬盘更换、阵列重建完整流程。以 Dell PowerEdge（PERC 控制器）为例。
>
> 撰写人：孟希东（测试）

---

## RAID 级别与容灾能力

| RAID | 原理 | 最少磁盘 | 可用容量 | 允许坏盘 | 坏盘后果 |
|------|------|----------|----------|----------|----------|
| RAID 0 | 条带化 | 2 | 100% | **0** | ❌ 全部数据丢失 |
| RAID 1 | 镜像 | 2 | 50% | **1** | ✅ 降级运行，自动重建 |
| RAID 5 | 条带+校验 | 3 | (N-1)/N | **1** | ✅ 降级运行，自动重建 |
| RAID 10 | 镜像+条带 | 4 | 50% | **每组1块** | ✅ 降级运行，自动重建 |

> ⚠️ **RAID ≠ 备份**。RAID 提供冗余和可用性，不能替代定期数据备份。

---

## 1. 故障发现与识别

### 物理指示灯
- 琥珀色闪烁 = 预警（Predictive Failure）
- 琥珀色常亮 = 故障（Failed）
- 绿色闪烁 = 正常读写

### iDRAC 检查
登录 iDRAC → Storage → Physical Disks → 查看 Status 列

### perccli 命令行
```bash
perccli /c0 show                   # 控制器和虚拟磁盘状态
perccli /c0/eall/sall show         # 所有物理磁盘状态
perccli /c0/v0 show                # 虚拟磁盘详情
```

> **状态说明**：Optimal = 正常，Degraded = 降级，Failed = 阵列失败，Rebuilding = 重建中

---

## 2. RAID 0 恢复

> ❌ **RAID 0 无冗余，任一盘故障 = 全部数据丢失，不可恢复**

1. 确认数据丢失（虚拟磁盘状态 Failed）
2. 如数据极重要且无备份 → **停止一切操作**，联系专业数据恢复公司
3. 更换故障硬盘（同规格）
4. 重建 RAID 0 阵列：
```bash
perccli /c0/v0 delete                        # 删除旧虚拟磁盘
perccli /c0 add vd r0 drives=32:0,32:1       # 创建新 RAID 0
```
5. 重装系统，从备份恢复数据

---

## 3. RAID 1 恢复（单盘故障）

1. 确认阵列 Degraded：`perccli /c0/v0 show`
2. 记录故障盘 Slot 号、序列号
3. **热插拔更换**（无需关机）：拔出故障盘 → 插入新盘 → 等待 10 秒
4. 确认自动重建：
```bash
perccli /c0/v0 show                          # State: Rebuilding
perccli /c0/eall/sall show rebuild           # 查看进度
```
5. 未自动重建则手动触发：
```bash
perccli /c0/e32/s1 set good
perccli /c0/e32/s1 start rebuild
```
6. 等待完成 → 确认 State: Optimal

---

## 4. RAID 5 恢复（单盘故障）

1. 确认阵列 Degraded
2. **立即降低 I/O 负载**（降级期间再坏一块 = 全部丢失）
3. 热插拔更换故障盘
4. 确认自动重建开始（PERC 用校验数据重算）
5. 监控进度（RAID 5 比 RAID 1 慢，大容量盘可能需要 10-40 小时）
```bash
perccli /c0/eall/sall show rebuild           # 每 30 分钟检查
```
6. 确认 Optimal

> ⚠️ **RAID 5 重建是最脆弱的时期**，所有磁盘负载极高。重建前务必确认备份可用，期间不要做大量 I/O。大容量（>4TB）建议使用 RAID 6 或 RAID 10。

---

## 5. RAID 10 恢复（单盘故障）

1. 确认 Degraded，确认故障盘所属镜像组（Span）
```bash
perccli /c0/v0 show all                      # 查看哪个 Span 受影响
```
2. 热插拔更换
3. 自动重建（RAID 10 只需复制镜像组的好盘数据，比 RAID 5 快很多）
4. 确认 Optimal

**不同 Span 各坏一块**：阵列仍可运行，依次更换即可。

**同一 Span 两块都坏**：❌ 该 Span 数据丢失 → 整个 RAID 10 失败 → 从备份恢复。

---

## 6. 通用硬盘更换流程（热插拔）

1. **准备**：新盘同型号同容量，≥ 故障盘
2. **定位**：`perccli /c0/e32/s2 start locate`（LED 闪烁）
3. **拔出**：按释放按钮 → 拉出托架
4. **安装**：新盘装入托架 → 推入槽位 → 听到咔嗒声
5. **等待**：10-30 秒，绿色闪烁 = 已识别
6. **确认重建**：`perccli /c0/eall/sall show rebuild`
7. **验证**：Optimal → 记录操作日志

### 重建时间参考

| 容量 | RAID 1 | RAID 5 | RAID 10 |
|------|--------|--------|---------|
| 500 GB | 1-2 h | 2-3 h | 1-2 h |
| 1 TB | 2-4 h | 4-6 h | 2-4 h |
| 4 TB | 6-10 h | 10-20 h | 6-10 h |
| 8 TB+ | 12-20 h | 20-40+ h | 12-20 h |

> SSD 重建时间通常为 HDD 的 1/5 到 1/10。

---

## 7. 最佳实践

### ✅ 应该做
- 更换前确认备份可用
- 使用同品牌同型号同容量替换盘
- 重建期间降低 I/O 负载
- 重建完成后执行一致性检查：`perccli /c0/v0 start cc`
- 配置 Hot Spare 热备盘：`perccli /c0/e32/s7 add hotsparedrive`
- 定期检查 SMART 数据

### ❌ 不应该做
- 重建期间重启服务器
- 同时拔出多块正常硬盘
- 使用容量小于故障盘的替换盘
- 忽略 Predictive Failure 预警
- 将 RAID 当作备份方案
