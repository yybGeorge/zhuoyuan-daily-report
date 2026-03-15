"""
抖音爬虫
使用 Selenium 模拟浏览器抓取抖音数据
"""
import re
import time
import requests
from typing import List
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

from .base import BaseScraper, Post


class DouyinScraper(BaseScraper):
    """抖音爬虫"""

    def __init__(self, user_id: str, headless: bool = True, timeout: int = 30):
        super().__init__(user_id, headless, timeout)
        self.base_url = f"https://www.douyin.com/user/{user_id}"
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
        # 移动端UA
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1')
        chrome_options.add_experimental_option("mobileEmulation", {"deviceName": "iPhone 12 Pro"})

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
        """解析数字字符串"""
        if not text:
            return 0
        text = text.strip()
        if '万' in text:
            return int(float(text.replace('万', '')) * 10000)
        if '千' in text:
            return int(float(text.replace('千', '')) * 1000)
        if 'W' in text or 'w' in text:
            return int(float(re.sub(r'[Ww]', '', text)) * 10000)
        if 'K' in text or 'k' in text:
            return int(float(re.sub(r'[Kk]', '', text)) * 1000)
        try:
            return int(float(text.replace(',', '')))
        except:
            return 0

    def get_posts(self, limit: int = 20) -> List[Post]:
        """获取抖音视频"""
        posts = []

        if not self.driver:
            self._init_driver()

        if not self.driver:
            return posts

        try:
            # 访问用户主页
            self.driver.get(self.base_url)
            time.sleep(5)

            # 滚动页面加载更多内容
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

            # 获取页面内容
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            # 查找视频元素
            video_items = soup.find_all('div', class_=lambda x: x and 'video-card' in x if x else False)

            if not video_items:
                # 尝试其他选择器
                video_items = soup.find_all('div', class_=lambda x: x and 'video-info' in x if x else False)

            for item in video_items[:limit]:
                try:
                    # 获取标题/内容
                    title_elem = item.find('p', class_=lambda x: x and 'title' in x if x else False)
                    if not title_elem:
                        title_elem = item.find('div', class_=lambda x: x and 'desc' in x if x else False)
                    content = title_elem.text if title_elem else ""

                    # 获取点赞数
                    like_elem = item.find('span', class_=lambda x: x and 'like' in x if x else False)
                    likes = self._parse_number(like_elem.text) if like_elem else 0

                    # 获取评论数
                    comment_elem = item.find('span', class_=lambda x: x and 'comment' in x if x else False)
                    comments = self._parse_number(comment_elem.text) if comment_elem else 0

                    # 获取分享数
                    share_elem = item.find('span', class_=lambda x: x and 'share' in x if x else False)
                    shares = self._parse_number(share_elem.text) if share_elem else 0

                    # 获取视频封面图
                    images = []
                    img_elems = item.find_all('img')
                    for img in img_elems:
                        src = img.get_attribute('src') or img.get_attribute('data-src')
                        if src and 'http' in src:
                            images.append(src)

                    if content or images:
                        posts.append(Post(
                            platform="抖音",
                            content=content[:500] if content else "暂无描述",
                            likes=likes,
                            comments=comments,
                            shares=shares,
                            url=self.base_url,
                            images=images[:1],  # 限制图片数量
                            created_at=datetime.now(),
                            author="卓沅"
                        ))

                except Exception as e:
                    print(f"Parse douyin post error: {e}")
                    continue

        except Exception as e:
            print(f"Get douyin posts error: {e}")

        return posts

    def get_liked_posts(self, limit: int = 20) -> List[Post]:
        """获取点赞的视频"""
        return []

    def get_profile(self) -> dict:
        """获取抖音用户信息"""
        profile = {
            "nickname": "卓沅",
            "followers": 0,
            "following": 0,
            "posts": 0,
            "avatar": "",
            "bio": ""
        }

        if not self.driver:
            self._init_driver()

        if not self.driver:
            return profile

        try:
            self.driver.get(self.base_url)
            time.sleep(3)

            # 获取页面内容
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            # 获取昵称
            try:
                nickname_elem = soup.find('h1', class_=lambda x: x and 'nickname' in x if x else False)
                if not nickname_elem:
                    nickname_elem = soup.find('span', class_=lambda x: x and 'user-name' in x if x else False)
                if nickname_elem:
                    profile["nickname"] = nickname_elem.text
            except:
                pass

            # 获取粉丝数
            try:
                followers_elem = soup.find('span', class_=lambda x: x and 'follower' in x if x else False)
                if followers_elem:
                    profile["followers"] = self._parse_number(followers_elem.text)
            except:
                pass

            # 获取头像
            try:
                avatar_elem = soup.find('img', class_=lambda x: x and 'avatar' in x if x else False)
                if avatar_elem:
                    profile["avatar"] = avatar_elem.get_attribute('src') or ''
            except:
                pass

        except Exception as e:
            print(f"Get douyin profile error: {e}")

        return profile

    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            self.driver = None
