# AIGC 知识库问答服务

一个基于 OpenAI 实现的知识库问答系统，支持文档上传、向量存储、聊天问答。

## 演示图例

### 聊天问答

![](https://cdn.jsdelivr.net/gh/shiyindaxiaojie/images/eden-aigc-qna/chat.png)

### 附件上传

![](https://cdn.jsdelivr.net/gh/shiyindaxiaojie/images/eden-aigc-qna/add-document.png)

### 文档管理

![](https://cdn.jsdelivr.net/gh/shiyindaxiaojie/images/eden-aigc-qna/document-management.png)

### 索引管理

![](https://cdn.jsdelivr.net/gh/shiyindaxiaojie/images/eden-aigc-qna/index-management.png)

## 准备工作

### 设置运行环境

本项目需要包含大量 `pip install` 执行，为了加速下载，您可能需要配置国内镜像源。您需要创建或编辑 `~/.pip/pip.conf` 文件（Linux/macOS）或 `%APPDATA%\pip\pip.ini` 文件（Windows），内容如下：
```ini
[global]
timeout = 6000
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
```


### 更新 Python 组件

```shell
# python.exe -m pip install --upgrade pip
pip install --upgrade pip
```

### 安装相关依赖

```shell
cd code
pip install -r requirements.txt
```

> 提示 missing `pandas` 错误，执行 `pip install openai[datalib]`
> 提示 `chromadb` 相关报错，请从 Windows 官网下载 `Visual Studio Install`，选择 C++ 组件执行安装。


## 如何启动

根目录下提供了 `.env.template` 环境配置文件，请根据注释填写相关配置，并另存为 `.env` 文件。

然后，在根目录运行以下命令

```shell
cd code
streamlit run Home.py
```

## 如何部署

推荐使用 Docker 镜像部署

```shell
docker build -t eden-aigc-qna:latest -f docker/Dockerfile .
```

