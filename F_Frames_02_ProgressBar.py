import csv
import os
import math
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

    # 竖线参数
    "total_length": 800,  # 竖线分布总长度(像素)
    "start_x": 560,  # 起始X坐标(整体左侧边距)
    "short_height": 40,  # 短竖线高度
    "long_height": 80,  # 长竖线高度
    "line_width": 4,  # 竖线宽度
    "line_color": (255, 255, 255, 255),  # 竖线颜色RGBA

    # 首尾文本参数
    "prefix_start": "",  # 起始文本前缀
    "suffix_start": "千米",  # 起始文本后缀
    "prefix_end": "",  # 结束文本前缀
    "suffix_end": "千米",  # 结束文本后缀
    "text_offset": 15,  # 文本与竖线垂直间距
    "start_font": "SourceHanSans-Heavy.ttc",  # 起始字体
    "end_font": "SourceHanSans-Heavy.ttc",  # 结束字体
    "font_size": 40,  # 字体大小
    "text_color": (0, 0, 0, 255),  # 文本颜色
    "text_stroke_width": 2,  # 文本描边宽度
    "text_stroke_color": (0, 255, 255, 255),  # 文本描边颜色

    # 进度条参数
    "progress_height": 60,  # 进度条高度
    "progress_color": (0, 200, 0, 255),  # 进度条颜色
    "progress_radius": 40,  # 进度条圆角半径

    # 动态文本参数
    "dynamic_offset": 40,  # 动态文本垂直间距
    "dynamic_font": "SourceHanSans-Heavy.ttc",  # 动态字体
    "dynamic_font_size": 40,  # 动态字体大小
    "dynamic_color": (0, 0, 0, 255),  # 动态文本颜色

    # 整体位置参数
    "vertical_offset": -400  # 整体元素的垂直偏移量（负值上移）
}

# ================== 核心功能类 ==================
class ProgressGenerator:
    def __init__(self, config, activity_index):
        self.config = config
        self.distances = []
        self.line_positions = []
        self.total_frames = 0
        self.input_csv = os.path.join(config["input_base_path"], f"{config['filename_format']}{activity_index}/DistanceConversed.csv")
        self.output_dir = os.path.join(config["output_base_path"], f"{config['filename_format']}{activity_index}/ProgressBar")
        
        # 初始化数据
        self._load_data()
        self._calculate_line_positions()
        
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _load_data(self):
        """加载CSV距离数据"""
        with open(self.input_csv, "r") as f:
            reader = csv.reader(f)
            self.distances = [float(row[0]) for row in reader]  # 直接使用读取的数据
            self.total_frames = len(self.distances)
    
    def _calculate_line_positions(self):
        """计算竖线分布位置"""
        spacing = self.config["total_length"] / 100  # 101个点形成100个间隔
        self.line_positions = [self.config["start_x"] + i * spacing for i in range(101)]
    
    def _draw_vertical_lines(self, draw):
        """绘制所有竖线"""
        vertical_offset = self.config["vertical_offset"]
        for idx, x in enumerate(self.line_positions):
            # 确定竖线高度
            if idx == 0 or idx % 10 == 0:
                height = self.config["long_height"]
            else:
                height = self.config["short_height"]
            
            # 计算坐标
            y_start = (self.config["frame_size"][1] // 2) - (height // 2) + vertical_offset
            y_end = y_start + height
            
            # 绘制竖线
            draw.line(
                [(x, y_start), (x, y_end)],
                fill=self.config["line_color"],
                width=self.config["line_width"]
            )
    
    def _draw_progress(self, draw, current_distance):
        """绘制进度条"""
        vertical_offset = self.config["vertical_offset"]
        final_distance = self.distances[-1]
        progress_ratio = current_distance / final_distance
        progress_width = progress_ratio * self.config["total_length"]
        
        # 定义进度条形状
        x0 = self.line_positions[0]
        y0 = (self.config["frame_size"][1] // 2) - self.config["progress_height"] // 2 + vertical_offset
        x1 = x0 + progress_width
        y1 = y0 + self.config["progress_height"]
        
        # 绘制圆角矩形进度条
        draw.rounded_rectangle(
            [x0, y0, x1, y1],
            radius=self.config["progress_radius"],
            fill=self.config["progress_color"]
        )
        return x1  # 返回当前进度条右端X坐标
    
    def _draw_text_annotations(self, draw, progress_end_x, frame_idx):
        """绘制所有文本标注"""
        # 绘制起始文本和结束文本（每一帧）
        self._draw_start_end_text(draw, is_start=True)
        self._draw_start_end_text(draw, is_start=False)
        
        # 绘制动态文本
        self._draw_dynamic_text(draw, progress_end_x, frame_idx)
    
    def _draw_start_end_text(self, draw, is_start):
        """绘制首尾固定文本"""
        vertical_offset = self.config["vertical_offset"]
        # 获取文本内容
        if is_start:
            text = f"{self.config['prefix_start']}{self.distances[0]}{self.config['suffix_start']}"
            x = self.line_positions[0]
        else:
            text = f"{self.config['prefix_end']}{self.distances[-1]}{self.config['suffix_end']}"
            x = self.line_positions[-1]

        font_path = self.config["start_font"] if is_start else self.config["end_font"]
        font = ImageFont.truetype(font_path, self.config["font_size"])

        # 检查字体文件是否存在
        if not os.path.isfile(font_path):
            raise FileNotFoundError(f"字体文件 {font_path} 不存在。")
        
        # 计算文本位置
        bbox = font.getbbox(text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        y = (self.config["frame_size"][1] // 2) - self.config["long_height"] // 2 - self.config["text_offset"] - text_height + vertical_offset
        
        # 绘制带描边的文本
        self._draw_text_with_stroke(draw, (x - text_width // 2, y), text, font, self.config["text_color"], self.config["text_stroke_color"], self.config["text_stroke_width"])

    def _draw_dynamic_text(self, draw, progress_x, frame_idx):
        """绘制动态跟随文本"""
        vertical_offset = self.config["vertical_offset"]
        text = f"{self.distances[frame_idx]}千米"  # 显示当前距离
        font_path = self.config["dynamic_font"]
        font = ImageFont.truetype(font_path, self.config["dynamic_font_size"])

        # 检查字体文件是否存在
        if not os.path.isfile(font_path):
            raise FileNotFoundError(f"字体文件 {font_path} 不存在。")
        
        # 计算文本位置
        bbox = font.getbbox(text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = progress_x - text_width // 2
        y = (self.config["frame_size"][1] // 2) + self.config["progress_height"] // 2 + self.config["dynamic_offset"] + vertical_offset
        
        # 绘制带描边的动态文本
        self._draw_text_with_stroke(draw, (x, y), text, font, self.config["dynamic_color"], self.config["text_stroke_color"], self.config["text_stroke_width"])
    
    def _draw_text_with_stroke(self, draw, position, text, font, fill, stroke_fill, stroke_width):
        """绘制带描边的文本"""
        x, y = position
        # 绘制描边
        for angle in range(0, 360, 45):
            offset_x = stroke_width * math.cos(math.radians(angle))
            offset_y = stroke_width * math.sin(math.radians(angle))
            draw.text((x + offset_x, y + offset_y), text, font=font, fill=stroke_fill)
        
        # 绘制文本
        draw.text(position, text, font=font, fill=fill)
    
    def generate_frame(self, frame_idx):
        """生成单个帧"""
        # 创建透明画布
        img = Image.new("RGBA", self.config["frame_size"], self.config["background_color"])
        draw = ImageDraw.Draw(img)
        
        # 绘制元素
        self._draw_vertical_lines(draw)
        current_distance = self.distances[frame_idx]
        progress_end_x = self._draw_progress(draw, current_distance)
        self._draw_text_annotations(draw, progress_end_x, frame_idx)
        
        # 保存帧
        img.save(os.path.join(self.output_dir, f"{self.config['frame_prefix']}{frame_idx:04d}.png"))
        if (frame_idx + 1) % 100 == 0 or frame_idx == self.total_frames - 1:
            print(f"生成进度：{frame_idx + 1}/{self.total_frames}")

    def generate_frames(self):
        """生成所有帧序列"""
        if self.config["use_multithreading"]:
            executor_class = concurrent.futures.ProcessPoolExecutor if self.config["use_multiprocessing"] else concurrent.futures.ThreadPoolExecutor
            with executor_class() as executor:
                futures = [executor.submit(self.generate_frame, frame_idx) for frame_idx in range(self.total_frames)]
                for future in concurrent.futures.as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        print(f"生成帧时出错: {e}")
        else:
            for frame_idx in range(self.total_frames):
                self.generate_frame(frame_idx)

# ================== 执行程序 ==================
if __name__ == "__main__":
    # 获取所有分割后的文件夹
    def process_folder(i, folder):
        generator = ProgressGenerator(CONFIG, i)
        generator.generate_frames()
        print(f"帧序列已生成至: {generator.output_dir}")

    activity_folders = [f for f in os.listdir(CONFIG["input_base_path"]) if os.path.isdir(os.path.join(CONFIG["input_base_path"], f))]

    for i, folder in enumerate(activity_folders, start=1):
        process_folder(i, folder)
