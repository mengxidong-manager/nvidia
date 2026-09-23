# ConnectX / InfiniBand 网络诊断命令手册

面向 CX8 端口告警与链路故障的现场排查参考

> 设备标识统一使用 `/dev/mst/mt4131_pciconf0`，请先用 `mst status -v` 确认实际编号后替换。

## 排查顺序

### 1. 确认设备存在与 PCIe 协商

```bash
mst status -v
lspci -d 15b3: -vvv | grep -E "LnkCap|LnkSta"
ibdev2netdev -v
```

先拿到真实设备名与网口映射。LnkCap 与 LnkSta 不一致说明 PCIe 没协商到应有的速率或宽度，可能是插槽接触问题。

### 2. 查物理层状态与 down reason

```bash
cat /sys/class/infiniband/mlx5_0/ports/1/phys_state
mlxlink -d /dev/mst/mt4131_pciconf0 -p 1 -m -e -c
mlxreg -d /dev/mst/mt4131_pciconf0 --reg_name PDDR --get --indexes "local_port=1,page_select=1"
```

phys_state 直接区分“插接问题”和“配置问题”。PDDR 寄存器会给出链路失败的具体原因编码。

### 3. 交叉验证光模块

```bash
ethtool -m <iface>
```

ethtool 走内核驱动路径，mlxlink 走 MFT 路径。一个能读一个不能，指向 I2C 通路问题；两个都读不出，优先怀疑模块未插到位或已损坏。

### 4. 核对固件与驱动版本

```bash
flint -d /dev/mst/mt4131_pciconf0 query
ofed_info -s
```

固件与 OFED 版本不匹配是隐蔽且常见的故障原因。flint query 输出里的 PSID 是板卡唯一型号标识。

### 5. 对齐时间线

```bash
dmesg -T | grep -i -E "mlx5|i2c|osfp|module|link"
```

把内核报错时间和应用日志里的失败时间对上，基本就能锁定因果关系。

## MFT 工具

NVIDIA Firmware Tools 套件。绝大部分命令需要 root 权限，且必须先执行 mst start。

### 设备发现

| 命令 | 说明 |
|---|---|
| `mst start` | 加载 MST 内核模块，在 /dev/mst/ 下创建设备节点。所有 MFT 命令的前提。 |
| `mst status -v` | 列出识别到的设备。-v 额外显示 PCI 地址、网口名、RDMA 设备名的对应关系。 |
| `mst cable add` | 额外扫描线缆和光模块，生成 *_cable_* 节点，之后才能使用 mlxcables。 |
| `mst stop` | 卸载驱动。设备被占用时会失败。 |

### 链路与模块诊断

| 命令 | 说明 |
|---|---|
| `mlxlink -d /dev/mst/mt4131_pciconf0 -p 1` | 端口 1 的链路概览：状态、协商速率、FEC 模式、链路 down 原因。 |
| `mlxlink -d /dev/mst/mt4131_pciconf0 -m` | 光模块信息：厂商、型号、序列号、温度、电压、各通道收发光功率。读不出通常意味着 I2C 故障或模块未插好。 |
| `mlxlink -d /dev/mst/mt4131_pciconf0 -c` | 物理层计数器：纠错前后误码率、有效错误数、链路 down 次数。 |
| `mlxlink -d /dev/mst/mt4131_pciconf0 -e` | 眼图张开度。数值偏小说明信号质量差，常见于光纤脏污、弯折半径过小、模块老化。 |
| `mlxlink -d /dev/mst/mt4131_pciconf0 --show_module` | 模块状态的详细展开，包含 CMIS 状态机所处阶段。 |
| `mlxlink -d /dev/mst/mt4131_pciconf0 --port_type PCIE -c` | 把诊断对象切到 PCIe 侧，看主机总线链路而非网络链路。 |
| `mlxlink -d /dev/mst/mt4131_pciconf0 -p 1 --amber_collect amber.csv` | 一次性打包导出全部链路遥测到 CSV。向 NVIDIA 报障时最省事的做法。 |
| `mlxlink -d /dev/mst/mt4131_pciconf0 -p 1 --rx_fec_histogram` | FEC 纠错分布直方图，判断误码是偶发还是持续。 |
| `mlxcables` | 列出所有已识别的线缆与模块设备节点。 |
| `mlxcables -d /dev/mst/mt4131_pciconf0_cable_0 -q` | 查询指定模块的详细参数。 |
| `mlxcables -d /dev/mst/mt4131_pciconf0_cable_0 --dump` | 导出模块 EEPROM 原始内容。 |
| `mget_temp -d /dev/mst/mt4131_pciconf0` | 读取 ASIC 芯片温度。过热会触发降速或直接关闭端口。 |

### 固件查询与升级

| 命令 | 说明 |
|---|---|
| `mlxfwmanager --query` | 查询系统内所有 NVIDIA 设备的当前固件版本、PSID 与可用更新。 |
| `mlxfwmanager -d /dev/mst/mt4131_pciconf0 --query` | 只查询指定设备。 |
| `mlxfwmanager --online -u -d /dev/mst/mt4131_pciconf0` | 联网自动匹配并下载固件后升级，需要能访问 NVIDIA 服务器。 |
| `mlxfwmanager -u -i fw.mfa2 --skip_if_same` | 从本地 mfa2 包升级，版本一致则跳过。 |
| `flint -d /dev/mst/mt4131_pciconf0 query` | 查固件版本、PSID、GUID/MAC。PSID 是板卡唯一型号标识，下载固件必须对上。 |
| `flint -d /dev/mst/mt4131_pciconf0 q full` | 更完整的输出，包含镜像各段信息。 |
| `flint -d /dev/mst/mt4131_pciconf0 hw query` | Flash 硬件信息与写保护状态。 |
| `flint -i fw.bin verify` | 校验镜像文件完整性。针对文件操作，不带 -d。 |
| `flint -d /dev/mst/mt4131_pciconf0 -i fw.bin burn` | 直接烧录 Flash。风险较高，日常升级优先用 mlxfwmanager。 |

### 配置修改与重置

| 命令 | 说明 |
|---|---|
| `mlxconfig -d /dev/mst/mt4131_pciconf0 query` | 查看全部当前配置项。 |
| `mlxconfig -d /dev/mst/mt4131_pciconf0 -e query` | 同时显示默认值、当前值、下次启动生效值。排查“改了没生效”时用。 |
| `mlxconfig -d /dev/mst/mt4131_pciconf0 query LINK_TYPE_P1` | 只查询单个配置项。 |
| `mlxconfig -d /dev/mst/mt4131_pciconf0 set LINK_TYPE_P1=2` | 设置端口 1 工作模式，1 为 InfiniBand，2 为 Ethernet。模式配错会导致完全连不上。 |
| `mlxconfig -d /dev/mst/mt4131_pciconf0 set SRIOV_EN=1 NUM_OF_VFS=8` | 启用 SR-IOV 并设置 VF 数量。 |
| `mlxconfig -d /dev/mst/mt4131_pciconf0 reset` | 全部配置恢复出厂默认。 |
| `mlxconfig -d /dev/mst/mt4131_pciconf0 -j /tmp/cfg.json query` | 配置导出为 JSON，便于比对多台机器的差异。 |
| `mlxfwreset -d /dev/mst/mt4131_pciconf0 query` | 查询当前平台支持哪些 reset level。 |
| `mlxfwreset -d /dev/mst/mt4131_pciconf0 -l 3 reset` | Level 3 重置，PCIe 设备的默认级别。 |
| `mlxfwreset -d /dev/mst/mt4131_pciconf0 -l 4 reset` | Level 4 重置，加载新 mlxconfig 配置需要。不支持则冷启动（断电，而非 reboot）。 |
| `mlxprivhost -d /dev/mst/mt4131_pciconf0 q` | 多主机场景下查询当前 host 的权限等级。 |

### 底层调试

| 命令 | 说明 |
|---|---|
| `mlxreg -d /dev/mst/mt4131_pciconf0 --reg_name PAOS --get --indexes "local_port=1"` | 读端口管理状态寄存器，确认端口是否被管理端 disable。 |
| `mlxreg -d /dev/mst/mt4131_pciconf0 --reg_name PMLP --get --indexes "local_port=1"` | 查看端口到物理 lane 的映射关系。 |
| `mlxreg -d /dev/mst/mt4131_pciconf0 --reg_name PDDR --get --indexes "local_port=1,page_select=1"` | 读取链路 down reason code。排障价值最高的寄存器。 |
| `mstregdump /dev/mst/mt4131_pciconf0 > dump.txt` | 全寄存器快照。设备是位置参数，不用 -d。 |
| `mlxdump -d /dev/mst/mt4131_pciconf0 fsdump --type FT > fsdump.txt` | 固件内部状态 dump，报障时提交给支持团队。 |
| `mlxvpd -d /dev/mst/mt4131_pciconf0` | 读板卡 VPD：序列号、部件号。走 RMA 流程时需要。 |

## 设备与拓扑映射

把物理端口、PCI 地址、RDMA 设备名、网口名对应起来。跨工具排障的第一步。

| 命令 | 说明 |
|---|---|
| `ibdev2netdev -v` | RDMA 设备、网口名、PCI 地址的对应表。后续所有命令的参数都从这里来。 |
| `ibv_devinfo -v` | RDMA 设备能力、端口状态、固件版本、MTU、链路层类型。 |
| `ibv_devices` | 简表，只列设备名和 GUID。 |
| `lspci -d 15b3: -vvv` | 15b3 是 Mellanox 厂商号。重点看 LnkCap 与 LnkSta，两者不一致说明插槽或信号有问题。 |
| `lspci -d 15b3: -tv` | 树状拓扑，确认卡挂在哪个 root port 或 PCIe switch 下，用于判断 NUMA 亲和性。 |

## 网口与光模块

不依赖 MFT 的路径，走内核驱动。与 mlxlink 的结果交叉验证，能有效区分故障层次。

### ethtool

| 命令 | 说明 |
|---|---|
| `ethtool <iface>` | 速率、双工、自协商、链路状态。 |
| `ethtool -m <iface>` | 读模块 EEPROM 与 DOM 数据。与 mlxlink -m 走不同代码路径，交叉验证价值大。 |
| `ethtool -i <iface>` | 驱动版本、固件版本、总线地址。 |
| `ethtool -S <iface>` | 全部统计计数器，mlx5 驱动会暴露上百项。 |
| `ethtool -S <iface> \| grep -i -E "err\|drop\|discard\|crc"` | 只看错误类计数。CRC 错误持续增长指向物理层。 |
| `ethtool -l <iface>` | 收发队列数量配置。 |
| `ethtool --show-fec <iface>` | FEC 模式。两端 FEC 配置不一致会导致链路起不来。 |
| `ethtool -d <iface>` | 寄存器 dump。 |

### sysfs 直读

| 命令 | 说明 |
|---|---|
| `cat /sys/class/net/<iface>/carrier` | 1 表示物理链路 up，0 表示 down。最快的物理层判断方式。 |
| `cat /sys/class/net/<iface>/operstate` | 接口运行状态：up / down / unknown。 |
| `cat /sys/class/infiniband/mlx5_0/ports/1/state` | 逻辑端口状态，4: ACTIVE 为正常。 |
| `cat /sys/class/infiniband/mlx5_0/ports/1/phys_state` | 物理状态。取值含义见文末对照表，是判断“没插好”还是“被关掉”的关键。 |
| `grep . /sys/class/infiniband/mlx5_0/ports/1/counters/*` | 标准 IB 错误计数器。 |
| `grep . /sys/class/infiniband/mlx5_0/ports/1/hw_counters/*` | 硬件级计数器，含 RoCE 拥塞与重传统计。 |

## InfiniBand 层

运行在 IB 模式时使用。Ethernet 模式下这些命令大多无输出。

| 命令 | 说明 |
|---|---|
| `ibstat` | 端口状态、LID、速率、物理状态。IB 侧最常用的一条。 |
| `ibstatus` | 同 ibstat，输出格式更简洁。 |
| `ibping -S` | 端到端连通性测试的服务端。 |
| `ibping -G <dest_gid>` | 端到端连通性测试的客户端。 |
| `ibhosts` | 列出子网内所有主机节点。 |
| `ibswitches` | 列出子网内所有交换机。 |
| `iblinkinfo` | 全网链路速率与对端连接关系。查找降速端口非常好用。 |
| `ibdiagnet -r --pm_pause_time 30` | 全网体检。自动标出误码超标、速率不一致、固件版本不统一的链路，IB 排障主力工具。 |
| `perfquery -x <lid> <port>` | 查端口性能与错误计数器，-x 为扩展计数器。 |
| `perfquery -R <lid> <port>` | 读完清零，用于观察一段时间内的增量。 |
| `ibnetdiscover` | 完整拓扑发现，输出全网连接图。 |
| `saquery` | 查询子网管理器。SM 未运行是“链路 up 但通信失败”的常见原因。 |

## 连通性与性能验证

链路恢复后用来确认实际可用。需要两台机器配合，先起服务端再起客户端。

| 命令 | 说明 |
|---|---|
| `ib_write_bw -d mlx5_0 -i 1 -F` | RDMA Write 带宽测试服务端。-i 指端口号，-F 忽略 CPU 频率告警。 |
| `ib_write_bw -d mlx5_0 -i 1 -F <server_ip>` | 客户端侧，跑出实际带宽。 |
| `ib_write_lat -d mlx5_0 -i 1 -F <server_ip>` | 时延测试。 |
| `ib_send_bw -d mlx5_0 -i 1 -F <server_ip>` | 换用 Send 操作类型，不同场景表现可能不同。 |
| `ib_read_bw -d mlx5_0 -i 1 -F <server_ip>` | 换用 Read 操作类型。 |
| `qperf <server> rc_bw rc_lat` | 轻量替代方案，一条命令同时测带宽与时延。 |
| `ucx_info -d` | 列出 UCX 可用的传输层。NCCL、MPI 等上层框架走不通时查这个。 |

## 日志与系统层

找时间线、确认版本匹配、排除系统配置干扰。

| 命令 | 说明 |
|---|---|
| `dmesg -T \| grep -i -E "mlx5\|i2c\|osfp\|module\|link\|pcie"` | 内核日志过滤。-T 显示可读时间戳，便于与应用日志对齐。 |
| `journalctl -k -b \| grep -i mlx5` | 本次启动以来的内核日志。 |
| `journalctl -u openibd -u opensmd --since "1 hour ago"` | IB 驱动服务与子网管理器的服务日志。 |
| `ofed_info -s` | OFED 版本号。版本与固件不匹配是隐蔽的常见问题。 |
| `/etc/init.d/openibd status` | IB 驱动栈加载状态。 |
| `lsmod \| grep mlx5` | 确认 mlx5_core 与 mlx5_ib 已加载。 |
| `modinfo mlx5_core \| head -20` | 驱动模块版本与可用参数。 |
| `mlnx_tune -r` | 系统调优体检，报出 PCIe 速率、IRQ 绑定、NUMA 亲和、节能模式等层面的问题。 |
| `hca_self_test.ofed` | 网卡自检脚本，一次性跑完基础检查项。 |

## phys_state 取值对照

| 值 | 状态 | 含义 |
|---|---|---|
| 1 | Sleep | 端口处于休眠，通常是被软件置位 |
| 2 | Polling | 正在寻找对端。指向对端未通、光纤未插好或模块故障 |
| 3 | Disabled | 被管理端主动关闭，检查配置而非硬件 |
| 4 | PortConfigurationTraining | 正在做链路训练，短暂停留正常，长期停留说明协商失败 |
| 5 | LinkUp | 物理链路正常 |
| 6 | LinkErrorRecovery | 正在做链路错误恢复，反复出现说明信号质量差 |
| 7 | PhyTest | 处于物理层测试模式 |

## 端口 LED 对照

| LED 状态 | 含义 | 处理 |
|---|---|---|
| 熄灭 | 链路未建立 | 检查模块是否插到位、对端是否上电 |
| 绿色常亮 | 链路有效，无流量 | 正常状态 |
| 绿色闪烁 | 链路有效，有流量 | 正常状态 |
| 琥珀色常亮 | 物理链路已建立（IB 模式） | 等待逻辑链路建立，检查子网管理器 |
| 琥珀色 1 Hz 闪烁 | beacon 定位命令 | 有人在执行点灯定位，不是故障 |
| 琥珀色 4 Hz 闪烁 | 链路错误 | I2C 访问失败或端口过流，故障排除前会持续闪烁 |

## 使用须知

**设备标识**　本文档统一使用 /dev/mst/mt4131_pciconf0。实际编号随芯片型号变化，请先运行 mst status -v 确认后替换。双端口卡的第二个端口为 .1 后缀。

**接口名占位**　<iface> 需替换为实际网口名，通过 ibdev2netdev -v 获取。mlx5_0 同理，多卡系统会有 mlx5_1、mlx5_2 等。

**烧录风险**　flint burn 与 mlxfwmanager -u 中途断电存在变砖风险。务必确认 PSID 匹配，生产环境先在备件上验证。

**开源替代**　mstflint 是 MFT 的开源精简版，命令名加 mst 前缀：mstflint、mstconfig、mstregdump、mstfwreset、mstlink。参数基本一致，但不含 mlxfwmanager。
