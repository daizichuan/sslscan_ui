import logging
from logging import Logger


class Log:
    def __init__(self):
        self.log_file = "../log/logging.log"

    def log_config(self):
        # 创建logger对象
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)  # log等级总开关

        # log输出格式
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

        # 控制台handler
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)  # log等级的开关
        stream_handler.setFormatter(formatter)

        # 文件handler
        file_handler = logging.FileHandler(self.log_file, encoding='utf8')
        file_handler.setLevel(logging.CRITICAL)  # log等级的开关
        file_handler.setFormatter(formatter)

        # 添加到logger
        logger.addHandler(stream_handler)
        logger.addHandler(file_handler)

        return logger


log: Logger = Log().log_config()

if __name__ == '__main__':
    # 输出日志 debug < info < warning < error < critical
    log.debug("debug")
    log.info("info")
    log.warning("warning")
    log.error("error")
    log.critical("critical")
