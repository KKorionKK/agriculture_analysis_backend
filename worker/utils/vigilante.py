import datetime
import os
import logging


class Vigilante:
    _log_format = (
        "%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s) - %(message)s"
    )

    def __init__(
            self,
            server_name: str = "server_name",
            console_stream: bool = False,
            log_in_file: bool = False,
            directory: str = None,
    ) -> None:
        self.server_name = server_name
        self.console_stream = console_stream
        if log_in_file:
            if directory is None:
                raise Exception("Directory must be specified if logging in file")
        self.log_in_file = log_in_file
        self.directory = directory

        self.initialized = True

        if self.directory:
            self.check_n_create_directory()

    def check_n_create_directory(self):
        if not os.path.exists(self.directory):
            os.mkdir(self.directory)

    def get_stream_handler(self):
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(logging.Formatter(self._log_format))
        return stream_handler

    def get_file_handler(self):
        filename = (
                self.server_name
                + "_"
                + datetime.datetime.now(datetime.timezone.utc).strftime("%d.%m.%Y")
                + ".log"
        )
        path = os.path.join(self.directory, filename)
        file_handler = logging.FileHandler(path, "a", encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(self._log_format))
        return file_handler

    def get_logger(self):
        logger = logging.getLogger(self.server_name)
        logger.setLevel(logging.INFO)
        if self.console_stream:
            logger.addHandler(self.get_stream_handler())
        if self.log_in_file:
            logger.addHandler(self.get_file_handler())
        return logger


class VigilanteSingleton(Vigilante):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(VigilanteSingleton, cls).__new__(cls)
        return cls.__instance

    def __init__(self, *args, **kwargs):
        if not hasattr(self, 'initialized'):
            super().__init__(*args, **kwargs)

    @classmethod
    def get_vigilante(cls):
        return cls.__instance
