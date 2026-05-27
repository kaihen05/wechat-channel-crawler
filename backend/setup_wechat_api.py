"""
快速配置微信 API 凭证脚本
"""
import os
from pathlib import Path

def setup_wechat_api():
    """设置微信 API 凭证"""
    
    print("=" * 60)
    print("微信 API 凭证配置向导")
    print("=" * 60)
    print()
    
    backend_dir = Path(__file__).parent
    env_file = backend_dir / ".env"
    
    # 检查是否存在 .env 文件
    if env_file.exists():
        print(f"发现现有 .env 文件: {env_file}")
        choice = input("是否要更新现有配置？(y/n): ").strip().lower()
        if choice != 'y':
            print("已取消配置")
            return
    
    print("\n请输入你的微信 API 凭证：")
    print("=" * 60)
    
    # 获取 AppID
    print("\n步骤 1: 输入 AppID")
    print("  - 格式: wx 开头的 16 位字符")
    print("  - 示例: wx1234567890abcdef")
    print("  - 获取方式: 登录微信公众平台 -> 设置与开发 -> 基本配置")
    appid = input("\n请输入 AppID: ").strip()
    
    # 验证 AppID 格式
    if not appid.startswith("wx") or len(appid) != 18:
        print("\n⚠️  警告: AppID 格式可能不正确")
        print("  正确格式应该是 wx 开头，后面跟 16 位字符（共 18 位）")
        choice = input("  是否继续？(y/n): ").strip().lower()
        if choice != 'y':
            print("已取消配置")
            return
    
    # 获取 AppSecret
    print("\n步骤 2: 输入 AppSecret")
    print("  - 格式: 32 位字符")
    print("  - 示例: 1234567890abcdefghijklmnopqrstuvwxyz")
    print("  - 获取方式: 登录微信公众平台 -> 设置与开发 -> 基本配置")
    print("  - ⚠️  重要: AppSecret 只显示一次，请妥善保管")
    appsecret = input("\n请输入 AppSecret: ").strip()
    
    # 验证 AppSecret 格式
    if len(appsecret) != 32:
        print("\n⚠️  警告: AppSecret 格式可能不正确")
        print("  正确格式应该是 32 位字符")
        choice = input("  是否继续？(y/n): ").strip().lower()
        if choice != 'y':
            print("已取消配置")
            return
    
    # 确认配置
    print("\n" + "=" * 60)
    print("请确认你的配置：")
    print("=" * 60)
    print(f"AppID: {appid}")
    print(f"AppSecret: {appsecret[:4]}...{appsecret[-4:]}")  # 只显示部分
    print("\n⚠️  重要提醒:")
    print("  - AppSecret 是敏感信息，请妥善保管")
    print("  - 不要分享给他人")
    print("  - 不要提交到代码仓库")
    
    choice = input("\n确认配置是否正确？(y/n): ").strip().lower()
    if choice != 'y':
        print("已取消配置")
        return
    
    # 创建或更新 .env 文件
    print("\n正在写入配置...")
    
    # 读取现有内容（如果存在）
    existing_content = ""
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            existing_content = f.read()
    
    # 检查是否已经配置了微信 API
    lines = existing_content.split('\n')
    new_lines = []
    has_appid = False
    has_appsecret = False
    
    for line in lines:
        if line.startswith('WECHAT_APPID='):
            new_lines.append(f'WECHAT_APPID={appid}')
            has_appid = True
        elif line.startswith('WECHAT_APPSECRET='):
            new_lines.append(f'WECHAT_APPSECRET={appsecret}')
            has_appsecret = True
        else:
            new_lines.append(line)
    
    # 如果没有找到配置，添加到文件末尾
    if not has_appid or not has_appsecret:
        if new_lines and new_lines[-1]:  # 如果最后一行不为空，添加空行
            new_lines.append('')
        if not has_appid:
            new_lines.append('WECHAT_APPID=' + appid)
        if not has_appsecret:
            new_lines.append('WECHAT_APPSECRET=' + appsecret)
    
    # 写入文件
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print("✅ 配置已保存到:", env_file)
    
    # 验证配置
    print("\n正在验证配置...")
    try:
        os.environ['WECHAT_APPID'] = appid
        os.environ['WECHAT_APPSECRET'] = appsecret
        
        from app.config import settings
        
        if settings.wechat_appid == appid and settings.wechat_appsecret == appsecret:
            print("✅ 配置验证成功！")
        else:
            print("⚠️  警告: 配置可能未生效")
            print(f"  期望 AppID: {appid}")
            print(f"  实际 AppID: {settings.wechat_appid}")
    except Exception as e:
        print(f"⚠️  警告: 验证时出错: {e}")
    
    # 提示重启服务器
    print("\n" + "=" * 60)
    print("配置完成！")
    print("=" * 60)
    print("\n下一步:")
    print("1. 重启服务器（必须）")
    print("   停止当前服务器（Ctrl + C）")
    print("   重新运行: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
    print()
    print("2. 运行测试脚本")
    print("   python test_wechat_api.py")
    print()
    print("3. 通过 Web 界面使用")
    print("   访问 http://localhost:8000/manage.html")
    print("   使用「通过微信 API 更新阅读量」功能")
    print()
    print("=" * 60)


def check_config():
    """检查当前配置"""
    print("\n" + "=" * 60)
    print("检查当前配置")
    print("=" * 60)
    
    backend_dir = Path(__file__).parent
    env_file = backend_dir / ".env"
    
    if not env_file.exists():
        print("\n❌ .env 文件不存在")
        print(f"   位置: {env_file}")
        print("\n请运行:")
        print("   python setup_wechat_api.py")
        return
    
    print(f"\n✅ .env 文件存在: {env_file}")
    
    # 读取配置
    import re
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查配置
    appid_match = re.search(r'WECHAT_APPID=([^\s]+)', content)
    appsecret_match = re.search(r'WECHAT_APPSECRET=([^\s]+)', content)
    
    if appid_match:
        appid = appid_match.group(1)
        print(f"\n✅ WECHAT_APPID 已配置: {appid}")
    else:
        print(f"\n❌ WECHAT_APPID 未配置")
    
    if appsecret_match:
        appsecret = appsecret_match.group(1)
        print(f"✅ WECHAT_APPSECRET 已配置: {appsecret[:4]}...{appsecret[-4:]}")
    else:
        print(f"❌ WECHAT_APPSECRET 未配置")
    
    # 尝试加载配置
    print("\n正在加载配置...")
    try:
        from app.config import settings
        
        if settings.wechat_appid:
            print(f"✅ 成功加载 AppID: {settings.wechat_appid}")
        else:
            print("❌ AppID 加载失败（为空）")
        
        if settings.wechat_appsecret:
            print(f"✅ 成功加载 AppSecret: {settings.wechat_appsecret[:4]}...{settings.wechat_appsecret[-4:]}")
        else:
            print("❌ AppSecret 加载失败（为空）")
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        check_config()
    else:
        setup_wechat_api()
