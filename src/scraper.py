import re
from collections import Counter

import feedparser
from loguru import logger

from . import analyzer
from . import const
from . import tools


class Blog:
    def __init__(self, rss):
        try:
            # 解析RSS feed
            self._feed = feedparser.parse(rss)
            # 解析feed中的所有文章
            self._posts = [Post(entry) for entry in self._feed.entries]
        except Exception as e:
            logger.error(f'Feedparser 解析 RSS feed 时发生错误： {str(e)}')
            raise

    def _get_feed_field(self, field):
        if field_value := self._feed.feed.get(field):
            return field_value
        logger.warning(f'Feedparser {field} 字段不存在！')
        return ""

    @property
    def title(self):
        # 获取RSS feed的标题
        return self._feed.feed.get('title')

    @property
    def link(self):
        # 获取RSS feed的链接
        return self._feed.feed.get('link')

    @property
    def life(self):
        # 获取RSS feed链接的域名存活时间
        return tools.get_domain_life(self.link)

    @property
    def article_count(self):
        # 获取文章数量
        return len(self._posts) if self._posts else 0

    @property
    def article_word_count(self):
        # 获取文章总字数
        return sum(post.word_count for post in self._posts) if self._posts else 0

    @property
    def keys(self):
        if self._posts:
            # 提取所有关键字
            all_keys = [key for post in self._posts for key in post.keys]

            # 过滤出中文关键字
            chinese_keys = [key for key in all_keys if re.search(r'[\u4e00-\u9fff]+', key)]

            # 计算关键字出现的次数
            keyword_counts = Counter(chinese_keys)

            # 提取出现次数最多的关键字
            top_keywords = keyword_counts.most_common(const.BLOG_MAX_KEYS)

            return top_keywords

        return []

    @property
    def category(self):
        # 获取博客的分类
        if self._posts:
            # 如果博客有帖子
            categories = [post.category for post in self._posts]
            # 获取所有帖子的分类
            cat_counts = Counter(categories)
            # 统计每个分类的个数
            most_common_cat = cat_counts.most_common(1)[0][0]
            # 获取出现次数最多的分类
            return most_common_cat
        # 如果博客没有帖子
        return const.BLOG_POST_CATEGORY_LIFE

    @property
    def post_lists(self):
        # 获取文章列表
        return self._posts if self._posts else []

    def __str__(self):
        return f"""
                博客： {self.title}
                链接： {self.link}
                时间： {self.life} 天
                文章： {self.article_count} 篇
                字数： {self.article_word_count} 个
                分类： {self.category}
                关键字： {self.keys}
            """


class Post:
    def __init__(self, entry):
        self.entry = entry
        # 文章内容
        self._content = self._get_content()
        # 文章时间
        self._time = tools.format_datetime(self._get_entry_field('published'))
        # 文章日期
        self._date = analyzer.special_date_calculation(self._time)
        # 特殊日期分
        self._special_date_score = analyzer.calculate_weight(self._get_entry_field('published'))
        # 关键字
        self._keys = analyzer.extract_keywords(text=self._content,
                                               topK=tools.get_multiple_of_100(self._content),
                                               stopwords='data/stop_words.txt')
        # 文章情感分
        self._sentiment_score = analyzer.analyze_sentiment(self._keys)
        # 分类
        self._category = analyzer.check_category(tech_terms_file='data/tech_terms.txt', keywords=self._keys)

    def _get_entry_field(self, field):
        return self.entry.get(field)

    def _get_content(self):
        """
           获取文章内容。
        :return: 文章的描述或内容，根据以下规则：
        - 如果'content'字段存在，那么返回'content'字段的值。
        - 如果'description'字段的长度小于128，并且'content'字段存在，那么返回'content'字段的值。
        - 否则，返回'description'字段的值。
        - 如果'description'和'content'字段都不存在，返回空字符串。
        """
        description = self._get_entry_field('description')
        content = self._get_entry_field('content')
        if content:
            content = content[0].get('value', '')

        description = tools.remove_html_tags(description) if description else ""
        content = tools.remove_html_tags(content) if content else ""

        if len(description) < 128 and content:
            return content
        else:
            return description

    @property
    def title(self):
        # 获取文章标题
        return self._get_entry_field('title')

    @property
    def content(self):
        # 获取文章内容
        return self._content

    @property
    def word_count(self):
        # 获取文章字数
        return len(self.content) if self.content else 0

    @property
    def time(self):
        # 获取文章时间
        return self._time

    @property
    def date(self):
        # 获取日期分
        return self._date

    @property
    def link(self):
        # 获取文章链接
        return self._get_entry_field('link')

    @property
    def keys(self):
        # 获取文章关键字
        return self._keys

    @property
    def category(self):
        # 获取文章分类
        return self._category

    @property
    def special_date_score(self):
        # 获取特殊日期分
        return self._special_date_score

    @property
    def sentiment_score(self):
        # 获取文章情感分
        return self._sentiment_score

    def __str__(self):
        return (f" 标题：{self.title}, "
                f" 内容：{self.content[:20]}..., "
                f" 时间：{self.time}, "
                f" 链接：{self.link}, "
                f" 日期分：{self.special_date_score}"
                f" 情感分：{self.sentiment_score}"
                f" 类目：{self.category}"
                f" 关键字：{self.keys}")
