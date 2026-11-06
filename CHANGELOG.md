# 变更日志 — 成长任务自动化（growth-tasks）

本文件记录本项目的变更。

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [未发布]

## [1.0.1] - 2026-11-06
### 安全

- **凭据缓存文件权限收紧**：为保持「单文件零依赖」约定，内联实现受限权限设置
- **设备私钥 PEM 与多账号 token 不再打印到 stdout**
## [1.0.0] - 2026-10-30

### 新增

- 产品介绍页上线：首屏、产品亮点、核心功能、用户价值、快速开始、页脚六个内容块
- 粒子背景：canvas 层置于内容之下，密度按面积与设备能力自适应；FPS 低于 45 连续两轮自动降档（1 → 0.6 → 0.3 → 停用）
- 下载入口：页面内直接获取 `workbuddy-growth-tasks.zip`，无需跳转
- 本页 changelog：站点巡检要求的版本记录页

### 安全

- 分发包**剔除** `auths/` 内全部真实登录凭证，仅保留空目录；使用前须在本机执行 `python workbuddy_checkin.py login` 生成
- 凭证只认 `auths/<uid>.json` 文件，不读任何 Token 环境变量；`.gitignore` 已排除 `auths/*`

### 变更

- 说明：工具本体为第三方逆向实现（Fork 自 L0NE-6/WorkBuddy-Daily，MIT），与腾讯官方无关
- 说明：覆盖 35 项任务、33 项全自动；刻意不做公益专家（涉及真实捐款）与微信学生认证（需实名）
- 说明：单文件 Python 3.8+，仅标准库，无第三方依赖