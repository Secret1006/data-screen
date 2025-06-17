# 主机状态监控系统
![image](https://img.shields.io/badge/Windows-blue.svg)  ![image](https://img.shields.io/badge/ubuntu:20.04-blue.svg)  ![image](https://img.shields.io/badge/Docker-blue.svg)  ![image](https://img.shields.io/badge/Ansibler-blue.svg)  ![image](https://img.shields.io/badge/Shell-blue.svg)  ![image](https://img.shields.io/badge/Python-blue.svg)   ![image](https://img.shields.io/badge/html-blue.svg)   ![image](https://img.shields.io/badge/Python-css.svg)  
基于Docker容器技术和Ansible自动化运维技术的主机状态监控系统，通过Web界面实时展示主机状态，并支持主机分组管理。

#### 该项目镜像已上传至阿里云：  
```bash
docker pull crpi-wjovngju7gnou1od.cn-guangzhou.personal.cr.aliyuncs.com/hupeiye/data-screen:latest
```

## ✨ 功能亮点
- 🌌 **科技风格大屏界面**：深蓝色科技风格，更适合监控应用场景
- 🔧 **主机分组管理**：可对主机分组进行增删改查操作
- 🔄 **实时状态监控**：手动/自动刷新主机状态（30秒间隔）
- 🖥️ **全屏模式**：一键切换全屏显示，满足大屏监控需求
- 🔍 **主机搜索**：快速查找指定IP的主机
- 🔒 **管理员登录**：安全登录和找回密码功能
- ⚡ **一键部署**：通过部署脚本快速部署整个系统（配置docker网络+部署应用）

## 📖 使用说明
### 系统应用部署：
  
  方式1：下载该项目文件并调用项目文件中的主部署脚本（scripts/deploy_main.sh）一键部署（配置docker网络+部署应用）
  
  方式2：拉取阿里云镜像
```bash
# 从阿里云拉取镜像
docker pull crpi-wjovngju7gnou1od.cn-guangzhou.personal.cr.aliyuncs.com/hupeiye/data-screen:latest

# 运行容器
docker run -d --name data-screen-app -p 80:5000 crpi-wjovngju7gnou1od.cn-guangzhou.personal.cr.aliyuncs.com/hupeiye/data-screen
```

### 管理员登录系统：
    
  初始临时账号：admin  
  初始临时密码：admin123 (首次登录后请立即修改)  

## 🖼️ 效果演示
### 管理员登录页面：
![image](https://github.com/Secret1006/data-screen/blob/master/images/1.png)
### 初次登录主机状态监控页面：
![image](https://github.com/Secret1006/data-screen/blob/master/images/2.png)
### 点击"修改密码"按钮跳转至管理员密码修改页面：
![image](https://github.com/Secret1006/data-screen/blob/master/images/3.png)
### 点击"主机管理"按钮跳转至主机管理页面：
![image](https://github.com/Secret1006/data-screen/blob/master/images/4.png)
### 添加/修改主机：
![image](https://github.com/Secret1006/data-screen/blob/master/images/5.png)
![image](https://github.com/Secret1006/data-screen/blob/master/images/7.png)
### 添加主机分组：
![image](https://github.com/Secret1006/data-screen/blob/master/images/12.png)
![image](https://github.com/Secret1006/data-screen/blob/master/images/13.png)
### 主机状态监控页面效果：
![image](https://github.com/Secret1006/data-screen/blob/master/images/10.png)
### 点击右上角图标进入全屏模式：
![image](https://github.com/Secret1006/data-screen/blob/master/images/11.png)  

## ⚠️ 当前问题
- ### 当前系统尚未开发找回密码功能，所以初次登录并修改密码后需妥善保存管理员密码！！！
- ### 当前主机管理监控页面可能部署在个别电脑中可能会导致布局出现问题，还没有得到完全解决！！！
