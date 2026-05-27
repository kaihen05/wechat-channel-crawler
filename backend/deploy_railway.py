#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
一键部署到 Railway（免费，公网可访问）
步骤：
1. 访问 https://railway.app 用 GitHub 登录
2. 点击 New Project → Deploy from local directory
3. 把 backend 文件夹拖进去
4. 添加环境变量 ACCESS_PASSWORD=你的密码
5. 等待部署完成，获得公网地址
"""

# 或者用命令行方式：
# 1. pip install railway
# 2. cd backend
# 3. railway init
# 4. railway up
# 5. railway variables set ACCESS_PASSWORD=你的密码
# 6. railway domain

print(__doc__)
