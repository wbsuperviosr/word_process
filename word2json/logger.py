import logging

level = logging.INFO
ws_format = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
ws_datefmt = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(level=level, format=ws_format, datefmt=ws_datefmt)
logger = logging.getLogger("PY Engine")
logger.setLevel(level)
