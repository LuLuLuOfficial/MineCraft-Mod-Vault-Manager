'''
------------------------------
    Command-Line Interface
          命令行界面
------------------------------
'''
from Data.Lib.PyLucas.Instance import LogManage

class CLI():
    def __init__(self):
        self.UserName: str = 'Nuhil Lucas'

        self.HistoryCommand: list = []

        self.__Commander: Commander = Commander()

    def Start(self):
        self.Initialize()
        self.Boot()

    def Initialize(self):
        from PyLucas.Function import Author_Lucas

        print(f'{"-"*100}\n{Author_Lucas()}{"-"*100}')

    def Boot(self):
        while 1:
            Command: str = input(f'{self.UserName}: ').upper()
            self.CommandExecute(Command)

    def CommandExecute(self, Command: str):
        match Command:
            case 'HELP':
                self.__Commander.Help()
            case 'CLEAR':
                self.__Commander.Clear()
            case 'PROJECTMANAGE':
                self.__Commander.ProjectManage()
            case _:
                print('CLI: Unknow Command.')

class Commander():
    def __init__(self):
        self.Path_CommandsDict: str = r'Data\Lib\Start\CLI\CommandsDict.json'

    def Help(self):
        from json import load
        with open(file=self.Path_CommandsDict, mode='r', encoding='utf-8') as file:
            CommandsDict: dict = load(file)
        CommandsList: tuple = tuple(CommandsDict.keys())
        GoNextPage: str = ''
        Start: int = 0
        End: int = 0

        FirstTime: bool = True
        while 1:
            match GoNextPage:
                case 'n':
                    if (Start+10) >= len(CommandsList): pass
                    else:
                        Start += 10
                        if (Start+10) > len(CommandsList): End = len(CommandsList)
                        else: End  = Start + 10
                case 'l':
                    if (Start-10) < 0: pass
                    else:
                        End = Start
                        Start -= 10
                case 'q':
                    break
                case _:
                    if (Start+10) >= len(CommandsList): End = len(CommandsList)
                    else: End = Start+10
            if not FirstTime:
                for n in range(15):
                    print('\033[F\033[K', end='')
            else:
                FirstTime = False
            print('Commands:')
            for Command in CommandsList[Start: End]:
                print(f'\t{Command}: {CommandsDict[Command]}')
            if (End-Start) != 10:
                print((10-End+Start)*'\n', end='')
            GoNextPage = input(f'\n\tPage: <{(Start+10)//10}>\n\t<-Enter \'n\' to Next Page, \'l\' to Last Page, \'q\' to Quit->\n')

    def Clear(self):
        from os import system
        system('cls')
    
if __name__ == "__main__":
    _CLI_: CLI = CLI()
    _CLI_.Start()