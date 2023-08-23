import logging
import logging.handlers


class Logger:
    def __init__(self, logger_name='puyiwm-aigc-qna', level=logging.INFO):
        self.logger_name = logger_name
        self.level = level

    def get_logger(self):
        # 创建一个日志器
        logger = logging.getLogger(self.logger_name)
        logger.setLevel(self.level)

        # 创建一个处理器和格式器，处理器将日志信息写入日志文件，格式器设置日志信息的显示格式
        handler = logging.handlers.RotatingFileHandler(self.logger_name + '.log', maxBytes=1024 * 1024, backupCount=5)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        # 将处理器添加到日志器上
        logger.addHandler(handler)

        return logger
