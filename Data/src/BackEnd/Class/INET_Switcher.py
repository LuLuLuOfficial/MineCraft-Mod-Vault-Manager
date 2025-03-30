from socket import AF_INET, AF_INET6
def Compel_IPV4(): return AF_INET
def Compel_IPV6(): return AF_INET6

class INET_Switcher():
    def __init__(self):
        from Data.src.BackEnd.Instance import LogManager, LogManage
        self.__Switch: bool = False
        self.LogManage: LogManager = LogManage

    def Switch(self, Target: str = 'None'):
        '''
        Target: str = 'IPV4' | 'IPV6' or 'None'
        '''

        import urllib3.util.connection  # 导入整个模块
        match Target:
            case 'IPV4':
                urllib3.util.connection.allowed_gai_family = Compel_IPV4
            case 'IPV6':
                urllib3.util.connection.allowed_gai_family = Compel_IPV6
            case 'None':
                self.__Switch = not self.__Switch
                if self.__Switch: urllib3.util.connection.allowed_gai_family = Compel_IPV4
                else: urllib3.util.connection.allowed_gai_family = Compel_IPV6
            case _:
                pass
        if self.LogManage: self.LogManage.LogOutput(LogMessage=f'Setting Requests To Force <{self.State}> Usage.')

    @property
    def State(self):
        if self.__Switch: return 'IPV4'
        else: return 'IPV6'

if __name__ == '__main__':
    from time import time
    from requests import get
    for n in range(10):
        Time_Start: float = time()
        Result = get("https://api64.ipify.org")
        Time_End: float = time()
        print(f'Round: {n}; TimeUse: {Time_End-Time_Start}; IP: {Result.text}')  # 输出应为 IPv4 地址