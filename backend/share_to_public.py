#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
使用 ngrok 内网穿透，让别人也能访问你的本地网站
使用方法：
1. pip install pyngrok
2. python share_to_public.py
3. 终端会显示一个公网网址，发给朋友即可
"""

import subprocess
import sys
import os

def main():
    print("=" * 60)
    print("  公众号聚合器 - 内网穿透工具")
    print("=" * 60)
    print()
    
    # 检查是否安装 pyngrok
    try:
        import pyngrok
    except ImportError:
        print("[1/2] 安装 pyngrok...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyngrok", "--quiet"])
        print("      安装完成！")
    
    print()
    print("[2/2] 启动内网穿透（映射 localhost:8000）...")
    print()
    print("⚠️  请确保你的服务已经在运行（另一个终端执行 python run.py）")
    print()
    
    from pyngrok import ngrok
    
    # 打开隧道
    public_url = ngrok.connect(8000)
    
    print("=" * 60)
    print("  ✅ 隧道已建立！")
    print()
    print(f"  🌐 公网地址: {public_url}")
    print()
    print("  把这个网址发给朋友，他们就能访问了！")
    print("  按 Ctrl+C 关闭隧道")
    print("=" * 60)
    
    try:
        # 保持运行
        from pyngrok import ngrok as _ngrok
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n隧道已关闭")
        ngrok.disconnect(public_url)


if __name__ == "__main__":
    main()
