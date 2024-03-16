# hola-trade

## 项目的目的

本项目是为了搭建一个 python 的底层自动化量化交易的框架，对 QMT 提供的函数进行封装，方便使用。

同时搭建量化策略的模板实现，方便用户基于此模板进行模板的定制。

## 搭建开发环境

```
conda create --name trade python=3.9 -y
conda activate trade
pip install -r requirements.txt

```

## 发布到 PyPI

```
./publish.sh

```

## 安装使用

```
pip install hola-trade

```
