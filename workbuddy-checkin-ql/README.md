# WorkBuddy 全能签到 · 青龙面板订阅

> WorkBuddy（腾讯 AI 编程助手）成长中心全自动化：**Token 自动续期 → 积分/用量/成长查询 → 每日签到
> → 18 项成长任务（17 全自动）→ 8 项互动玩法 → 5 项开学季任务 + 大转盘抽奖 → 3 项小程序任务
> → 自动领奖 → 中文报告推送**
>
> 单文件 · 零依赖（仅 Python 标准库）· 多账号并行 · 无需安装桌面端

---

## ✨ 功能特性

- 🔐 **Token 永续**：accessToken 7 天内过期（或缺失）时自动用 refreshToken 走官方刷新接口轮换新令牌并回写凭证，无需反复重新登录
- ✅ **35 项覆盖，33 项全自动**：签到 / 成长任务 / 互动玩法 / 开学季活动 / 小程序任务全打通
- 🖥️ **无头点亮桌面任务**：由 uid 稳定派生设备指纹，按官方客户端事件契约向桌面域 / Web 域 / 小程序域三通道上报遥测，无需安装任何桌面端
- 💬 **真实 AI 对话**：GLM-5.2 模型对话、聊天5次、专家团、夜猫子等任务走官方 Web 对话接口真实发起
- 🔐 **自动解密**：新版桌面端（5.6.x）凭证字段加密为 `$wbEncrypted` 信封（AES-256-GCM at-rest），`login` 自动调用本机 WorkBuddy.exe 取出构建密钥解密
- 🧩 **幂等安全**：重复运行只补缺口，不会重复领取或重复操作
- ⏱️ **时间预算**：单账号请求预算（默认 900s）+ 随机延时（延时不计入预算），保证在青龙超时上限前收尾
- 🔄 **分类退避重试**：网络不可达（5/15/30/60/90s）与 5xx（3/10s）分桶退避；4xx 不重试；POST 写操作默认不重试防重复提交
- 🚀 **任务列表缓存**：高频进度查询走线程内缓存（20s TTL），单账号省 30-50 秒请求预算
- 🕐 **北京时间日志**：时间戳统一 UTC+8，不受容器本地时区影响
- 📢 **通知推送**：自动对接青龙面板 `notify.py`，运行结束推送中文报告

## 📁 目录结构

```
workbuddy-checkin-ql/
├── workbuddy_checkin.py   # 签到脚本（青龙面板格式，含 cron + new Env 声明）
├── README.md              # 本文档
└── auths/                 # 凭证目录（多账号 = 多文件，仅脚本根目录读取）
    ├── 4edbe83a-xxxx.json # 账号1 凭证
    └── 9f2c1a7b-xxxx.json # 账号2 凭证
```

## 🚀 快速开始（青龙三步）

### 1. 订阅仓库与上传脚本

- 方法一、📌 订阅仓库

  - 添加订阅拉取仓库
    在青龙「订阅管理」中添加订阅：
    - 订阅链接地址: `https://wget.la/https://github.com/xz0609/workbuddy-checkin-ql.git`
    - 添加完成后，点击 `运行` 按钮，拉取仓库代码。

- 方法二、上传脚本
将 `workbuddy_checkin.py` 上传到青龙面板脚本管理（或拉取订阅仓库）。

### 2. 导入凭证

在本机（已登录 WorkBuddy 桌面端的电脑）执行：

```bash
python workbuddy_checkin.py login
```

脚本会自动定位本机登录态；**新版桌面端（5.6.x）已把凭证字段加密为 `$wbEncrypted` 信封
（AES-256-GCM at-rest 加密），login 会自动调用本机 WorkBuddy.exe 取出构建密钥完成解密**，
保存明文凭证为 `auths/<uid>.json`。然后把整个 `auths` 目录上传到青龙容器内脚本同级目录：

```
scripts/
├── workbuddy_checkin.py
└── auths/
    ├── 4edbe83a-xxxx.json    # 账号1
    └── 9f2c1a7b-xxxx.json    # 账号2（多账号放多个文件即可）
```

### 3. 创建定时任务(仅限方法二，使用方法一的话可跳过此项)

| 项目 | 值 |
|---|---|
| 任务名称 | WorkBuddy 签到 |
| 命令 | `task workbuddy_checkin.py` |
| 定时规则 | `3 */8 * * *`（每日 00:03 / 08:03 / 16:03） |

完成。脚本不读任何 Token 环境变量，凭证只认 `auths/*.json` 文件。

## 🔑 凭证说明

**login 自动扫描的本机凭据文件**（按优先级）：

| 平台 | 路径 |
|---|---|
| Windows 桌面端 | `%LOCALAPPDATA%\CodeBuddyExtension\Data\Public\auth\workbuddy-desktop.info` |
| Linux CodeBuddy CLI | `~/.local/share/CodeBuddyExtension/Data/Public/auth/Tencent-Cloud.coding-copilot.info` |

- 文件名以 `account.uid` 的值命名，保存为 `auths/<uid>.json`（JSON 格式，内容与桌面端一致）
- **自动解密**：2026-09 起 5.6.x 桌面端把 `accessToken` / `refreshToken` / `nickname` 等字段
  加密为 `$wbEncrypted` 信封。`login` 检测到加密字段时，自动以 `ELECTRON_RUN_AS_NODE` 模式
  调用本机 WorkBuddy.exe（通过注册表卸载信息自动定位）取出内嵌构建密钥并解密；
  接口请求/响应不受影响（明文请求返回明文）
- **多账号**：在本机切换登录 WorkBuddy 桌面端后重复执行 `login`，或直接把多个凭据文件放进 `auths/` 目录
- **Token 永续**：运行中自动轮换并回写 `auths/<uid>.json`，只要每 30 天内至少跑一次脚本，凭证长期有效

## 📦 任务覆盖（共 35 项，33 项全自动）

### ✅ 每日签到（1 项）
连签 / 累计积分，走签到域独立接口。

### ☁️ 成长中心任务（18 项，17 全自动）

| 任务 | 方式 |
|---|---|
| 设计创意模式 / 探索优秀灵感 / 设置自动化任务 | 遥测事件上报 |
| 桌面端对话 / 尝鲜热门技能 | 稳定指纹事件链（无需桌面端） |
| 体验资料库 | Web 域点击事件 |
| 腾讯轻量云专家 / 召唤5次专家 | 专家市场 + 遥测 |
| 和平精英主题 | 主题切换 API + 遥测 |
| 发现应用 / 企鹅教师助手 | Buddy 五连事件链 |
| GLM-5.2 模型对话 / 和AI聊天5次 / 夜猫子活动 | 官方 Web 对话接口真实发起 |
| 召唤3次专家团 | 真实团队对话 + 全字段遥测 |
| 使用5个模板 | 批量遥测 |
| 领取Buddy（新账号） | 领养链路 |
| 公益专家 | ❌ 人工（涉及真实捐款，脚本不做） |

> 另有「工作台搭建师」任务需 Windows 真实桌面端，无头环境无法点亮，不计入覆盖。

### 🎮 互动玩法（8 项）
抽奖 · 盲盒 · Buddy 信息 · 派猫猫旅行 · 连签兑换（7d/14d/28d 三档）· 补签卡（断登自动补，每轮 1 张）· 礼包补偿 · 徽章

### 🏫 开学季活动（5 项，4 全自动 + 大转盘抽奖）

| 任务 | 方式 |
|---|---|
| 分享活动给好友 | share-complete 接口 |
| 与AI对话3次 | 小程序域事件上报 |
| 桌面端对话1次 | 指纹事件链（copilot 域） |
| 召唤开学季专家并对话 | 专家市场 + 遥测 |
| 微信学生认证 | ❌ 人工（需微信实名） |
| 幸运大转盘 | 自动抽完余额（含瑞幸/KFC/酷狗实物券） |

### 📱 小程序任务（3 项）
小程序内完成 1 次对话 · 参与校园日有奖活动 · **新任务自动适配**（mp 口径出现未知小程序任务时自动接单 + 上报 + 领奖）

## ⌨️ 命令行子命令

```bash
python workbuddy_checkin.py            # 全流程（默认：签到 + 成长中心 + 玩法 + 开学季 + 推送）
python workbuddy_checkin.py growth     # 仅成长中心 + 互动玩法（不签到）
python workbuddy_checkin.py school     # 仅开学季活动 + 小程序任务
python workbuddy_checkin.py query      # 仅查询积分/用量/成长
python workbuddy_checkin.py refresh    # 仅强制刷新 Token（RT 轮换并回写）
python workbuddy_checkin.py login      # 读取本机登录态，导入 auths/<uid>.json（本地执行）
python workbuddy_checkin.py status     # 查签到状态（调试）
python workbuddy_checkin.py claim      # 仅领取签到（调试，幂等）
python workbuddy_checkin.py all        # 状态 + 领取（调试）
```

## ⚙️ 环境变量（全部可选）

| 变量 | 默认 | 说明 |
|---|---|---|
| `WORKBUDDY_BUDGET_SECONDS` | `900` | 单账号请求时间预算（秒），须小于青龙任务超时上限 |
| `RANDOM_SIGNIN` | `true` | 随机延时开关；设 `false` 关闭 |
| `MAX_RANDOM_DELAY` | `3600` | 每账号随机延时上限（秒），多账号错峰执行 |
| `WORKBUDDY_NO_SCHOOL` | 空 | 设 `true` 跳过开学季活动（活动结束后省时间） |

> **夜猫子窗口**：black_cat 任务仅在北京时间 23:00-08:00 计数，默认 cron（00:03/08:03/16:03）中
> 00:03 的那轮在窗口内；如需 23:30 加跑一轮，另建定时任务执行 `growth` 即可。

## 📢 通知

脚本目录放置青龙自带的 `notify.py` 后自动发送签到结果；未放置时仅打印到日志。
推送内容为各账号中文报告：签到结果 / 积分套餐 / 用量 / 等级连签能量 / 未完成任务分布。

## ❓ 常见问题

**Q: 提示"未找到任何凭证"？**
`auths/` 目录不存在或没有 `*.json` 文件。先在本机执行 `login`，再把 `auths/` 目录上传到脚本同级。

**Q: 日志出现"登录态已失效（HTTP 401）"或"凭证已加密"？**
桌面端刷新令牌后凭证已轮换/加密。重新执行 `login`（会自动解密新版加密凭证）并更新 `auths/` 即可。

**Q: 报"时间预算耗尽"？**
全流程含多次真实 AI 对话，单账号默认预算 900s。若日志显示大量任务"下次再跑"，属正常轮转——一天多轮 cron 会把剩余任务补完；也可调大 `WORKBUDDY_BUDGET_SECONDS`（须小于青龙超时上限）。

**Q: 旧版 `.info` 凭证还能用吗？**
不能直接识别。把 `auths/<uid>.info` 重命名为 `auths/<uid>.json` 即可（内容格式未变）。

**Q: login 提示"未找到 WorkBuddy.exe"？**
自动解密需要本机安装有桌面端（用于取出内嵌构建密钥）。确认已安装后重试，或把脚本放到装有桌面端的机器上执行 `login`。

**Q: 多账号会同时执行吗？**
并行执行（每账号独立线程），但各自先随机延时 0~3600 秒错峰；设 `RANDOM_SIGNIN=false` 可关闭。

**Q: 桌面端任务真的不用装桌面端？**
是。桌面端对话 / 尝鲜热门技能 / 开学季桌面对话通过「uid 派生稳定设备指纹 + 多域遥测上报」点亮，服务器视角等同真实桌面端使用。

## 📄 依赖

- Python 3.8+（仅标准库，无需 pip install 任何包）
- 解密环节需本机安装 WorkBuddy 桌面端（仅在 `login` 时使用，青龙运行无需）

## 🔒 免责声明

本脚本为第三方逆向脚本，与官方无关，接口随时可能失效，仅供个人学习研究。请合理使用，风险自担。

## 致谢

- [L0NE-6/WorkBuddy-Daily](https://github.com/L0NE-6/WorkBuddy-Daily) — Fork来源, 基于此项目修改

## License

[MIT](LICENSE)