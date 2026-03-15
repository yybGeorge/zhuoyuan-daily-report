"""
卓沅每日动态报告 - 主程序
"""
import argparse
import sys
from datetime import datetime
from typing import List

from config import (
    ZHUOYUAN_WEBO_UID,
    ZHUOYUAN_XHS_UID,
    ZHUOYUAN_DOUYIN_UID,
    SMTP_SERVER,
    SMTP_PORT,
    SMTP_USERNAME,
    SMTP_PASSWORD,
    EMAIL_FROM,
    EMAIL_TO,
    HEADLESS,
    TIMEOUT,
    SCHEDULE_TIME
)
from scrapers.weibo import WeiboScraper
from scrapers.xiaohongshu import XiaohongshuScraper
from scrapers.douyin import DouyinScraper
from email_sender import EmailSender


def fetch_all_posts() -> tuple:
    """获取所有平台的帖子"""
    weibo_posts = []
    xhs_posts = []
    douyin_posts = []

    # 微博
    print("正在获取微博动态...")
    weibo = WeiboScraper(ZHUOYUAN_WEBO_UID, HEADLESS, TIMEOUT)
    try:
        weibo_posts = weibo.get_posts()
    except Exception as e:
        print(f"微博获取失败: {e}")
    finally:
        weibo.close()

    # 小红书
    print("正在获取小红书动态...")
    xhs = XiaohongshuScraper(ZHUOYUAN_XHS_UID, HEADLESS, TIMEOUT)
    try:
        xhs_posts = xhs.get_posts()
    except Exception as e:
        print(f"小红书获取失败: {e}")
    finally:
        xhs.close()

    # 抖音
    print("正在获取抖音动态...")
    douyin = DouyinScraper(ZHUOYUAN_DOUYIN_UID, HEADLESS, TIMEOUT)
    try:
        douyin_posts = douyin.get_posts()
    except Exception as e:
        print(f"抖音获取失败: {e}")
    finally:
        douyin.close()

    return weibo_posts, xhs_posts, douyin_posts


def generate_report(weibo_posts: list, xhs_posts: list, douyin_posts: list) -> str:
    """生成报告文本"""
    report = []
    report.append("=" * 50)
    report.append(f"卓沅每日动态报告 - {datetime.now().strftime('%Y年%m月%d日')}")
    report.append("=" * 50)
    report.append("")

    if weibo_posts:
        report.append(f"📱 微博 ({len(weibo_posts)}条)")
        for i, post in enumerate(weibo_posts, 1):
            report.append(f"  {i}. {post.content[:60]}...")
            report.append(f"     👍{post.likes} 💬{post.comments}")
        report.append("")

    if xhs_posts:
        report.append(f"📕 小红书 ({len(xhs_posts)}条)")
        for i, post in enumerate(xhs_posts, 1):
            report.append(f"  {i}. {post.content[:60]}...")
            report.append(f"     👍{post.likes} 💬{post.comments}")
        report.append("")

    if douyin_posts:
        report.append(f"🎵 抖音 ({len(douyin_posts)}条)")
        for i, post in enumerate(douyin_posts, 1):
            report.append(f"  {i}. {post.content[:60]}...")
            report.append(f"     ❤️{post.likes} 💬{post.comments}")
        report.append("")

    if not weibo_posts and not xhs_posts and not douyin_posts:
        report.append("今日暂无动态更新")

    return "\n".join(report)


def send_email(weibo_posts: list, xhs_posts: list, douyin_posts: list) -> bool:
    """发送邮件报告"""
    if not SMTP_USERNAME or not SMTP_PASSWORD or not EMAIL_FROM or not EMAIL_TO:
        print("邮件配置不完整，跳过发送")
        return False

    sender = EmailSender(
        smtp_server=SMTP_SERVER,
        smtp_port=SMTP_PORT,
        username=SMTP_USERNAME,
        password=SMTP_PASSWORD,
        from_email=EMAIL_FROM
    )

    subject = f"🌟 卓沅每日动态报告 - {datetime.now().strftime('%Y年%m月%d日')}"
    return sender.send_report(EMAIL_TO, subject, weibo_posts, xhs_posts, douyin_posts)


def run_schedule():
    """定时任务"""
    from apscheduler.schedulers.blocking import BlockingScheduler

    scheduler = BlockingScheduler()
    hour, minute = SCHEDULE_TIME.split(":")

    scheduler.add_job(
        main,
        'cron',
        hour=int(hour),
        minute=int(minute),
        id='daily_report'
    )

    print(f"定时任务已启动，每天 {SCHEDULE_TIME} 运行")
    scheduler.start()


def main():
    """主函数"""
    print(f"\n{'='*50}")
    print(f"开始获取卓沅每日动态 - {datetime.now()}")
    print(f"{'='*50}\n")

    # 获取数据
    weibo_posts, xhs_posts, douyin_posts = fetch_all_posts()

    # 控制台输出
    report = generate_report(weibo_posts, xhs_posts, douyin_posts)
    print("\n" + report)

    # 发送邮件
    send_email(weibo_posts, xhs_posts, douyin_posts)

    print("\n完成!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="卓沅每日动态报告")
    parser.add_argument("--schedule", action="store_true", help="启动定时任务")
    args = parser.parse_args()

    if args.schedule:
        run_schedule()
    else:
        main()
