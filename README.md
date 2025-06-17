# 主机状态监控系统

基于Docker容器技术和Ansible自动化运维技术的主机状态监控系统，通过Web界面实时展示主机状态，并支持主机分组管理。

#### 该项目镜像已上传至阿里云  
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
- **系统应用部署**：
  
  方式一：下载该项目文件并调用项目文件中的主部署脚本（scripts/deploy_main.sh）一键部署（配置docker网络+部署应用）
  
  方式二：拉取阿里云镜像
```bash
# 从阿里云拉取镜像
docker pull crpi-wjovngju7gnou1od.cn-guangzhou.personal.cr.aliyuncs.com/hupeiye/data-screen:latest

# 运行容器
docker run -d --name data-screen-app -p 80:5000 crpi-wjovngju7gnou1od.cn-guangzhou.personal.cr.aliyuncs.com/hupeiye/data-screen
```

- **管理员登录系统**：
    
  初始临时账号：admin  
  初始临时密码：admin123 (首次登录后请立即修改)  
  


## 🖼️ 效果演示
