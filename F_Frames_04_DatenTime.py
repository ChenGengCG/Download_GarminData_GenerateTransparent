import csv
import os
from PIL import Image, ImageDraw, ImageFont
import concurrent.futures

# ================== 配置参数 ==================
CONFIG = {
    "input_base_path": "./DataProcess/E_ConversedData",  # 输入文件夹路径
    "output_base_path": "./DataProcess/F_Frames",  # 输出文件夹路径
    "filename_format": "Activity",  # 文件夹名称格式
    "frame_size": (1920, 1080),  # 帧尺寸(宽,高)
    "background_color": (0, 0, 0, 0),  # 透明背景RGBA
    "frame_prefix": "frame_",  # 帧序列自动编号前的名称
    "use_multithreading": True,  # 是否使用多线程
    "use_multiprocessing": True,  # 是否使用多核心

    # CSV文件配置列表（可配置多个）
    "csv_configs": [
        {
            "file": "DateDelta.csv",
            "position": (1500, 700),
            "font": "SourceHanSans-Heavy.ttc",
            "font_size": 50,
            "font_color": (0, 0, 0, 255),
            "stroke_color": (0, 255, 255, 255),  # 描边颜色
            "stroke_width": 2,  # 描边宽度
            "row_spacing": 20
        },
        {
            "file": "DateTime.csv",  # CSV文件路径
            "position": (1500, 800),  # 起始坐标(x,y)
            "font": "SourceHanSans-Heavy.ttc",  # 字体文件路径
            "font_size": 50,  # 字体大小
            "font_color": (0, 0, 0, 255),
            "stroke_color": (0, 255, 255, 255),  # 描边颜色
            "stroke_width": 2,  # 描边宽度
            "row_spacing": 20  # 行间距(像素)
        },
        {
            "file": "DateDay.csv",  # CSV文件路径
            "position": (1500, 900),  # 起始坐标(x,y)
            "font": "SourceHanSans-Heavy.ttc",  # 字体文件路径
            "font_size": 50,  # 字体大小
            "font_color": (0, 0, 0, 255),
            "stroke_color": (0, 255, 255, 255),  # 描边颜色
            "stroke_width": 2,  # 描边宽度
            "row_spacing": 20  # 行间距(像素)
        }
    ]
}

# ================== 核心功能 ==================
class TextFrameGenerator:
    def __init__(self, config, activity_index):
        self.config = config
        self.csv_data = []
        self.max_rows = 0
        self.input_folder_path = os.path.join(config["input_base_path"], f"{config['filename_format']}{activity_index}")
        self.output_dir = os.path.join(config["output_base_path"], f"{config['filename_format']}{activity_index}/DatenTime")
        
        # 验证并加载所有CSV数据
        self._load_csv_files()
        
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _load_csv_files(self):
        """加载并验证所有CSV文件"""
        for cfg in self.config["csv_configs"]:
            try:
                file_path = os.path.join(self.input_folder_path, cfg["file"])
                with open(file_path, "r") as f:
                    reader = csv.reader(f)
                    data = [row[0] for row in reader]  # 假设每行只有一列数据
                    self.csv_data.append(data)
                    
                    # 更新最大行数
                    if len(data) > self.max_rows:
                        self.max_rows = len(data)
            except Exception as e:
                print(f"读取 {cfg['file']} 时出错: {e}")
                raise
        
        # 验证所有CSV行数一致
        for i, data in enumerate(self.csv_data):
            if len(data) != self.max_rows:
                raise ValueError(f"文件 {self.config['csv_configs'][i]['file']} 行数不一致")

    def _draw_text_with_stroke(self, draw, position, text, font, fill, stroke_fill, stroke_width):
        """在指定位置绘制带描边的文本"""
        x, y = position
        # 绘制描边
        for offset in range(-stroke_width, stroke_width + 1):
            if offset != 0:
                draw.text((x + offset, y), text, font=font, fill=stroke_fill)
                draw.text((x - offset, y), text, font=font, fill=stroke_fill)
                draw.text((x, y + offset), text, font=font, fill=stroke_fill)
                draw.text((x, y - offset), text, font=font, fill=stroke_fill)
        # 绘制文本
        draw.text(position, text, font=font, fill=fill)

    def _create_frame(self, frame_num):
        """创建单个帧"""
        # 创建透明画布
        img = Image.new("RGBA", self.config["frame_size"], self.config["background_color"])
        draw = ImageDraw.Draw(img)
        
        # 遍历所有CSV配置
        for cfg_idx, cfg in enumerate(self.config["csv_configs"]):
            data = self.csv_data[cfg_idx]
            x, y = cfg["position"]  # 重新设置初始位置
            font = ImageFont.truetype(cfg["font"], cfg["font_size"])
            
            # 处理当前行数据
            current_data = f"{data[frame_num]}"
            
            # 绘制带描边的文本
            self._draw_text_with_stroke(draw, (x, y), current_data, font, 
                                        fill=cfg["font_color"], 
                                        stroke_fill=cfg["stroke_color"], 
                                        stroke_width=cfg["stroke_width"])
            
            # 更新位置（如果有多行数据）
            y += cfg["row_spacing"]
        
        return img

    def generate_frame(self, frame_num):
        """生成单个帧并保存"""
        frame = self._create_frame(frame_num)
        frame_path = os.path.join(self.output_dir, f"{self.config['frame_prefix']}{frame_num:04d}.png")
        frame.save(frame_path)
        if (frame_num + 1) % 100 == 0 or frame_num == self.max_rows - 1:
            print(f"生成进度: {frame_num+1}/{self.max_rows}")
        return frame_path

    def generate_frames(self):
        """生成所有帧"""
        if self.config["use_multithreading"]:
            executor_class = concurrent.futures.ProcessPoolExecutor if self.config["use_multiprocessing"] else concurrent.futures.ThreadPoolExecutor
            with executor_class() as executor:
                futures = [executor.submit(self.generate_frame, frame_num) for frame_num in range(self.max_rows)]
                for future in concurrent.futures.as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        print(f"生成帧时出错: {e}")
        else:
            for frame_num in range(self.max_rows):
                self.generate_frame(frame_num)

# ================== 执行程序 ==================
if __name__ == "__main__":
    # 获取所有分割后的文件夹
    def process_folder(i, folder):
        generator = TextFrameGenerator(CONFIG, i)
        generator.generate_frames()
        print(f"帧序列已生成至: {generator.output_dir}")

    activity_folders = [f for f in os.listdir(CONFIG["input_base_path"]) if os.path.isdir(os.path.join(CONFIG["input_base_path"], f))]

    for i, folder in enumerate(activity_folders, start=1):
        process_folder(i, folder)
