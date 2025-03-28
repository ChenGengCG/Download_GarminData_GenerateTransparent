import pandas as pd
import os

# 配置区域
input_base_path = "./DataProcess/D_DividedData"  # 输入文件夹路径
output_base_path = "./DataProcess/E_ConversedData"  # 输出文件夹路径
filename_format = "Activity"  # 输出文件夹名称格式

input_distance_file = "Distance.csv"  # 输入距离文件
output_distance_file = "DistanceConversed.csv"  # 输出距离文件

def process_distance_file(input_file, output_file):
    """
    读取 CSV 文件，将每个值除以 1000，保留两位小数，并将结果输出到新的 CSV 文件。

    :param input_file: 输入 CSV 文件的路径。
    :param output_file: 输出 CSV 文件的路径。
    """
    # 读取 CSV 文件
    df = pd.read_csv(input_file, header=None)
    
    # 除以 1000 并保留两位小数
    result_df = df / 1000
    result_df = result_df.round(2)
    
    # 输出到新的 CSV 文件
    result_df.to_csv(output_file, index=False, header=False)
    print(f"处理后的距离数据保存到 '{output_file}'")

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
        
        # 处理距离文件
        process_distance_file(
            os.path.join(input_folder_path, input_distance_file),
            os.path.join(output_folder_path, output_distance_file)
        )

if __name__ == "__main__":
    main()
