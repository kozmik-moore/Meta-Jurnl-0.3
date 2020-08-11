"""Contains the classes and functions that form the underlying logic of the journal application"""
from configurations import current_database


class App:
    def __init__(self):
        self._path = current_database()
        self._pages = []
