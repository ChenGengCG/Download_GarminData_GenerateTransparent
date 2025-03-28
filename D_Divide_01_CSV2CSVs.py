import csv
import os

# 配置区域
input_csv_path = "./DataProcess/C_CSVData"  # 输入 CSV 文件路径
output_base_path = "./DataProcess/D_DividedData"  # 输出文件夹路径
filename_format = "Activity"  # 输出文件夹名称格式

# 输出配置（文件名: 需要保留的列）
output_config = {
        "Date.csv": ["timestamp"],  
        "Latitude.csv": ["position_lat"],         
        "Longitude.csv": ["position_long"],
        "Distance.csv": ["distance"],
        "Speed.csv": ["enhanced_speed"],
        "Altitude.csv": ["enhanced_altitude"],
        "Power.csv": ["power"],
        "VerticalOscillation.csv": ["vertical_oscillation"],
        "StanceTime.csv": ["stance_time"],
        "VerticalRatio.csv": ["vertical_ratio"],
        "StepLength.csv": ["step_length"],
        "HeartRate.csv": ["heart_rate"],
        "Cadencea.csv": ["cadence"],
        "Cadenceb.csv": ["fractional_cadence"]
}

def split_csv_with_config(input_file, output_config, output_folder):
    """
    按列分割 CSV 文件核心函数
    :param input_file: 输入 CSV 文件路径
    :param output_config: 输出配置字典 {输出文件名: [要保留的列名列表]}
    :param output_folder: 输出文件夹路径
    """
    # 读取输入文件的列名
    with open(input_file, 'r', newline='', encoding='utf-8') as f_in:
        reader = csv.DictReader(f_in)
        original_columns = reader.fieldnames
        
        # 验证所有配置中的列名合法
        for filename, columns in output_config.items():
            for col in columns:
                if col not in original_columns:
                    raise ValueError(f"列 '{col}' 不存在于输入文件中")

        # 初始化输出文件写入器
        writers = {}
        for filename, columns in output_config.items():
            output_file_path = os.path.join(output_folder, filename)
            f_out = open(output_file_path, 'w', newline='', encoding='utf-8')
            writer = csv.DictWriter(f_out, fieldnames=columns)
            writer.writeheader()  # 写入标题
            writers[filename] = (writer, f_out)

        # 逐行处理数据
        for row in reader:
            for filename, (writer, _) in writers.items():
                selected_cols = {col: row[col] for col in output_config[filename]}
                writer.writerow(selected_cols)

        # 关闭所有输出文件
        for _, f_out in writers.values():
            f_out.close()

    # 删除每个输出文件的第一行（标题行）
    for filename in output_config.keys():
        output_file_path = os.path.join(output_folder, filename)
        with open(output_file_path, 'r', newline='', encoding='utf-8') as f:
            lines = f.readlines()
        with open(output_file_path, 'w', newline='', encoding='utf-8') as f:
            f.writelines(lines[1:])  # 跳过第一行

def main():
    # 确保输出文件夹存在
    if not os.path.exists(output_base_path):
        os.makedirs(output_base_path)

    # 获取所有 .csv 文件
    csv_files = [f for f in os.listdir(input_csv_path) if f.endswith('.csv')]

    # 依次处理每个 .csv 文件
    for i, csv_file in enumerate(csv_files, start=1):
        input_file_path = os.path.join(input_csv_path, csv_file)
        output_folder = os.path.join(output_base_path, f"{filename_format}{i}")
        
        # 确保输出文件夹存在
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        split_csv_with_config(input_file_path, output_config, output_folder)

    print(f'已完成')
if __name__ == "__main__":
    main()
