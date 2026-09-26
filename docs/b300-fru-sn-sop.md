# 技嘉 B300 FRU 序列号修改 SOP

更换主板后通过 ipmitool 恢复主板 SN 与整机 SN 的标准作业流程。

| 字段 | 命令参数 | 样例 | 长度 |
|---|---|---|---|
| 整机 SN | `field p 4` | `XXXXXXXXXXXXXX` | 14 位 |
| 主板 SN | `field b 2` | `XXXXXXXXXXX` | 11 位 |

## 01　适用范围

| 项 | 内容 |
|---|---|
| 适用场景 | 更换主板后恢复主板 SN；整机 SN 丢失或错误需要重写 |
| 适用设备 | 技嘉 HGX B300 系列服务器 |
| 执行人 | 经授权的现场工程师，需持有效工单 |
| 前置条件 | BMC 网络可达、持有管理员凭据、已从工单确认目标 SN |
| 本次范围 | 仅修改 Board Serial 与 Product Serial，不涉及 Chassis Serial |

> **以下情况不适用本 SOP，请联系厂商支持**：BMC 无法登录；`fru print` 输出出现 checksum 错误，说明 FRU 区域已损坏；目标 SN 无法从工单或设备标签确认。不要凭猜测写入。

## 02　风险提示

> **FRU 写入即刻生效且不可撤销。** 没有版本历史，写错只能再写一次覆盖，前提是你知道原值。因此第 05 节的备份是强制步骤，不是可选项。

> **写入期间不得断电或重启 BMC。** FRU EEPROM 写到一半掉电会导致该区域校验失败，后果是整机识别异常，可能需要返厂。

> **SN 错误会影响保修。** 主板 SN 与整机 SN 不匹配，或与厂商出厂记录不符，售后可能拒保。执行前务必与工单逐字符核对。

## 03　工具安装

### Ubuntu / Debian

```bash
apt update
apt install -y ipmitool
ipmitool -V
```

### RHEL / CentOS / Rocky

```bash
dnf install -y ipmitool
# 旧版本发行版
yum install -y OpenIPMI ipmitool
ipmitool -V
```

建议版本 **1.8.18 以上**。低版本的 `fru edit` 子命令支持不完整，可能出现静默失败。

### 本机直连方式（优先推荐）

如果能在被操作的服务器本机上执行，走内核接口而不走网络更稳妥，中途不会因为网络抖动中断写入。

```bash
modprobe ipmi_si
modprobe ipmi_devintf
systemctl start ipmi          # 部分发行版需要

ipmitool -I open fru print 0
```

采用本机方式时，后续所有命令把 `-H $BMC -U $BMCUSER -P $BMCPASS -I lanplus` 整段替换为 `-I open` 即可。

### Windows

从 ipmitool 官方发布页下载 Windows 构建，解压后在 PowerShell 中使用，命令参数与 Linux 完全一致。

## 04　建立连接

```bash
export BMC=<BMC_IP>
export BMCUSER=<user>
export BMCPASS=<password>

ipmitool -H $BMC -U $BMCUSER -P $BMCPASS -I lanplus mc info
```

能返回 BMC 固件版本即连接正常。连接失败时按以下顺序排查：

```bash
# 换加密套件
ipmitool -H $BMC -U $BMCUSER -P $BMCPASS -I lanplus -C 17 mc info
ipmitool -H $BMC -U $BMCUSER -P $BMCPASS -I lanplus -C 3 mc info

# 确认端口可达，IPMI over LAN 走 UDP 623
nc -zvu $BMC 623
```

> **凭据安全。** 命令行带明文密码会进入 shell history 和进程列表。正式环境建议改用 `-f <密码文件>`，或用 `-a` 交互式输入。操作完成后执行 `history -c` 清理。

## 05　备份现有 FRU

> **这一步不完成不得进入第 08 节。** 二进制备份是唯一能完整回滚的依据。

```bash
mkdir -p /root/fru-backup
cd /root/fru-backup

# 二进制完整备份
ipmitool -H $BMC -U $BMCUSER -P $BMCPASS -I lanplus \
  fru read 0 fru0-before-$(date +%F-%H%M).bin

# 文本快照，便于人工核对
ipmitool -H $BMC -U $BMCUSER -P $BMCPASS -I lanplus \
  fru print 0 > fru0-before-$(date +%F-%H%M).txt

ls -l
cat fru0-before-*.txt
```

确认 `.bin` 文件大小非零、`.txt` 内容完整，并将两个文件复制到本机之外的位置留存。

### 读取当前值并记录到工单

```bash
ipmitool -H $BMC -U $BMCUSER -P $BMCPASS -I lanplus fru print 0
```

逐字符抄录输出中的 `Board Serial` 与 `Product Serial` 当前值。同时确认输出末尾没有 checksum 相关报错。

## 06　字段对照

`fru edit <FRU_ID> field <区域> <索引> <新值>` 三个参数的含义如下。

### 区域代码

| 代码 | 区域 |
|---|---|
| `c` | Chassis Area 机箱区 |
| `b` | Board Area 主板区 |
| `p` | Product Area 产品区 |

### Board Area 索引

| 索引 | 字段 | 本次操作 |
|---|---|---|
| 0 | Board Manufacturer | — |
| 1 | Board Product Name | — |
| **2** | **Board Serial** | **主板 SN，本次修改** |
| 3 | Board Part Number | — |
| 4 | FRU File ID | — |

### Product Area 索引

| 索引 | 字段 | 本次操作 |
|---|---|---|
| 0 | Product Manufacturer | — |
| 1 | Product Name | — |
| 2 | Product Part Number | — |
| 3 | Product Version | — |
| **4** | **Product Serial** | **整机 SN，本次修改** |
| 5 | Product Asset Tag | — |
| 6 | FRU File ID | — |

## 07　长度预检

> **ipmitool 的 `fru edit` 不能改变字段长度。** 新值长度必须与原值完全一致，否则命令报错；部分版本会静默截断，后果更严重。

技嘉 B300 的 SN 格式：整机 SN 14 位、主板 SN 11 位，均为纯大写字母与数字。上述长度依据实际样例，不同批次可能存在差异，**每次仍以设备标签和当前 FRU 读数为准**。

> ⚠️ **SN 等同于凭据，不要外传。** 技嘉部分批次的 BMC 出厂密码就是主板 SN，机箱标签条上序列号条码与 BMC 密码条码成对印刷。因此主板 SN 不要写进公开文档、工单截图或聊天记录。本文档所有样例已替换为 `X` 占位符，实际值请从设备标签或 `fru print` 现场读取。

### 自动校验

```bash
NEW_MB="XXXXXXXXXXX"          # 替换为目标主板 SN
NEW_SYS="XXXXXXXXXXXXXX"      # 替换为目标整机 SN

OLD_MB=$(ipmitool -H $BMC -U $BMCUSER -P $BMCPASS -I lanplus fru print 0 \
         | grep "Board Serial" | cut -d: -f2- | xargs)
OLD_SYS=$(ipmitool -H $BMC -U $BMCUSER -P $BMCPASS -I lanplus fru print 0 \
         | grep "Product Serial" | cut -d: -f2- | xargs)

printf "主板 SN  当前 [%s] %d 位 -> 目标 [%s] %d 位\n" \
       "$OLD_MB" ${#OLD_MB} "$NEW_MB" ${#NEW_MB}
printf "整机 SN  当前 [%s] %d 位 -> 目标 [%s] %d 位\n" \
       "$OLD_SYS" ${#OLD_SYS} "$NEW_SYS" ${#NEW_SYS}

[ ${#NEW_MB} -eq ${#OLD_MB} ]   && echo "主板 SN 长度匹配" || echo "主板 SN 长度不符，停止"
[ ${#NEW_SYS} -eq ${#OLD_SYS} ] && echo "整机 SN 长度匹配" || echo "整机 SN 长度不符，停止"
```

两项都显示「长度匹配」才进入下一节。长度不符时的处理：

- **新值较短**：用尾部空格补齐到相同长度
- **新值较长**：只能编辑二进制 FRU 后整体写回，见第 10 节

## 08　执行修改

一次改一个字段，改完立即验证，不要连续执行两条命令。

### 修改主板 SN

```bash
ipmitool -H $BMC -U $BMCUSER -P $BMCPASS -I lanplus \
  fru edit 0x0 field b 2 "$NEW_MB"

ipmitool -H $BMC -U $BMCUSER -P $BMCPASS -I lanplus \
  fru print 0 | grep "Board Serial"
```

### 修改整机 SN

确认主板 SN 无误后再执行。

```bash
ipmitool -H $BMC -U $BMCUSER -P $BMCPASS -I lanplus \
  fru edit 0x0 field p 4 "$NEW_SYS"

ipmitool -H $BMC -U $BMCUSER -P $BMCPASS -I lanplus \
  fru print 0 | grep "Product Serial"
```

## 09　验证与收尾

### BMC 冷复位

让新值在各管理接口生效。复位约需 1 到 2 分钟，期间不要断电。

```bash
ipmitool -H $BMC -U $BMCUSER -P $BMCPASS -I lanplus mc reset cold

sleep 120
ipmitool -H $BMC -U $BMCUSER -P $BMCPASS -I lanplus fru print 0
```

### 操作系统侧交叉验证

需要主机重启后 BIOS 重新读取 FRU，SMBIOS 才会更新。

```bash
dmidecode -s baseboard-serial-number
dmidecode -s system-serial-number
```

### Redfish 交叉验证

```bash
curl -sk -u $BMCUSER:$BMCPASS https://$BMC/redfish/v1/Systems/ | jq
curl -sk -u $BMCUSER:$BMCPASS https://$BMC/redfish/v1/Chassis/ | jq
```

### 留存修改后备份

```bash
cd /root/fru-backup
ipmitool -H $BMC -U $BMCUSER -P $BMCPASS -I lanplus \
  fru read 0 fru0-after-$(date +%F-%H%M).bin
ipmitool -H $BMC -U $BMCUSER -P $BMCPASS -I lanplus \
  fru print 0 > fru0-after-$(date +%F-%H%M).txt

history -c
```

## 10　异常处理与回滚

### 完整回滚

用第 05 节的二进制备份整体写回。

```bash
ipmitool -H $BMC -U $BMCUSER -P $BMCPASS -I lanplus \
  fru write 0 /root/fru-backup/fru0-before-<时间戳>.bin

ipmitool -H $BMC -U $BMCUSER -P $BMCPASS -I lanplus mc reset cold
```

### 长度不一致时的二进制改法

> **FRU 各区域末尾有校验字节，手工改动必须同步重算。** 字段前一字节是长度与类型编码，改内容时需一并调整。没有把握就不要手改二进制，联系技嘉支持获取官方 FRU 烧录工具。

```bash
ipmitool ... fru read 0 fru0-edit.bin
hexdump -C fru0-edit.bin | less
# 推荐用 frugy 等工具处理，避免手工破坏校验和
ipmitool ... fru write 0 fru0-edit.bin
```

### 常见报错

| 报错 | 原因与处理 |
|---|---|
| Length of the new string is not the same | 新值长度不符，回到第 07 节重新核对 |
| FRU write failed | 权限不足，确认账号具备 Administrator 权限 |
| Unable to establish IPMI v2 / RMCP+ session | 凭据或加密套件问题，尝试 `-C 17` 或 `-C 3` |
| fru print 出现 checksum 错误 | FRU 区域已损坏，立即停止操作，联系厂商 |
| 写入后值未变化 | 执行 `mc reset cold` 后再查询 |

## 11　记录模板

每次操作填写一份，随工单归档。

```
操作日期：
执行人：
工单号：
服务器位置（机房 / 机柜 / U 位）：
BMC IP：

修改前
  Board Serial   ：                    长度：
  Product Serial ：                    长度：
  备份文件路径   ：

修改后
  Board Serial   ：                    长度：
  Product Serial ：                    长度：
  备份文件路径   ：

备注：
```

### 执行检查项

- [ ] 已从工单确认目标 SN，逐字符核对
- [ ] 已完成二进制与文本双重备份，并复制到本机之外
- [ ] 长度预检两项均显示匹配
- [ ] 主板 SN 修改后已单独验证
- [ ] 整机 SN 修改后已单独验证
- [ ] 已执行 BMC 冷复位并复查
- [ ] 已留存修改后的 FRU 备份
- [ ] 已清理 shell history
- [ ] dmidecode 验证（需主机重启后执行）

---

本 SOP 适用于技嘉 HGX B300 系列服务器，仅涉及 Board Serial 与 Product Serial 两个字段。SN 长度依据实际样例整理，不同批次可能存在差异，现场以设备标签与当前 FRU 读数为准。
