import os
from dotenv import load_dotenv

load_dotenv()

# 卓沅的社交媒体账号ID (需要根据实际页面获取)
ZHUOYUAN_WEBO_UID = os.getenv("ZHUOYUAN_WEBO_UID", "1234567890")
ZHUOYUAN_XHS_UID = os.getenv("ZHUOYUAN_XHS_UID", "zhuoyuan")
ZHUOYUAN_DOUYIN_UID = os.getenv("ZHUOYUAN_DOUYIN_UID", "zhuoyuan")

# 邮件配置
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "")
EMAIL_TO = os.getenv("EMAIL_TO", "")

# 爬虫配置
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
TIMEOUT = int(os.getenv("TIMEOUT", "30"))

# 定时任务配置
SCHEDULE_TIME = os.getenv("SCHEDULE_TIME", "09:00")
