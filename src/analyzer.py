import jieba.analyse
import pytz
from dateutil.parser import parse
from loguru import logger
from lunardate import LunarDate
from snownlp import SnowNLP

from . import const


# 计算文本内容情感分数
def analyze_sentiment(keys):
    """
    博客文章情感分计算

    :param keys:文章关键字
    :return:分数
    """
    score_lists = [SnowNLP(key).sentiments for key in keys]
    all_score = sum(score_lists)

    if len(score_lists) > 10:
        max_score = max(score_lists)
        min_score = min(score_lists)
        average_score = (all_score - max_score - min_score) / (len(keys) - 2)
        return int(average_score * 1000)
    elif 10 > len(score_lists) > 6:
        average_score = all_score / len(keys)
        return int(average_score * 900)
    elif 6 > len(score_lists) > 3:
        average_score = all_score / len(keys)
        return int(average_score * 800)
    elif 3 > len(score_lists) > 0:
        average_score = all_score / len(keys)
        return int(average_score * 500)
    else:
        return 0


def extract_keywords(text,
                     topK,
                     stopwords):
    """
    文章关键字提取
    :param text:文章文本
    :param topK:关键字数量
    :param stopwords:停词文本（去掉无意义词组）
    :return:
    """
    try:
        jieba.analyse.set_stop_words(stopwords)
        keywords = jieba.analyse.extract_tags(text, topK=topK)
        return keywords
    except ValueError as e:
        logger.error(f"关键词提取出错：{e}")
        return None, []
    except ModuleNotFoundError as e:
        logger.error(f"关键词提取出错：{e}")
        return None, []


def check_category(tech_terms_file, keywords):
    """
    文章分类判断
    :param keywords: 文章关键词
    :param tech_terms_file: 分类词典文件
    :return: 分类常量
    """
    with open(tech_terms_file, 'r', encoding='utf-8') as f:
        tech_terms_set = {line.strip().lower() for line in f}  # 读取分类词典文件，将其转化为小写并创建集合

    for keyword in keywords:
        if keyword.lower() in tech_terms_set:  # 判断关键词是否在分类词典集合中
            return const.BLOG_POST_CATEGORY_TECH  # 若关键词存在，则返回技术类分类常量

    return const.BLOG_POST_CATEGORY_LIFE  # 若关键词不存在，则返回生活类分类常量


def calculate_weight(time_str: str) -> int:
    """
    计算文章特殊日期的权重分数。
    - 传统节假日 +10
    - 节假日 +7
    - 凌晨 +5
    - 早上 +4
    - 下午 +3
    - 晚上 +2

    :param time_str: 时间字符串
    :return: 总分数（整数）
    """
    dt = parse(time_str)
    dt = dt.astimezone(pytz.timezone(const.TIME_ZONE))

    weight = 0

    # 计算农历节假日的权重
    lunar_date = LunarDate.fromSolarDate(dt.year, dt.month, dt.day)
    if (lunar_date.month, lunar_date.day) in const.LUNAR_HOLIDAYS:
        weight += 10

    # 计算公历节假日的权重
    if (dt.month, dt.day) in const.SOLAR_HOLIDAYS:
        weight += 7

    # 计算时间节点的权重
    if 22 <= dt.hour or dt.hour < 7:
        weight += 5
    elif 7 <= dt.hour < 12:
        weight += 4
    elif 12 <= dt.hour < 18:
        weight += 3
    elif 18 <= dt.hour < 22:
        weight += 2
    else:
        weight += 0

    return weight


def special_date_calculation(time_str):
    """
    特殊日期计算。
    :param time_str: 时间字符串
    :return:总分数
    """
    dt = parse(time_str)
    dt = dt.astimezone(pytz.timezone(const.TIME_ZONE))

    # 农历节假日计算
    lunar_date = LunarDate.fromSolarDate(dt.year, dt.month, dt.day)
    if (lunar_date.month, lunar_date.day) in const.LUNAR_HOLIDAYS:
        return const.LUNAR_HOLIDAYS[(lunar_date.month, lunar_date.day)]

    # 公历节假日计算
    if (dt.month, dt.day) in const.SOLAR_HOLIDAYS:
        return const.SOLAR_HOLIDAYS[(dt.month, dt.day)]

    return f"{dt.month}月{dt.day}日"
