from dataclasses import dataclass
from enum import Enum
from typing import List

@dataclass
class Site:
    """
    站点数据模型
        - service： 服务模式
        - title： 站点标题
    """
    service: int
    title: str

    def to_dict(self) -> dict:
        """
        将Site对象转换为字典形式
        """
        return {k: v if not isinstance(v, Enum) else v.value for k, v in vars(self).items()}

@dataclass
class Blog:
    """
    博客数据模型
        - name：名称
        - link：链接
        - life：域名注册天数
        - article_count：博客文章总和
        - article_word_count：博客文章字数总和
        - top_post_keys：博客关键字
        - category：博客分类
    """
    name: str
    link: str
    life: int
    article_count: int
    article_word_count: int
    top_post_keys: List[str]
    category: int

    def to_dict(self) -> dict:
        """
        将Blog对象转换为字典形式
        """
        return {k: v if not isinstance(v, Enum) else v.value for k, v in vars(self).items()}

@dataclass
class Post:
    """
    文章数据模型
        - title：标题
        - content：内容
        - keys：关键字列表
        - date：日期字符串
    """
    title: str
    content: str
    keys: List[str]
    time: str
    date: str

    def to_dict(self) -> dict:
        """
        将Post对象转换为字典形式
        """
        return {k: v if not isinstance(v, Enum) else v.value for k, v in vars(self).items()}

@dataclass
class Custom:
    """
    自定义数据模型
        - yiyan：一言
    """
    yiyan: str

    def to_dict(self) -> dict:
        """
        将Custom对象转换为字典形式
        """
        return vars(self)
