import pandas as pd
import numpy as np
import os
import shutil

# 配置区域
input_base_path = "./DataProcess/D_DividedData"  # 输入文件夹路径
output_base_path = "./DataProcess/E_ConversedData"  # 输出文件夹路径
filename_format = "Activity"  # 输出文件夹名称格式

# 要处理的文件和输出配置
input_speed_file = "Speed.csv"  # 输入速度文件
output_speed_file = "SpeedConversed.csv"  # 输出速度文件

input_cadence_a_file = "Cadencea.csv"  # 输入步幅文件 A
input_cadence_b_file = "Cadenceb.csv"  # 输入步幅文件 B
output_cadence_file = "CadenceConversed.csv"  # 输出步幅文件

input_power_file = "Power.csv"  # 输入功率文件
output_power_file = "PowerConversed.csv"  # 输出功率文件

# 要直接转移的文件
files_to_transfer = [
    "HeartRate.csv"  # 直接转移的文件
]

def convert_all_speed_to_pace(input_file, output_file):
    """
    将 CSV 文件中的所有速度 (km/h) 列转换为跑步配速 (min/km)，并将零速度替换为特殊符号。
    修改后的数据将保存到新文件中。
    
    :param input_file: 输入 CSV 文件的名称。
    :param output_file: 输出 CSV 文件的名称。
    """
    # 读取 CSV 文件
    df = pd.read_csv(input_file, header=None)
    
    # 将速度 (km/h) 转换为配速 (min/km) 的函数
    def speed_to_pace(speed):
        if speed <= 1.2:
            return "--"  # 零速度的特殊符号
        pace = 60 / (speed * 3.6)
        minutes = int(pace)
        seconds = int((pace - minutes) * 60)
        return f"{minutes}:{seconds:02d}"
    
    # 将转换函数应用于所有列
    for col in df.columns:
        df[col] = df[col].apply(lambda x: speed_to_pace(x) if isinstance(x, (int, float)) else x)

    # 保存修改后的 DataFrame 到新 CSV 文件
    df.to_csv(output_file, index=False, header=False)
    print(f"将所有速度列转换为配速并保存到 '{output_file}'")

def transfer_files(input_folder_path, output_folder_path, files_to_transfer):
    """
    将指定的文件不加改动直接转移到目标文件夹中。
    
    :param input_folder_path: 输入文件夹的路径。
    :param output_folder_path: 输出文件夹的路径。
    :param files_to_transfer: 要直接转移的文件列表。
    """
    for transfer_file in files_to_transfer:
        input_file_path = os.path.join(input_folder_path, transfer_file)
        output_file_path = os.path.join(output_folder_path, transfer_file)
        if os.path.exists(output_file_path):
            os.remove(output_file_path)  # 如果存在同名文件，则删除
        shutil.copy(input_file_path, output_file_path)
        print(f"已将心率数据直接转移到 '{output_file_path}'")

def process_csv_files(file1, file2, output_file):
    """
    读取两个 CSV 文件，将它们按次序相加，再乘以 2，并将结果输出到新的 CSV 文件中。
    只保留结果的整数部分。

    :param file1: 第一个输入 CSV 文件的路径。
    :param file2: 第二个输入 CSV 文件的路径。
    :param output_file: 输出 CSV 文件的路径。
    """
    # 读取 CSV 文件
    df1 = pd.read_csv(file1, header=None)
    df2 = pd.read_csv(file2, header=None)
    
    # 按次序相加并乘以 2
    result_df = (df1 + df2) * 2

    # 只保留整数部分
    result_df = np.floor(result_df).astype(int)

    # 判断是否小于115，若小于115，则输出相应结果
    result_df = result_df.map(lambda x: '--' if x < 115 else x)
    
    # 输出到新的 CSV 文件
    result_df.to_csv(output_file, index=False, header=False)
    print(f"处理后的步频数据保存到 '{output_file}'")

def process_csv_power(file1, output_file):
    """
    读取 CSV 文件，判断是否小于200，若小于200，则输出一符号，再将结果输出到新的 CSV 文件。

    :param file1: 输入 CSV 文件的路径。
    :param output_file: 输出 CSV 文件的路径。
    """
    # 读取 CSV 文件
    dfpower = pd.read_csv(file1, header=None)

    # 判断是否小于200，若小于200，则输出一符号
    dfpower = dfpower.map(lambda x: '--' if x < 200 else x)
    
    # 输出到新的 CSV 文件
    dfpower.to_csv(output_file, index=False, header=False)
    print(f"处理后的功率数据保存到 '{output_file}'")

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
        
        # 处理速度文件
        convert_all_speed_to_pace(os.path.join(input_folder_path, input_speed_file), os.path.join(output_folder_path, output_speed_file))

        # 直接转移文件
        transfer_files(input_folder_path, output_folder_path, files_to_transfer)
        
        # 处理步幅文件
        process_csv_files(os.path.join(input_folder_path, input_cadence_a_file), os.path.join(input_folder_path, input_cadence_b_file), os.path.join(output_folder_path, output_cadence_file))
        
        # 处理功率文件
        process_csv_power(os.path.join(input_folder_path, input_power_file), os.path.join(output_folder_path, output_power_file))

if __name__ == "__main__":
    main()
