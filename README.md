# OpenAI 快速入门

## 运行环境



## 准备工作

### 更新 Python 组件

```shell
# python.exe -m pip install --upgrade pip
pip install --upgrade pip
```

### 安装 OpenAI CLI 工具

```shell
pip install --upgrade openai
# 如果提示 missing `pandas` 错误，执行以下命令
pip install openai[datalib] 
```

### 安装 Embedding 依赖组件

```shell
pip install numpy cmake scipy setuptools-rust chromadb
```

如果执行报错，请从 Windows 官网下载 `Visual Studio Install`，选择 C++ 组件执行安装。

### 安装 OpenAI 可选组件

```shell
pip install pymupdf faiss-gpu faiss-cpu
pip install atlassian-python-api
```




