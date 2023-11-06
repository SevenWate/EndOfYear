from functools import lru_cache

from loguru import logger

from . import models
from . import scraper


@lru_cache(maxsize=None)
class Generator:

    def __init__(self, rss):
        """
        初始化Generator类
        :param rss: RSS链接
        """
        try:
            self._my_blog = scraper.Blog(rss)
            logger.debug(self._my_blog)
            for i, post in enumerate(self._my_blog.post_lists, 1):
                logger.info(f"Post #{i}:")
                logger.info(post)
        except Exception as e:
            logger.error(f"Generator 无法创建 Blog 对象: {str(e)}")

    def blog(self):
        """
        获取博客信息
        :return: Blog字典
        """
        return models.Blog(
            name=self._my_blog.title,
            link=self._my_blog.link,
            life=self._my_blog.life,
            article_count=self._my_blog.article_count,
            article_word_count=self._my_blog.article_word_count,
            top_post_keys=self._my_blog.keys,
            category=self._my_blog.category
        ).to_dict()

    def special_post(self):
        """
        获取特殊日期的文章
        :return: Post字典
        """
        max_item_special_date = self._get_post_with_max("special_date_score")
        return models.Post(
            title=max_item_special_date.title,
            content=max_item_special_date.content,
            keys=max_item_special_date.keys,
            time=max_item_special_date.time,
            date=max_item_special_date.date
        ).to_dict()

    def sentiment_post(self):
        """
        获取情感最优文章
        :return: Post字典
        """
        max_item_sentiment = self._get_post_with_max("sentiment_score")
        return models.Post(
            title=max_item_sentiment.title,
            content=max_item_sentiment.content,
            keys=max_item_sentiment.keys,
            time=max_item_sentiment.time,
            date=max_item_sentiment.date
        ).to_dict()

    def long_post(self):
        """
        获取最长文章数据
        :return: Post字典
        """
        max_item_long = self._get_post_with_max("word_count")
        return models.Post(
            title=max_item_long.title,
            content=max_item_long.content,
            keys=max_item_long.keys,
            time=max_item_long.time,
            date=max_item_long.date,
        ).to_dict()

    def short_post(self):
        """
        获取最短文章数据
        :return: Post字典
        """
        max_item_short = self._get_post_with_min("word_count")
        return models.Post(
            title=max_item_short.title,
            content=max_item_short.content,
            keys=max_item_short.keys,
            time=max_item_short.time,
            date=max_item_short.date,
        ).to_dict()

    def _get_post_with_max(self, score_attr):
        """
        获取具有最大属性值的文章
        :param score_attr: 属性
        :return:
        """
        max_score = max(getattr(post, score_attr) for post in self._my_blog.post_lists)
        max_posts = [post for post in self._my_blog.post_lists if getattr(post, score_attr) == max_score]
        if max_posts:
            return max_posts[0]
        return None

    def _get_post_with_min(self, score_attr):
        """
        获取具有最小属性值的文章
        :param score_attr:
        :return:
        """
        min_score = min(getattr(post, score_attr) for post in self._my_blog.post_lists)
        min_posts = [post for post in self._my_blog.post_lists if getattr(post, score_attr) == min_score]
        if min_posts:
            return min_posts[0]
        return None
