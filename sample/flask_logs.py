import logging
from logging.config import dictConfig
import socket


class LogModule(object):
    def __init__(self, app=None, **kwargs):
        if app is not None:
            self.init_app(app, **kwargs)

    def init_app(self, app):
        filename=app.config["filename"]
        subject=app.config["subject"]
        from_address=socket.gethostname()
        to_address=app.config["to_address"]

        formatter = {
            "formatters": {
                "default": {
                    "format": "[%(asctime)s.%(msecs)03d] %(levelname)s %(name)s:%(funcName)s: %(message)s",
                    "datefmt": "%d/%b/%Y:%H:%M:%S",
                },
                "access": {"format": "%(message)s"},
            }
        }
        logger = {
            "loggers": {
                "": {"level": logging.INFO, "handlers": ["file","mail"], "propagate": False},
                "root": {"level": logging.INFO, "handlers": ["file","mail"],"propagate":False},
                "app.access": {
                    "level": logging.INFO,
                    "handlers": ["file","mail"],
                    "propagate": False,
                },
            }
        }
        
        logging_handler = {
                "handlers": {
                    "file": {
                        "level": logging.INFO,
                        "class": "logging.handlers.RotatingFileHandler",
                        "filename": filename,
                        "backupCount": 3,
                        "maxBytes": 100000,
                        "formatter": "default",
                        "delay": True,
                    },
                    "mail": {
                        "level": logging.ERROR,
                        "class": 'logging.handlers.SMTPHandler',
                        "mailhost":("localhost"),
                       "fromaddr":from_address,
                       "toaddrs":[to_address,],
                        "subject":subject,
                    },
                }
            }

        log_config = {
            "version": 1,
            "formatters": formatter["formatters"],
            "loggers": logger["loggers"],
            "handlers": logging_handler["handlers"],
        }
        dictConfig(log_config)