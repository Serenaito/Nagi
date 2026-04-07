import json
import os
from pathlib import Path


class Config:
    """配置管理类，支持 JSON 文件存盘"""

    def __init__(self, config_file="config.json"):
        self.config_file = Path(config_file)
        self.config = {
            "window_topmost": False,
            "minimize_to_tray": True,
            "background_transparent": True,
            "current_model": "",
            "window_movable": True,  # 是否允许移动窗口
            "window_x": None,  # 窗口 X 坐标，None 表示使用默认位置
            "window_y": None,  # 窗口 Y 坐标，None 表示使用默认位置
            "network_enabled": True,  # 是否启用网络服务
            "network_host": "127.0.0.1",  # 网络服务监听地址
            "network_port": 9527,  # 网络服务监听端口
        }
        self.load()

    def get_available_models(self):
        """扫描 Resources 目录下的模型目录"""
        resources_path = Path(__file__).parent / "Resources"
        models = []
        if resources_path.exists():
            for item in resources_path.iterdir():
                if item.is_dir() and not item.name.startswith("."):
                    models.append(item.name)
        return sorted(models)
    
    def get_current_mode(self):
        models = self.get_available_models()
        current_model = self.get("current_model", "")

        if current_model and current_model in models:
            # 加载配置的模型
            model_path = current_model
            return model_path
        elif models:
            # 默认加载第一个模型
            model_path = models[0]
            self.set("current_model", models[0])

        return model_path
    
    def load(self):
        """从 JSON 文件加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"加载配置失败：{e}")
    
    def save(self):
        """保存配置到 JSON 文件"""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"保存配置失败：{e}")
    
    def get(self, key, default=None):
        """获取配置值"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """设置配置值并自动保存"""
        self.config[key] = value
        self.save()