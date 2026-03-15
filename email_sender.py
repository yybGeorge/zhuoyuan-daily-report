"""
邮件发送模块
生成图文并茂的HTML邮件报告
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from typing import List
from datetime import datetime
from jinja2 import Template

from scrapers.base import Post


# HTML 邮件模板
EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }
        .header h1 { margin: 0; font-size: 24px; }
        .header p { margin: 10px 0 0; opacity: 0.9; }
        .platform-section { padding: 20px; border-bottom: 1px solid #eee; }
        .platform-header { display: flex; align-items: center; margin-bottom: 15px; }
        .platform-icon { width: 32px; height: 32px; border-radius: 8px; margin-right: 12px; display: flex; align-items: center; justify-content: center; font-size: 18px; }
        .platform-name { font-size: 18px; font-weight: 600; }
        .post-card { background: #f9f9f9; border-radius: 8px; padding: 15px; margin-bottom: 12px; }
        .post-content { margin-bottom: 10px; line-height: 1.5; }
        .post-stats { display: flex; gap: 15px; color: #666; font-size: 13px; }
        .post-stats span { display: flex; align-items: center; gap: 4px; }
        .post-images { display: flex; gap: 8px; margin-top: 10px; flex-wrap: wrap; }
        .post-images img { width: 120px; height: 120px; object-fit: cover; border-radius: 6px; }
        .footer { padding: 20px; text-align: center; color: #999; font-size: 12px; }
        .no-data { text-align: center; padding: 30px; color: #999; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌟 卓沅每日动态报告</h1>
            <p>{{ date }}</p>
        </div>

        {% if weibo_posts %}
        <div class="platform-section">
            <div class="platform-header">
                <div class="platform-icon" style="background: #FF8202; color: white;">微博</div>
                <span class="platform-name">微博动态</span>
            </div>
            {% for post in weibo_posts %}
            <div class="post-card">
                <div class="post-content">{{ post.content }}</div>
                <div class="post-stats">
                    <span>👍 {{ post.likes }}</span>
                    <span>💬 {{ post.comments }}</span>
                    <span>🔄 {{ post.shares }}</span>
                </div>
                {% if post.images %}
                <div class="post-images">
                    {% for img in post.images %}
                    <img src="{{ img }}" alt="图片">
                    {% endfor %}
                </div>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        {% endif %}

        {% if xhs_posts %}
        <div class="platform-section">
            <div class="platform-header">
                <div class="platform-icon" style="background: #FF2442; color: white;">小红书</div>
                <span class="platform-name">小红书笔记</span>
            </div>
            {% for post in xhs_posts %}
            <div class="post-card">
                <div class="post-content">{{ post.content }}</div>
                <div class="post-stats">
                    <span>👍 {{ post.likes }}</span>
                    <span>💬 {{ post.comments }}</span>
                    <span>⭐ {{ post.shares }}</span>
                </div>
                {% if post.images %}
                <div class="post-images">
                    {% for img in post.images %}
                    <img src="{{ img }}" alt="图片">
                    {% endfor %}
                </div>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        {% endif %}

        {% if douyin_posts %}
        <div class="platform-section">
            <div class="platform-header">
                <div class="platform-icon" style="background: #1E1E1E; color: white;">抖音</div>
                <span class="platform-name">抖音视频</span>
            </div>
            {% for post in douyin_posts %}
            <div class="post-card">
                <div class="post-content">{{ post.content }}</div>
                <div class="post-stats">
                    <span>❤️ {{ post.likes }}</span>
                    <span>💬 {{ post.comments }}</span>
                    <span>▶️ {{ post.shares }}</span>
                </div>
            </div>
            {% endfor %}
        </div>
        {% endif %}

        {% if not weibo_posts and not xhs_posts and not douyin_posts %}
        <div class="no-data">
            <p>今日暂无动态更新</p>
        </div>
        {% endif %}

        <div class="footer">
            <p>由 自动脚本 生成 | {{ timestamp }}</p>
        </div>
    </div>
</body>
</html>
"""


class EmailSender:
    """邮件发送器"""

    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str, from_email: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email

    def send_report(
        self,
        to_email: str,
        subject: str,
        weibo_posts: List[Post],
        xhs_posts: List[Post],
        douyin_posts: List[Post]
    ) -> bool:
        """发送每日报告邮件"""
        try:
            # 渲染 HTML
            template = Template(EMAIL_TEMPLATE)
            html_content = template.render(
                date=datetime.now().strftime("%Y年%m月%d日"),
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                weibo_posts=weibo_posts,
                xhs_posts=xhs_posts,
                douyin_posts=douyin_posts
            )

            # 创建邮件
            msg = MIMEMultipart('related')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject

            # 添加 HTML 内容
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))

            # 发送邮件
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            print(f"邮件发送成功: {subject}")
            return True

        except Exception as e:
            print(f"邮件发送失败: {e}")
            return False
