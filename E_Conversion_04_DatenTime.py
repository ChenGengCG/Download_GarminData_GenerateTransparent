import pandas as pd
from datetime import datetime, timedelta
import pytz
import os

# 配置区域
input_base_path = "./DataProcess/D_DividedData"  # 输入文件夹路径
output_base_path = "./DataProcess/E_ConversedData"  # 输出文件夹路径
filename_format = "Activity"  # 输出文件夹名称格式
input_date_file = "Date.csv"  # 输入日期文件
output_date_day_file = "DateDay.csv"  # 输出日期文件
output_date_time_file = "DateTime.csv"  # 输出时间文件
output_date_delta_file = "DateDelta.csv"  # 输出相对时间文件

def process_date_file(input_file, output_day_file, output_time_file, output_delta_file):
    """
    读取 CSV 文件，将时间转换为目标时区，并提取日期、时间和相对时间，保存到新的 CSV 文件中。

    :param input_file: 输入 CSV 文件的路径。
    :param output_day_file: 输出日期信息的 CSV 文件路径。
    :param output_time_file: 输出时间信息的 CSV 文件路径。
    :param output_delta_file: 输出相对时间信息的 CSV 文件路径。
    """
    # 读取 CSV 文件
    df = pd.read_csv(input_file, header=None)
    timestamps = df[0].to_list()

    # 定义原始时区和目标时区
    original_tz = pytz.timezone('UTC')
    target_tz = pytz.timezone('Asia/Shanghai')

    # 转换时间并提取日期和时间
    dates = []
    times = []
    relative_times = []
    base_time = None

    for timestamp in timestamps:
        # 解析时间
        try:
            # 解析时间，处理 YYYY-MM-DD HH:MM:SS 格式
            dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                # 解析时间，处理 YYYY/MM/DD HH:MM:SS 格式
                dt = datetime.strptime(timestamp, '%Y/%m/%d %H:%M:%S')
            except ValueError:
                raise ValueError(f"时间数据 '{timestamp}' 格式不正确")

        dt = original_tz.localize(dt)
        dt = dt.astimezone(target_tz)

        # 提取日期和时间
        date_str = dt.strftime('%Y/%m/%d')
        time_str = dt.strftime('%H:%M:%S')
        dates.append(date_str)
        times.append(time_str)

        # 计算相对时间
        if base_time is None:
            base_time = dt
        relative_time = (dt - base_time).total_seconds()
        hours, remainder = divmod(int(relative_time), 3600)
        minutes, seconds = divmod(remainder, 60)
        relative_time_str = f'{hours:02}:{minutes:02}:{seconds:02}'
        relative_times.append(relative_time_str)

    # 保存到新的 CSV 文件
    pd.DataFrame(dates).to_csv(output_day_file, header=False, index=False)
    pd.DataFrame(times).to_csv(output_time_file, header=False, index=False)
    pd.DataFrame(relative_times).to_csv(output_delta_file, header=False, index=False)
    print(f"处理后的数据已保存到 '{output_day_file}', '{output_time_file}', '{output_delta_file}'")

def main():
    # 确保输出文件夹存在
    if not os.path.exists(output_base_path):
        os.makedirs(output_base_path)

    # 获取所有分割后的文件夹
    activity_folders = [f for f in os.listdir(input_base_path) if os.path.isdir(os.path.join(input_base_path, f))]

    # 依次处理每个文件夹
    for i, folder in enumerate(activity_folders, start=1):
        input_folder_path = os.path.join(input_base_path, folder)
        output_folder_path = os.path.join(output_base_path, f"{filename_format}{i}")
        
        # 确保输出文件夹存在
        if not os.path.exists(output_folder_path):
            os.makedirs(output_folder_path)
        
        # 处理日期文件
        process_date_file(
            os.path.join(input_folder_path, input_date_file),
            os.path.join(output_folder_path, output_date_day_file),
            os.path.join(output_folder_path, output_date_time_file),
            os.path.join(output_folder_path, output_date_delta_file)
        )

if __name__ == "__main__":
    main()
