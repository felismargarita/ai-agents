import mysql.connector
from mysql.connector import Error
import os


def execute(sql: str):
  try:
      # 1. 建立数据库连接 [1,2,5](@ref)
      conn = mysql.connector.connect(
          host=os.getenv("MYSQL_HOST"),      # 数据库IP地址
          user=os.getenv("MYSQL_USER"),  # 用户名
          password=os.getenv("MYSQL_PASSWORD"), # 密码
          database=os.getenv("MYSQL_SCHEMA")  # 数据库名
      )
      
      if conn.is_connected():
          db_info = conn.get_server_info()
          print(f"✅ 成功连接 MySQL 服务器 (版本: {db_info})")
          
          # 2. 创建游标对象 [1,6](@ref)
          cursor = conn.cursor()
          
          cursor.execute(sql)
          
          # 4. 获取并处理结果 [1,4](@ref)
          # 方法1: 获取所有结果
          results = cursor.fetchall()
          print(f"查询到 {cursor.rowcount} 条记录")
          
          # 方法2: 逐行获取（适合大数据量）
          # for (id, name, email) in cursor:
          #     print(f"ID: {id}, Name: {name}, Email: {email}")
          
          # 5. 打印结果
          # print("\n查询结果：", results)

          return results

  except Error as e:
      print(f"❌ 数据库错误: {e}")
      
  finally:
      # 6. 关闭资源（必须执行）[4,6](@ref)
      if 'cursor' in locals() and cursor is not None:
          cursor.close()
      if conn.is_connected():
          conn.close()
          print("✅ 数据库连接已关闭")