import logging
import os
from datetime import datetime

# 建立 logs 資料夾
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 設定 Log 檔案名稱
log_filename = f"{LOG_DIR}/system_{datetime.now().strftime('%Y-%m-%d')}.log"

# 設定 Logger
logger = logging.getLogger("SmartAgentLogger")
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    # 1. 寫入檔案
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 2. 輸出到螢幕
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

def log_info(msg): logger.info(msg)
def log_error(msg): logger.error(msg)
def log_warning(msg): logger.warning(msg)
def log_debug(msg): logger.debug(msg)