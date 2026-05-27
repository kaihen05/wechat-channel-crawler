"""
API 调用限制器使用示例
"""
from app.services.api_limiter import get_limiter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_basic_usage():
    """基本使用示例"""
    print("=" * 60)
    print("示例 1: 基本使用")
    print("=" * 60)
    
    # 创建限制器（保守策略）
    limiter = get_limiter("conservative")
    
    # 检查是否可以调用
    can_call, reason = limiter.can_call()
    if can_call:
        print("✅ 可以调用 API")
        
        # 执行 API 调用...
        success = True
        
        # 记录调用
        limiter.record_call(success=True)
    else:
        print(f"❌ 无法调用 API: {reason}")
    
    # 查看统计信息
    stats = limiter.get_stats()
    print(f"\n统计信息:")
    print(f"  本小时调用: {stats['hourly_calls']}/{stats['hourly_limit']}")
    print(f"  今日调用: {stats['daily_calls']}/{stats['daily_limit']}")
    print(f"  成功率: {stats['success_rate']}%")


def example_with_retry():
    """带重试的调用示例"""
    print("\n" + "=" * 60)
    print("示例 2: 带重试的调用")
    print("=" * 60)
    
    limiter = get_limiter("balanced")
    
    def call_api_with_retry(max_retries=3):
        """带重试的 API 调用"""
        for attempt in range(max_retries):
            # 检查是否可以调用
            can_call, reason = limiter.can_call()
            if not can_call:
                print(f"❌ 尝试 {attempt + 1}/{max_retries}: {reason}")
                if "限制" in reason:
                    # 达到限制，无法继续
                    break
                continue
            
            # 模拟 API 调用
            print(f"📞 尝试 {attempt + 1}/{max_retries}: 调用 API...")
            
            # 这里执行实际的 API 调用
            # result = call_wechat_api(...)
            
            # 模拟成功
            success = True
            limiter.record_call(success=success)
            
            print(f"✅ 调用成功")
            return True
        
        return False
    
    # 尝试调用
    call_api_with_retry(max_retries=3)


def example_wait_until_can_call():
    """等待直到可以调用的示例"""
    print("\n" + "=" * 60)
    print("示例 3: 等待直到可以调用")
    print("=" * 60)
    
    limiter = get_limiter("conservative")
    
    # 快速模拟多次调用
    print("模拟快速调用...")
    for i in range(25):  # 尝试调用 25 次（超过每小时限制 20 次）
        can_call, reason = limiter.can_call()
        if can_call:
            limiter.record_call(success=True)
            print(f"✅ 第 {i + 1} 次调用成功")
        else:
            print(f"⏳ 第 {i + 1} 次调用受阻: {reason}")
            if "延迟" in reason:
                import re
                delay_match = re.search(r'(\d+) 秒', reason)
                if delay_match:
                    delay = int(delay_match.group(1))
                    import time
                    time.sleep(delay)
                    continue
            else:
                break
    
    # 查看统计
    stats = limiter.get_stats()
    print(f"\n最终统计:")
    print(f"  本小时调用: {stats['hourly_calls']}/{stats['hourly_limit']}")
    print(f"  剩余额度: {stats['hourly_remaining']}")


def example_different_strategies():
    """不同策略对比"""
    print("\n" + "=" * 60)
    print("示例 4: 不同策略对比")
    print("=" * 60)
    
    strategies = ["conservative", "balanced", "aggressive"]
    
    for strategy in strategies:
        limiter = get_limiter(strategy)
        stats = limiter.get_stats()
        
        print(f"\n{strategy.upper()} 策略:")
        print(f"  每小时限制: {stats['hourly_limit']}")
        print(f"  每日限制: {stats['daily_limit']}")
        print(f"  描述: {limiter.strategy}")


def example_statistics():
    """统计信息示例"""
    print("\n" + "=" * 60)
    print("示例 5: 详细统计信息")
    print("=" * 60)
    
    limiter = get_limiter("conservative")
    
    # 模拟一些调用
    for i in range(10):
        limiter.record_call(success=(i % 3 != 0))  # 每第 3 次失败
    
    # 获取详细统计
    stats = limiter.get_stats()
    
    print("\n详细统计:")
    print(f"  策略: {stats['strategy']}")
    print(f"  本小时调用: {stats['hourly_calls']}/{stats['hourly_limit']}")
    print(f"  今日调用: {stats['daily_calls']}/{stats['daily_limit']}")
    print(f"  本小时剩余: {stats['hourly_remaining']}")
    print(f"  今日剩余: {stats['daily_remaining']}")
    print(f"  成功率: {stats['success_rate']}%")
    print(f"  总调用次数: {stats['total_calls']}")
    print(f"  预计达到限制: {stats['hours_until_limit']} 小时后")


def example_real_world_usage():
    """真实世界使用场景"""
    print("\n" + "=" * 60)
    print("示例 6: 真实世界使用场景")
    print("=" * 60)
    
    limiter = get_limiter("conservative")
    
    def update_articles(date_range):
        """更新文章阅读量"""
        begin_date, end_date = date_range
        
        # 检查是否可以调用
        can_call, reason = limiter.can_call()
        if not can_call:
            logger.warning(f"无法更新文章: {reason}")
            return False
        
        logger.info(f"开始更新文章 {begin_date} - {end_date}")
        
        # 这里调用实际的更新逻辑
        # result = wechat_api.get_article_read_stats(...)
        
        # 模拟成功
        success = True
        limiter.record_call(success=success)
        
        if success:
            logger.info(f"文章更新成功")
        else:
            logger.error(f"文章更新失败")
        
        return success
    
    # 模拟日常更新计划
    update_schedule = [
        ("20260401", "20260407", "周度报告"),
        ("20260408", "20260414", "周度报告"),
        ("20260415", "20260415", "今日更新"),
    ]
    
    print("\n执行更新计划:")
    for begin, end, task in update_schedule:
        print(f"\n任务: {task} ({begin} - {end})")
        result = update_articles((begin, end))
        if result:
            print(f"  ✅ 完成")
        else:
            print(f"  ❌ 跳过")
        
        # 查看当前状态
        stats = limiter.get_stats()
        print(f"  已使用: {stats['daily_calls']}/{stats['daily_limit']}")
        print(f"  剩余: {stats['daily_remaining']}")
        
        # 延迟，避免连续调用
        import time
        time.sleep(1)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("API 调用限制器使用示例")
    print("=" * 60)
    
    # 运行所有示例
    example_basic_usage()
    example_with_retry()
    example_wait_until_can_call()
    example_different_strategies()
    example_statistics()
    example_real_world_usage()
    
    print("\n" + "=" * 60)
    print("所有示例运行完成！")
    print("=" * 60)
