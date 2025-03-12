import logging
import os
from logging.handlers import RotatingFileHandler
import time
from functools import wraps

def setup_logger(name, log_file=None, level=logging.INFO, enable_file_logging=False):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if logger.handlers:
        logger.handlers = []
    
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(detailed_formatter)
    logger.addHandler(console_handler)
    
    if enable_file_logging and log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(module_name):
    enable_file_logging = os.environ.get('ENABLE_FILE_LOGGING', 'false').lower() == 'true'
    
    return setup_logger(
        f"recife.{module_name}", 
        log_file=f"logs/{module_name}.log" if enable_file_logging else None,
        level=logging.INFO,
        enable_file_logging=enable_file_logging
    )

def log_time(logger):
    def decorator(func):
        @wraps(func) 
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.info(f"{func.__name__} completed in {elapsed:.2f}s")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"{func.__name__} failed after {elapsed:.2f}s: {str(e)}")
                raise
        return wrapper
    return decorator