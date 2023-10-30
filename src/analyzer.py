from typing import Any

import jieba.analyse
import pytz
from dateutil.parser import parse
from loguru import logger
from lunardate import LunarDate
from snownlp import SnowNLP


# 计算文本内容情感分数
def analyze_sentiment(text):
    """
    博客文章情感分计算（有点问题，酌情使用）
    :param text:文章文本
    :return:分数
    """
    s = SnowNLP(text)
    return round(s.sentiments * 100)


def classify_and_extract_keywords(text: str, topK: int, stopwords: str,
                                  tech_terms_file: str) -> tuple[None, list[Any]] | tuple[int, Any]:
    """
    博客文章关键字提取
    :param text:文章文本
    :param topK:关键字数量，建议20个
    :param stopwords:停词文本，去掉无意义词组
    :param tech_terms_file:专业词语，区分文章类目
    :return:
    """
    try:
        jieba.analyse.set_stop_words(stopwords)
        keywords = jieba.analyse.extract_tags(text, topK=topK)
    except ValueError as e:
        logger.error(f"关键词提取出错：{e}")
        return None, []
    except ModuleNotFoundError as e:
        logger.error(f"关键词提取出错：{e}")
        return None, []

    with open(tech_terms_file, 'r', encoding='utf-8') as f:
        tech_terms_set = {line.strip().lower() for line in f}

    for keyword in keywords:
        if keyword.lower() in tech_terms_set:
            return 1, keywords

    return 2, keywords


def calculate_weight(time_str: str):
    """
    博客文章特殊日期权重分数计算。
        - 传统节假日 +10
        - 节假日 +7
        - 凌晨 +5
        - 早上 +4
        - 下午 +3
        - 晚上 +2
    :param time_str: 时间字符串
    :return:总分数，特殊日期
    """
    dt = parse(time_str)
    dt = dt.astimezone(pytz.timezone('Asia/Shanghai'))

    weight = 0
    date_str = ""

    # 农历节日权重计算
    LUNAR_HOLIDAYS = {
        (1, 1): '春节',
        (1, 15): '元宵节',
        (2, 2): '龙抬头',
        (5, 5): '端午节',
        (7, 7): '七夕节',
        (7, 15): '中元节',
        (8, 15): '中秋节',
        (9, 9): '重阳节',
        (12, 8): '腊八节',
        (12, 23): '小年',
        (12, 30): '除夕'
    }

    lunar_date = LunarDate.fromSolarDate(dt.year, dt.month, dt.day)
    if (lunar_date.month, lunar_date.day) in LUNAR_HOLIDAYS:
        weight += 10
        date_str = LUNAR_HOLIDAYS[(lunar_date.month, lunar_date.day)]

    # 公历节日权重计算
    SOLAR_HOLIDAYS = {
        (1, 1): '元旦',
        (2, 14): '情人节',
        (3, 8): '国际妇女节',
        (4, 4): '清明节',
        (5, 1): '国际劳动节',
        (10, 1): '国庆节',
        (12, 13): '南京大屠杀纪念日',
        (9, 18): '九一八事变纪念日',
        (12, 7): '南京保卫战胜利纪念日',
        (8, 15): '抗日战争胜利纪念日'
    }

    if (dt.month, dt.day) in SOLAR_HOLIDAYS:
        weight += 7
        date_str = SOLAR_HOLIDAYS[(dt.month, dt.day)]

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

    if not date_str:
        date_str = f"{dt.month}月{dt.day}日"

    return weight, date_str
