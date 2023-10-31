# EndOfYear

EndOfYear 点燃个人博客的年度辉煌！

![EndOfYear](static/endofyear.jpg)

## 用法

### 要求

- RSS 源必须输出文章全部内容，否则数据分析不准确。
- Github 运行可能无法访问 RSS 源，请使用本地 Docker 运行。
- 如果生成年度报告，请结合博客实际情况设置 RSS 输出文章数量。

### Github

1.  Fork 项目到个人仓库。
2. 手动配置仓库的 Workflow permissions 设置为 **Read and write permissions**，否则无法写入 html 分支。
    1. 导航到 **Settings**（设置）选项卡。
    2. 在左侧导航栏中，点击 **Actions**（操作）。
    3. 在 **General**（常规）页面下滑，找到 **Workflow permissions**（工作流权限）。
    4. 在 **Workflow permissions** 中，选择 **Read and write permissions**（读写权限）。
    5. 最后点击 **Save**（保存）。
3. 在仓库首页打开目录下的 `config.ini` 配置文件，点击右上角工具栏的 **🖋️（钢笔）** 图标，在线编辑文件。
    - `web`：配置为 `false`。
    - `rss`：配置为 RSS 地址。

```ini
[default]
web = false

[blog]
rss = https://blog.7wate.com/rss.xml
data =
```

4. 点击右上角的 **Commit changes** 提交到 `main` 分支，会自动运行 Actions。
5. 等待 Actions 运行成功，将会部署静态网站文件至 `html` 分支。
6. 开启 GitHub 仓库的 Pages 功能，默认为根目录。
7. 访问个人网址，就可以看到啦~

### Docker

1. 拉取 [endofyear](https://hub.docker.com/r/sevenwate/endofyear) 最新镜像。

```shell
docker pull sevenwate/endofyear:latest
```

2. 映射容器 7777 端口至宿主机端口，指定 `rss` 环境变量，然后运行 Docker。

```shell
# 请将 https://blog.7wate.com/rss.xml 替换为自己的 RSS 地址。
docker run -p 7777:7777 --env rss=https://blog.7wate.com/rss.xml sevenwate/endofyear:latest
```

3. 访问网址 `localhost:7777`

## Q&A

### Github Actions 运行失败

请查阅 Actions 的第六步输出的 Log 日志排错。

### Docker 运行无法访问 Web 服务

1. 请检查**容器映射端口**至宿主机。
2. 请检查是否配置 **rss 环境变量**。
3. 请查看 Docker **运行日志**。

### 博客数据分析不准确

目前会根据个人时间进一步迭代，可以点个 Watch 订阅进度。

## 流程

EndOfYear 通过 RSS 获取博客文章数据，对文章数据进行统计、分析和整理，最终输出为 HTML，客观地反映了博客一年的写作情况。

```mermaid
sequenceDiagram
    actor User
    participant Flask
    participant Config
    participant Generator
    participant Scraper
    participant Analyzer

    User ->> Flask: Access service
    Flask ->> Config: Check cache
    activate Config
    alt Cache exists
        Config -->> Flask: Return cached data
    else Cache does not exist
        Config ->> Generator: Run data generator
        activate Generator
        Generator ->> Scraper: Run data scraping
        activate Scraper
        Scraper -->> Generator: Return scraped data
        deactivate Scraper
        Generator ->> Analyzer: Run data analysis
        activate Analyzer
        Analyzer -->> Generator: Return analyzed data
        deactivate Analyzer
        Generator -->> Config: Return organized data
        deactivate Generator
        Config -->> Flask: Return data
    end
    Flask -->> User: Return HTML page
    deactivate Config
```

1. 用户访问 Flask 服务。
2. Flask 检查缓存是否存在。
    - 如果缓存存在，Flask直接返回缓存数据。
    - 如果缓存不存在，继续下一步。
3. Config 模块运行数据生成器（Generator）。
4. Generator 模块运行数据抓取器（Scraper）来获取RSS数据。
5. Scraper 将抓取的数据返回给 Generator。
6. Generator 运行数据分析器（Analyzer）对数据进行分析。
7. Analyzer 将分析后的数据返回给 Generator。
8. Generator 整理结构化数据后将其返回给 Flask,Config 模块。
9. Flask 使用整理后的数据渲染 HTML 页面。
10. Flask 返回渲染后的 HTML 页面给用户。


## 路线图

EndOfYear 目前处于初始阶段，如果您有兴趣，可以为其做出贡献。计划路线如下：

###  V1

- [ ] 对博客系统的数据源进行全面、规模性的测试。
- [ ] 进一步细化数据分析维度和数据颗粒度，精准描绘用户画像。
- [ ] 渲染数据的规范，约束主题开发，提高主题的兼容性。
- [ ] 剥离数据分析和主题，提供更好地适用方式。

###  V2

- [ ] 进一步丰富和完善主题。
- [ ] EndOfYear 项目展示首页，使用文档，主题开发等。
- [ ] 实现轻量化的运行部署，一键运行。
- [ ] 探索以插件的方式附加到博客系统的方法。


## 协议

EndOfYear 采用 GPL 3.0 协议。
