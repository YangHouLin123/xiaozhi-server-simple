import os
import argparse
from ruamel.yaml import YAML
from collections.abc import Mapping

default_config_file = "config.yaml"

def get_project_dir():
    """获取项目根目录"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'

def get_config_file():
    global default_config_file
    # 判断是否存在私有的配置文件
    config_file = default_config_file
    if os.path.exists(get_project_dir() + "data/." + default_config_file):
        config_file = "data/." + default_config_file
    return config_file

def load_config():
    """加载配置文件"""
    parser = argparse.ArgumentParser(description="Server configuration")
    config_file = get_config_file()
    parser.add_argument("--config_path", type=str, default=config_file)
    args = parser.parse_args()
    return read_config(args.config_path)

def read_config(config_path):
    yaml = YAML(typ='safe')
    with open(config_path, "r", encoding="utf-8") as file:
        config = yaml.load(file)
    return config

def check_config_file():
    """检查配置文件是否存在"""
    if not os.path.exists(get_config_file()):
        raise FileNotFoundError(f"配置文件 {get_config_file()} 不存在")
