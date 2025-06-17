FROM ubuntu:20.04

# 安装基础工具和Ansible依赖
RUN sed -i 's/archive.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    sed -i 's/security.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    iputils-ping net-tools python3 python3-pip openssh-client sshpass && \
    pip3 install ansible && \
    rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 配置Ansible环境
RUN mkdir -p /etc/ansible
COPY ansible/hosts /etc/ansible/hosts
COPY ansible/ansible.cfg /etc/ansible/ansible.cfg

# 安装后端Python依赖（Flask）
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# 复制代码
COPY app/app.py .
COPY app/templates ./templates
COPY app/static ./static

# 暴露端口
EXPOSE 5000

CMD ["python3", "app.py"]