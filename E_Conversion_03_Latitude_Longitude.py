import pandas as pd
import numpy as np
import os

# 配置区域
input_base_path = "./DataProcess/D_DividedData"  # 输入文件夹路径
output_base_path = "./DataProcess/E_ConversedData"  # 输出文件夹路径
filename_format = "Activity"  # 输出文件夹名称格式

input_lat_file = "Latitude.csv"  # 输入纬度文件
input_lon_file = "Longitude.csv"  # 输入经度文件
output_lat_file = "LatitudeDeg.csv"  # 输出转换后的纬度文件
output_lon_file = "LongitudeDeg.csv"  # 输出转换后的经度文件
output_lat_inter_file = "LatitudeDegInter.csv"  # 输出插值后的纬度文件
output_lon_inter_file = "LongitudeDegInter.csv"  # 输出插值后的经度文件

def convert_and_store_lat_lon(lat_file, lon_file, lat_output_file, lon_output_file, lat_inter_file, lon_inter_file):
    """
    将两个 CSV 文件中的原始纬度和经度信息进行转换，并保存到单独的 CSV 文件中。
    
    :param lat_file: 包含原始纬度信息的输入 CSV 文件名称。
    :param lon_file: 包含原始经度信息的输入 CSV 文件名称。
    :param lat_output_file: 存储转换后的纬度信息的输出 CSV 文件名称。
    :param lon_output_file: 存储转换后的经度信息的输出 CSV 文件名称。
    :param lat_inter_file: 存储插值后的纬度信息的输出 CSV 文件名称。
    :param lon_inter_file: 存储插值后的经度信息的输出 CSV 文件名称。
    """
    # 定义转换因子
    conversion_factor = (2**31 - 1)
    
    # 读取 CSV 文件
    raw_lat_df = pd.read_csv(lat_file, header=None).values.flatten()
    raw_lon_df = pd.read_csv(lon_file, header=None).values.flatten()
    
    # 将原始数据转换为度数
    lat_df = raw_lat_df.astype(float) / conversion_factor * 180
    lon_df = raw_lon_df.astype(float) / conversion_factor * 180

    # 定义插值因子
    factor = 10  # 每两个原始数据间插入9个值，总共生成10个值

    # 创建插值函数
    def interpolate(data, factor):
        x = np.arange(len(data))
        xi = np.linspace(0, len(data) - 1, len(data) * factor - (factor - 1))
        return np.interp(xi, x, data)

    # 对经纬度数据进行插值
    lon_interpolated = interpolate(lon_df, factor)
    lat_interpolated = interpolate(lat_df, factor)
    
    # 保存转换后的 DataFrame 到新的 CSV 文件
    pd.DataFrame(lat_df).to_csv(lat_output_file, index=False, header=False)
    print(f"转换后的纬度信息已保存到 '{lat_output_file}'")
    
    pd.DataFrame(lon_df).to_csv(lon_output_file, index=False, header=False)
    print(f"转换后的经度信息已保存到 '{lon_output_file}'")

    # 保存插值后的 DataFrame 到新的 CSV 文件
    pd.DataFrame(lat_interpolated).to_csv(lat_inter_file, index=False, header=False)
    print(f"插值后的纬度信息已保存到 '{lat_inter_file}'")
    
    pd.DataFrame(lon_interpolated).to_csv(lon_inter_file, index=False, header=False)
    print(f"插值后的经度信息已保存到 '{lon_inter_file}'")

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
        
        # 处理纬度和经度文件
        convert_and_store_lat_lon(
            os.path.join(input_folder_path, input_lat_file),
            os.path.join(input_folder_path, input_lon_file),
            os.path.join(output_folder_path, output_lat_file),
            os.path.join(output_folder_path, output_lon_file),
            os.path.join(output_folder_path, output_lat_inter_file),
            os.path.join(output_folder_path, output_lon_inter_file)
        )

if __name__ == "__main__":
    main()
