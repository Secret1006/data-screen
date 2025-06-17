#!/bin/bash
# docker网络自动配置脚本(对docker网络进行实际自动化探测并修改配置)

set -e  # 遇到错误立即退出

echo "========== 网络自动化配置 =========="

# 探测宿主机网络配置
HOST_IP=$(ip route get 1 | awk '{print $7; exit}')
HOST_IP_THIRD_OCTET=$(echo $HOST_IP | awk -F. '{print $3}')  # 从宿主机ip地址中提取第三个数字段
SUBNET=$(echo $HOST_IP | awk -F. '{print $1"."$2"."$3".0/24"}')
GATEWAY=$(ip route | awk '/default/ {print $3; exit}')
DNS_SERVER=$(grep nameserver /etc/resolv.conf | head -n1 | awk '{print $2}')
echo "检测到当前宿主机网络配置:"
echo "  宿主机IP: $HOST_IP"
echo "  网段: $SUBNET"
echo "  网关: $GATEWAY"
echo "  DNS: $DNS_SERVER"

# 生成与宿主机不冲突的Docker子网(172.18.x.0/24)
DOCKER_SUBNET_BASE="172.18"  # 定义Docker专用网络基础段，避免与宿主机网络冲突
DOCKER_SUBNET="$DOCKER_SUBNET_BASE.$HOST_IP_THIRD_OCTET.0/24"  # 将生成Docker子网与宿主机关联
DOCKER_GATEWAY="$DOCKER_SUBNET_BASE.$HOST_IP_THIRD_OCTET.1"  # 将生成Docker网关固定为172.18.x.1

# 检查生成的Docker网络是否被占用
#if docker network inspect --f '{{range .IPAM.Config}}{{.Subnet}}{{println}}{{end}}' $(docker network ls -q) | grep -q "^${DOCKER_SUBNET}$"; then
#    echo "⚠️ 子网 $DOCKER_SUBNET 已被占用！"
#else
#    echo "✅ 子网 $DOCKER_SUBNET 可用"
#fi

# 创建/更新Docker网络  
echo "Docker网络配置:"
echo "  子网: $DOCKER_SUBNET"
echo "  网关: $DOCKER_GATEWAY"

# 清理并重建网络
echo "配置Docker网络..."
docker network rm data-screen-net 2>/dev/null || true  # 清除旧网络(如果需要)
docker network create \
    --subnet $DOCKER_SUBNET \
    --gateway $DOCKER_GATEWAY \
    data-screen-net

echo "✅ Docker网络配置完成: data-screen-net"