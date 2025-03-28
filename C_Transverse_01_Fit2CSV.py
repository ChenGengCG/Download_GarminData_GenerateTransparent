from fitparse import FitFile
import pandas as pd
import os

# 设置要读取和转换的 .fit 文件的路径及转换后的保存路径
fit_files_path = "./DataProcess/B_FITData"  # 解压出的 .fit 文件存放路径
save_path = "./DataProcess/C_CSVData"  # 转换后的 .csv 文件存放路径
filename_format = "CSVData"  # 转换后的文件名称格式

def fit_to_csv(fit_file_name, new_file_name):
    """将 .fit 文件转换为 .csv 文件。"""
    fit_file = FitFile(fit_file_name)
    data = []
    for record in fit_file.get_messages('record'):
        fields = record.get_values()
        data.append(fields)
    
    df = pd.DataFrame(data)
    new_file_path = os.path.join(save_path, new_file_name)
    
    if os.path.exists(new_file_path):
        os.remove(new_file_path)
        
    df.to_csv(new_file_path, index=False)

def main():
    # 确保转换后的保存目录存在
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # 获取所有 .fit 文件
    fit_files = [f for f in os.listdir(fit_files_path) if f.endswith('.fit')]

    # 依次处理每个 .fit 文件
    for i, fit_file in enumerate(fit_files, start=1):
        fit_file_path = os.path.join(fit_files_path, fit_file)
        new_file_name = f"{filename_format}{i}.csv"
        fit_to_csv(fit_file_path, new_file_name)

    print(f"已完成")


if __name__ == "__main__":
    main()
