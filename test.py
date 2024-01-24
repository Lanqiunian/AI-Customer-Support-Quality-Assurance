from datetime import datetime


def calculate_time_difference(time1, time2):
    # 定义时间的格式
    time_format = '%Y/%m/%d %H:%M'

    # 将字符串时间转换为datetime对象
    datetime1 = datetime.strptime(time1, time_format)
    datetime2 = datetime.strptime(time2, time_format)

    # 计算时间差异并转换为分钟
    time_difference = abs(datetime1 - datetime2)
    minutes_difference = time_difference.total_seconds() / 60

    return minutes_difference


# 测试函数
time_diff = calculate_time_difference("2023/8/20 16:05", "2023/8/20 16:06")
print(f"时间差（分钟）: {time_diff}")
