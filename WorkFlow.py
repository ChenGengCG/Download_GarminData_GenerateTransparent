import subprocess

# 文件名列表
filenames = [
    "A_Download_01_GarminActivity.py",
    "B_Unzip_01_ZIP2FIT.py",
    "C_Transverse_01_Fit2CSV.py",
    "D_Divide_01_CSV2CSVs.py",
    "E_Conversion_01_Speed_HeartRate_Cadence_Power.py",
    "E_Conversion_02_Distance.py",
    "E_Conversion_03_Latitude_Longitude.py",
    "E_Conversion_04_DatenTime.py",
    "F_Frames_01_Speed_HeartRate_Cadence_Power.py",
    "F_Frames_02_ProgressBar.py",
    "F_Frames_03_Trace.py",
    "F_Frames_04_DatenTime.py"
]

# 依次执行每个.py文件
for filename in filenames:
    print(f"正在执行: {filename}")
    result = subprocess.run(["python", filename], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"执行 {filename} 时出错: {result.stderr}")
    print(f"完成: {filename}\n")
