FROM python:3.11.0

WORKDIR /app

ADD . /app

RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && pip install -r requirements.txt

EXPOSE 7777

CMD [ "python", "./main.py" ]
