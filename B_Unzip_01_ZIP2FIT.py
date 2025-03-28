import os
import zipfile

# 设置要读取和解压的.zip文件的路径及解压后的保存路径
zip_files_path = "./DataProcess/A_OriginZIPData"  # 下载的.zip文件存放路径
extract_path = "./DataProcess/B_FITData"  # 解压后的文件存放路径
filename_format = "FITData"  # 解压后的文件名称格式

def unzip_and_rename(zip_file_name, new_file_name):
    """解压 .zip 文件并重命名解压后的文件。"""
    with zipfile.ZipFile(zip_file_name, 'r') as zip_ref:
        # 获取 zip 存档中的所有文件列表
        zip_info_list = zip_ref.infolist()
        
        # 解压并重命名每个文件
        for zip_info in zip_info_list:
            # 解压文件
            extracted_path = zip_ref.extract(zip_info, extract_path)

            # 获取原始文件名
            original_file_name = os.path.basename(zip_info.filename)

            # 定义新的文件路径
            new_file_path = os.path.join(os.path.dirname(extracted_path), new_file_name)

            # 如果存在同名文件，则删除
            if os.path.exists(new_file_path):
                os.remove(new_file_path)

            # 重命名文件
            os.rename(extracted_path, new_file_path)

def main():
    # 确保解压后的保存目录存在
    if not os.path.exists(extract_path):
        os.makedirs(extract_path)

    # 获取所有.zip文件
    zip_files = [f for f in os.listdir(zip_files_path) if f.endswith('.zip')]
    
    # 依次处理每个.zip文件
    for i, zip_file in enumerate(zip_files, start=1):
        zip_file_path = os.path.join(zip_files_path, zip_file)
        new_file_name = f"{filename_format}{i}.fit"
        unzip_and_rename(zip_file_path, new_file_name)
        
    print(f"已完成")


if __name__ == "__main__":
    main()
