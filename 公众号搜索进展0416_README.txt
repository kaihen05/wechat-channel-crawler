# 公众号搜索进展0416
# 生成时间: 2026-04-16 21:11:47

## 项目概述
微信公众号渠道资源收集系统 - 用于高校社团公众号文章的定期收集和管理

## 技术栈
- 后端: Python 3.9+ / FastAPI / SQLAlchemy / httpx
- 数据库: SQLite
- 定时任务: APScheduler
- 前端: 原生HTML + TailwindCSS (CDN)
- AI: DeepSeek API (分类+学校识别)

## 已添加的公众号分类

### 游戏类 (5个高校, ~20个公众号)
- 清华、北大、浙大、上交、复旦等高校游戏/电竞社团

### 产品类 (4个公众号)
- AttraX (清华)
- 弦计划ProjectString (浙大)
- 交大创协 (上交)
- 复旦互联网联盟 (复旦)

### 技术类 (12个公众号)
- 清华: 学生网络安全技术协会、THUAGI、数据派THU
- 北大: pkuCC、学生Linux俱乐部、PKUSAA
- 浙大: 浙大网安、Room78算法竞赛社、ZJUSCT
- 上交: 0ops、交龙机器人俱乐部
- 复旦: FudanEGA电子创客社团

## 快速开始
请查看 启动指南.md，按步骤操作即可运行。

## 文件说明
- backend/app/ - 后端核心代码
- backend/.env.example - 环境变量模板
- backend/requirements.txt - Python依赖
- backend/data/channels.db - SQLite数据库 (含已收集数据)
- 启动指南.md - 新手启动步骤
- README.md - 项目详细文档
