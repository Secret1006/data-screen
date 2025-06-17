#!/bin/bash
# 数据大屏独立应用部署脚本(构建镜像并运行容器)

set -e  # 遇到错误立即退出

echo "========== 应用部署 =========="

# 设置镜像名称和容器名称
IMAGE_NAME="data-screen"  # 镜像名称
CONTAINER_NAME="data-screen-app"  # 容器名称

echo "清理旧容器..."
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

# 构建新镜像
echo "构建Docker镜像..."    
docker build -t $IMAGE_NAME .  

# 运行容器
echo "启动应用容器(端口映射:5000)..."
docker run -d \
  --name $CONTAINER_NAME \
  --network data-screen-net \
  -p 80:5000 \
  $IMAGE_NAME

echo "✅ 数据大屏应用部署完成"
echo " - 容器名称: $CONTAINER_NAME 端口: 5000"
echo " - 容器状态: $(docker inspect -f '{{.State.Status}}' $CONTAINER_NAME)"  # 查看容器运行状态
echo " - 访问地址: http://$(ip route get 1 2>/dev/null | awk '{print $7; exit}' | { read ip; echo "${ip:-localhost}"; })"