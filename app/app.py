from flask import Flask, render_template, jsonify, request, session, redirect, url_for, make_response
import subprocess
import re
import os
import json
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # 请替换为强密钥
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # 禁用默认缓存

# 管理员凭据文件路径
ADMIN_CREDENTIALS_FILE = 'admin_credentials.json'

# 初始化管理员凭据文件
def init_admin_credentials():
    if not os.path.exists(ADMIN_CREDENTIALS_FILE):
        default_credentials = {
            'username': 'admin',
            'password': 'admin123'
        }
        with open(ADMIN_CREDENTIALS_FILE, 'w') as f:
            json.dump(default_credentials, f)

# 获取管理员凭据
def get_admin_credentials():
    if not os.path.exists(ADMIN_CREDENTIALS_FILE):
        init_admin_credentials()
    
    with open(ADMIN_CREDENTIALS_FILE, 'r') as f:
        return json.load(f)

# 更新管理员凭据
def update_admin_credentials(new_username, new_password):
    credentials = {
        'username': new_username,
        'password': new_password
    }
    with open(ADMIN_CREDENTIALS_FILE, 'w') as f:
        json.dump(credentials, f)

# 登录检查装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# 禁用缓存装饰器
def no_cache(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = make_response(f(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    return decorated_function

# 获取hosts文件路径
HOSTS_PATH = '/etc/ansible/hosts'

# 初始化管理员凭据
init_admin_credentials()

# 读取hosts文件获取所有主机信息
def get_hosts_data():
    groups = {}
    current_group = None
    
    try:
        with open(HOSTS_PATH, 'r') as f:
            for line in f:
                line = line.strip()
                
                # 跳过注释和空行
                if not line or line.startswith('#'):
                    continue
                
                # 检测组定义
                if line.startswith('[') and line.endswith(']'):
                    current_group = line[1:-1]
                    groups[current_group] = []
                    continue
                
                # 处理主机行
                if current_group:
                    parts = line.split()
                    if not parts:
                        continue
                    
                    host = {"ip": parts[0]}
                    for part in parts[1:]:
                        if '=' in part:
                            key, value = part.split('=', 1)
                            host[key] = value
                    
                    groups[current_group].append(host)
    
    except Exception as e:
        print(f"读取hosts文件失败: {str(e)}")
    
    return groups

# 更新hosts文件
def update_hosts_file(groups):
    try:
        content = []
        
        for group, hosts in groups.items():
            content.append(f"[{group}]\n")
            for host in hosts:
                line = host["ip"]
                if "ansible_user" in host:
                    line += f" ansible_user={host['ansible_user']}"
                if "ansible_password" in host:
                    line += f" ansible_password={host['ansible_password']}"
                if "ansible_port" in host:
                    line += f" ansible_port={host['ansible_port']}"
                content.append(line + "\n")
            content.append("\n")
        
        with open(HOSTS_PATH, 'w') as f:
            f.writelines(content)
        
        return True
    except Exception as e:
        print(f"更新hosts文件失败: {str(e)}")
        return False

# 主机管理页面路由
@app.route('/host_manager')
@login_required
@no_cache
def host_manager():
    return render_template('host_manager.html', username=session.get('username'))

# 登录路由
@app.route('/login', methods=['GET', 'POST'])
@no_cache  # 禁用缓存
def login():
    # 如果已登录，重定向到首页
    if 'logged_in' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        credentials = get_admin_credentials()
        
        if username == credentials['username'] and password == credentials['password']:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='用户名或密码错误')
    
    return render_template('login.html')

# 注销路由
@app.route('/logout')
@no_cache  # 禁用缓存
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('login'))

# 密码修改路由
@app.route('/change_password', methods=['GET', 'POST'])
@login_required
@no_cache
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        credentials = get_admin_credentials()
        
        # 验证当前密码
        if current_password != credentials['password']:
            return render_template('change_password.html', error='当前密码不正确')
        
        # 验证新密码
        if not new_password:
            return render_template('change_password.html', error='新密码不能为空')
        
        if new_password != confirm_password:
            return render_template('change_password.html', error='新密码和确认密码不一致')
        
        # 更新密码
        update_admin_credentials(credentials['username'], new_password)
        
        # 更新会话中的用户名
        session['username'] = credentials['username']
        
        return render_template('change_password.html', success='密码修改成功！')
    
    return render_template('change_password.html')

@app.route('/')
@login_required
@no_cache  # 禁用缓存
def index():
    return render_template('index.html', username=session.get('username'))

@app.route('/run-ansible')
@login_required
@no_cache  # 禁用缓存
def run_ansible():
    try:
        # 获取所有组的主机信息
        groups = get_hosts_data()
        
        # 收集所有主机（按组和IP排序）
        all_hosts = []
        seen_ips = set()
        
        # 按组名排序
        sorted_groups = sorted(groups.items(), key=lambda x: x[0].lower())
        
        # 遍历排序后的组
        for group, hosts in sorted_groups:
            # 按IP地址排序
            sorted_hosts = sorted(hosts, key=lambda h: tuple(map(int, h['ip'].split('.'))))
            for host in sorted_hosts:
                ip = host["ip"]
                if ip not in seen_ips:
                    seen_ips.add(ip)
                    # 添加组信息到主机
                    host_with_group = host.copy()
                    host_with_group["group"] = group
                    all_hosts.append(host_with_group)
        
        print(f"从hosts文件读取的所有主机: {all_hosts}")  # 调试信息
        
        # 创建主机映射（Host-1, Host-2等） - 保持原有顺序
        host_mapping = {host["ip"]: f"Host-{index+1}" for index, host in enumerate(all_hosts)}
        
        # 执行ansible命令（禁用颜色输出便于解析）
        result = subprocess.run(
            ['ansible', 'all', '-m', 'ping'],
            capture_output=True,
            text=True,
            env=dict(os.environ, ANSIBLE_NOCOLOR='1')
        )
        output = result.stdout
        print(f"Ansible输出: {output}")  # 调试信息
        
        # 解析Ansible输出
        hosts_status = []
        success_count = 0
        unreachable_count = 0
        failed_count = 0
        
        # 使用字典存储解析结果，以便按主机名/IP查找
        host_status_map = {}
        
        # 使用正则表达式匹配主机状态
        pattern = r'^(\S+)\s+\|\s+(SUCCESS|UNREACHABLE!|FAILED!)\s+\=>'
        for line in output.splitlines():
            match = re.match(pattern, line)
            if match:
                host = match.group(1)
                status = match.group(2)
                
                # 标准化状态
                if status == "SUCCESS":
                    status = "success"
                    success_count += 1
                elif status == "UNREACHABLE!":
                    status = "unreachable"
                    unreachable_count += 1
                else:
                    status = "failed"
                    failed_count += 1
                
                # 存储到字典中
                host_status_map[host] = status
        
        # 按照所有主机列表的顺序构建结果
        for host_info in all_hosts:
            host_ip = host_info["ip"]
            # 获取状态（如果存在），否则设为未知
            status = host_status_map.get(host_ip, "unknown")
            
            # 获取主机编号
            host_id = host_mapping.get(host_ip, "未知主机")
            
            hosts_status.append({
                "host": host_id,
                "status": status,
                "host_id": host_id,
                "host_ip": host_ip,
                "group": host_info.get("group", "未知组")  # 添加组信息
            })
        
        total_hosts = len(hosts_status)
        online_count = success_count
        
        return jsonify({
            "hosts_status": hosts_status,
            "stats": {
                "total": total_hosts,
                "online": online_count,
                "offline": unreachable_count + failed_count
            }
        })
        
    except Exception as e:
        print(f"执行Ansible时出错: {str(e)}")  # 调试信息
        return jsonify({"error": str(e)})

# 主机管理API
@app.route('/api/hosts', methods=['GET', 'POST', 'DELETE', 'PUT'])
@login_required
@no_cache  # 禁用缓存
def manage_hosts():
    try:
        if request.method == 'GET':
            groups = get_hosts_data()
            return jsonify({"groups": groups})
        
        data = request.get_json()
        
        # 添加新组
        if request.method == 'POST' and data.get('action') == 'add_group':
            group_name = data.get('group_name')
            if not group_name:
                return jsonify({"error": "组名不能为空"}), 400
            
            groups = get_hosts_data()
            if group_name in groups:
                return jsonify({"error": "组已存在"}), 400
            
            groups[group_name] = []
            if update_hosts_file(groups):
                return jsonify({"message": "组添加成功", "groups": groups})
            else:
                return jsonify({"error": "更新hosts文件失败"}), 500
        
        # 删除组
        if request.method == 'DELETE' and data.get('action') == 'delete_group':
            group_name = data.get('group_name')
            if not group_name:
                return jsonify({"error": "组名不能为空"}), 400
            
            groups = get_hosts_data()
            if group_name not in groups:
                return jsonify({"error": "组不存在"}), 404
            
            del groups[group_name]
            if update_hosts_file(groups):
                return jsonify({"message": "组删除成功", "groups": groups})
            else:
                return jsonify({"error": "更新hosts文件失败"}), 500
        
        # 添加主机
        if request.method == 'POST' and data.get('action') == 'add_host':
            group_name = data.get('group_name')
            host_data = data.get('host')
            
            if not group_name:
                return jsonify({"error": "组名不能为空"}), 400
            if not host_data or not host_data.get('ip'):
                return jsonify({"error": "主机地址不能为空"}), 400
            
            groups = get_hosts_data()
            if group_name not in groups:
                return jsonify({"error": "组不存在"}), 404
            
            # 检查主机是否已存在
            for host in groups[group_name]:
                if host["ip"] == host_data["ip"]:
                    return jsonify({"error": "主机已存在"}), 400
            
            # 添加新主机
            new_host = {
                "ip": host_data["ip"]
            }
            if "user" in host_data:
                new_host["ansible_user"] = host_data["user"]
            if "password" in host_data:
                new_host["ansible_password"] = host_data["password"]
            if "port" in host_data:
                new_host["ansible_port"] = host_data["port"]
            
            groups[group_name].append(new_host)
            
            if update_hosts_file(groups):
                return jsonify({"message": "主机添加成功", "groups": groups})
            else:
                return jsonify({"error": "更新hosts文件失败"}), 500
        
        # 删除主机
        if request.method == 'DELETE' and data.get('action') == 'delete_host':
            group_name = data.get('group_name')
            host_ip = data.get('host_ip')
            
            if not group_name or not host_ip:
                return jsonify({"error": "组名和主机IP不能为空"}), 400
            
            groups = get_hosts_data()
            if group_name not in groups:
                return jsonify({"error": "组不存在"}), 404
            
            # 查找并删除主机
            new_hosts = [h for h in groups[group_name] if h["ip"] != host_ip]
            if len(new_hosts) == len(groups[group_name]):
                return jsonify({"error": "主机不存在"}), 404
            
            groups[group_name] = new_hosts
            if update_hosts_file(groups):
                return jsonify({"message": "主机删除成功", "groups": groups})
            else:
                return jsonify({"error": "更新hosts文件失败"}), 500
        
        # 更新主机
        if request.method == 'PUT' and data.get('action') == 'update_host':
            group_name = data.get('group_name')
            host_ip = data.get('host_ip')
            new_host_data = data.get('new_host')
            
            if not group_name or not host_ip or not new_host_data:
                return jsonify({"error": "参数不完整"}), 400
            
            groups = get_hosts_data()
            if group_name not in groups:
                return jsonify({"error": "组不存在"}), 404
            
            # 查找并更新主机
            updated = False
            for host in groups[group_name]:
                if host["ip"] == host_ip:
                    # 更新主机属性
                    host["ip"] = new_host_data.get("ip", host_ip)
                    if "user" in new_host_data:
                        host["ansible_user"] = new_host_data["user"]
                    else:
                        if "ansible_user" in host:
                            del host["ansible_user"]
                    if "password" in new_host_data:
                        host["ansible_password"] = new_host_data["password"]
                    else:
                        if "ansible_password" in host:
                            del host["ansible_password"]
                    if "port" in new_host_data:
                        host["ansible_port"] = new_host_data["port"]
                    else:
                        if "ansible_port" in host:
                            del host["ansible_port"]
                    updated = True
                    break
            
            if not updated:
                return jsonify({"error": "主机不存在"}), 404
            
            # 检查是否需要移动到其他组
            new_group = new_host_data.get("group")
            if new_group and new_group != group_name:
                if new_group not in groups:
                    groups[new_group] = []
                
                # 移动主机到新组
                groups[new_group].append(host)
                groups[group_name] = [h for h in groups[group_name] if h["ip"] != host_ip]
            
            if update_hosts_file(groups):
                return jsonify({"message": "主机更新成功", "groups": groups})
            else:
                return jsonify({"error": "更新hosts文件失败"}), 500
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)