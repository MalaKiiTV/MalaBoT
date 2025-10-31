"""
Enhanced Logging System
Provides structured, comprehensive logging for all bot operations
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

class BotLogger:
    """
    Enhanced logging system with:
    - Separate log files per system
    - Automatic rotation
    - Structured formatting
    - Multiple log levels
    """
    
    def __init__(self, log_dir: str = "data/logs"):
        self.log_dir = log_dir
        self.loggers = {}
        
        # Create log directory
        os.makedirs(log_dir, exist_ok=True)
        
        # Setup main loggers
        self._setup_loggers()
    
    def _setup_loggers(self):
        """Setup all system loggers"""
        
        # Define logger configurations
        logger_configs = {
            'bot': 'bot.log',
            'database': 'database.log',
            'role_connections': 'role_connections.log',
            'verification': 'verification.log',
            'xp': 'xp.log',
            'welcome': 'welcome.log',
            'errors': 'errors.log',
            'audit': 'audit.log',
            'backup': 'backup.log',
            'health': 'health.log'
        }
        
        for logger_name, log_file in logger_configs.items():
            self.loggers[logger_name] = self._create_logger(
                logger_name,
                os.path.join(self.log_dir, log_file)
            )
    
    def _create_logger(self, name: str, log_file: str) -> logging.Logger:
        """Create a configured logger"""
        
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        logger.handlers = []
        
        # File handler with rotation (10MB per file, keep 5 files)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler (only INFO and above)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger by name"""
        if name not in self.loggers:
            # Create new logger if doesn't exist
            log_file = os.path.join(self.log_dir, f"{name}.log")
            self.loggers[name] = self._create_logger(name, log_file)
        
        return self.loggers[name]


# Global logger instance
_bot_logger = None

def setup_logging(log_dir: str = "data/logs"):
    """Setup global logging system"""
    global _bot_logger
    _bot_logger = BotLogger(log_dir)
    return _bot_logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger by name"""
    global _bot_logger
    if _bot_logger is None:
        _bot_logger = BotLogger()
    return _bot_logger.get_logger(name)


# Convenience logging functions
def log_bot(message: str, level: str = "info"):
    """Log to bot.log"""
    logger = get_logger('bot')
    getattr(logger, level)(message)

def log_database(message: str, level: str = "info"):
    """Log to database.log"""
    logger = get_logger('database')
    getattr(logger, level)(message)

def log_error(message: str, exc_info=None):
    """Log to errors.log"""
    logger = get_logger('errors')
    logger.error(message, exc_info=exc_info)

def log_audit(user_id: int, action: str, details: str):
    """Log to audit.log"""
    logger = get_logger('audit')
    logger.info(f"User {user_id} | {action} | {details}")

def log_role_connection(message: str, level: str = "info"):
    """Log to role_connections.log"""
    logger = get_logger('role_connections')
    getattr(logger, level)(message)

def log_verification(message: str, level: str = "info"):
    """Log to verification.log"""
    logger = get_logger('verification')
    getattr(logger, level)(message)

def log_xp(message: str, level: str = "info"):
    """Log to xp.log"""
    logger = get_logger('xp')
    getattr(logger, level)(message)

def log_welcome(message: str, level: str = "info"):
    """Log to welcome.log"""
    logger = get_logger('welcome')
    getattr(logger, level)(message)

def log_backup(message: str, level: str = "info"):
    """Log to backup.log"""
    logger = get_logger('backup')
    getattr(logger, level)(message)

def log_health(message: str, level: str = "info"):
    """Log to health.log"""
    logger = get_logger('health')
    getattr(logger, level)(message)