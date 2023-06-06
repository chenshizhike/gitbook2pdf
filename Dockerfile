FROM python:3.9.16-alpine

ENV USERNAME=app GID=1000 UID=1000

ENV LANG=zh_CN.UTF-8 LANGUAGE=zh_CN.UTF-8 

ENV BOOKDIR /app

RUN addgroup --gid $GID $USERNAME \
    && adduser --uid $UID --ingroup $USERNAME --disabled-password $USERNAME \
    && mkdir $BOOKDIR \
    && chown -R $UID:$GID $BOOKDIR

# Install jpeg-dev pango-dev libxslt-dev zlib-dev libffi-dev cairo-dev gdk-pixbuf-dev
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories \
    && apk update \
    && apk --no-cache add jpeg-dev pango-dev libxslt-dev zlib-dev libffi-dev cairo-dev gdk-pixbuf-dev \
    && rm -rf /var/cache/apk/* \
    && rm -rf /tmp/*

USER $USERNAME

COPY --chown=$UID:$GID gitbook2pdf $BOOKDIR

WORKDIR $BOOKDIR

RUN python -m pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple \
    && pip config set global.index-url https://mirrors.aliyun.com/pypi/simple \
    && python -m pip install -r requirements.txt

ENTRYPOINT [ "python","gitbook.py" ]



