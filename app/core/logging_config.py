import logging
import logging.config
import sys
from pythonjsonlogger import jsonlogger
import logging_loki
import atexit

DEFAULT_LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s - (%(filename)s:%(lineno)d)",
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s %(filename)s %(lineno)d %(patient_id)s %(symptoms)s %(diagnosis_status)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "DEBUG",
            "stream": sys.stdout,
        },
        "file": {
            "class": "logging.FileHandler",
            "formatter": "json",
            "filename": "logs/app.log",
            "mode": "a",
            "level": "DEBUG",
        }
    },
    "loggers": {
        "": {  # root logger
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "AutoMedAI_FastAPI": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

class LokiHandlerWithCleanup(logging_loki.LokiHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        atexit.register(self.cleanup)
        print(f"Loki handler initialized with args: {args}, kwargs: {kwargs}")
    
    def cleanup(self):
        """Ensure proper cleanup of Loki connection"""
        try:
            self.session.close()
        except:
            pass
            
    def emit(self, record):
        """Override emit to add debug information"""
        print(f"Attempting to emit log to Loki: {record.getMessage()}")
        try:
            super().emit(record)
            print("Successfully emitted log to Loki")
        except Exception as e:
            print(f"Failed to emit log to Loki: {str(e)}")
            self.handleError(record)

def setup_logging(loki_url=None, app_name="AutoMedAI_FastAPI"):
    """
    Configure and set up logging with optional Loki integration.
    
    Args:
        loki_url (str): URL for Loki logging. If None or empty, Loki logging is disabled.
        app_name (str): Name of the application logger to return.
    
    Returns:
        logging.Logger: Configured logger instance for the application.
    """
    import os
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    config = DEFAULT_LOGGING.copy()
    
    print(f"Setting up logging with Loki URL: {loki_url}")

    if loki_url:
        try:
            print("Configuring Loki handler...")
            # Add Loki handler if URL is provided
            config["handlers"]["loki"] = {
                "class": "app.core.logging_config.LokiHandlerWithCleanup",
                "url": loki_url,
                "tags": {"application": "AutoMedAI", "service": "fastapi_app"},
                "version": "1",
                "formatter": "json",
            }
            
            # Add Loki handler to the application logger
            config["loggers"][app_name]["handlers"].append("loki")
            print("Loki handler configured successfully")
        except Exception as e:
            print(f"Warning: Failed to configure Loki logging: {e}")
            # Continue without Loki logging
    
    # Apply the configuration
    logging.config.dictConfig(config)
    
    # Get and return the logger
    logger = logging.getLogger(app_name)
    logger.info(f"Logging configured. Loki URL: {loki_url if loki_url else 'Not configured'}")
    
    return logger 