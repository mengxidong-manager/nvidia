# AIDC 每日一图

每天一张 AIDC / GPU 集群运维知识卡，发布在 X：[@startre47133551](https://x.com/startre47133551) 和小红书：[祁山晴彦](https://www.xiaohongshu.com/user/profile/638dbb9e000000001f01629e)（小红书号 5315285201）

## 已发布

| Day | 主题 | 主要来源 |
|---|---|---|
| 01 | GPU XID 错误码速查 | NVIDIA XID Errors 文档 · GPU 集群故障排查手册 |
| 02 | ECC 与 Row Remap | NVIDIA GPU Memory Error Management |
| 03 | nvidia-smi 救命命令 | NVIDIA nvidia-smi 官方手册 |
| 04 | GPU 降频的 4 种原因 | NVIDIA NVML Clocks Event Reasons · nvidia-smi 官方手册 |
| 05 | NVLink 排障 | NVIDIA nvidia-smi 手册 · XID Catalog · Fabric Manager 用户指南 |
| 06 | DCGM diag 跑几级？ | NVIDIA DCGM Diagnostics 文档 · dcgmi diag 命令参考 |
| 07 | 掉卡 SOP：推理 vs 训练 | GPU 集群掉卡故障处理手册 · PyTorch torchrun / NCCL 环境变量文档 |
| 08 | 集合通信原语 | AI 集群常见通信模式 · nccl-tests PERFORMANCE 文档 |
| 09 | 并行策略与通信量 | AI 集群常见通信模式 · Megatron-LM（SC21） |
| 10 | Rail 优化拓扑 | B300 集群架构笔记 · NCCL 2.12 PXN 博客 |
| 11 | RoCEv2 vs InfiniBand | B300 集群架构笔记 · IP Infusion《RoCE vs InfiniBand》 |
| 12 | 800G 光模块与 breakout | 800G 光模块连接笔记 · NVIDIA MMS4X00 / MMS4A20 手册 |
| 13 | 光纤连接器选型 | 800G 光模块连接笔记 · CX-8 自环笔记 · FOA 光纤色标 · Fluke MPO 极性指南 |
| 14 | NCCL 调试变量 | GPU 集群故障排查手册 · NVIDIA NCCL 环境变量与日志文档 · PyTorch ProcessGroupNCCL 文档 |
| 15 | GPU Operator 全家福 | K8s GPU 调度与部署指南 · NVIDIA GPU Operator v26.7.1 文档与源码 · DCGM Exporter |

## 选题计划

| 周 | 主题 |
|---|---|
| 第 1 周 GPU 排障 | 01 XID 速查 ✅ · 02 ECC 与 Row Remap ✅ · 03 nvidia-smi 救命命令 ✅ · 04 GPU 降频的 4 种原因 ✅ · 05 NVLink 排障 ✅ · 06 DCGM diag r1/r2/r3 怎么选 ✅ · 07 掉卡 SOP：推理 vs 训练 ✅ |
| 第 2 周 AI 网络 | 08 集合通信原语 ✅ · 09 TP/PP/DP/EP 与通信量 ✅ · 10 Rail 优化拓扑 ✅ · 11 RoCEv2 vs InfiniBand ✅ · 12 800G 光模块与 breakout ✅ · 13 光纤连接器选型 ✅ · 14 NCCL 调试变量 ✅ |
| 第 3 周 K8s × GPU | 15 GPU Operator 全家福 ✅ · 16 GPU 调用链 · 17 Time-Slicing / MIG / DRA · 18 GPU Pod 排障 · 19 DCGM 告警阈值 · 20 etcd 空间超限 · 21 K8s HA 架构 |
| 第 4 周 机房基础设施 | 22 从市电到 0.7V · 23 四级备电时间接力 · 24 UPS vs 240V vs 800V HVDC · 25 冷热通道封闭 · 26 冷板 / 浸没 / 喷淋 · 27 PUE、WUE、Tokens per Watt · 28 CDU 液冷运维 |
| 第 5 周 机柜级系统 | 29 GB300 NVL72 解剖 · 30 Vera Rubin NVL72 看点 |

## 目录结构

```
aidc-daily/
├── render.py        # 渲染脚本：页头、页脚、字体都在这里
├── series.css       # 全系列共用样式
├── setup_fonts.sh   # 下载字体（首次运行）
└── days/
    ├── day01.json   # 标题、副标题、出处、X 文案（caption）、小红书标题和正文（xhs）
    ├── day01.html   # 这一天的正文分格
    └── day01.css    # 这一天专用的样式
```

## 出一张新图

```bash
pip install playwright qrcode pillow && playwright install chromium   # 首次
./setup_fonts.sh                                          # 首次
python3 render.py day04                                   # X 版：out/day04.png
python3 render.py day04 xhs                               # 小红书版：out/xhs/day04.png
```

新一天只需在 `days/` 下加 `dayNN.json`、`dayNN.html`（可选 `dayNN.css`）。
可用环境变量 `AIDC_FONTS` 指定字体目录，`CHROME_PATH` 指定浏览器路径。

## 风格约定

- 尺寸：宽 1080px，2 倍导出（2160px 宽 PNG）
- 字体：ZCOOL KuaiLe（标题）、LXGW WenKai（中文正文）、Kalam（英文手写）
- 配色：藏青 `#1d2b4f` 主色，青 `#1797b8` 对策 / 正常，红 `#e2315f` 风险 / 换卡，橙 `#f08a24` 处置
- 顶部不放标识；底部左侧 AIDC NOTES，右侧 X 账号（小红书版为小红书账号 + 主页二维码）
- 小红书标题不超过 20 字
- 每张收尾一组「三条铁律」
- 所有命令、阈值、错误码发布前对照官方文档核实
