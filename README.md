# 🚪 DOOR Studio — A Doorway to AI

**door / dɔːr/ — 每一扇门背后，都是一个新世界。**
Every door opens into a new world.

DOOR Studio 是一个由工程师驱动的 AI 产品工作室。我们不是在做"另一个工具"，而是在搭建一套自洽的 AI 生态——从身份、云盘、支付，到 AI 能力、游戏平台与安全底座，所有服务彼此联通，共用一套账号、一套密钥、一套架构。

DOOR Studio is an engineer-driven AI product studio. We are not building "yet another tool" — we are building a self-contained AI ecosystem: identity, cloud drive, payments, AI capabilities, game platform and a security foundation — all interconnected, sharing one account system, one key system, and one architecture.

---

## 🌟 生态全景 · Ecosystem Overview

```
                    ┌─────────────────────────────┐
                    │        DOOR 账号中心         │
                    │    DOOR Unified Identity    │
                    └──────────────┬──────────────┘
                                   │ 一套账号 · 一处登录
              ┌────────────────────┼────────────────────┐
              ▼                    ▼                    ▼
   ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
   │  DOOR AI         │  │  DOOR 云盘       │  │  DOOR 支付       │
   │  AI API 控制台    │  │  Cloud Drive     │  │  Payments        │
   └──────────────────┘  └──────────────────┘  └──────────────────┘
              ┌────────────────────┼────────────────────┐
              ▼                    ▼                    ▼
   ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
   │  DOOR 工作台      │  │  DOOR 主机       │  │  DOOR 安全中心    │
   │  Workbench        │  │  Hosting         │  │  Security        │
   └──────────────────┘  └──────────────────┘  └──────────────────┘
```

## 🧩 服务矩阵 · Service Matrix

| 服务 Service | 定位 Positioning | 域名 Domain |
|---|---|---|
| **DOOR 账号中心** | 统一身份与注册 Unified Identity | `door-register.pages.dev` |
| **DOOR AI** | AI API 控制台 · 密钥 · 模型 | `door-ai.pages.dev` |
| **DOOR 云盘** | 文件存储与分享 Cloud Drive | `door-drive.pages.dev` |
| **DOOR 支付** | 计费与交易 Payments | `door-pay.pages.dev` |
| **DOOR 工作台** | 工程工作台 Workbench | `door-workbench.pages.dev` |
| **DOOR 主机** | 站点托管 Hosting | `door-host.pages.dev` |
| **DOOR 安全中心** | 账号安全 Security Center | `door-safe.pages.dev` |
| **DOOR 游戏平台** | 游戏服务 Game Platform | `door-game-platform.pages.dev` |
| **DOOR 搜索** | 自建垂直搜索 Vertical Search | `door-search` |

## 🛠 基础设施 · Infrastructure

DOOR 生态建立在 **Cloudflare** 之上，做到全球边缘就近响应、天然高可用：

| 层 Layer | 技术 Technology | 说明 Notes |
|---|---|---|
| **前端 Frontend** | Cloudflare Pages | 所有站点静态托管，全球 CDN |
| **后端 Backend** | Cloudflare Workers | 无服务器函数，边缘计算 |
| **数据库 Database** | Cloudflare D1 | SQLite 兼容，结构化数据 |
| **缓存/会话 Cache** | Cloudflare KV | 全局键值存储，会话与文件 |

## 🧠 核心项目 · Core Projects

### DOOR Search — 自建垂直搜索引擎
不依赖第三方搜索，自己抓取、自己索引、自己排序。面向中文互联网，做真正"搜得到"的垂直搜索。

> Built our own crawler, indexer and ranker. A vertical search engine for the Chinese web that actually finds what you're looking for.

### DOOR AI — AI API 控制台
统一接入多模型，提供密钥管理、用量计量与充值体系。让 AI 能力像水电一样即开即用。

> A unified gateway to multiple AI models — key management, usage metering, and billing. AI capability, on tap.

### DOOR Core — 核心服务底座
账号、鉴权、密钥、限流等公共能力抽成一套核心服务，所有 door 子站复用，一处治理、全局生效。

> Account, auth, keys and rate-limiting as one shared core. One governance, applied everywhere.

---

## 🔐 安全 · Security

- 全站 HTTPS，边缘防 DDoS
- 密钥中心化管理，敏感令牌独立存放
- 安全中心提供账号防护与异常告警

## 📌 路线图 · Roadmap

- [ ] 开放公共 API 文档
- [ ] DOOR 应用市场
- [ ] 多语言站点支持
- [ ] 社区与贡献者计划

---

## 📄 License

© 2026 DOOR Studio. All rights reserved.
