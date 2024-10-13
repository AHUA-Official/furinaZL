# -*- coding: utf-8 -*-
import random
import time
from datetime import datetime, timedelta
import json
import pytz
from apscheduler.schedulers.background import BackgroundScheduler

from flask import Flask, request, jsonify
import sqlite3
import requests
import monitoropration
app = Flask(__name__)







app = Flask(__name__)


# 初始化监控信息的数据表单
#创建一个monitor的数据库   创建一个monitorinfo的表单



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

# 随便发啥都返回他的POST报文的receive all 报文 的接口


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)



