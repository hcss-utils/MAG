# -*- coding: utf-8 -*-
import logging


def create_logger(name: str):
    """Create logger with DEBUG level & stream handler."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s")
    sh.setFormatter(formatter)
    logger.addHandler(sh)
    return logger


logger = create_logger("mag-api-wrapper")
