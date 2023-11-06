import configparser
import os
from urllib.parse import urlparse

from loguru import logger

from . import const
from .tools import check_website_status


class Config:
    def __init__(self, path):
        """
        初始化配置文件 config.ini
        :param path:文件路径
        """
        if not os.path.isfile(path):
            logger.error(f"配置文件 {path} 不存在或不是一个文件")
            raise FileNotFoundError

        self.path = path
        self.config = configparser.ConfigParser()

        try:
            self.config.read(self.path)
        except configparser.ParsingError as e:
            logger.error(f"解析配置文件 {self.path} 错误： {str(e)}")
            raise

        except PermissionError as e:
            logger.error(f"没有权限读取配置文件 {self.path}： {str(e)}")
            raise

    @property
    def rss_url(self):
        try:
            url = self.config.get('blog', 'rss', fallback=None)
        except configparser.NoSectionError:
            logger.error('未找到 blog 配置项，请检查拼写')
            return None

        if not url:
            logger.debug('rss 文件配置值为空，尝试读取环境变量')
            url = os.environ.get('rss')
            if url is None:
                logger.error('rss 文件配置值为空，环境变量为空……')
                return None

        # 如果网址不可访问，返回 None
        if not check_website_status(url):
            logger.error(f"rss URL {url} 不可访问")
            return None

        return url

    @property
    def rss_domain(self):
        rss_url = self.rss_url

        if rss_url is None:
            return None

        parsed = urlparse(rss_url)
        domain_parts = parsed.netloc.split('.')

        if len(domain_parts) < 2:
            logger.error(f"提供的 URL {rss_url} 的域名格式错误")
            return None

        return '.'.join(domain_parts[-2:])

    @property
    def web_status(self):
        try:
            web_status = self.config.get('default', 'web', fallback=None)
        except configparser.NoSectionError:
            logger.error('未找到 web 配置项，请检查拼写')
            return None

        if web_status is None:
            logger.error('web 配置值为空')
            return const.SITE_SERVICE_WEB

        if web_status == "True" or web_status == "true" or web_status == "t" or web_status == "T":
            return const.SITE_SERVICE_WEB

        if web_status == "False" or web_status == "false" or web_status == "f" or web_status == "F":
            return const.SITE_SERVICE_STATIC
