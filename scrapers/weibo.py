"""
微博爬虫
使用 Selenium 模拟浏览器抓取微博数据
"""
import re
import json
import time
import requests
from typing import List, Optional
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

from .base import BaseScraper, Post


class WeiboScraper(BaseScraper):
    """微博爬虫"""

    def __init__(self, user_id: str, headless: bool = True, timeout: int = 30):
        super().__init__(user_id, headless, timeout)
        self.base_url = f"https://m.weibo.cn/user/hotflow?uid={user_id}&page=1"
        self.pc_url = f"https://weibo.com/u/{user_id}?is_all=1"
        self.driver = None

    def _init_driver(self):
        """初始化浏览器驱动"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1')
        chrome_options.add_argument('--accept-lang=zh-CN,zh')

        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(self.timeout)
        except Exception as e:
            print(f"Chrome driver init failed: {e}")
            try:
                from selenium.webdriver.edge.service import Service as EdgeService
                from webdriver_manager.microsoft import EdgeChromiumDriverManager
                service = EdgeService(EdgeChromiumDriverManager().install())
                self.driver = webdriver.Edge(service=service, options=chrome_options)
            except:
                print("No available browser driver")

    def _parse_number(self, text: str) -> int:
        """解析数字字符串 (如 1.2万 -> 12000)"""
        if not text:
            return 0
        text = text.strip()
        if '万' in text:
            num = float(text.replace('万', '')) * 10000
            return int(num)
        if '千' in text:
            num = float(text.replace('千', '')) * 1000
            return int(num)
        try:
            return int(float(text.replace(',', '')))
        except:
            return 0

    def get_posts(self, limit: int = 20) -> List[Post]:
        """获取微博帖子 - 使用移动端API"""
        posts = []

        # 尝试使用移动端API
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
                'Referer': 'https://m.weibo.cn/'
            }
            url = f"https://m.weibo.cn/user/hotflow?uid={self.user_id}&page=1"
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get('ok') == 1 and data.get('data'):
                    for item in data['data'].get('data', [])[:limit]:
                        try:
                            content = item.get('text', '') or item.get('text_raw', '')
                            # 清理HTML标签
                            if '<!' in content:
                                soup = BeautifulSoup(content, 'html.parser')
                                content = soup.get_text()

                            posts.append(Post(
                                platform="微博",
                                content=content[:500],
                                likes=item.get('attitudes_count', 0),
                                comments=item.get('comments_count', 0),
                                shares=item.get('reposts_count', 0),
                                url=f"https://m.weibo.cn/status/{item.get('id', '')}",
                                images=[],
                                created_at=datetime.now(),
                                author="卓沅"
                            ))
                        except Exception as e:
                            continue
                return posts
        except Exception as e:
            print(f"Get weibo posts via API error: {e}")

        # 备用: 尝试使用Selenium
        if not self.driver:
            self._init_driver()

        if not self.driver:
            return posts

        try:
            # 访问移动端页面
            mobile_url = f"https://m.weibo.cn/u/{self.user_id}"
            self.driver.get(mobile_url)
            time.sleep(3)

            # 获取页面内容
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            # 尝试解析微博内容
            items = soup.find_all('div', class_='card')

            for item in items[:limit]:
                try:
                    content_elem = item.find('div', class_='weibo-text')
                    if not content_elem:
                        content_elem = item.find('span', class_='txt')
                    content = content_elem.text if content_elem else ""

                    if content:
                        posts.append(Post(
                            platform="微博",
                            content=content[:500],
                            likes=0,
                            comments=0,
                            shares=0,
                            url=self.pc_url,
                            images=[],
                            created_at=datetime.now(),
                            author="卓沅"
                        ))
                except:
                    continue

        except Exception as e:
            print(f"Get weibo posts via Selenium error: {e}")

        return posts

    def get_liked_posts(self, limit: int = 20) -> List[Post]:
        """获取点赞的微博"""
        return []

    def get_profile(self) -> dict:
        """获取微博用户信息"""
        profile = {
            "nickname": "卓沅",
            "followers": 0,
            "following": 0,
            "posts": 0,
            "avatar": "",
            "bio": ""
        }

        try:
            # 尝试使用API获取用户信息
            headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1'
            }
            url = f"https://m.weibo.cn/profile/info?uid={self.user_id}"
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get('ok') == 1 and data.get('data'):
                    user_info = data['data'].get('userInfo', {})
                    profile["nickname"] = user_info.get('screen_name', '卓沅')
                    profile["followers"] = user_info.get('followers_count', 0)
                    profile["following"] = user_info.get('follow_count', 0)
                    profile["posts"] = user_info.get('statuses_count', 0)
                    profile["avatar"] = user_info.get('profile_image_url', '')
                    profile["bio"] = user_info.get('description', '')
                    return profile
        except Exception as e:
            print(f"Get weibo profile error: {e}")

        return profile

    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            self.driver = None
