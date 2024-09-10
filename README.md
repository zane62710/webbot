# webbot
网页客服智能助理开发使用指南

## 2. 开发环境

### 2.1 英特尔至强可扩展处理器G8i云环境

PAI-DSW（Data Science Workshop）是为算法开发者量身打造的一站式AI开发平台，集成了JupyterLab、WebIDE、Terminal多种云端开发环境，提供代码编写、调试及运行的沉浸式体验。提供丰富的异构计算资源，预置多种开源框架的镜像，实现开箱即用的高效开发模式。



### 2.2大模型

‌Qwen2-7B‌是Qwen2系列模型的一部分，属于阿里通义千问项目的一部分。Qwen2系列模型包括不同尺寸的预训练和指令微调模型，其中Qwen2-7B是该系列中的一个模型。这一系列模型的发布旨在提供不同规模和能力的语言处理模型，以满足不同用户的需求。



### 2.3部署环境要求

操作系统版本:ubuntu22.04

Cuda版本：cuda12.1.0
Python版本:py310
torch版本:2.3.0

## 3. 开发步骤

### 3.1 购买G8i云环境

打开阿里云ECS工作台https://ecs.console.aliyun.com/home

![image-20240911000401166](http://tc.sql2022.cn/tc/jinh_pc/image-20240911000401166.png)



点击购买，选择规格为`Intel Xeon(Emerald Rapids) Platinum 8575C/Intel Xeon(Sapphire Rapids) Platinum 8475B`

![image-20240911002741310](http://tc.sql2022.cn/tc/jinh_pc/image-20240911002741310.png)



其余操作根据自身实际需求填写，确认下单
![image-20240911002846100](http://tc.sql2022.cn/tc/jinh_pc/image-20240911002846100.png)

![image-20240911003617870](http://tc.sql2022.cn/tc/jinh_pc/image-20240911003617870.png)

### 3.2 部署开发环境

使用Finalshell远程登录主机
![image-20240911003248728](http://tc.sql2022.cn/tc/jinh_pc/image-20240911003248728.png)

在云服务器ECS上安装Docker，可使用阿里云提供的Docker镜像源快速部署。

1. 登录ECS管理控制台，找到目标ECS实例，单击实例ID，进入实例详情页。

2. 选择定时与自动化任务 > 安装/卸载扩展程序 > 安装扩展程序。

![image-20240911003810877](http://tc.sql2022.cn/tc/jinh_pc/image-20240911003810877.png)

等待安装完成

![image-20240911003854745](http://tc.sql2022.cn/tc/jinh_pc/image-20240911003854745.png)

运行Intel xFasterTransformer容器。

```bash
sudo docker pull registry.openanolis.cn/openanolis/xfastertransformer:1.7.3-23
sudo docker run -it --name xFT -h xFT --privileged --shm-size=16g --network host -v /mnt:/mnt -w /mnt/xFasterTransformer registry.openanolis.cn/openanolis/xfastertransformer:1.7.3-23
```

![image-20240911004035274](http://tc.sql2022.cn/tc/jinh_pc/image-20240911004035274.png)

![image-20240911004432848](http://tc.sql2022.cn/tc/jinh_pc/image-20240911004432848.png)

安装依赖

```bash
# 在容器中安装依赖软件
yum update -y
yum install -y wget git git-lfs vim tmux
```

![image-20240911004608184](http://tc.sql2022.cn/tc/jinh_pc/image-20240911004608184.png)

```bash
# 启用Git LFS
git lfs install
```

![image-20240911004706765](http://tc.sql2022.cn/tc/jinh_pc/image-20240911004706765.png)

创建模型所在目录

```
mkdir -p /model/data
cd /model/data
```

![image-20240911004836165](http://tc.sql2022.cn/tc/jinh_pc/image-20240911004836165.png)

创建tmux session

```bash
tmux
```

下载Qwen-7B-Chat

```bash
git clone https://www.modelscope.cn/qwen/Qwen-7B-Chat.git /model/data/qwen
```

![image-20240911005043209](http://tc.sql2022.cn/tc/jinh_pc/image-20240911005043209.png)

模型数据是HuggingFace格式，需要转换成xFasterTransformer格式。生成的模型文件夹为/model/data/qwen-7b-chat-xft。

```python
python -c 'import xfastertransformer as xft; xft.QwenConvert().convert("/model/data/qwen")'c
```



### 3.3 构建千问模型

在容器中安装依赖

```bash
cd /root/xFasterTransformer/examples/web_demo
pip install -r requirements.txt
```

![image-20240911014840546](http://tc.sql2022.cn/tc/jinh_pc/image-20240911014840546.png)

启动WebUI

```bash
OMP_NUM_THREADS=$(($(lscpu | grep "^CPU(s):" | awk '{print $NF}') / 2)) GRADIO_SERVER_NAME="0.0.0.0" numactl -C $(seq -s, 0 2 $(($(lscpu | grep "^CPU(s):" | awk '{print $NF}') - 2))) -m 0 python Qwen.py -t /model/data/qwen -m /model/data/qwen-xft -d bf16
```

![image-20240911020503341](http://tc.sql2022.cn/tc/jinh_pc/image-20240911020503341.png)

### 3.4 应用构建

使用API形式进行部署
![image-20240911022501325](http://tc.sql2022.cn/tc/jinh_pc/image-20240911022501325.png)

在nginx中配置反向代理
![image-20240911022548094](http://tc.sql2022.cn/tc/jinh_pc/image-20240911022548094.png)

在前端页面调用

![image-20240911022830625](http://tc.sql2022.cn/tc/jinh_pc/image-20240911022830625.png)

展示效果如下



![image-20240911023234716](http://tc.sql2022.cn/tc/jinh_pc/image-20240911023234716.png)

![image-20240911023156058](http://tc.sql2022.cn/tc/jinh_pc/image-20240911023156058.png)



效果

