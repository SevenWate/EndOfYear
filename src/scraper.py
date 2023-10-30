import feedparser
from loguru import logger

from . import tools


class Blog:
    def __init__(self, url):
        try:
            self.feed = feedparser.parse(url)
        except Exception as e:
            logger.error(f'解析 RSS feed 时发生错误： {str(e)}')
            raise
        self.posts = [Post(entry) for entry in self.feed.entries]

    def _get_feed_field(self, field):
        """
        从 RSS feed 中获取特定字段
        """
        field_value = self.feed.feed.get(field)
        if field_value is None:
            logger.warning(f'{field} 字段不存在！')
        return field_value

    @property
    def title(self):
        return self._get_feed_field('title')

    @property
    def link(self):
        return self._get_feed_field('link')

    @property
    def life(self):
        domain = tools.get_domain(self.link)
        return tools.get_domain_life(domain)

    @property
    def article_count(self):
        return len(self.posts)

    @property
    def article_word_count(self):
        return sum(post.word_count for post in self.posts)

    def post_lists(self):
        return self.posts

    def __str__(self):
        return f"Blog: {self.title}, Life:{self.life}, Count{self.article_count}. Word count:{self.article_word_count}"


class Post:
    def __init__(self, entry):
        # 日期权重
        self._weight = None
        # 日子
        self._date = None
        # 情感分
        self._score = None
        # 关键字
        self._keys = None
        # 分类
        self._category = None
        self.entry = entry

    def _get_entry_field(self, field):
        """
        从 RSS entry 中获取特定字段
        """
        field_value = self.entry.get(field)
        if field_value is None:
            pass
            # logger.warning(f'{field} 字段不存在！')
        return field_value

    @property
    def title(self):
        return self._get_entry_field('title')

    @property
    def content(self):
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
    def time(self):
        return self._get_entry_field('published')

    @property
    def link(self):
        return self._get_entry_field('link')

    @property
    def word_count(self):
        return len(self.content) if self.content else 0

    @property
    def keys(self):
        return self._keys

    @keys.setter
    def keys(self, value):
        self._keys = value

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        self._score = value

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        self._category = value

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value):
        self._date = value

    @property
    def weight(self):
        return self._weight

    @weight.setter
    def weight(self, value):
        self._weight = value

    def __str__(self):
        return (f"Post title={self.title[:20]}..., "
                f" content={self.content[:20]}..., "
                f" time={self.time}, "
                f" link={self.link}, "
                f" word_count={self.word_count}")
