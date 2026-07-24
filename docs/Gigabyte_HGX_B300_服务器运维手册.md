# Gigabyte HGX B300 (G894 系列) 服务器运维手册

> 基于 Gigabyte G894-SD3/ZD3-AAX7（NVIDIA HGX B300 8-GPU 参考架构）实机盘点整理，覆盖硬件识别、BMC 管理、供电、网络布线标签体系、故障排查全流程
>
> 撰写人：孟希東

---

## 一、硬件规格总览

| 项目 | 规格 |
|------|------|
| 型号 | Gigabyte G894-SD3-AAX7（Intel 版）/ G894-ZD3-AAX7（AMD 版） |
| 尺寸 | 8U 机架式，风冷 |
| GPU | NVIDIA HGX B300，8 × Blackwell Ultra SXM GPU |
| GPU 互联 | NVLink + NVLink Switch，1.8 TB/s GPU-GPU 带宽，总带宽 14.4 TB/s |
| CPU | 双路 Intel Xeon 6700/6500 系列 或 AMD EPYC 9005/9004 系列 |
| 内存 | 8/12 通道 DDR5 RDIMM，最多 24-32 根 DIMM |
| GPU 网络 | 8 × 800 Gb/s OSFP 端口，支持 InfiniBand XDR 或双 400Gb/s Ethernet（板载 ConnectX-8 SuperNIC） |
| 管理网络 | 2 × 10Gb/s LAN（Intel X710-AT2）+ 1 × MLAN 管理口 |
| 存储 | 8 × 2.5" Gen5 NVMe 热插拔盘位 |
| PCIe 扩展 | 4 × FHHL PCIe Gen5 x16 |
| 电源 | 12 × 3000W 80 PLUS 钛金认证冗余电源（Delta） |
| DPU 兼容 | 支持 NVIDIA BlueField-3 DPU |
| 定位 | Neocloud / 云服务商 AI 训练与推理旗舰平台 |

---

## 二、前面板 I/O 详解

对照实机拍摄照片核对如下：

### 前置 I/O 板（I/O board）

| 接口 | 数量 | 说明 |
|------|------|------|
| USB 3.2 Gen1 (Type-A) | 2 | 本地应急接键盘/U盘 |
| VGA | 1 | 本地调试视频输出 |
| RJ45 | 2 | 数据 LAN 口（Intel X710-AT2） |
| MLAN（管理口） | 1 | 默认 BMC 管理网口，实机照片中蓝色网线插入的即此接口 |
| Power 按钮（带 LED） | 1 | 开关机 |
| ID 按钮（带 LED） | 1 | 机箱定位灯，远程运维辅助现场物理定位 |
| NMI 按钮 | 1 | 不可屏蔽中断，用于触发内核 crash dump |
| Reset 按钮 | 1 | 硬件复位 |
| Storage 活动 LED | 1 | 存储读写状态指示 |
| System 状态 LED | 1 | 系统健康状态指示 |

> 注：当前后两个 MLAN 口都插了网线时，前置 MLAN 口默认生效为管理口。

### 后置 I/O

| 接口 | 数量 | 说明 |
|------|------|------|
| OSFP 端口 | 8 | GPU 网络端口，对应 8 颗 GPU 的 ConnectX-8 SuperNIC，支持 IB XDR 或双 400G Ethernet |
| MLAN | 1 | 后置管理口（板载 MLAN board） |

### 存储

- 8 × 2.5" Gen5 NVMe 热插拔盘位（前面板照片中可见 0-3 号盘位，另 4 个在机箱另一侧）
- 绿色拉手为热插拔盘位标准设计，插拔时需按压释放锁扣

---

## 三、BMC 带外管理

### 3.1 唯一密码标签

Gigabyte 出厂时为每台设备的 BMC 生成**唯一密码**（非统一默认密码），以物理标签形式贴在机箱抽拉标签条上，包含：

- 序列号条码（如 `GQK4R7412A0006`）
- BMC 密码条码（如 `QG2P8000013`）

🔴 **安全要求**：
1. 首次登录 BMC 后**立即修改默认密码**
2. 将原始密码录入企业密码管理系统（Vault/CyberArk 等），不要长期依赖物理标签作为唯一凭证来源
3. 标签照片属于敏感信息，不得外发或公开发布
4. 批量上架时建议统一通过自动化脚本（Redfish API）批量修改初始密码，而非逐台手动操作

### 3.2 BMC 访问方式

```bash
# Web UI 访问
https://<BMC_IP>/

# ipmitool 命令行访问
ipmitool -I lanplus -H <BMC_IP> -U admin -P <密码> chassis status

# 查看 FRU 信息（核实具体型号/序列号）
ipmitool -I lanplus -H <BMC_IP> -U admin -P <密码> fru print

# 查看传感器数据（温度/风扇转速/电压）
ipmitool -I lanplus -H <BMC_IP> -U admin -P <密码> sdr list

# 远程电源控制
ipmitool -I lanplus -H <BMC_IP> -U admin -P <密码> chassis power status
ipmitool -I lanplus -H <BMC_IP> -U admin -P <密码> chassis power cycle
ipmitool -I lanplus -H <BMC_IP> -U admin -P <密码> chassis power on
ipmitool -I lanplus -H <BMC_IP> -U admin -P <密码> chassis power off

# 远程点亮 ID 定位灯（30 秒后自动熄灭）
ipmitool -I lanplus -H <BMC_IP> -U admin -P <密码> chassis identify 30
```

### 3.3 Redfish API 批量管理（推荐用于规模化运维）

```bash
# 获取系统信息
curl -k -u admin:<密码> https://<BMC_IP>/redfish/v1/Systems/1

# 获取健康状态
curl -k -u admin:<密码> https://<BMC_IP>/redfish/v1/Systems/1 | jq '.Status'

# 批量修改初始密码（示例，需按 Gigabyte Redfish Schema 调整）
curl -k -u admin:<旧密码> -X PATCH \
  https://<BMC_IP>/redfish/v1/AccountService/Accounts/2 \
  -H "Content-Type: application/json" \
  -d '{"Password": "<新密码>"}'
```

---

## 四、供电系统

### 4.1 PSU 规格

12 × 3000W 80 PLUS 钛金认证冗余电源（Delta 制造），支持多种输入：

| 输入类型 | 规格 |
|----------|------|
| AC 115-127V | 14.2A，50-60Hz |
| AC 200-220V | 15.8A，50-60Hz |
| AC 220-240V | 14.9A，50-60Hz |
| DC 240V（仅中国区） | 14A |

对应之前梳理的**数据中心 240V HVDC 直流供电架构**——这台服务器原生支持 240V DC 输入，可直接对接国内主流 HVDC 供电体系，无需 UPS 交流逆变环节。

### 4.2 冗余供电标签体系

实机布线中可见白色标签标注电源来源，格式为：

```
B300-K23-15U-PDUA    ← 机型-机柜号-U位-PDU路（A路）
B300-K23-15U-PDUB    ← 机型-机柜号-U位-PDU路（B路）
K23-PDUB-5           ← 机柜号-PDU路-序号
```

这对应我们之前梳理的**双路市电/2N 冗余供电架构**——PDU-A 和 PDU-B 分别接入两路独立的市电/UPS/HVDC 输入，任一路故障不影响服务器运行。

### 4.3 PSU 热插拔更换流程

```
1. 通过 BMC sdr list 或 PSU 面板 LED 确认故障 PSU（红色/琥珀色 = 故障，绿色常亮 = 正常）
2. 确认冗余：核实另一路 PDU 输入正常，且总负载不超过单路供电上限
3. 拔出故障 PSU 的电源线（先拔电源线，非直接抽模块）
4. 按压 PSU 释放卡扣，抽出故障模块
5. 插入新 PSU 模块，确认卡扣锁定到位
6. 插入电源线，确认防脱落卡扣锁定
7. 确认新 PSU LED 变绿，BMC sdr list 状态恢复 Optimal
8. 记录更换日志：PSU 序列号、更换时间、故障现象、处理人
```

> ⚠️ 12 电源位设计通常为 N+N 或更高冗余，允许多个 PSU 故障仍能维持运行，但生产环境应在发现故障后**尽快更换**，避免冗余度被持续消耗。

---

## 五、GPU 网络与布线标签体系

### 5.1 网络架构

每台 G894 服务器 8 颗 B300 GPU 各自搭配一张 ConnectX-8 SuperNIC，共 8 个 800Gb/s OSFP 端口，支持：

- **InfiniBand XDR**：传统 HPC/AI 训练首选，硬件级集合通信加速
- **双 400Gb/s Ethernet（RoCE）**：NVIDIA Spectrum-X 方案，适合推理为主或运维熟悉以太网的场景

实机布线证实采用 **RoCE 多路径组网**（Fat-Tree/Clos 拓扑），每张网卡分别上联到不同的 leaf 交换机，任一 leaf 交换机或链路故障不会导致整机断网，只是降低部分带宽。

### 5.2 布线标签体系解读

现场标签体系包含机房、机柜、U 位、交换机、端口的完整信息链：

| 标签类型 | 格式示例 | 字段拆解 |
|----------|----------|----------|
| 存储网络标签 | `C-394 // s110-k23-u15-ST-2` | C-394=配线柜端口 / s110=机房编号 / k23=机柜号 / u15=U位 / ST-2=存储端口2 |
| RoCE 网络标签 | `osadrt-s110-i2u18-roce-leaf-31-55` | osadrt=集群前缀 / s110=机房 / i2u18=交换机机柜i2的U18位 / roce-leaf-31=第31号leaf交换机 / 55=端口/链路号 |
| 电源标签 | `B300-K23-15U-PDUB` | B300=机型 / K23=机柜号 / 15U=U位 / PDUB=B路供电 |

### 5.3 布线维护规范

```
□ 任何网线/光纤更换后，必须同步更新标签内容并拍照存档
□ 标签脱落或字迹模糊时，24 小时内补贴，避免影响故障定位效率
□ 光纤护线夹（cable boot）确保固定牢靠，防止意外拉扯导致光纤断裂
□ 新增/变更布线时，标签命名严格遵循现有命名规范，避免出现命名体系混乱
□ 定期（建议每季度）核对标签记录与实际布线的一致性，发现不符及时更正
```

> 📌 **标签体系是大规模 GPU 集群运维的生命线**。没有清晰规范的标签，一旦发生网络故障，运维人员几乎无法在合理时间内定位到具体物理端口，这在数百上千节点规模的集群中是致命的效率瓶颈。

---

## 六、日常巡检清单

```
□ 前面板风扇墙：检查所有风扇模块蓝色卡扣螺丝无松动，运转无异响
□ NVMe 盘位（8个）：确认指示灯为绿色常亮（正常）或绿色闪烁（读写中）
□ PSU 模块（12个）：确认所有 LED 常亮绿色，无红色/琥珀色故障灯
□ BMC 管理网口：确认链路灯常亮，BMC Web UI 可正常访问
□ OSFP 网络端口（8个）：检查光模块指示灯状态，光纤护线夹无脱落
□ 布线标签：检查标签清晰可读，与实际记录一致
□ System 状态 LED：确认为正常颜色（通常绿色）
□ 温度/风扇转速：通过 BMC sdr list 检查无异常告警
```

---

## 七、故障排查速查表

| 现象 | 可能原因 | 排查步骤 |
|------|----------|----------|
| BMC 无法访问 | 网线松动 / BMC 固件挂起 | 检查 MLAN 口链路灯 → 重插网线 → 现场用 `ID` 灯确认物理机器 → 必要时通过前面板 `RST` 复位 |
| PSU 故障灯亮 | PSU 硬件故障 / 输入侧断电 | 确认对应 PDU-A/B 路是否有输入 → 确认冗余侧承载正常 → 按流程热插拔更换 PSU |
| 某 GPU 网络端口离线 | 光模块故障 / 光纤污染 / 对端交换机故障 | 对照标签定位 leaf 交换机编号 → 检查光模块收发光功率 → 清洁或更换光纤/光模块 |
| NVMe 盘位掉线 | 硬盘故障 / 托架接触不良 | 通过 BMC 确认故障盘位 → 热插拔更换（参考 Dell_RAID故障恢复手册.md 通用流程） |
| GPU 报 XID 错误 | GPU 硬件/驱动异常 | 参考《GPU集群常见问题与故障排查手册.md》XID 错误码速查表处理 |
| 系统无响应/死锁 | OS 内核挂起 | 触发前面板 `NMI` 生成 crash dump → 分析后 `RST` 复位 |
| 风扇异响 | 轴承磨损 / 异物卡滞 | 通过 BMC sdr 数据检查转速异常，计划性更换风扇模块 |
| GPU 间通信异常/训练吞吐骤降 | NVLink 链路故障 | `nvidia-smi nvlink -e` 检查错误计数，参考 GPU 故障排查手册 NVLink 章节 |

---

## 八、与既有文档的关联

| 场景 | 参考文档 |
|------|----------|
| GPU 硬件层面故障（XID/ECC/NVLink） | [GPU集群常见问题与故障排查手册.md](GPU集群常见问题与故障排查手册.md) |
| B300 芯片规格与架构原理 | [B300_GB300_NVL72_技术全解.md](B300_GB300_NVL72_技术全解.md) |
| 硬盘 RAID 故障恢复 | [Dell_RAID故障恢复手册.md](Dell_RAID故障恢复手册.md) |
| 数据中心供电架构（240V HVDC/双路市电） | [数据中心供电架构详解.md](数据中心供电架构详解.md) |
| GPU 在 K8s 中的调度与训练/推理部署 | kubernetes 仓库 [K8s_GPU训练与推理全栈架构指南.md](https://github.com/mengxidong-manager/kubernetes/blob/main/docs/K8s_GPU训练与推理全栈架构指南.md) |
