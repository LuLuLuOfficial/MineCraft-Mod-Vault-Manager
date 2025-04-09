LogLevel: list[str] = ['Error', 'Warn', 'Normal']

from PyLucas import LogManager
LogManage: LogManager = LogManager(OutPutPath_Root=r'Data\Log')

from src.BackEnd.Class.INET_Switcher import INET_Switcher
INET_Switch: INET_Switcher = INET_Switcher()