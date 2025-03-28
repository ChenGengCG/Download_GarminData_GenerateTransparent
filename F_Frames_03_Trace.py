import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import imageio.v2 as imageio
from PIL import Image, ImageDraw
from math import cos, sin, radians
import matplotlib.colors as mcolors
from concurrent.futures import ThreadPoolExecutor, as_completed

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

    # 输入文件配置
    'lon_file': 'LongitudeDegInter.csv',  # 经度数据文件
    'lat_file': 'latitudeDegInter.csv',  # 纬度数据文件

    # 轨迹图配置
    'map_output_image': 'trajectory_map.png',  # 输出轨迹图路径
    'map_size': (500, 500),  # 图片尺寸（宽，高）
    'map_dpi': 10,  # 图片DPI
    'line_width': 75,  # 轨迹线宽（磅）
    'line_color': '#7472d7',  # RGBA颜色（蓝）

    # 视频配置
    'video_size': (1920, 1080),  # 视频尺寸（宽,高）
    'video_dpi': 16,  # 视频DPI
    'fps': 1,  # 帧率（每秒1帧）
    'map_position': (50, 25),  # 轨迹图在视频中的位置（左上角坐标）
    'temp_dir': 'TraceFrames',  # 临时帧存储目录

    # 飞机样式配置（使用0-255整数RGBA）
    'aircraft_color': '#00FFFF',  # 机身颜色
    'aircraft_outline_color': '#f74c4c',  # 描边颜色
    'aircraft_outline_width': 10,  # 描边宽度
    'aircraft_radius': 20,  # 圆形半径（像素）
}

# ================== 功能实现区 ==================
class GeoVideoGenerator:
    def __init__(self, config, activity_index):
        self.config = config
        self.activity_index = activity_index
        self.lon_file = os.path.join(config["input_base_path"], f"{config['filename_format']}{activity_index}/{config['lon_file']}")
        self.lat_file = os.path.join(config["input_base_path"], f"{config['filename_format']}{activity_index}/{config['lat_file']}")
        self.output_dir = os.path.join(config["output_base_path"], f"{config['filename_format']}{activity_index}/Trace")
        self.map_output_image = os.path.join(self.output_dir, config['map_output_image'])
        self.temp_dir = os.path.join(self.output_dir, config['temp_dir'])

        # 加载数据
        self._load_data()
        self._calculate_coordinate_system()
        self._precompute_positions()

        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)

    def _load_data(self):
        """加载经度纬度数据"""
        self.lon = pd.read_csv(self.lon_file, header=None).values.flatten()
        self.lat = pd.read_csv(self.lat_file, header=None).values.flatten()

        if len(self.lon) != len(self.lat):
            raise ValueError("经度与纬度数据长度不一致")

        self.data_points = len(self.lon)

    def _calculate_coordinate_system(self):
        """计算保持原始比例的坐标系统"""
        # 获取实际地理范围
        self.lon_min, self.lon_max = np.min(self.lon), np.max(self.lon)
        self.lat_min, self.lat_max = np.min(self.lat), np.max(self.lat)

        # 增加边距
        lon_margin = (self.lon_max - self.lon_min) * 0.1
        lat_margin = (self.lat_max - self.lat_min) * 0.1
        self.lon_min -= lon_margin
        self.lon_max += lon_margin
        self.lat_min -= lat_margin
        self.lat_max += lat_margin

        # 计算实际宽高比
        geo_width = self.lon_max - self.lon_min
        geo_height = self.lat_max - self.lat_min
        self.aspect_ratio = geo_width / geo_height

        # 计算绘图区域有效尺寸
        map_width, map_height = self.config['map_size']
        canvas_aspect = map_width / map_height

        # 调整绘图范围保持原始比例
        if self.aspect_ratio > canvas_aspect:
            adj_height = geo_width / canvas_aspect
            self.lat_center = (self.lat_max + self.lat_min) / 2
            self.lat_min = self.lat_center - adj_height / 2
            self.lat_max = self.lat_center + adj_height / 2
        else:
            adj_width = geo_height * canvas_aspect
            self.lon_center = (self.lon_max + self.lon_min) / 2
            self.lon_min = self.lon_center - adj_width / 2
            self.lon_max = self.lon_center + adj_width / 2

        # 计算缩放比例
        self.lon_scale = map_width / (self.lon_max - self.lon_min)
        self.lat_scale = map_height / (self.lat_max - self.lat_min)

    def _precompute_positions(self):
        """预计算所有点的坐标位置和方向"""
        # 计算图片坐标
        self.x = (self.lon - self.lon_min) * self.lon_scale
        self.y = (self.lat_max - self.lat) * self.lat_scale

        # 预计算方向
        self.angles = np.zeros(self.data_points)
        for i in range(self.data_points - 1):
            dx = self.lon[i + 1] - self.lon[i]
            dy = self.lat[i + 1] - self.lat[i]
            self.angles[i] = np.degrees(np.arctan2(dy, dx))
        self.angles[-1] = self.angles[-2]

    def generate_trajectory_map(self):
        """生成透明轨迹图"""
        fig = plt.figure(
            figsize=(
                self.config['map_size'][0] / self.config['map_dpi'],
                self.config['map_size'][1] / self.config['map_dpi']
            ),
            dpi=self.config['map_dpi'],
            facecolor='none'
        )

        ax = fig.add_axes([0, 0, 1, 1])

        # 将颜色值从十六进制字符串转换为RGBA格式
        rgba_color = mcolors.hex2color(self.config['line_color'])

        # 绘制轨迹线
        ax.plot(self.x, self.y,
                linewidth=self.config['line_width'],
                color=rgba_color)

        # 隐藏坐标轴和边框
        ax.set_axis_off()
        ax.set_xlim(0, self.config['map_size'][0])
        ax.set_ylim(self.config['map_size'][1], 0)  # 保持y轴方向

        # 保存透明图像
        plt.savefig(
            self.map_output_image,
            transparent=True,
            bbox_inches='tight',
            pad_inches=0
        )
        plt.close()

    def _create_aircraft(self, angle):
        """创建带描边的圆形图形"""
        cfg = {
            'color': self.config['aircraft_color'],
            'outline_color': self.config['aircraft_outline_color'],
            'outline_width': self.config['aircraft_outline_width'],
            'radius': self.config['aircraft_radius']
        }
        img = Image.new('RGBA', (cfg['radius'] * 2 + cfg['outline_width'] * 2, cfg['radius'] * 2 + cfg['outline_width'] * 2), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 定义圆形边界
        outer_bounds = [
            cfg['outline_width'],
            cfg['outline_width'],
            cfg['radius'] * 2 + cfg['outline_width'],
            cfg['radius'] * 2 + cfg['outline_width']
        ]

        # 绘制外圆（描边）
        draw.ellipse(outer_bounds, fill=cfg['outline_color'])

        # 定义内圆边界
        inner_bounds = [
            cfg['outline_width'] + cfg['outline_width'] // 2,
            cfg['outline_width'] + cfg['outline_width'] // 2,
            cfg['radius'] * 2 + cfg['outline_width'] // 2,
            cfg['radius'] * 2 + cfg['outline_width'] // 2
        ]

        # 绘制内圆（填充）
        draw.ellipse(inner_bounds, fill=cfg['color'])

        return img, img.width // 2, img.height // 2

    def _generate_single_frame(self, i, map_img):
        video_w, video_h = self.config['video_size']
        map_x, map_y = self.config['map_position']

        frame = Image.new('RGBA', (video_w, video_h), (0, 0, 0, 0))
        frame.paste(map_img, (map_x, map_y), map_img)

        # 计算飞机位置
        px = int(map_x + self.x[i])
        py = int(map_y + self.y[i])

        # 生成飞机图形
        aircraft_img, cx, cy = self._create_aircraft(self.angles[i])

        # 定位飞机
        frame.paste(aircraft_img, (px - cx, py - cy), aircraft_img)

        frame_path = os.path.join(self.temp_dir, f"{self.config['frame_prefix']}{i:04d}.png")
        frame.save(frame_path)
        return frame_path

    def generate_video_frames(self):
        """并行生成视频帧"""
        map_img = Image.open(self.map_output_image).convert('RGBA')

        os.makedirs(self.temp_dir, exist_ok=True)

        # 使用多线程并行生成帧
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self._generate_single_frame, i, map_img) for i in range(self.data_points)]
            for future in as_completed(futures):
                try:
                    future.result()  # 检查异常
                except Exception as e:
                    print(f"帧生成错误: {e}")


# ================== 执行主程序 ==================
if __name__ == '__main__':
    # 获取所有分割后的文件夹
    def process_folder(i, folder):
        generator = GeoVideoGenerator(CONFIG, i)
        print(f"正在生成轨迹图: {folder}...")
        generator.generate_trajectory_map()
        print(f"正在生成视频帧: {folder}...")
        generator.generate_video_frames()
        print(f"帧序列已生成至: {generator.output_dir}")

    activity_folders = [f for f in os.listdir(CONFIG["input_base_path"]) if os.path.isdir(os.path.join(CONFIG["input_base_path"], f))]

    for i, folder in enumerate(activity_folders, start=1):
        process_folder(i, folder)
