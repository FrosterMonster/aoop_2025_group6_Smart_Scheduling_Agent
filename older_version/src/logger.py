import logging
import os
from datetime import datetime

# 建立 logs 資料夾
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 設定 Log 檔案名稱 (e.g., logs/system_2025-12-30.log)
log_filename = f"{LOG_DIR}/system_{datetime.now().strftime('%Y-%m-%d')}.log"

# 設定 Logger
logger = logging.getLogger("SmartAgentLogger")
logger.setLevel(logging.DEBUG)

# 避免重複添加 Handler
if not logger.handlers:
    # 1. 寫入檔案的 Handler
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s')
    file_handler.setFormatter(file_formatter)

    # 2. 輸出到 Console 的 Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)

    # 加入 Handler
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

def log_info(message):
    logger.info(message)

def log_error(message):
    logger.error(message)

def log_debug(message):
    logger.debug(message)

def log_warning(message):
    logger.warning(message)