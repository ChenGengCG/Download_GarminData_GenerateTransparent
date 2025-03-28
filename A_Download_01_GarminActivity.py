import datetime
import json
import logging
import os
import sys
from getpass import getpass

import requests
from garth.exc import GarthHTTPError

from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
)

# 配置调试日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 设置电子邮件和密码
email = "ckn69734@gmail.com"  # 替换为你的电子邮件
password = "Ckn69734"        # 替换为你的密码
tokenstore = os.getenv("GARMINTOKENS") or "~/.garminconnect"
api = None

# 设置要下载的活动数量和保存文件的相对路径及名称格式
num_activities = 5  # 修改为你需要的数量
save_path = "./DataProcess/A_OriginZIPData"  # 设置保存文件的相对路径
filename_format = "OriginZIPData"  # 设置文件名称格式

def display_json(api_call, output):
    """格式化API输出以便更好地阅读。"""
    dashed = "-" * 20
    header = f"{dashed} {api_call} {dashed}"
    footer = "-" * len(header)

    print(header)
    print(json.dumps(output, indent=4))
    print(footer)

def init_api(email, password):
    """使用你的凭据初始化Garmin API。"""
    try:
        print(f"尝试使用目录 '{tokenstore}' 中的令牌数据登录Garmin Connect...\n")
        garmin = Garmin()
        garmin.login(tokenstore)
    except (FileNotFoundError, GarthHTTPError, GarminConnectAuthenticationError):
        print(
            "登录令牌不存在，请使用你的Garmin Connect凭据登录以生成它们。\n"
            f"它们将存储在 '{tokenstore}' 中以供将来使用。\n"
        )
        try:
            garmin = Garmin(email=email, password=password, is_cn=False)
            garmin.login()
            garmin.garth.dump(tokenstore)
            print(f"OAuth令牌存储在目录 '{tokenstore}' 中以供将来使用。\n")
        except (
            FileNotFoundError,
            GarthHTTPError,
            GarminConnectAuthenticationError,
            requests.exceptions.HTTPError,
        ) as err:
            logger.error(err)
            return None
    return garmin

def download_activity(api, activity_id, filename):
    """将活动下载为.zip文件。"""
    try:
        activity = api.get_activity(activity_id)
        activity_name = activity.get("activityName", "Unknown Activity")
        activity_start_time = activity.get("startTimeLocal", None)

        print(f"下载活动 {activity_id} ({activity_name})")
        
        fit_data = api.download_activity(activity_id, dl_fmt=api.ActivityDownloadFormat.ORIGINAL)
        output_file = filename
        with open(output_file, "wb") as fb:
            fb.write(fit_data)
        print(f"活动数据下载到文件 {output_file}")

    except (
        GarminConnectConnectionError,
        GarminConnectAuthenticationError,
        GarminConnectTooManyRequestsError,
        requests.exceptions.HTTPError,
        GarthHTTPError,
    ) as err:
        logger.error(err)

def main():
    global api
    print("\n*** Garmin Connect API - 下载活动 ***\n")

    if not api:
        api = init_api(email, password)

    if api:
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        activities = api.get_activities(0, num_activities)
        for i, activity in enumerate(activities, start=1):
            activity_id = activity["activityId"]
            filename = os.path.join(save_path, f"OriginZIPData{i}.zip")
            download_activity(api, activity_id, filename)
    else:
        print("无法登录Garmin Connect，请稍后再试。")

if __name__ == "__main__":
    main()
