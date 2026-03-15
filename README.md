# zyy每日动态报告

每日自动抓取zyy在微博、小红书、抖音的动态，生成图文并茂的邮件报告。

## 功能

- 自动抓取微博、小红书、抖音的公开动态
- 汇总点赞量高的帖子
- 生成图文并茂的邮件报告
- 支持手动运行和定时自动运行

## 使用方法

```bash
# 安装依赖
pip install -r requirements.txt

# 手动运行
python main.py

# 设置定时任务 (每天早上9点自动运行)
python main.py --schedule
```
