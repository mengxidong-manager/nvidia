# 阿里云 IPSec VPN 配置指南

> 从零配置阿里云 IPSec-VPN，实现本地数据中心与 VPC 加密互通。
>
> 撰写人：孟希東

---

架构：本地IDC ⇔ IPSec隧道 ⇔ 阿里云VPN网关 → VPC

步骤：前置准备(网段规划) → 创建 VPN 网关 → 创建用户网关 → 创建 IPSec 连接(IKEv2/aes256/sha256/group14) → 配置三层路由 → 配置本地设备 → 连通性验证

故障排查：IKE失败(PSK/算法不匹配) · IPSec失败(感兴趣流/PFS) · 隧道通但ping不通(路由/安全组/ACL)

*完整版请参考仓库历史版本或 HTML 文档*
