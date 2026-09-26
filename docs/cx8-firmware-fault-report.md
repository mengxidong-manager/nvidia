# ConnectX-8 端口全数无法启用 故障报告

B300 NVL8 平台 16 个 CX8 端口因固件初始化异常停止响应

报告日期：2026-09-26

---

## 结论

ConnectX-8 固件 **40.48.1132** 在驱动加载的初始化末期报出内部错误 `ext_synd 0x035e`，约 8 秒后固件心跳停止响应，驱动判定设备健康状态失效。受影响范围为全部 **16 个 CX8 端口，复现率 100%**。

固件在网络设备注册完成前即已停止工作，因此端口无法进入可用状态，光模块激光器未被开启，对端交换机侧表现为完全无光输入。

同一台机器上的 ConnectX-7 使用相同的驱动、内核与 OFED，加载过程完全正常，可排除软件栈层面的共性问题。问题被隔离至 **CX8 固件本身**。

现场已无可自行处置的余地，建议冷启动验证一次后提交厂商。

## 环境

| 项 | 内容 |
|---|---|
| 整机型号 | Giga Computing G894-ZD3-AAX7-000 / MZB3-PE2-000 |
| 平台标识 | NVIDIA B300 NVL8 Umbriel System |
| BIOS | R05_F04（2026-04-22） |
| CPU | AMD EPYC 9555 64-Core |
| 操作系统 | Ubuntu 24.04，内核 6.8.0-136-generic |
| OFED | OFED-internal-26.04-0.8.6 |
| MFT | 4.36.0-147 |
| GPU | 8 × NVIDIA B300 SXM6，驱动 595.71.05，CUDA 13.2 |
| 故障网卡 | 8 × ConnectX-8（MT4131），共 16 个端口 |
| 对照网卡 | 1 × ConnectX-7 mezz（MT4129），共 4 个端口 |
| CX8 固件 | FW 40.48.1132 / PXE 3.9.0101 / UEFI 14.41.0014 |
| CX8 PSID | NVD0000000072（OEM 定制） |
| CX8 料号 | P6612_Ax，Description 为 NVIDIA B300 |
| 光模块 | RTXM600-2401，Power Class 8（>14 W，MAX 16 W） |
| 对端交换机 | H3C LS9867-128DH，400G 端口 |

## 故障现象

**交换机侧**　端口无法 UP。`display transceiver diagnosis` 显示本端 Tx 正常（各通道 0.50 ~ 0.73 dBm），四个通道 Rx 一致为 -36.96 dBm，低于低告警门限 -8.40 dBm 达 28 dB，判定为无光输入。

**服务器侧**　16 个 CX8 端口全部无法 UP。`mlxlink` 显示 State 为 Close port，Physical state 为 ETH_AN_FSM_ENABLE，Speed 与 FEC 均为 N/A。

**光模块**　8 个 lane 的 Tx Power 全部为 -40 dBm，即激光器未开启；同时 8 个 lane 的 Rx Power 为 0.398 ~ 2.028 dBm，正常收到交换机发来的光。

## 根因证据

驱动加载过程中，每个 CX8 端口的事件序列完全一致，以 `0000:73:00.0` 为例：

```
03:00:42  firmware version: 40.48.1132
03:00:43  Rate limit / E-Switch / Flow counters 初始化正常
03:00:44  MLX5E: StrdRq(1) RqSz(8) StrdSz(2048)
03:00:44  Health issue observed, firmware internal error, severity(3) ERROR
03:00:44  ext_synd 0x035e
03:00:52  poll_health: device's health compromised - reached miss count
03:01:09  enp115s0f0np0: renamed from eth0
```

固件在 netdev 注册**之前**即已停止响应。后续所有端口启用操作作用于一个已失效的固件，这解释了为何 `ip link set up` 与 `mlxlink --port_state UP` 均无效果。

| 项 | 实测 |
|---|---|
| 错误码 | `synd 0x1: firmware internal error`，`ext_synd 0x035e`，severity 3 (ERROR) |
| 复现率 | 16 / 16 端口，100%。dmesg 中共 32 条 ext_synd 记录，全部为 0x035e |
| 心跳停止 | `poll_health:1151: device's health compromised - reached miss count`，16 个端口各出现 1 次 |
| assert_var[0] | 0x00000003，所有端口完全一致；assert_var[1] 至 [5] 全为 0 |
| assert_exit_ptr | 0x00000000，表明并非代码崩溃，无出错地址 |
| assert_callra | 0x00000000，无调用返回地址，无调用栈 |
| rfr / crr | 0 / 0，固件未请求重置，也未处于恢复流程中 |
| hw_id | 0x0000021e（ConnectX-8），所有端口一致 |
| irisc_index | 分布于 0、2、3、5、7，不同卡的不同内部处理器均受影响 |

### 受影响端口清单

`time` 为固件记录该次异常时的内部时间戳。注意 `0000:e3:00.0` 与 `0000:e3:00.1` 的该值为 0，该卡固件计时从未启动。

| PCI 地址 | RDMA 设备 | 网口 | 首次报错 | irisc_index | fw time |
|---|---|---|---|---|---|
| 0000:03:00.0 | mlx5_2 | enp3s0f0np0 | 03:00:47 | 5 | 196 |
| 0000:03:00.1 | mlx5_3 | enp3s0f1np0 | 03:00:49 | 5 | 196 |
| 0000:13:00.0 | mlx5_6 | enp19s0f0np0 | 03:00:53 | 7 | 203 |
| 0000:13:00.1 | mlx5_7 | enp19s0f1np0 | 03:00:55 | 7 | 203 |
| 0000:63:00.0 | mlx5_4 | enp99s0f0np0 | 03:00:50 | 3 | 210 |
| 0000:63:00.1 | mlx5_5 | enp99s0f1np0 | 03:00:52 | 3 | 210 |
| 0000:73:00.0 | mlx5_0 | enp115s0f0np0 | 03:00:44 | 0 | 217 |
| 0000:73:00.1 | mlx5_1 | enp115s0f1np0 | 03:00:46 | 0 | 217 |
| 0000:83:00.0 | mlx5_14 | enp131s0f0np0 | 03:01:01 | 2 | 224 |
| 0000:83:00.1 | mlx5_15 | enp131s0f1np0 | 03:01:03 | 2 | 224 |
| 0000:93:00.0 | mlx5_18 | enp147s0f0np0 | 03:01:07 | 2 | 231 |
| 0000:93:00.1 | mlx5_19 | enp147s0f1np0 | 03:01:09 | 2 | 231 |
| 0000:e3:00.0 | mlx5_16 | enp227s0f0np0 | 03:01:04 | 7 | 0 |
| 0000:e3:00.1 | mlx5_17 | enp227s0f1np0 | 03:01:06 | 7 | 0 |
| 0000:f3:00.0 | mlx5_8 | enp243s0f0np0 | 03:00:57 | 5 | 245 |
| 0000:f3:00.1 | mlx5_9 | enp243s0f1np0 | 03:00:58 | 5 | 245 |

## 已排除的假设

以下方向均经实测排除，不再需要重复验证。

**光纤极性错误（Type-A / Type-B）**

服务器侧 8 个 lane 的 Rx Power 全部正常收光，实测 0.398 ~ 2.028 dBm，规格范围 [-8.928 .. 6.999]。极性接反会导致两端均收不到光，与实测矛盾。

**光模块故障**

Tx Fault、Tx LOS、Rx LOS、Tx CDR LOL、Rx CDR LOL 全部为 0；CDR RX / TX 八通道均为 ON；模块 EEPROM 可正常读取。激光器硬件无故障，属被主动关闭。

**光纤脏污或端面损伤**

交换机侧四个通道 Rx 一致归零（-36.96 dBm），而非单通道劣化。并行光的单纤问题会表现为通道间不均衡。

**端口未启用**

对全部 20 个网口执行 `ip link set up`，均返回成功；复查 mlxlink 仍为 Close port，Tx Power 仍为 -40 dBm。

**工作模式错误（InfiniBand / Ethernet）**

CX8 网口命名为 enp*，已处于以太网模式；同机 CX7 命名为 ibs*（IB 模式），命名规则可直接区分。

**PCIe 链路异常**

lspci 实测 20 个 CX8 端点均为 LnkCap 64GT/s x16、LnkSta 64GT/s x16，协商结果与能力一致，卡内交换机各下行口亦为 Gen6。dmesg 中 504 Gb/s 的提示源自卡上行口连接的 AMD 根端口为 Gen5，属集成交换机架构的正常表现，详见留意事项。

**GPU 或显存相关**

nvidia-smi 显示 8 颗 GPU 全部在位，Volatile Uncorr. ECC 均为 0，温度 32 ~ 41 °C、功耗 178 ~ 186 W 均正常，无运行进程。

**驱动 / 内核 / OFED 问题**

同机 ConnectX-7（0000:d9:00.0-3）使用同一 mlx5_core 驱动、同一内核、同一 OFED，加载过程完全正常，无任何 health 报错。这是最强的隔离证据。

**单卡硬件损坏**

8 块卡、16 个端口 100% 复现同一错误码，且 assert_var[0] 完全一致。多卡同时硬件故障且症状完全相同，概率极低。

## 已尝试的处置

| 动作 | 命令 | 结果 |
|---|---|---|
| 清除测试残留状态 | `mlxlink --test_mode DS / --loopback NO / --port_state UP` | 无效，State 保持 Close port，Tx Power 保持 -40 dBm |
| 操作系统侧启用端口 | `ip link set <iface> up` | 覆盖全部 20 个网口，命令均返回成功，但 State 与 Tx Power 无变化 |
| 固件级重置 | `mlxfwreset -d /dev/mst/mt4131_pciconf0 -l 3 reset` | 被拒绝执行。同一 PCIe switch 下挂载 GPU（0000:06:00.0），工具检测到 nvidia 驱动绑定后中止，属保护机制，未强制绕过 |

### PCIe 拓扑

ConnectX-8 集成 PCIe 交换机，网络端点与 GPU 同挂其下。这是 mlxfwreset 的 Secondary Bus Reset 会波及 GPU 的原因，也是 dmesg 中 504 Gb/s 带宽提示的来源。上表为第一块卡，其余七块结构相同。

```
AMD 根端口 00:01.1                        Gen5  32GT/s x16
  └─ 01:00.0  Mellanox PCIe 桥（卡上行口）   Gen5  32GT/s x16
       ├─ 02:00.0 ─ 03:00.0 / 03:00.1       Gen6  64GT/s x16   CX8 网络端点
       └─ 02:02.0 ─ … ─ 06:00.0             Gen6              NVIDIA GPU
```

## 建议动作

### 1. 冷启动验证

完全断电后重新上电（非 reboot），观察错误是否复现。这是唯一尚未尝试、且可能清除固件残留状态的手段，成本低、风险小。

起机后执行 `dmesg | grep -c ext_synd`。计数归零且端口 State 变为 Active 即为恢复；仍为 32 则确认为持续性问题。

### 2. 提交厂商

PSID NVD0000000072 为 OEM 定制标识，固件须从技嘉或 NVIDIA 获取对应版本，不可使用公版镜像。ext_synd 0x035e 的具体含义需 NVIDIA 内部错误码表解读，现场无法自行判定。

提交本报告及诊断包，材料清单见附录。

## 需要留意的事项

**固件升级需谨慎**　在厂商确认 0x035e 含义之前不建议自行升级固件。8 块卡表现完全一致，更像是固件与本平台的批次性适配问题；盲目升级可能引入新变量，并破坏现场证据。

**dmesg 中的 PCIe 带宽提示属正常现象**　日志中 `504.112 Gb/s available PCIe bandwidth, limited by 32.0 GT/s` 一句容易被误读为故障，实际是 ConnectX-8 集成 PCIe 交换机架构的正常表现。该卡的上行口连接 AMD EPYC 9555 根端口，受平台限制为 Gen5 32GT/s；而卡内交换机到网络端点、以及到 GPU 的链路均为 Gen6 64GT/s。GPUDirect RDMA 流量经卡内交换机直达 GPU 显存，不经过主机根端口，504 Gb/s 仅约束需落到 CPU 内存的流量。此项无需处置。

**诊断工具缺失**　本机 MFT 中缺少 flint 与 mstregdump，诊断包内对应文件为空。可安装开源 mstflint 包补齐（命令名带 mst 前缀），或从技嘉获取完整 MFT。核心版本信息已由 mlxfwmanager --query 覆盖，不影响报障。

## 附录：诊断包内容

文件名 `cx8-case-2026-09-26-0502.tar.gz`

| 文件 | 内容 |
|---|---|
| `dmesg-before-reboot.txt` | 完整内核日志，含 32 条 ext_synd 记录与 16 条 health compromised |
| `fwmanager.txt` | mlxfwmanager --query 输出，含 PSID、料号、各版本号 |
| `lspci.txt` | lspci -d 15b3: -vvv，含全部 PCIe 链路能力与实际协商结果 |
| `pcie-tree.txt` | lspci -tv，PCIe 拓扑，可见 GPU 与网卡的挂载关系 |
| `ofed.txt` | ofed_info -s 输出 |
| `flint-*.txt / dump-*.txt` | 因工具缺失为空，补齐 mstflint 后可重新采集 |

---

本报告依据 2026-09-26 03:00 启动周期的诊断数据整理。`ext_synd 0x035e` 的具体语义需由 NVIDIA 内部错误码表解读，本报告不作推测。
