import sqlite3
import app
conn = sqlite3.connect('monitor.db')

print('成功打开数据库')




def init_db():
    try:
        conn = sqlite3.connect('monitor.db')
        print('成功打开数据库')
        c = conn.cursor()
        c.execute('''
                CREATE TABLE IF NOT EXISTS monitorinfo (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time TEXT,
                    end_time TEXT,
                    triggermethod TEXT,
                    dataform TEXT,
                    datainfo TEXT
                )
            ''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()



def insert_data(start_time, end_time, triggermethod, dataform, datainfo):
    try:
        conn = sqlite3.connect('monitor.db')
        c = conn.cursor()
        c.execute('''
                INSERT INTO monitorinfo (start_time, end_time, triggermethod, dataform, datainfo)
                VALUES (?, ?, ?, ?, ?)
            ''', (start_time, end_time, triggermethod, dataform, datainfo))
        conn.commit()
        print('数据插入成功')
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()


def query_data(query_params=None):
    try:
        conn = sqlite3.connect('monitor.db')
        c = conn.cursor()
        # 基础的查询语句
        query = 'SELECT * FROM monitorinfo'
        # 检查是否有查询参数
        if query_params:
            # 初始化条件列表
            conditions = []
            params = []

            # 处理时间查询条件
            if 'start_time' in query_params:
                start_time = query_params.pop('start_time')
                conditions.append("datetime(start_time, 'utc') >= datetime(?, 'utc')")
                params.append(start_time)
            if 'end_time' in query_params:
                end_time = query_params.pop('end_time')
                conditions.append("datetime(end_time, 'utc') <= datetime(?, 'utc')")
                params.append(end_time)

            # 添加其他查询条件
            for key, value in query_params.items():
                conditions.append(f"{key} = ?")
                params.append(value)

            # 如果有多个条件，则用 AND 连接
            if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)
                c.execute(query, params)
            else:
                c.execute(query)
        else:
            c.execute(query)

        rows = c.fetchall()

        for row in rows:
            print(row)
        if query_params:
            print(f"满足查询条件 {query_params} 的记录是：")
            return rows
        else:
            print(f"满足查询条件 {query_params} 的记录是：")
            return rows

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()


def update_data(id, start_time, end_time, triggermethod, dataform, datainfo):
    try:
        conn = sqlite3.connect('monitor.db')
        c = conn.cursor()
        c.execute('''
                UPDATE monitorinfo
                SET start_time = ?, end_time = ?, triggermethod = ?, dataform = ?, datainfo = ?
                WHERE id = ?
            ''', (start_time, end_time, triggermethod, dataform, datainfo, id))
        conn.commit()
        print('数据更新成功')
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

# 删除数据
def delete_data(id):
    try:
        conn = sqlite3.connect('monitor.db')
        c = conn.cursor()
        c.execute('DELETE FROM monitorinfo WHERE id = ?', (id,))
        conn.commit()
        print('数据删除成功')
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

#清空表单全部数据
def clear_table():
    try:
        conn = sqlite3.connect('monitor.db')
        c = conn.cursor()
        # 删除表中的所有数据
        c.execute('DELETE FROM monitorinfo')
        conn.commit()
        print('表单数据已清空')
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()






































































#
# init_db()
#
# # 插入数据
# insert_data('2024-01-01 08:00', '2024-01-01 09:00', 'method1', 'form1', 'info1')
#
# # 查询数据
# query_data()
#
# # 更新数据
# update_data(1, '2024-01-02 08:00', '2024-01-02 09:00', 'method2', 'form2', 'info2')
#
# # 查询数据
# query_data()
#
# # 删除数据
# query_data({'start_time': '2024-01-01 08:00'})
#
# # 查询多个条件的数据，例如查询 start_time 为 '2024-01-01 08:00' 并且 triggermethod 为 'method2' 的数据
# query_data({'start_time': '2024-01-01 08:00', 'triggermethod': 'method2'})
#
# # 查询数据
# init_db()
# query_data()
# clear_table()
# query_data()
# insert_data('2024-01-01 07:30', '2024-01-01 09:00', 'method1', 'form1', 'info1')
# insert_data('2024-01-01 08:30', '2024-01-01 09:00', 'method1', 'form1', 'info1')
# insert_data('2024-01-01 09:30', '2024-01-01 10:00', 'method1', 'form1', 'info1')
# query_data({'start_time': '2024-01-01 08:00'})  # 查询所有开始时间在 '2024-01-01 08:00' 之后的记录
# query_data({'end_time': '2024-01-01 09:00'})   # 查询所有结束时间在 '2024-01-02 09:00' 之前的记录
# query_data({'start_time': '2024-01-01 08:20', 'end_time': '2024-01-01 10:00'})