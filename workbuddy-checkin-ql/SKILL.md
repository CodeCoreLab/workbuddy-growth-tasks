---
name: workbuddy-growth-tasks
description: >
  WorkBuddy（腾讯 AI 编程助手）新手任务/成长中心全自动化 Skill。
  触发词：WorkBuddy 签到、新手任务、成长中心、积分任务、派猫猫旅行、每日签到自动化、
  workbuddy-checkin、成长值、Buddy 加油站。安装后由 Agent 按本文件驱动
  workbuddy_checkin.py 完成签到、成长任务、互动玩法与积分报告。
version: 1.0.0
author: 基于 xz0609/workbuddy-checkin-ql（MIT）封装
license: MIT
---

# WorkBuddy 新手任务全自动 Skill

> 一句话：给 Agent 一个 `workbuddy_checkin.py`，把 WorkBuddy 成长中心 35 项任务
> （33 项全自动）变成一条命令。多账号并行、Token 永续、零第三方依赖。

## 何时用本 Skill

- 每天自动签到领 100 积分（连签第 7 天 1000）
- 新账号批量点亮新手任务/成长任务（实测单号一次 +1000 积分 +40 能量）
- 查询积分余额/用量/等级
- 派猫猫旅行自动领奖、盲盒、抽奖、补签

## 安装与目录约定

```
<skill-dir>/
├── SKILL.md               # 本文件
├── workbuddy_checkin.py   # 核心脚本（单文件，仅 Python 3.8+ 标准库）
└── auths/                 # 凭证目录（一账号一文件：<uid>.json）
```

- 脚本按**自身所在目录**找 `auths/`，无需任何环境变量
- Python 3.8+，`pip install` 什么都可以不装

## Agent 执行手册

### 1. 导入凭证（本机一次性）

用户本机装有并登录 WorkBuddy 桌面端时：

```bash
python <skill-dir>/workbuddy_checkin.py login
```

脚本自动定位登录态（含 5.6.x `$wbEncrypted` 加密凭证自动解密），落盘为
`auths/<uid>.json`。多账号 = 在桌面端切换账号后重复执行，或直接拷贝多个
json 进 `auths/`。

凭证文件结构（也可手工构造，例如从账号池导出文件转换）：

```json
{
  "account": { "uid": "<uuid>", "nickname": "显示名", "email": "" },
  "auth": {
    "accessToken": "<JWT>",
    "refreshToken": "<JWT>",
    "domain": "copilot.tencent.com",
    "expiresAt": 1795257606000
  }
}
```

### 2. 日常执行（按场景选命令）

| 场景 | 命令 |
|------|------|
| 每日全流程（签到+成长+玩法+活动） | `python workbuddy_checkin.py` |
| 只跑成长任务+玩法（不签到） | `python workbuddy_checkin.py growth` |
| 只跑开学季+小程序活动 | `python workbuddy_checkin.py school` |
| 查积分/用量/等级（只读） | `python workbuddy_checkin.py query` |
| 强制刷新 Token | `python workbuddy_checkin.py refresh` |
| 调试：查签到状态 / 领签到 / 状态+领取 | `status` / `claim` / `all` |

**Agent 报告规约**：执行后用 `query` 或脚本 stdout 汇报，先结论后明细——
① 每号签到结果与积分变动 ② 新领奖任务清单（🎁 行）③ 未完成任务与需人工项
④ 异常（401/预算耗尽）原样转述。禁止打印任何 token 片段。

### 3. 定时运行（任选其一）

- **WorkBuddy 自动化**（automation_update）：rrule 建议
  `FREQ=DAILY;BYHOUR=2;BYMINUTE=10`（02:10 在夜猫子任务窗口内），prompt 写死
  「幂等，已签自动跳过，禁止重复重跑」
- **青龙面板**：命令 `task workbuddy_checkin.py`，cron `3 */8 * * *`
- **Windows 计划任务**：每日一次即可，Token 30 天内至少跑一次即永续

### 4. 环境变量（全部可选）

| 变量 | 默认 | 说明 |
|------|------|------|
| `RANDOM_SIGNIN` | `true` | 多账号随机错峰（0~3600s）。手动/调试设 `false` 立即跑 |
| `WORKBUDDY_BUDGET_SECONDS` | `900` | 单账号请求预算；全流程含真实 AI 对话，日志出现"下次再跑"属正常轮转 |
| `MAX_RANDOM_DELAY` | `3600` | 错峰上限（秒） |
| `WORKBUDDY_NO_SCHOOL` | 空 | 设 `true` 跳过开学季活动（活动结束后省时间） |

## 任务覆盖速览（35 项，33 全自动）

- **签到（1）**：daily-checkin，幂等
- **成长中心（18 项，17 自动）**：设计创意模式(+300)/探索灵感/自动化任务/桌面对话/
  热门技能/资料库/轻量云专家/召唤专家×2/和平精英主题/发现应用/GLM-5.2 对话/
  聊天5次/夜猫子(23:00-08:00)/专家团/模板5次/领取Buddy；❌公益专家（真实捐款不做）
- **互动玩法（8）**：抽奖/盲盒/Buddy 信息/派猫猫/连签兑换 7d·14d·28d/补签卡/礼包/徽章
- **开学季（5+1）**：分享/对话3次/桌面对话/召唤专家+大转盘；❌微信学生认证（需实名）
- **小程序（3）**：对话1次/校园活动/未知新任务自动适配
- 桌面任务通过「uid 派生设备指纹 + 三域遥测」无头点亮，**无需安装桌面端**

## 失败处置（Agent 必读）

| 信号 | 处置 |
|------|------|
| `未找到任何凭证` | `auths/` 缺失，先跑 `login` 或手工放 `<uid>.json` |
| `HTTP 401` / `凭证已加密` | 桌面端已轮换令牌 → 重跑 `login` 更新 auths/ |
| `时间预算耗尽` | 正常轮转，等下一轮 cron 补完；急可调大预算 |
| `login 提示未找到 WorkBuddy.exe` | 本机无桌面端，去装有桌面端的机器执行 login |
| 大面积接口报错 | 上游接口可能改版（逆向脚本，随时会失效），停止重试，如实报告 |

**铁律**：不打印/外传 accessToken；POST 写操作失败不自动重试（防重复提交）；
网络不可达只报一次；退出码 0=成功或幂等跳过，2=凭证问题，其余原样上报。

## 边界与声明

- 本 Skill 为第三方逆向实现（Fork 自 L0NE-6/WorkBuddy-Daily，感谢原作），
  与腾讯官方无关，接口随时可能变更失效，仅供个人学习研究，风险自担
- 含真实捐款（公益专家）与微信实名的任务**刻意不做**，需人工
- `auths/` 内是明文登录凭证：禁提交 Git、禁外发、禁入日志

## 实测记录（2026-10，5 账号）

- 全流程单轮 ~3.5 分钟（`RANDOM_SIGNIN=false` 时），exit=0
- 新账号首轮：每号点亮 8 项成长任务，+1000 积分 +40 能量；等级 2→13
- Token 续期自动完成，iat 起算 7 天内自动 RT 轮换回写
