from flask import Flask, render_template, redirect, url_for
from loguru import logger

from src import const
from src import models
from src import tools
from src.config import Config
from src.generator import Generator

app = Flask(__name__)
logger.add("endofyear.log")


@app.route('/')
def home():
    # 重定向 painting
    return redirect(url_for('painting'))


@app.route('/painting')
def painting():
    # 读取配置文件
    config = Config("config.ini")

    # 站点数据
    site = models.Site(
        service=config.web_status,
        title=const.SITE_NAME
    ).to_dict()

    # 自定义数据
    custom = models.Custom(
        yiyan=tools.get_yiyan()
    ).to_dict()

    # 初始化数据生成器
    generator = Generator(config.rss_url)
    logger.info(f"Site: {site}")
    logger.info(f"Blog: {generator.blog()}")
    logger.info(f"Special Post: {generator.special_post()}")
    logger.info(f"Sentiment Post: {generator.sentiment_post()}")
    logger.info(f"Long Post: {generator.long_post()}")
    logger.info(f"Short Post: {generator.short_post()}")

    # 服务模式
    if config.web_status == const.SITE_SERVICE_STATIC:
        # 静态网站模式
        html_static_file = render_template('painting.html',
                                           site=site,
                                           blog=generator.blog(),
                                           special_post=generator.special_post(),
                                           sentiment_post=generator.sentiment_post(),
                                           long_post=generator.long_post(),
                                           short_post=generator.short_post(),
                                           custom=custom
                                           )

        with open("static/index.html", "w") as f:
            f.write(html_static_file)

        return 'OK'
    else:
        # web 模式
        return render_template('painting.html',
                               site=site,
                               blog=generator.blog(),
                               special_post=generator.special_post(),
                               sentiment_post=generator.sentiment_post(),
                               long_post=generator.long_post(),
                               short_post=generator.short_post(),
                               custom=custom
                               )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7777, debug=True)
