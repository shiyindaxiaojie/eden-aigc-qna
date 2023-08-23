# 使用基础镜像
FROM python:3.9.10-slim-buster as builder

# 设置工作目录
WORKDIR /app

# 复制源程序
COPY ./code /app

# 创建容器镜像
FROM python:3.9.10-slim-buster

# 镜像元数据
LABEL maintainer="梦想歌 <shiyindaxiaojie@gmail.com>"
LABEL version="0.0.1"
ARG USER=tmpuser
ARG GROUP=tmpgroup
ARG HOME=/app

# 环境变量
ENV OPENAI_API_TYPE azure
ENV OPENAI_API_BASE ""
ENV OPENAI_API_KEY ""
ENV OPENAI_API_VERSION 2023-05-15
ENV OPENAI_ENGINE gpt-35-turbo
ENV OPENAI_EMBEDDINGS_ENGINE text-embedding-ada-002
ENV OPENAI_DEPLOYMENT_TYPE "Chat"
ENV OPENAI_TEMPERATURE "0.7"
ENV OPENAI_MAX_TOKENS "-1"
ENV OPENAI_CHUNK_SIZE 500
ENV OPENAI_CHUNK_OVERLAP 100
# 向量存储
ENV VECTOR_STORE_TYPE Redis
ENV MILVUS_HOST ""
ENV MILVUS_PORT 19530
ENV MILVUS_USERNAME aigc
ENV MILVUS_PASSWORD ""
ENV REDIS_HOST ""
ENV REDIS_PORT 6379
ENV REDIS_PASSWORD ""
# 文件存储
ENV BLOB_STORE_ENABLED true
ENV BLOB_STORE_TYPE COS
ENV QCLOUD_COS_REGION ""
ENV QCLOUD_COS_SECRET_ID ""
ENV QCLOUD_COS_SECRET_KEY ""
ENV QCLOUD_COS_TOKEN ""
ENV QCLOUD_COS_BUCKET ""
# 聊天设置
ENV CHAT_AI_AVATAR_STYLE bottts
ENV CHAT_AI_SEED Lucy
ENV CHAT_USER_AVATAR_STYLE fun-emoji
ENV CHAT_USER_SEED Felix

# 创建普通用户并设置工作目录
RUN groupadd -g 1000 $GROUP \
  && useradd -u 1000 -g $GROUP -d $HOME -s /bin/bash $USER \
  && mkdir -p $HOME \
  && chown -R $USER:$GROUP $HOME \
  && chmod -R a+rwX $HOME
WORKDIR $HOME

# 复制应用程序依赖项和模块
COPY --from=builder /app/ ./

# 初始化环境
RUN apt-get update &&  \
    apt-get install python-tk python3-tk tk-dev -y && \
    pip install -r requirements.txt

EXPOSE 80
ENTRYPOINT echo "The application will start in ${START_DELAY_SECS}s..." && sleep ${START_DELAY_SECS} && exec streamlit run Home.py --server.port=80 --server.enableXsrfProtection=false