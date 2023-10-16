import streamlit as st
import pandas as pd
import numpy as np
import psycopg2
from datetime import datetime, timedelta
import altair as alt

# 定义函数部分————开始
# PostgreSQL 连接信息
def connect_to_postgresql():
    # 如果用docker，需要实际的容器 IP 地址替换这里
    DB_HOST = "172.17.0.2"
    # 数据库端口号，通常是默认的 5432
    DB_PORT = "5432"
    # 数据库名称
    DB_NAME = "filecoindata"
    # 数据库用户名
    DB_USER = "txys"
    # 数据库密码
    DB_PASS = "txys2023"
    
    try:
        # 连接到 PostgreSQL 数据库
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        # 链接成功加说明
        return conn
    except Exception as e:
        print(f"An error occurred while connecting to PostgreSQL: {str(e)}")
        return None
    # 这里加链接数据库成功

# 查询函数，这部分用于构建之后所有计算的基础dataframe
def query_data_from_postgresql(conn, table_name):
    try:
        # 构建 SQL 查询语句
        query_base = f"SELECT * FROM {table_name};"
        
        # 查询数据
        df_base_ = []
        df_base_ = pd.read_sql_query(query_base, conn)
        return df_base_
    except Exception as e:
        print(f"An error occurred while querying data: {str(e)}")
        return None
    
# 计算7日函数，数据并返回一个包含7日数据的 DataFrame
def calculate_week_dataframe(df_base):
    # df_week_base 继承 df_base 全部数据
    df_week_base = pd.DataFrame()
    # 复制基础数据列到 df_week_base
    df_week_base['时间'] = df_base['time']
    df_week_base['节点号'] = df_base['node_id']
    df_week_base['总余额'] = df_base['total_balance']
    df_week_base['可提现'] = df_base['ava_balance']
    df_week_base['质押'] = df_base['ini_pledge']
    df_week_base['锁仓'] = df_base['lock_balance']
    df_week_base['owner余额'] = df_base['owner_balance']
    df_week_base['算力'] = df_base['power']
    df_week_base['理论幸运值'] = df_base['luck']
    
    # 使用 groupby 按照 '节点号' 分组，相同 '节点号' 的才可以进行计算
    grouped = df_week_base.groupby('节点号')

    # 计算变化和比率列
    df_week_base['总余额增减'] = grouped['总余额'].diff().round(2)
    df_week_base['总余额增减%'] = ((df_week_base['总余额增减'] / grouped['总余额'].shift(1)) * 100).round(2)
    df_week_base['可提现增减'] = grouped['可提现'].diff().round(2)
    df_week_base['可提现增减%'] = ((df_week_base['可提现增减'] / grouped['可提现'].shift(1)) * 100).round(2)
    df_week_base['质押增减'] = grouped['质押'].diff().round(2)
    df_week_base['质押增减%'] = ((df_week_base['质押增减'] / grouped['质押'].shift(1)) * 100).round(2)
    df_week_base['锁仓增减'] = grouped['锁仓'].diff().round(2)
    df_week_base['锁仓增减%'] = ((df_week_base['锁仓增减'] / grouped['锁仓'].shift(1)) * 100).round(2)
    df_week_base['owner余额增减'] = grouped['owner余额'].diff().round(2)
    df_week_base['owner余额增减%'] = ((df_week_base['owner余额增减'] / grouped['owner余额'].shift(1)) * 100).round(2)
    df_week_base['算力增减'] = grouped['算力'].diff().round(2)
    df_week_base['算力增减百分比'] = ((df_week_base['算力增减'] / grouped['算力'].shift(1)) * 100).round(2)

    # 计算 day_luck（这个特殊），注意此处先计算，后分组
    df_week_base['幸运值%'] = (df_week_base['总余额增减'] / df_week_base['算力'] / df_week_base['理论幸运值']).round(2)

    # 移除第一行 NaN 值
    df_week_base = df_week_base.dropna()
    
    # df_week_all_ 作为7日截取数据的节点汇总df
    # df_week_key_作为7日关键数据汇总的df
    # df_week_node_作为7日以节点号的数据汇总的df
    # 都先为空
    df_week_all_ = pd.DataFrame()
    df_week_node_ = pd.DataFrame()
    df_week_key_ = pd.DataFrame()
   
    # 计算出今日的日期today变量（date格式，对标df_base['时间']]）
    today = pd.to_datetime('today').date()
    
    # 计算出7天前的日期weekday变量（7日时间变量）
    weekday = (today - pd.DateOffset(days=6)).date()
    
    # 过滤出 df_week_base表中 2个时间段之间的全部行数据，导入df_week_all_
    df_week_all_ = df_week_base[(df_week_base['时间'] >= weekday) & (df_week_base['时间'] <= today)]


    # # 使用 groupby 按照 '节点号' 分组，相同 '节点号' 的才可以进行计算
    # grouped_node = df_week_all_.groupby('节点号')

    # 筛选出 today 时间下的 各 '节点号' 的节点号、算力、总余额，导入df_week_node_
    power_data_ = []
    power_data_ = df_week_all_[df_week_all_['时间'] == today]
    df_week_node_['节点号'] = power_data_['节点号'].reset_index(drop=True)
    df_week_node_['算力'] = power_data_['算力'].reset_index(drop=True)
    df_week_node_['总余额'] = power_data_['总余额'].reset_index(drop=True)


    # 筛选出 weekday 时间下的 各 '节点号' 的总余额，导入df_week_node_
    blance_data_ = []
    blance_data_ = df_week_all_[df_week_all_['时间'] == weekday]
    df_week_node_['7日前总余额'] = blance_data_['总余额'].reset_index(drop=True)

    # df_week_node_['总余额'] 减去 df_week_node_['7日前总余额']，求差后导入df_week_node_
    df_week_node_['总余额增减'] = df_week_node_['总余额'] - df_week_node_['7日前总余额']

    # 计算幸运值（这个特殊）
    df_week_node_['幸运值%'] = df_week_node_['总余额增减'] / df_week_node_['算力'] / df_week_all_['理论幸运值'].reset_index(drop=True)
    
    # 汇总出 today 时间下的 所有 '节点号' 的总余额（即today时间的df_week_all_['总余额']），求和后导入df_week_key_
    today_data_ = []
    today_data_ = df_week_all_[df_week_all_['时间'] == today]
    df_week_key_['总量'] = [today_data_['总余额'].sum()]

    # 汇总出 weekday 时间的 所有 '节点号' 的总余额（即weekday时间的df_week_all_['总余额']），求和后导入df_week_key_
    week_data_ = []
    week_data_ = df_week_all_[df_week_all_['时间'] == weekday]
    df_week_key_['7日前总量'] = [week_data_['总余额'].sum()]
    
    # df_week_key_['总量'] 减去 df_week_key_['7日前总量']，求差后导入df_week_key_
    df_week_key_['总增长量'] = df_week_key_['总量'] - df_week_key_['7日前总量']
    
    # df_week_key_['总增长量'] 除以 df_week_key_['7日前总量']，求商导入df_week_key_
    df_week_key_['总增长率'] = (df_week_key_['总增长量'] / df_week_key_['7日前总量']) * 100

    return df_week_key_, df_week_node_

# 计算30日函数，数据并返回一个包含30日数据的 DataFrame
def calculate_month_dataframe(df_base):
    # df_month_base 继承 df_base 全部数据
    df_month_base = pd.DataFrame()
    # 复制基础数据列到 df_week_base
    df_month_base['时间'] = df_base['time']
    df_month_base['节点号'] = df_base['node_id']
    df_month_base['总余额'] = df_base['total_balance']
    df_month_base['可提现'] = df_base['ava_balance']
    df_month_base['质押'] = df_base['ini_pledge']
    df_month_base['锁仓'] = df_base['lock_balance']
    df_month_base['owner余额'] = df_base['owner_balance']
    df_month_base['算力'] = df_base['power']
    df_month_base['理论幸运值'] = df_base['luck']
    
    # 使用 groupby 按照 '节点号'分组，相同 '节点号' 的才可以进行计算
    grouped = df_month_base.groupby('节点号')

    # 计算变化和比率列
    df_month_base['总余额增减'] = grouped['总余额'].diff().round(2)
    df_month_base['总余额增减%'] = ((df_month_base['总余额增减'] / grouped['总余额'].shift(1)) * 100).round(2)
    df_month_base['可提现增减'] = grouped['可提现'].diff().round(2)
    df_month_base['可提现增减%'] = ((df_month_base['可提现增减'] / grouped['可提现'].shift(1)) * 100).round(2)
    df_month_base['质押增减'] = grouped['质押'].diff().round(2)
    df_month_base['质押增减%'] = ((df_month_base['质押增减'] / grouped['质押'].shift(1)) * 100).round(2)
    df_month_base['锁仓增减'] = grouped['锁仓'].diff().round(2)
    df_month_base['锁仓增减%'] = ((df_month_base['锁仓增减'] / grouped['锁仓'].shift(1)) * 100).round(2)
    df_month_base['owner余额增减'] = grouped['owner余额'].diff().round(2)
    df_month_base['owner余额增减%'] = ((df_month_base['owner余额增减'] / grouped['owner余额'].shift(1)) * 100).round(2)
    df_month_base['算力增减'] = grouped['算力'].diff().round(2)
    df_month_base['算力增减百分比'] = ((df_month_base['算力增减'] / grouped['算力'].shift(1)) * 100).round(2)

    # 计算 幸运值（这个特殊），注意此处先计算，后分组
    df_month_base['幸运值%'] = (df_month_base['总余额增减'] / df_month_base['算力'] / df_month_base['理论幸运值']).round(2)

    # 移除第一行 NaN 值
    df_month_base = df_month_base.dropna()
    
    # df_month_all_ 作为30日截取数据的节点汇总df
    # df_month_key_作为30日关键数据汇总的df
    # df_month_node_作为30日以节点号的数据汇总的df
    # 都先为空
    df_month_all_ = pd.DataFrame()
    df_month_node_ = pd.DataFrame()
    df_month_key_ = pd.DataFrame()

    
    # 计算出今日的日期today变量（date格式，对标df_base['时间']]）
    today = pd.to_datetime('today').date()
    
    # 计算出30天前的日期monthday变量（30日时间变量）
    monthday = (today - pd.DateOffset(days=29)).date()

    # 过滤出 df_month_base表中 2个时间段之间的全部行数据，导入df_month_all_
    df_month_all_ = df_month_base[(df_month_base['时间'] >= monthday) & (df_month_base['时间'] <= today)]

    # # 使用 groupby 按照 '节点号' 分组，相同 '节点号' 的才可以进行计算
    # grouped_node = df_month_all_.groupby('节点号')

    # 筛选出 today 时间下的 各 '节点号' 的节点号、算力、总余额，导入df_week_node_
    power_data_ = []
    power_data_ = df_month_all_[df_month_all_['时间'] == today]
    df_month_node_['节点号'] = power_data_['节点号'].reset_index(drop=True)
    df_month_node_['算力'] = power_data_['算力'].reset_index(drop=True)
    df_month_node_['总余额'] = power_data_['总余额'].reset_index(drop=True)

    # 筛选出 weekday 时间下的 各 '节点号' 的总余额，导入df_week_node_
    blance_data_ = []
    blance_data_ = df_month_all_[df_month_all_['时间'] == monthday]
    df_month_node_['30日前总余额'] = blance_data_['总余额'].reset_index(drop=True)

    # df_week_node_['总余额'] 减去 df_week_node_['7日前总余额']，求差后导入df_week_node_
    df_month_node_['总余额增减'] = df_month_node_['总余额'] - df_month_node_['30日前总余额']

    # 计算幸运值（这个特殊）
    df_month_node_['幸运值%'] = df_month_node_['总余额增减'] / df_month_node_['算力'] / df_month_all_['理论幸运值'].reset_index(drop=True)

    # 汇总出 today 时间下的 所有 '节点号' 的总余额（即today时间的df_month_all_['总余额']），求和后导入df_month_key_
    today_data_ = []
    today_data_ = df_month_all_[df_month_all_['时间'] == today]
    df_month_key_['总量'] = [today_data_['总余额'].sum()]
    
    # 汇总出 monthday 时间的 所有 '节点号' 的总余额（即weekday时间的df_month_all_['总余额']），求和后导入df_month_key_
    month_data_ = []
    month_data_ = df_month_all_[df_month_all_['时间'] == monthday]
    df_month_key_['30日前总量'] = [month_data_['总余额'].sum()]
    
    # df_month_key_['总量'] 减去 df_month_key_['30日前总量']，求差后导入df_month_key_
    df_month_key_['总增长量'] = df_month_key_['总量'] - df_month_key_['30日前总量']
    
    # df_month_key_['总增长量'] 除以 df_month_key_['30日前总量']，求商导入df_month_key_
    df_month_key_['总增长率'] = (df_month_key_['总增长量'] / df_month_key_['30日前总量']) * 100

    return df_month_key_, df_month_node_


# 画图函数
def draw_chart(df_week_node, df_month_node, chart_name):

    title1 = '7日'+chart_name+'数据'
    # 计算7日均值
    mean1 = df_week_node[chart_name].mean()
    
    # 构造7日图表
    chart1 = alt.Chart(df_week_node[['节点号', chart_name]]).mark_bar().encode(
        x='节点号',
        y=chart_name,
        color=alt.condition(
            alt.datum[chart_name] < mean1,
            alt.value('red'),
            alt.value('steelblue')
        )
    ).properties(
        title = title1
    )

    mean_name1 = 'mean' + '(' + chart_name + ')'
    mean_line1 = alt.Chart(df_week_node[['节点号', chart_name]]).mark_rule(color='green').encode(y=mean_name1)
    
    # 7日文本标记
    text1 = chart1.mark_text(
        align='center',
        baseline='middle',
        # baseline='top',
        dx=0).encode(
        text=chart_name
    )
    

    # 构造30日图表
    title2 = '30日'+chart_name+'数据'
    # 计算30日均值
    mean2 = df_month_node[chart_name].mean()

    chart2 = alt.Chart(df_month_node[['节点号', chart_name]]).mark_bar().encode(
        x='节点号',
        y=chart_name,
        color=alt.condition(
            alt.datum[chart_name] < mean2,
            alt.value('red'),
            alt.value('steelblue')
        )
    ).properties(
        title = title2
    )

    mean_name2 = 'mean' + '(' + chart_name + ')'
    # mean_line2 = alt.Chart(df_month_node[['节点号', chart_name]]).mark_rule(color='green').encode(y='mean(幸运值%)')
    mean_line2 = alt.Chart(df_month_node[['节点号', chart_name]]).mark_rule(color='green').encode(y=mean_name2)
    
    # 30日文本标记
    text2 = chart2.mark_text(
        align='center',
        baseline='middle',
        dx=0).encode(
        text=chart_name
    )

    #可以通过设置图表的 width 和 height 参数来控制两个柱状图的间距:
    # 设置图表1的宽度
    chart1 = chart1.properties(width=200) 
    # 设置图表2的宽度  
    chart2 = chart2.properties(width=200)
    # 设置图表1的高度
    chart1 = chart1.properties(height=400)
    # 设置图表2的高度
    chart2 = chart2.properties(height=400)
    
    # 并列显示
    final_chart_ = alt.hconcat(
        chart1 + mean_line1 + text1,
        chart2 + mean_line2 + text2
    )

    return final_chart_

# 定义函数部分————结束

# 主程序部分————开始
# 一般用try开始

# 连接到 PostgreSQL
conn = connect_to_postgresql()
# print (conn)

# 指定要查询的数据库表名
table_name = "base_statistics"

# 执行查询函数，生成基础数据df表单
df_base = query_data_from_postgresql(conn, table_name)
print('基础数据')
print(df_base)
    
# 执行计算7日函数，生成最终展示的7日两份df数据（汇总数据和全部数据）
df_week_key, df_week_node = calculate_week_dataframe(df_base)
print('7日数据')
print(df_week_key)
print(df_week_node)

# 执行计算30日函数，生成最终展示的30日两份df数据（汇总数据和全部数据）
df_month_key, df_month_node = calculate_month_dataframe(df_base)
print('30日数据')
print(df_month_key)
print(df_month_node)

# 第一部分：数据汇总部分
st.title('F-业务数据汇总')

# 数据汇总部分
st.title('7日数据汇总')
col1, col2, col3 = st.columns(3)
col1.metric("当前总量", f"{(df_week_key['总量'].values).round(2)}" "FIL")
col2.metric("总增长量", f"{(df_week_key['总增长量'].values).round(2)}" "FIL")
col3.metric("总增长率", f"{(df_week_key['总增长率'].values).round(2)}" "%")
st.title('30日数据汇总')
col1, col2, col3 = st.columns(3)
col1.metric("总当前量", f"{(df_month_key['总量'].values).round(2)}" "FIL")
col2.metric("总增长量", f"{(df_month_key['总增长量'].values).round(2)}" "FIL")
col3.metric("总增长率", f"{(df_month_key['总增长率'].values).round(2)}" "%")


# 第二部分：图标展示


#2.1  幸运值柱状图幸运值柱状图
st.title('幸运值柱状图')
chart_name1 = '幸运值%'
final_chart1 = draw_chart(df_week_node, df_month_node, chart_name1)
st.altair_chart(final_chart1)


# #2.2  各个节点算力图
st.title('算力柱状图')
chart_name2 = '算力'
final_chart2 = draw_chart(df_week_node, df_month_node, chart_name2)
st.altair_chart(final_chart2)


# #2.3  各个节点的总额柱状图
st.title('总余额柱状图')
chart_name3 = '总余额'
final_chart3 = draw_chart(df_week_node, df_month_node, chart_name3)
st.altair_chart(final_chart3)


#第三部分数据详单
st.title('7日汇总数据单')
st.dataframe(df_week_key)
st.title('7日数据详单')
st.dataframe(df_week_node)

st.title('30日汇总数据单')
st.dataframe(df_month_key)
st.title('30日数据详单')
st.dataframe(df_month_node)

# 主程序部分————结束
