

class __ProjectsManager__():
    '''Not Include Error Handling Module.'''
    def __init__(self):
        from Data.Lib.BackEnd.Instance import LogManager, LogManage
        from PyLucas import ConfigEditor
        self.LogManage: LogManager = LogManage

        self.Path_Projects: str = ''
        self.Projects: ConfigEditor = None

        self.Projects_History_UnDo: list[dict] = []
        self.Projects_History_ReDo: list[dict] = []
        self.History_Limit: int = 10

        self.Initialize()

    def Initialize(self):
        from PyLucas import ConfigEditor

        self.Path_Projects = r'Data\Config\Projects\Projects.toml'
        self.Projects = ConfigEditor(self.Path_Projects)

    def Legality_Check(self, Mode: tuple = ('__ALL__',), Project_ID: str = None, Mods_Location: str = None, BasicMsg: tuple[str] = None):
        '''
        Project_ID: str = 'Project_ID'\n
        Mods_Location: str = r'Mods_Location'\n
        BasicMsg: tuple[str] = ('1.20.1', 'Fabric')\n
        Mode: tuple = ('__ALL__',) | ('Project_ID', 'Mods_Location', 'BasicMsg',)\n
        '''

        if Mode == ('__ALL__',):
            Mode: tuple = ('Project_ID', 'Mods_Location', 'BasicMsg',)
        for Check in Mode:
            match Check:
                case 'Project_ID':  # 检查 项目名称
                    from Data.Lib.BackEnd.Function.Function import CheckValid_str
                    from Data.Lib.BackEnd.Class.LucasException import StringFormatError, DuplicateObject

                    if not CheckValid_str(String=Project_ID, Format=r'[A-Za-z0-9_]+'):
                        raise StringFormatError(Message='Project_ID not fit the format.',
                                                String=f'{Project_ID}',
                                                Format=r'[A-Za-z0-9_]+')
                    for Project_ID_Existing in self.Projects.Get_Keys():
                        if Project_ID == Project_ID_Existing:
                            raise DuplicateObject(Message='Project Project_ID Duplicate.',
                                                  Object_ID=[Project_ID_Existing, Project_ID],
                                                  Attribute=['Project_ID', Project_ID])
                        
                case 'Mods_Location':   # 检查 管理路径
                    from Data.Lib.BackEnd.Class.LucasException import DuplicateObject

                    for Project_ID_Existing in self.Projects.Get_Keys():
                        if Mods_Location == self.Projects.Get_Value(Key_Locate=f'{Project_ID_Existing}.Mods_Location'):
                            raise DuplicateObject(Message='Project Mods_Location Duplicate.',
                                                  Object_ID=[Project_ID_Existing, Project_ID],
                                                  Attribute=['Mods_Location', Mods_Location])
                        
                case 'BasicMsg':    # 检查 MOD加载器|游戏版本
                    from Data.Lib.BackEnd.Class.LucasException import UnSupportLoader, UnSupportVersion
                    from Data.Lib.BackEnd.API.API_Modrinth import Check_GameVersion, Check_ModeLoader

                    try:
                        Checked_GameVersion: bool = Check_GameVersion(BasicMsg[0])
                        Checked_ModeLoader: bool = Check_ModeLoader(BasicMsg[1])
                    except Exception as E:
                        raise E
                    else:
                        if not Checked_GameVersion:
                            raise UnSupportVersion(GameVersion=BasicMsg[0])
                        if not Checked_ModeLoader:
                            raise UnSupportLoader(ModLoader=BasicMsg[1])
                case _:
                    raise ValueError(f'Mode = {Mode}')

    def RecordHistory(self, Mode: str):
        '''
        Mode: str = 'Undo' | 'ReDo' | 'Undo_Clear' | 'ReDo_Clear' | 'Undo&ReDo_Clear'
        '''
        match Mode:
            case 'Undo':
                self.Projects_History_UnDo.append(self.Projects.Get_Data_Toml)
                while len(self.Projects_History_UnDo) > self.History_Limit: self.Projects_History_UnDo.pop(0)
            case 'ReDo':
                self.Projects_History_ReDo.append(self.Projects.Get_Data_Toml)
                while len(self.Projects_History_ReDo) > self.History_Limit: self.Projects_History_ReDo.pop(0)
            case 'Undo_Clear':
                self.Projects_History_UnDo = []
            case 'ReDo_Clear':
                self.Projects_History_ReDo = []
            case 'Undo&ReDo_Clear':
                self.Projects_History_UnDo.append(self.Projects.Get_Data_Toml)
                while len(self.Projects_History_UnDo) > self.History_Limit: self.Projects_History_UnDo.pop(0)
                self.Projects_History_ReDo = []

    def UnDo(self):
        if not self.Projects_History_UnDo:
            return
        self.RecordHistory('ReDo')
        self.Projects.OverWrite_Data(self.Projects_History_UnDo[-1])
        self.Projects_History_UnDo.pop(-1)

    def ReDo(self):
        if not self.Projects_History_ReDo:
            return
        self.RecordHistory('UnDo')
        self.Projects.OverWrite_Data_Toml(self.Projects_History_ReDo[-1])
        self.Projects_History_ReDo.pop(-1)

    def Create(self, Project_ID: str, Project_Name: str, Mods_Location: str, BasicMsg: tuple[str]):
        '''
        Project_ID: str = 'Project_ID'\n
        Mods_Location: str = r'Mods_Location'\n
        BasicMsg: tuple[str] = ('1.20.1', 'Fabric')\n
        '''
        from PyLucas.Func import GetTimeStamp
        
        if Project_ID in ['__None__', '', None]:    # 如未设定 Project_ID 则生成 Project_ID
            Projects_ID: tuple = self.Projects.Get_Keys()
            n: int = 0
            Temp_Project_ID: int = 0
            while n < len(Projects_ID):
                if str(Temp_Project_ID) == Projects_ID[n]:
                    Temp_Project_ID += 1
                    n = 0
                    continue
                n += 1
            Project_ID = str(Temp_Project_ID)

        '''Legality Check'''
        self.Legality_Check(Project_ID=Project_ID, Mods_Location=Mods_Location, BasicMsg=BasicMsg)

        # Project Create
        Project_Info = {
            "Project_Name": Project_Name,
            "Game_Version": BasicMsg[0],
            "Mods_Loader": BasicMsg[1],
            "Mods_Location": Mods_Location,
            "Date_Created": GetTimeStamp(),
        }

        self.Projects.Set_Value(Key_Locate=f'{Project_ID}', Value=Project_Info)

    def Modify(self ,Project_ID: str, Project_Name: str = None, Mods_Location: str = None, BasicMsg: tuple[str] = None):
        '''
        Project_ID: str = 'Project_ID'\n
        Project_Name: str = 'Project_Name_New'\n
        Mods_Location: str = r'Mods_Location'\n
        BasicMsg: tuple[str] = ('1.20.1', 'Fabric')\n
        '''
        from Data.Lib.BackEnd.Class.LucasException import NonExistentObject

        if not Project_ID in self.Projects.Get_Keys():
            raise NonExistentObject(Message='The Requested Project Not Exist.',
                                    Object_ID=Project_ID)

        if Project_Name:
            self.Projects.Set_Value(Key_Locate=f'{Project_ID}.Project_Name', Value=Project_Name)
        if BasicMsg:
            self.Legality_Check(Mode=('BasicMsg',), BasicMsg=BasicMsg)
            self.Projects.Set_Value(Key_Locate=f'{Project_ID}.Game_Version', Value=BasicMsg[0])
            self.Projects.Set_Value(Key_Locate=f'{Project_ID}.Mods_Loader', Value=BasicMsg[1])
        if Mods_Location and Mods_Location != self.Projects.Get_Value(f'{Project_ID}.Mods_Location'):
            self.Legality_Check(Mode=('Mods_Location',), Mods_Location=Mods_Location)
            self.Projects.Set_Value(Key_Locate=f'{Project_ID}.Mods_Location', Value=Mods_Location)

    def Delete(self, Project_ID: str):
        from Data.Lib.BackEnd.Class.LucasException import NonExistentObject

        if not Project_ID in self.Projects.Get_Keys():
            raise NonExistentObject(Message='The Requested Project Not Exist.',
                                    Object_ID=Project_ID)
        
        self.Projects.POP_Key(Key_Locate=Project_ID)

class ProjectsManager():
    '''SuperStructure'''
    def __init__(self):
        from Data.Lib.BackEnd.Instance import LogManager, LogManage

        self.LogManage: LogManager = LogManage
        self.__ProjectManage: __ProjectsManager__ = None
        # self.History_Enable: bool = True

        self.__Initialize()

    def __Initialize(self):
        try:
            self.__ProjectManage = __ProjectsManager__()
        except Exception as E:
            match type(E).__name__:
                case 'TOMLDecodeError':
                    self.LogManage.LogOutput(Level='Error', LogMessage=f'<Project Initialize> TOML Decode Error -> {E}')
                case _:
                    self.LogManage.LogOutput(Level='Error', LogMessage=f'<Project Initialize> Unexpected Error -> {E}')
            raise E
        else:
            self.LogManage.LogOutput(Level='Normal', LogMessage=f'<Project Initialize> Project Initialize Succeeded')

    @property
    def Projects(self):
        return self.__ProjectManage.Projects

    def History(self, Mode: str = 'Load', Config: dict = {"History Limit": 10}):
        '''
        Mode: str = 'Load' | 'Save' | 'Config'
        Config: dict = {"History Limit": 10}
        '''
        if Mode == 'Config':
            for ConfigKey in tuple(Config.keys()):
                match ConfigKey:
                    case 'History Limit': self.__ProjectManage.History_Limit = Config["History Limit"]
            return

        from PyLucas import ConfigEditor
        Projects_History: ConfigEditor = ConfigEditor(r'Data\Config\Projects\Projects_History.toml')
        match Mode:
            case 'Load':
                self.__ProjectManage.Projects_History_UnDo = Projects_History.Get_Data_Toml
            case 'Save':
                Projects_History.Set_Value(Key_Locate='History', Value=self.__ProjectManage.Projects_History_UnDo)
        del Projects_History

    def Project_Info(self, Project_ID: str) -> dict:
        if Project_ID in self.Projects.Get_Keys():
            return self.Projects.Get_Value('Project_ID')
        else:
            return False

    def Create(self, Project_ID: str, Project_Name: str, Mods_Location: str, BasicMsg: tuple[str]):
        self.__ProjectManage.RecordHistory('Undo&ReDo_Clear')
        self.LogManage.LogOutput(Level='Normal', LogMessage=f'<Project Create> Added History Projects')

        try:
            self.__ProjectManage.Create(Project_ID, Project_Name, Mods_Location, BasicMsg)
        except Exception as E:
            match type(E).__name__:
                case 'UnSupportProjectID':
                    self.LogManage.LogOutput(Level='Warn', LogMessage=f'<Project Create> {E}')
                case 'DuplicateObject':
                    self.LogManage.LogOutput(Level='Warn', LogMessage=f'<Project Create> {E}')
                case 'PathHasBeenManaged':
                    self.LogManage.LogOutput(Level='Warn', LogMessage=f'<Project Create> {E}')
                case 'BadConnection':
                    self.LogManage.LogOutput(Level='Warn', LogMessage=f'<Project Create> {E}')
                case 'FileNotExists':
                    self.LogManage.LogOutput(Level='Warn', LogMessage=f'<Project Create> {E}')
                case 'UnSupportLoader':
                    self.LogManage.LogOutput(Level='Warn', LogMessage=f'<Project Create> {E}')
                case 'UnSupportVersion':
                    self.LogManage.LogOutput(Level='Warn', LogMessage=f'<Project Create> {E}')
                case _:
                    self.LogManage.LogOutput(Level='Error', LogMessage=f'<Project Create> Unexpected Error -> {E}')

            self.__ProjectManage.UnDo()
            self.LogManage.LogOutput(Level='Normal', LogMessage=f'<Project Create> Retraction to Previous History')
            return False
        else:
            self.LogManage.LogOutput(Level='Normal', LogMessage=f'<Project Create> Project Create Succeeded -> {Project_ID}')
            return True

    def Modify(self ,Project_ID: str, Project_Name: str = None, Mods_Location: str = None, BasicMsg: tuple[str] = None):
        self.__ProjectManage.RecordHistory('Undo&ReDo_Clear')
        self.LogManage.LogOutput(Level='Normal', LogMessage=f'<Project Modify> Added History Projects')

        try:
            self.__ProjectManage.Modify(Project_ID, Project_Name, Mods_Location, BasicMsg)
        except Exception as E:
            match type(E).__name__:
                case 'NonExistentObject':
                    self.LogManage.LogOutput(Level='Warn', LogMessage=f'<Project Modify> {E}')
                case 'DuplicateObject':
                    self.LogManage.LogOutput(Level='Warn', LogMessage=f'<Project Modify> {E}')
                case 'PathHasBeenManaged':
                    self.LogManage.LogOutput(Level='Warn', LogMessage=f'<Project Modify> {E}')
                case 'BadConnection':
                    self.LogManage.LogOutput(Level='Warn', LogMessage=f'<Project Modify> {E}')
                case 'FileNotExists':
                    self.LogManage.LogOutput(Level='Warn', LogMessage=f'<Project Modify> {E}')
                case 'UnSupportVersion':
                    self.LogManage.LogOutput(Level='Warn', LogMessage=f'<Project Modify> {E}')
                case 'UnSupportLoader':
                    self.LogManage.LogOutput(Level='Warn', LogMessage=f'<Project Modify> {E}')
                case _:
                    self.LogManage.LogOutput(Level='Error', LogMessage=f'<Project Modify> Unexpected Error -> {E}')

            self.__ProjectManage.UnDo()
            self.LogManage.LogOutput(Level='Normal', LogMessage=f'<Project Modify> Retraction to Previous History')
            return False
        finally:
            self.LogManage.LogOutput(Level='Normal', LogMessage=f'<Project Modify> Project Modify Succeeded -> {Project_ID}')
            return True

    def Delete(self, Project_ID: str):
        self.__ProjectManage.RecordHistory('Undo&ReDo_Clear')
        self.LogManage.LogOutput(Level='Normal', LogMessage=f'<Project Delete> Added History Projects')

        try:
            self.__ProjectManage.Delete(Project_ID)
        except Exception as E:
            match type(E).__name__:
                case 'NonExistentObject':
                    self.LogManage.LogOutput(Level='Warn', LogMessage=f'<Project Delete> {E}')
                case _:
                    self.LogManage.LogOutput(Level='Error', LogMessage=f'<Project Delete> Unexpected Error -> {E}')

            self.__ProjectManage.UnDo()
            self.LogManage.LogOutput(Level='Normal', LogMessage=f'<Project Delete> Retraction to Previous History')
            return False
        else:
            self.LogManage.LogOutput(Level='Normal', LogMessage=f'<Project Delete> Project Delete Succeeded -> {Project_ID}')
            return True

    def UnDo(self):
        self.__ProjectManage.UnDo()
        self.LogManage.LogOutput(Level='Normal', LogMessage=f'<Project UnDo> Project Undo Operation Succeeded')

    def ReDo(self):
        self.__ProjectManage.ReDo()
        self.LogManage.LogOutput(Level='Normal', LogMessage=f'<Project ReDo> Project ReDo Operation Succeeded')

if __name__ == '__main__':
    from time import sleep

    from Data.Lib.BackEnd.Instance import INET_Switch
    
    INET_Switch.Switch(Target= 'IPV4')
    ProjectManage: ProjectsManager = ProjectsManager()

    ProjectManage.Create(Project_ID='Test_01', Project_Name='测试_01', Mods_Location=r'Test\Mods_01', BasicMsg=('1.19.1', 'fabric'))
    sleep(0.5)
    ProjectManage.UnDo()
    sleep(0.5)
    ProjectManage.ReDo()
    sleep(0.5)
    ProjectManage.Create(Project_ID='Test_02', Project_Name='测试_02', Mods_Location=r'Test\Mods_02', BasicMsg=('1.20.1', 'fabric'))
    sleep(0.5)
    ProjectManage.Modify(Project_ID='Test_02', Project_Name='测试_02_改', Mods_Location=r'Test\Mods_03', BasicMsg=('1.20.2', 'forge'))
    sleep(0.5)
    ProjectManage.Modify(Project_ID='Test_02', Project_Name='测试_02', Mods_Location=r'Test\Mods_03', BasicMsg=('1.20.1', 'fabric'))
    sleep(0.5)
    ProjectManage.Delete(Project_ID='Test_01')
    sleep(0.5)
    ProjectManage.Delete(Project_ID='Test_02')
    ProjectManage.Save_History()