from collections import Counter

from loguru import logger

from .analyzer import analyze_sentiment, calculate_weight, classify_and_extract_keywords
from .config import Config
from .scraper import Blog
from .tools import get_yiyan


def build_data():
    """
    目前只有一个主题，构建数据部分后期会再进行重构拆分
    :return: 网页渲染数据
    """
    # 读取配置
    config = Config("config.ini")

    # 创建博客对象
    try:
        my_blog = Blog(config.rss_url)
    except Exception as e:
        logger.error(f"Feed 无法创建博客对象: {str(e)}")
        return None

    logger.debug(my_blog)

    # 构建博客基本数据
    data = {
        "blog_name": my_blog.title,
        "blog_link": my_blog.link,
        "blog_article_count": my_blog.article_count,
        "blog_article_word_count": my_blog.article_word_count,
        "blog_end_yiyan": get_yiyan()
    }

    if my_blog.life is None:
        data.update({
            "blog_life": 0
        })
    else:
        data.update({
            "blog_life_year": my_blog.life // 365,
            "blog_life_day": my_blog.life % 365,
        })

    # 博客文章处理
    for i, post in enumerate(my_blog.post_lists(), 1):
        # 情感分
        post.score = analyze_sentiment(post.content)
        # 分类, 关键字
        post.category, post.keys = classify_and_extract_keywords(text=post.content, topK=21,
                                                                 stopwords='data/stop_words.txt',
                                                                 tech_terms_file='data/tech_terms.txt')
        # 权重, 日子计算
        post.weight, post.date = calculate_weight(post.time)

        logger.info(f"Post #{i}:")
        logger.info(post)

    # 博客文章权重计算
    weights = [post.weight for post in my_blog.post_lists()]
    max_weight = max(weights)
    max_item = [post for post in my_blog.post_lists() if post.weight == max_weight][0]

    data.update({
        "blog_title": max_item.title,
        "blog_content": max_item.content[0:50],
        "blog_content_date": max_item.date,
    })

    # 暂时只有一个主题
    # 博客关键词计算 5 个
    all_keys = []
    for post in my_blog.post_lists():
        all_keys.extend(post.keys)

    keyword_counts = Counter(all_keys)
    top_keywords = keyword_counts.most_common(5)
    data.update({
        "blog_top_keywords": top_keywords
    })

    # 博客分类计算
    categories = [post.category for post in my_blog.post_lists()]
    cat_counts = Counter(categories)
    most_common_cat = cat_counts.most_common(1)[0][0]

    data.update({
        "blog_category": "技术" if most_common_cat == 1 else "生活"
    })

    # 输出
    logger.debug(data)
    # 写入 config.ini 避免重复计算
    config.blog_data = data
    return data
