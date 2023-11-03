from flask import Flask, render_template, redirect, url_for
from loguru import logger

import const
import models
import tools
from generator import Generator

app = Flask(__name__)
logger.add("endofyear.log")


@app.route('/')
def home():
    # 重定向 painting
    return redirect(url_for('painting'))


@app.route('/painting')
def painting():
    # 站点数据
    site = models.Site(
        service=const.SITE_SERVICE,
        title=const.SITE_NAME
    ).to_dict()

    # 自定义数据
    custom = models.Custom(
        yiyan=tools.get_yiyan()
    ).to_dict()

    # 初始化数据生成器
    generator = Generator("https://blog.7wate.com/rss.xml")

    # 渲染模板
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
