from datetime import datetime
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from loguru import logger


def check_website_status(url):
    """
    检测网站是否可以正常访问，取决于 status == 200
    :param url:网址
    :return:True 可以访问，False 不可以。
    """
    try:
        response = requests.get(url, timeout=30)  # Set timeout to 5 seconds
        if response.status_code == 200:
            return True
        else:
            logger.error(f"{url} 网站无法访问,状态码:{response.status_code}")
            return False
    except requests.Timeout as e:
        logger.error(f"{url} 请求超时 30 秒,错误:{e}")
        return False
    except requests.ConnectionError as e:
        logger.error(f"{url} 连接错误,错误:{e}")
        return False
    except requests.RequestException as e:
        logger.error(f"{url} 网站无法访问,错误:{e}")
        return False
    except Exception as e:
        logger.error(f"{url} 未知错误,错误:{e}")
        return False


def get_domain(url):
    """
    获取 url 注册域名，二级域名 + 顶级域名
    :param url:url 地址
    :return:注册域名
    """
    parsed_uri = urlparse(url)
    subdomain = parsed_uri.netloc.split('.')[-2]  # 获取二级域名部分
    top_domain = parsed_uri.netloc.split('.')[-1]  # 获取顶级域名部分
    return f"{subdomain}.{top_domain}"


def get_domain_life(url):
    """
    域名注册天数
    :param url:注册域名
    :return:天数
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    domain_url = f"https://rdap.verisign.com/com/v1/domain/{url}"

    try:
        response = requests.get(domain_url, headers=headers, timeout=30)
        response.raise_for_status()  # Raises stored HTTPError, if one occurred.

        registration_date = response.json().get('events')[0].get('eventDate')
        if registration_date is None:
            logger.error("无效响应，未找到 'eventDate'")
            return None

        date_format = "%Y-%m-%dT%H:%M:%SZ"

        # 将字符串转换为日期对象
        your_date = datetime.strptime(registration_date, date_format)

        # 当前日期
        now = datetime.now()  # 使用当前日期

        # 计算天数差
        delta = now - your_date

        return delta.days

    except requests.exceptions.HTTPError as err:
        logger.error(f"HTTP 错误: {err}")
    except requests.exceptions.RequestException as err:
        logger.error(f"请求错误: {err}")
    except ValueError as err:
        logger.error(f"日期解析错误: {err}")
    except Exception as err:
        logger.error(f"未预期的错误: {err}")

    return None


def remove_html_tags(text):
    """
    移除无用 html 标签
    :param text:源文本
    :return:文本
    """
    return BeautifulSoup(text, "html.parser").get_text()


def get_yiyan():
    """
    获取一言文学语句
    :return:一言
    """
    try:
        response = requests.get("https://v1.hitokoto.cn/?c=d&min_length=12&encode=text", timeout=30)  # Set timeout to 5 seconds
        if response.status_code == 200:
            return response.text
        else:
            logger.error(f"一言网站无法访问,状态码:{response.status_code}")
            return False
    except requests.Timeout as e:
        logger.error(f"一言请求超时 30 秒,错误:{e}")
        return False
    except requests.ConnectionError as e:
        logger.error(f"一言连接错误,错误:{e}")
        return False
    except requests.RequestException as e:
        logger.error(f"一言网站无法访问,错误:{e}")
        return False
    except Exception as e:
        logger.error(f"一言未知错误,错误:{e}")
        return False