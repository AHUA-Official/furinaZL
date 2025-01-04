# -*- coding: utf-8 -*-
# @author       lei.zhang
# @start        2024-10-13
# @lastupdate   2024-10-13
import random
import time
from datetime import datetime, timedelta
import json
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify
import paramiko


from flask import Flask, request, jsonify
import sqlite3
import requests
import monitoropration



app = Flask(__name__)
app.config.from_file("config.json", load=json.load)
with open("config.json", "r", encoding="utf-8") as config_file:
    app.config.update(json.load(config_file))







app = Flask(__name__)


# 初始化监控信息的数据表单
#创建一个monitor的数据库   创建一个monitorinfo的表单


# 定义一个全局字典用于存储配置
global_config = {}

# 初始化时加载 config.json 文件到全局字典
def load_initial_config():
    global global_config
    with open("config.json", "r", encoding="utf-8") as config_file:
        global_config = json.load(config_file)

load_initial_config()  # 启动时加载配置


# 服务器信息
servers = {
    "main_node": {"hostname": "8.137.104.90", "port": 22, "username": "root", "password": "zilic401689."},
    "huawei_cloud": {"hostname": "139.9.196.12", "port": 22, "username": "root", "password": "furina1013."},
    "jd_cloud": {"hostname": "117.72.84.25", "port": 22, "username": "root", "password": "furina@1013"},
    "tencent_cloud": {"hostname": "49.234.47.133", "port": 22, "username": "root", "password": "furina1013."}
}

def execute_ssh_command(server, command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(server['hostname'], server['port'], server['username'], server['password'])
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        if error:
            return {'status': 'error', 'message': error, 'server': server['hostname']}
        return {'status': 'success', 'output': output, 'server': server['hostname']}
    except Exception as e:
        return {'status': 'error', 'message': str(e), 'server': server['hostname']}
    finally:
        ssh.close()

@app.route('/scan_cpus', methods=['GET'])
def scan_cpus():
    cpu_usage = []
    command = "top -bn1 | grep 'Cpu(s)' | sed 's/.*, *\([0-9.]*\)%* id.*/\1/' | awk '{print 100 - $1}'"

    for name, server in servers.items():
        result = execute_ssh_command(server, command)
        if result['status'] == 'success':
            cpu_usage.append({'server': name, 'cpu_usage': result['output']})
        else:
            cpu_usage.append(result)

    print(cpu_usage)  # 打印在控制台
    return jsonify(cpu_usage)  # 通过Web返回
@app.route('/scan_disk', methods=['GET'])
def scan_disk():
    disk_usage = []
    command = "df -h | awk 'NR==2{printf \"%s: Used: %.2f%%, Total: %s\\n\", $1, $5, $2}'"

    for name, server in servers.items():
        result = execute_ssh_command(server, command)
        if result['status'] == 'success':
            # 解析输出，假设输出格式为 "/dev/sda1: Used: 76.9%, Total: 50G"
            disk_info = result['output']
            disk_usage.append({'server': name, 'disk_usage': disk_info})
        else:
            disk_usage.append(result)

    print(disk_usage)  # 打印在控制台
    return jsonify(disk_usage)  # 通过Web返回
@app.route('/scan_cpu_info', methods=['GET'])
def scan_cpu_info():
    cpu_info = []
    command = "lscpu"

    for name, server in servers.items():
        result = execute_ssh_command(server, command)
        if result['status'] == 'success':
            cpu_info.append({'server': name, 'cpu_info': result['output']})
        else:
            cpu_info.append(result)

    print(cpu_info)  # 打印在控制台
    return jsonify(cpu_info)  # 通过Web返回
@app.route('/scan_memory', methods=['GET'])
def scan_memory():
    memory_info = []
    command = "free -m | awk '/Mem:/ {printf \"%s: Used: %s MB, Free: %s MB, Total: %s MB\\n\", $2, $3, $4, $2}'"

    for name, server in servers.items():
        result = execute_ssh_command(server, command)
        if result['status'] == 'success':
            memory_info.append({'server': name, 'memory_info': result['output']})
        else:
            memory_info.append(result)

    print(memory_info)  # 打印在控制台
    return jsonify(memory_info)  # 通过Web返回
@app.route('/scan_dns', methods=['GET'])
def scan_dns():
    dns_info = []
    command = "cat /etc/resolv.conf"

    for name, server in servers.items():
        result = execute_ssh_command(server, command)
        if result['status'] == 'success':
            dns_info.append({'server': name, 'dns_info': result['output']})
        else:
            dns_info.append(result)

    print(dns_info)  # 打印在控制台
    return jsonify(dns_info)  # 通过Web返回
@app.route('/scan_ip_route', methods=['GET'])
def scan_ip_route():
    ip_route_info = []
    command = "ip route show"

    for name, server in servers.items():
        result = execute_ssh_command(server, command)
        if result['status'] == 'success':
            ip_route_info.append({'server': name, 'ip_route_info': result['output']})
        else:
            ip_route_info.append(result)

    print(ip_route_info)  # 打印在控制台
    return jsonify(ip_route_info)  # 通过Web返回

#
@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/isok')
def imfine():
    return jsonify({'status': 'OK'})

# trigger_fake_temprature     get请求   用于触发向http://127.0.0.1:5001/receiver_tem 发送一些伪造的数据报文
@app.route('/trigger_fake_temperature', methods=['GET'])
def trigger_fake_temperature():
    print(global_config)

    #fake_temperatures发出去的时候是是一个json化的列表    utc格式的时间戳对应着当前的温度   温度是2位小数  代表意思是精确到两位小数的摄氏度
    fake_temperatures = []
    for _ in range(10):
        temperature = round(random.uniform(20, 30), 2)
        # 获取当前时间的UTC时间戳
        utc_now = datetime.now(pytz.utc)

        # 将时间戳转换为字符串格式，以便JSON化
        mytimestamp = utc_now.isoformat()

        dt = datetime.fromisoformat(mytimestamp.replace('+00:00', 'Z'))

        # 将datetime对象转换为UTC时间的字符串，去掉微秒
        timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
        time.sleep(0.2)
        fake_temperatures.append({
            'timestamp': timestamp,
            'temperature': temperature
        })
    data = {
        'triggermethod': 'fake_trigger',
        'dataform': 'temperature',
        'datainfo': fake_temperatures
    }

    url = 'http://127.0.0.1:5000/basic_Monitor_receiver'
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            return jsonify(response.json()), response.status_code
        else:
            return jsonify(
                {'error': 'Failed to send temperature data', 'status': response.status_code}), response.status_code
    except requests.exceptions.RequestException as e:
        # 处理请求异常
        return jsonify({'error': str(e)}), 500


@app.route('/trigger_fake_humidity', methods=['GET'])
def trigger_fake_humidity():

    fake_humidity = []
    for _ in range(10):
        humidity = round(random.uniform(20, 30), 2)
        # 获取当前时间的UTC时间戳
        utc_now = datetime.now(pytz.utc)

        # 将时间戳转换为字符串格式，以便JSON化
        mytimestamp = utc_now.isoformat()

        dt = datetime.fromisoformat(mytimestamp.replace('+00:00', 'Z'))

        # 将datetime对象转换为UTC时间的字符串，去掉微秒
        timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
        time.sleep(0.2)
        fake_humidity.append({
            'timestamp': timestamp,
            'humidity': humidity
        })
    data = {
        'triggermethod': 'fake_trigger',
        'dataform': 'humidity',
        'datainfo': fake_humidity
    }

    url = 'http://127.0.0.1:5000/basic_Monitor_receiver'
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            return jsonify(response.json()), response.status_code
        else:
            return jsonify(
                {'error': 'Failed to send temperature data', 'status': response.status_code}), response.status_code
    except requests.exceptions.RequestException as e:
        # 处理请求异常
        return jsonify({'error': str(e)}), 500


# Hardware Monitoring   basic_Monitor_receiver
# 接收温度数据的路由
@app.route('/basic_Monitor_receiver', methods=['POST'])
def receive_data():
    data = request.json
    triggermethod = data.get('triggermethod')
    dataform = data.get('dataform')
    datainfo = data.get('datainfo')

    if datainfo:
        timestamps = [datetime.fromisoformat(item['timestamp']) for item in datainfo]
        start_time = min(timestamps).isoformat() + 'Z'
        end_time = max(timestamps).isoformat() + 'Z'
    else:
        start_time = end_time = datetime.now(pytz.utc).isoformat() + 'Z'

    # 将数据存储到数据库
    monitoropration.insert_data(start_time, end_time, triggermethod, dataform, json.dumps(datainfo))
    #从数据库里面把这个东西再查回来    作为json返回
    # 返回响应
    query_params = {
        'start_time': start_time,
        'end_time': end_time,
        'triggermethod': triggermethod,
        'dataform': dataform,

    }
    print("使用的上传参数应该是")
    print("query_params:", query_params)
    result = monitoropration.query_data(query_params)

    return jsonify({
        'message': '%s data received'%dataform,
        'triggermethod': triggermethod,
        'start_time': start_time,
        'end_time': end_time,
        'dataform': dataform,
        'datainfo': datainfo,
        'dbrecord': result
    }), 200
#触发定时任务  这个是定时轮询任务   同时也支持get请求手动触发 上传当前时间和当前时间前15分钟的时间这个里面的时间段里面的从monitor里面拿到的数据
#指定方向是 POST   方向是  8.137.104.90:5000  /receive all
# 定时任务来轮询数据，并且这个任务可以通过 GET 请求手动触发。这个任务会获取当前时间和当前时间前15分钟内的数据，并将这些数据通过 POST 请求发送到指定的地址（8.137.104.90:5000/receive_all）。
#这个需求的完成方法是？


# 初始化调度器
scheduler = BackgroundScheduler(timezone="UTC")
scheduler.start()
#传入时间偏移量
def getnow(offset_seconds=0):
    # 获取当前时间的UTC时间戳
    utc_now = datetime.now(pytz.utc)
    if offset_seconds != 0:
        utc_now = utc_now - timedelta(seconds=offset_seconds)

    # 将时间戳转换为字符串格式，以便JSON化
    mytimestamp = utc_now.isoformat()

    dt = datetime.fromisoformat(mytimestamp.replace('+00:00', 'Z'))

    # 将datetime对象转换为UTC时间的字符串，去掉微秒
    timestamp= dt.strftime('%Y-%m-%d %H:%M:%S')
    re=datetime.fromisoformat(timestamp).isoformat() + 'Z'

    return re

# 定义定时任务函数
def poll_and_send_data():
    end_time = getnow(0)
    start_time = getnow(1880000000)# 传入时间便宜30分钟

    query_params = {
        'start_time': start_time,
        'end_time': end_time

    }
    print("查询是")
    print(query_params)
    result = monitoropration.query_data(query_params)
    print(result)

    url = 'http://127.0.0.1:5000/receive_all'
    try:
        response = requests.post(url, json=result)
        if response.status_code == 200:
            print("有结构的")
            return {'status': 'success', 'data': result}


        else:
            print(f"Failed to send data, status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while sending data: {e}")


# 配置定时任务
scheduler.add_job(poll_and_send_data, 'interval', minutes=15)

# 随便发啥都返回他的POST报文的receive all 报文 的接口
@app.route('/receive_all', methods=['POST'])
def receive_all():
    # 获取请求体中的数据
    data = request.get_data()
    # 将数据转换为字符串（如果需要的话）
    data_str = data.decode('utf-8') if data else 'No data received'
    # 返回接收到的数据
    return jsonify({'received_data': data_str})

# 提供手动触发的路由
@app.route('/update_monitor', methods=['GET'])
def manual_poll_and_send():
    result =poll_and_send_data()
    print(result)
    return jsonify({
        'dbrecord': result
    }), 200

# 提供下达config配置的接口  并且需要支持热更新   就是不能重启才生效  要run的时候就生效的那种  就是查看怕config.json文件和修改这个文件 最后返回都是该文件最后的样子
@app.route('/config', methods=['GET', 'POST'])
def config_handler():
    if request.method == 'GET':
        try:
            # 每次 GET 请求时，读取并返回 config.json 文件内容
            with open("config.json", "r", encoding="utf-8") as config_file:
                global_config = json.load(config_file)

                return jsonify({"message": "配置已成功更新", "config":global_config }), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    elif request.method == 'POST':
        try:
            # 获取客户端传入的 JSON 数据
            new_config = request.json

            # 读取当前配置文件
            with open("config.json", "r", encoding="utf-8") as config_file:
                current_config = json.load(config_file)

            # 更新配置
            current_config.update(new_config)

            # 保存更新后的配置到 config.json 文件
            with open("config.json", "w", encoding="utf-8") as config_file:
                json.dump(current_config, config_file, indent=4, ensure_ascii=False)

            # 更新 app.config 使新配置立即生效
            app.config.update(current_config)

            # 重新读取配置文件以获取更新后的配置
            with open("config.json", "r", encoding="utf-8") as config_file:
                updated_config = json.load(config_file)

            return jsonify({"message": "配置已成功更新", "config": updated_config}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
@app.route('/config_useless', methods=['GET', 'POST'])
def update_config():
    global job  # 获取全局调度任务

    if request.method == 'GET':
        # 过滤掉不能序列化的配置项
        def filter_config(config):
            filtered_config = {}
            for key, value in config.items():
                try:
                    # 尝试将配置项序列化为 JSON，如果成功则保留
                    json.dumps(value)
                    filtered_config[key] = value
                except (TypeError, ValueError):
                    # 如果配置项不能被序列化则跳过
                    filtered_config[key] = str(value)  # 或者用 str 转换为字符串
            return filtered_config

        filtered_config = filter_config(app.config)
        return jsonify(filtered_config), 200

    elif request.method == 'POST':
        try:
            # 获取传入的 JSON 数据
            new_config = request.json

            # 更新调度器间隔
            if 'SCHEDULER_INTERVAL_MINUTES' in new_config:
                new_interval = new_config['SCHEDULER_INTERVAL_MINUTES']

                # 更新 app.config
                app.config['SCHEDULER_INTERVAL_MINUTES'] = new_interval

                # 重新调整调度器的间隔
                job.reschedule(trigger='interval', minutes=new_interval)

            # 其他配置的热更新
            if 'MONITOR_URL' in new_config:
                app.config['MONITOR_URL'] = new_config['MONITOR_URL']

            return jsonify({"message": "配置已成功更新", "config": dict(app.config)}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500


if __name__ == '__main__':


    #monitoropration.init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)



