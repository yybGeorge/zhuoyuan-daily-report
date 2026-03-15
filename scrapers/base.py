"""
社交媒体爬虫基类
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class Post:
    """帖子数据模型"""
    platform: str
    content: str
    likes: int
    comments: int
    shares: int
    url: str
    images: List[str]
    created_at: datetime
    author: str

    def __str__(self):
        return f"[{self.platform}] {self.content[:50]}... (👍{self.likes})"


class BaseScraper(ABC):
    """爬虫基类"""

    def __init__(self, user_id: str, headless: bool = True, timeout: int = 30):
        self.user_id = user_id
        self.headless = headless
        self.timeout = timeout

    @abstractmethod
    def get_posts(self, limit: int = 20) -> List[Post]:
        """获取用户发布的帖子"""
        pass

    @abstractmethod
    def get_liked_posts(self, limit: int = 20) -> List[Post]:
        """获取用户点赞的帖子"""
        pass

    @abstractmethod
    def get_profile(self) -> dict:
        """获取用户基本信息"""
        pass

    def close(self):
        """关闭爬虫资源"""
        pass
