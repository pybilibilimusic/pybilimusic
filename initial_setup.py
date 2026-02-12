import configparser
import os
import sys
from pathlib import Path

class Config():
    def __init__(self):
        self.config_path = Path("config.ini")
        self.config = configparser.ConfigParser()

    def default_config(self):
        self.config['first_run'] = {'first_run': '0'}
        self.config['save_location'] = {'default_save_location':'./temp'}
        self.config['paths'] = {
            'logs': './log',
            'video_temp': './video_temp',
            'mp3': './mp3'
        }


    def setup_directories(self):
        dirs = [
            self.config['paths']['logs'],
            self.config['paths']['uploads'],
            self.config['paths']['logs']
            self.config['paths']['video_temp'],
            self.config['paths']['mp3']
        ]

        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)


    # def inquiry(self,context):
    #     while True:
    #         user_choice = input(context)

    def initial_setup(self):

# 检测到为初次使用，执行初始化程序……(first_run=0)
#请选择语言：(开发中)
#请选择下载时保存的默认文件夹（默认为./temp）：
#请选择转换后生成MP3文件的保存位置：
