'''
__Mods_Archives -> ModsArchive & GroupsArchive
__Mods_Archive -> ModArchive_Mod01, ModArchive_Mod02, ...
Groups_Archive -> GroupArchive_Group01, ModArchive_Group02, ...
___Mod_Archive -> ModArchive_Info
_Group_Archive -> GroupArchive_Info
'''

class __ModsArchivesManager__():
    def __init__(self, Project_ID: str, Project_Info: dict):
        from PyLucas import ConfigEditor

        self.Project_ID: str = Project_ID
        self.Project_Info: dict = Project_Info

        self.Path_ModsFolder: str = Project_Info["Mods_Location"]
        self.PathMods_Config: str = rf'{self.Path_ModsFolder}\Mods_Archives.toml'

        self.Mods_Archives: ConfigEditor
        
        self.Mods_Archives_Backup: dict = {}

        self.Initialize()

    def Initialize(self):
        from PyLucas import ConfigEditor

        self.Mods_Archives: ConfigEditor = ConfigEditor(self.PathMods_Config)
        self.Mods_Archives.Set_Data_Basic({"Mods": {},
                                           "Groups": {
                                               "Disabled": {
                                                   "GroupName": "禁用",
                                                   "ModsList": []}}})

    def Backup(self, Mode: str = 'Backup'):
        '''
        Mode: str = 'Backup' | 'WriteBack'
        '''
        match Mode:
            case 'Backup':
                self.Mods_Archives_Backup = self.Mods_Archives.Get_Data_Toml
            case 'WriteBack':
                self.Mods_Archives.OverWrite_Data(Data_Toml=self.Mods_Archives_Backup)

    def ExistCheck(self, Mode: str, RaiseBy: str, ID: str):
        '''
        Mode: str = 'Mod' | 'Group' -> Mod ExistCheck | Group ExistCheck\n
        ID: str = {Mod_ID} | {Group_ID}\n
        RaiseBy: str = 'Exist' | 'NotExist' -> Raise Error When {RaiseBy}\n
        '''
        from Data.src.BackEnd.Class.LucasException import NonExistentObject, DuplicateObject

        match Mode:
            case 'Mod': IDs: tuple[str] = self.Mods_Archives.Get_Keys('Mods')
            case 'Group': IDs: tuple[str] = self.Mods_Archives.Get_Keys('Groups')
        match RaiseBy:
            case 'NotExist':
                if not ID in IDs: raise NonExistentObject(Message=f'The Requested {Mode} Archive Not Exist.',
                                                          Object_ID=ID)
            case 'Exist':
                if ID in IDs: raise DuplicateObject(Message=f'{Mode} Archive {Mode}_ID Duplicate.',
                                                    Object_ID=[ID, ID],
                                                    Attribute=[ID, ID])

    def Mod_Search(self, Mod_Name: str, Platform: str, **kwargs):
        '''
        Mod_Name: str = {Mod Name}
        Platform: str = 'Modrinth' | 'CurseForge' | ...
        kwargs: dict = {"query": '被用以搜索的关键字 即 Mod_Name',
                        "facets": [用于筛选结果的分类器],
                        "index": '用于对搜索结果进行排序的排序方法',
                        "offset": 搜索的偏移量 即跳过的结果数,
                        "limit": 搜索返回的结果数} -> 如果 Platform 为 Modrinth 时的情况
        '''

        match Platform:
            case 'Modrinth':
                from Data.src.BackEnd.API.API_Modrinth import Mod_Search

                if not kwargs:
                    kwargs = {"query": '',
                              "facets": [["project_type:mod"]],
                              "index": 'relevance',
                              "offset": 0,
                              "limit": 10}
                    
                return Mod_Search(Mod_Name=Mod_Name, Project_Info=self.Project_Info, Params=kwargs)
            case 'CurseForge':
                # from Data.src.BackEnd.API.API_CurseForge import Mod_Search
                return [], {}
            case _:
                from Data.src.BackEnd.Class.LucasException import UnSupportedPlatform
                raise UnSupportedPlatform(Platform=Platform)

    def Mod_Addition(self, Mod_ID: str, Platform: str):
        match Platform:
            case 'Modrinth':
                from Data.src.BackEnd.API.API_Modrinth import Mod_Locate

                # self.Backup()
                self.ExistCheck(Mode='Mod', ID=Mod_ID, RaiseBy='Exist')

                Mod_Archive: dict = Mod_Locate(Mod_ID, self.Project_Info)
                self.Mods_Archives.Set_Value(Key_Locate='Mods', Value={Mod_ID: Mod_Archive})
                self.Mod_DownLoad(Mod_Archive)

            case 'CurseForge':
                # from Data.src.BackEnd.API.API_CurseForge import Mod_Locate
                pass
            case _:
                from Data.src.BackEnd.Class.LucasException import UnSupportedPlatform
                raise UnSupportedPlatform(Platform=Platform)

    def Mod_DownLoad(self, Mods_Archive: list[dict] | tuple[dict] | dict, DownloadOnly: bool = False):
        '''这个函数不会被用户直接的调用 仅仅作为其他函数的一部分被调用 帮助其他函数实现功能'''
        from Data.src.BackEnd.Class.LucasException import FileDownloadFailed
        from Data.src.BackEnd.Function.Function import Download

        if type(Mods_Archive) == dict: Mods_Archive: tuple = (Mods_Archive,)
        for Mod_Archive in Mods_Archive:
            ExceptionList: list[dict] = []
            try:
                Download(Path_Folder=self.Path_ModsFolder,
                         File_Name=Mod_Archive["filename"],
                         Download_URL=Mod_Archive["DownLoadURL"],
                         Hashes=Mod_Archive["hashes"])
            except Exception as E:
                ExceptionList.append({type(E).__name__: E.args})
            else:
                if not DownloadOnly: Mod_Archive["Downloaded"] = 1
        if ExceptionList:
            raise FileDownloadFailed(*ExceptionList,
                                     FilePath='Multiple Files',
                                     Type='Multiple Failures')

    def Mod_Remove(self, Mods_ID: tuple[str]) -> list:
        from os import remove, rename
        from os.path import exists

        Remove_Failed: list = []
        Mod_Archive: dict = {}

        for Mod_ID in Mods_ID:
            self.Backup()

            Mod_Archive = self.Mods_Archives.Get_Value(f'Mods.{Mod_ID}')
            Path_Mod: str = rf'{self.Path_ModsFolder}\{Mod_Archive["filename"]}'
            try:
                self.ExistCheck(Mode='Mod', ID=Mod_ID, RaiseBy='NotExist')
                # Trying To Delete Mods
                rename(Path_Mod, f'{Path_Mod}.Delete')
                Mod_Archive["Downloaded"] = 0
                for Group_ID in Mod_Archive["Groups"]:
                    self.Mods_Archives.Get_Value(f'Groups.{Group_ID}').remove(Mod_ID)
                self.Mods_Archives.POP_Key(f'Mods.{Mod_ID}')
                remove(f'{Path_Mod}.Delete')
            except Exception as E:
                self.Backup(Mode='WriteBack')
                if exists(f'{Path_Mod}.Delete'):
                    rename(f'{Path_Mod}.Delete', Path_Mod)
                elif not exists(f'{Path_Mod}'):
                    self.Mod_DownLoad(Mod_Archive)
                Remove_Failed.append(Mod_ID)

        return Remove_Failed

    def Mod_Update(self, Mods_ID: tuple[str]) -> list:
        from os import remove, rename
        from os.path import exists
        from Data.src.BackEnd.API.API_Modrinth import Mod_Locate

        if Mods_ID == ('__ALL__',): Mods_ID = self.Mods_Archives.Get_Keys('Mods')
        Update_Failed: list = []
        Mod_Archive: dict = {}
        Platform: str = None
        Path_Mod: str = None
        Path_Mod_Updated: str = None

        for Mod_ID in Mods_ID:
            self.Backup()

            try:
                self.ExistCheck(Mode='Mod', ID=Mod_ID, RaiseBy='NotExist')

                Platform= self.Mods_Archives.Get_Value(f'Mods.{Mod_ID}.Platform')
                Path_Mod = rf"{self.Path_ModsFolder}\{self.Mods_Archives.Get_Value(f'Mods.{Mod_ID}.filename')}"
                Path_Mod_Updated = None

                rename(Path_Mod, f'{Path_Mod}.Update')

                match Platform:
                    case 'Modrinth':
                        Mod_Archive = Mod_Locate(Mod_ID, self.Project_Info)
                    case 'CurseForge':
                        pass
                Path_Mod_Updated = rf'{self.Path_ModsFolder}\{Mod_Archive["filename"]}'
                self.Mod_DownLoad(Mods_Archive=Mod_Archive, DownloadOnly=True)
                
                self.Mods_Archives.Set_Value(Key_Locate=f'Mods.{Mod_ID}.DownLoadURL', Value=Mod_Archive["DownLoadURL"])
                self.Mods_Archives.Set_Value(Key_Locate=f'Mods.{Mod_ID}.version_type', Value=Mod_Archive["version_type"])
                self.Mods_Archives.Set_Value(Key_Locate=f'Mods.{Mod_ID}.hashes', Value=Mod_Archive["hashes"])
                self.Mods_Archives.Set_Value(Key_Locate=f'Mods.{Mod_ID}.filename', Value=Mod_Archive["filename"])
                
                remove(f'{Path_Mod}.Update')
            except Exception as E:
                self.Backup(Mode='WriteBack')
                if exists(Path_Mod_Updated):
                    remove(Path_Mod_Updated)
                if exists(f'{Path_Mod}.Update'):
                    rename(f'{Path_Mod}.Update', Path_Mod)
                elif not exists(f'{Path_Mod}'):
                    Mods_Archive = self.Mods_Archives.Get_Value(f'Mods.{Mod_ID}')
                    self.Mod_DownLoad(Mods_Archive)
                Update_Failed.append(Mod_ID)

        return Update_Failed

    def Group_Create(self, Group_ID: str):
        from Data.src.BackEnd.Function.Function import CheckValid_str
        from Data.src.BackEnd.Class.LucasException import StringFormatError

        if Group_ID.upper() == 'DISABLED': Group_ID = 'Disabled'
        self.ExistCheck(Mode='Group', ID=Group_ID, RaiseBy='Exist')
        if not CheckValid_str(String=Group_ID, Format=r'[A-Za-z0-9_]+'):
            raise StringFormatError(Message='Group_ID not fit the format.',
                                    String=f'{Group_ID}',
                                    Format=r'[A-Za-z0-9_]+')

        self.Mods_Archives.Set_Value(Key_Locate=f'Groups.{Group_ID}',
                                     Value={"GroupName": Group_ID,
                                            "ModsList": []})

    def Group_Delete(self, Group_ID: str):
        from Data.src.BackEnd.Class.LucasException import ProtectedObject

        self.ExistCheck(Mode='Group', ID=Group_ID, RaiseBy='Exist')
        if Group_ID.upper() == 'DISABLED': raise ProtectedObject(Message='Target Group was Protected, Cannot be Deleted.',
                                                           Object_Locate=f'Groups.{Group_ID}')

        self.Mods_Archives.POP_Key(f'Groups.{Group_ID}')

    def Group_Addition(self, Group_ID: str, Mods_ID: tuple[str]):
        from os import rename
        from os.path import exists

        self.ExistCheck(Mode='Group', ID=Group_ID, RaiseBy='NotExist')
        Addition_Failed: list = []

        match Group_ID:
            case 'Disabled':
                FileName_Mod: str = None
                Path_Mod: str = ''
                Mod_Archive: dict = {}
                for Mod_ID in Mods_ID:
                    self.Backup()
                    try:
                        self.ExistCheck(Mode='Mod', ID=Mod_ID, RaiseBy='NotExist')

                        if not Mod_ID in self.Mods_Archives.Get_Value(f'Groups.{Group_ID}.ModsList'):
                            FileName_Mod: str = self.Mods_Archives.Get_Value(f'Mods.{Mod_ID}.filename')
                            Path_Mod = rf'{self.Path_ModsFolder}\{FileName_Mod}'
                            rename(Path_Mod, f'{Path_Mod}.Disabled')
                            self.Mods_Archives.Set_Value(Key_Locate=f'Mods.{Mod_ID}.filename', Value=f'{FileName_Mod}.Disabled')
                            self.Mods_Archives.Get_Value(f'Mods.{Mod_ID}.Groups').append(Group_ID)
                            self.Mods_Archives.Get_Value(f'Groups.{Group_ID}.ModsList').append(Mod_ID)
                    except Exception as E:
                        self.Backup('WriteBack')
                        if exists(f'{Path_Mod}.Disabled'):
                            rename(f'{Path_Mod}.Disabled', Path_Mod)
                        elif not exists(f'{Path_Mod}'):
                            Mod_Archive = self.Mods_Archives.Get_Value(f'Mods.{Mod_ID}')
                            self.Mod_DownLoad(Mod_Archive)
                        Addition_Failed.append(Mod_ID)
            case _:
                for Mod_ID in Mods_ID:
                    self.Backup()
                    try:
                        self.ExistCheck(Mode='Mod', ID=Mod_ID, RaiseBy='NotExist')

                        if not Mod_ID in self.Mods_Archives.Get_Value(f'Groups.{Group_ID}.ModsList'):
                            self.Mods_Archives.Get_Value(f'Mods.{Mod_ID}.Groups').append(Group_ID)
                            self.Mods_Archives.Get_Value(f'Groups.{Group_ID}.ModsList').append(Mod_ID)
                    except Exception as E:
                        self.Backup('WriteBack')
                        Addition_Failed.append(Mod_ID)

        return Addition_Failed

    def Group_Remove(self, Group_ID: str, Mods_ID: tuple[str]):
        from os import rename
        from os.path import exists

        self.ExistCheck(Mode='Group', ID=Group_ID, RaiseBy='NotExist')
        Remove_Failed: list = []

        match Group_ID:
            case 'Disabled':
                FileName_Mod: str = None
                Path_Mod: str = ''
                Mod_Archive: dict = {}
                for Mod_ID in Mods_ID:
                    self.Backup()
                    try:
                        self.ExistCheck(Mode='Mod', ID=Mod_ID, RaiseBy='NotExist')

                        if Mod_ID in self.Mods_Archives.Get_Value(f'Groups.{Group_ID}.ModsList'):
                            FileName_Mod: str = self.Mods_Archives.Get_Value(f'Mods.{Mod_ID}.filename')
                            Path_Mod = rf'{self.Path_ModsFolder}\{FileName_Mod}'
                            rename(Path_Mod, f'{Path_Mod[:-9]}')
                            self.Mods_Archives.Set_Value(Key_Locate=f'Mods.{Mod_ID}.filename', Value=f'{FileName_Mod[:-9]}')
                            self.Mods_Archives.Get_Value(f'Mods.{Mod_ID}.Groups').remove(Group_ID)
                            self.Mods_Archives.Get_Value(f'Groups.{Group_ID}.ModsList').remove(Mod_ID)
                    except Exception as E:
                        self.Backup('WriteBack')
                        if exists(f'{Path_Mod[:-9]}'):
                            rename(f'{Path_Mod[:-9]}', Path_Mod)
                        elif not exists(f'{Path_Mod[:-9]}'):
                            Mod_Archive = self.Mods_Archives.Get_Value(f'Mods.{Mod_ID}')
                            self.Mod_DownLoad(Mod_Archive)
                        Remove_Failed.append(Mod_ID)
            case _:
                for Mod_ID in Mods_ID:
                    self.Backup()
                    try:
                        self.ExistCheck(Mode='Mod', ID=Mod_ID, RaiseBy='NotExist')

                        if Mod_ID in self.Mods_Archives.Get_Value(f'Groups.{Group_ID}.ModsList'):
                            self.Mods_Archives.Get_Value(f'Mods.{Mod_ID}.Groups').remove(Group_ID)
                            self.Mods_Archives.Get_Value(f'Groups.{Group_ID}.ModsList').remove(Mod_ID)
                    except Exception as E:
                        self.Backup('WriteBack')
                        Remove_Failed.append(Mod_ID)

        return Remove_Failed

class __Mod__():
    def __init__(self, __MAM__: __ModsArchivesManager__):
        from Data.src.BackEnd.Instance import LogManager, LogManage

        self.LogManage: LogManager = LogManage
        self.__MAM__: __ModsArchivesManager__ = __MAM__

    def Search(self, Mod_Name: str, Platform: str, **kwargs):
        '''
        Mod_Name: str = {Mod Name}
        Platform: str = 'Modrinth' | 'CurseForge' | ...
        kwargs: dict = {"query": '被用以搜索的关键字 即 Mod_Name',
                        "facets": [用于筛选结果的分类器],
                        "index": '用于对搜索结果进行排序的排序方法',
                        "offset": 搜索的偏移量 即跳过的结果数,
                        "limit": 搜索返回的结果数} -> 如果 Platform 为 Modrinth 时的情况
        '''
        try:
            HitsMods_Info, Pagination = self.__MAM__.Mod_Search(Mod_Name=Mod_Name, Platform=Platform, **kwargs)
        except Exception as E:
            match type(E).__name__:
                case '___':
                    self.LogManage.LogOutput(Level='Warn', LogMessage=f'<Mod Search> {E}')
                case _:
                    self.LogManage.LogOutput(Level='Error', LogMessage=f'<Mod Search> Unexpected Error -> {E}')
            return [], {}
        else:
            self.LogManage.LogOutput(Level='Normal', LogMessage=f'<Mod Search> Mod Search Succeeded -> {Mod_Name} in {Platform}')
            return HitsMods_Info, Pagination

    def Addition(self, Mod_ID: str, Platform: str):
        try:
            self.__MAM__.Mod_Addition(Mod_ID=Mod_ID, Platform=Platform)
        except Exception as E:
            match type(E).__name__:
                case '___':
                    self.LogManage.LogOutput(Level='Warn', LogMessage=f'<Mod Addition> {E}')
                case _:
                    self.LogManage.LogOutput(Level='Error', LogMessage=f'<Mod Addition> Unexpected Error -> {E}')

            return False
        else:
            self.LogManage.LogOutput(Level='Normal', LogMessage=f'<Mod Addition> Mod Addition Succeeded -> {Mod_ID}')
            return True

    def Remove(self, Mods_ID: list[str] | tuple[str] | str) -> list:
        match str(type(Mods_ID)):
            case "<class 'str'>":
                Mods_ID: tuple = (Mods_ID,)
            case "<class 'list'>":
                Mods_ID: tuple = tuple(Mods_ID)
            case "<class 'tuple'>":
                Mods_ID: tuple = Mods_ID
            case _:
                return
        try:
            Remove_Failed: list = self.__MAM__.Mod_Remove(Mods_ID=Mods_ID)
        except Exception as E:
            match type(E).__name__:
                case '___':
                    self.LogManage.LogOutput(Level='Warn', LogMessage=f'<Mod Remove> {E}')
                case _:
                    self.LogManage.LogOutput(Level='Error', LogMessage=f'<Mod Remove> Unexpected Error -> {E}')
        else:
            self.LogManage.LogOutput(Level='Normal', LogMessage=f'<Mod Remove> Mod Remove Succeeded')
            return Remove_Failed

    def UpDate(self, Mods_ID: list[str] | tuple[str] | str) -> list:
        match str(type(Mods_ID)):
            case "<class 'str'>":
                Mods_ID: tuple = (Mods_ID,)
            case "<class 'list'>":
                Mods_ID: tuple = tuple(Mods_ID)
            case "<class 'tuple'>":
                Mods_ID: tuple = Mods_ID
            case _:
                return

        try:
            Update_Failed: list = self.__MAM__.Mod_Update(Mods_ID=Mods_ID)
        except Exception as E:
            match type(E).__name__:
                case '___':
                    self.LogManage.LogOutput(Level='Warn', LogMessage=f'<Mod UpDate> {E}')
                case _:
                    self.LogManage.LogOutput(Level='Error', LogMessage=f'<Mod UpDate> Unexpected Error -> {E}')
        else:
            self.LogManage.LogOutput(Level='Normal', LogMessage=f'<Mod UpDate> Mod UpDate Succeeded')
            return Update_Failed

    def ReName(self, Mod_ID: str, Mod_Name: str):
        try:
            self.__MAM__.Mods_Archives.Set_Value(Key_Locate=f'Mods.{Mod_ID}.ModName', Value=Mod_Name)
        except Exception as E:
            match type(E).__name__:
                case '___':
                    self.LogManage.LogOutput(Level='Warn', LogMessage=f'<Mod ReName> {E}')
                case _:
                    self.LogManage.LogOutput(Level='Error', LogMessage=f'<Mod ReName> Unexpected Error -> {E}')
        else:
            self.LogManage.LogOutput(Level='Normal', LogMessage=f'<Mod ReName> Mod ReName Succeeded')
            return True

    def Disable(self, Mods_ID: list[str] | tuple[str] | str, Mode: any = True):
        match str(type(Mods_ID)):
            case "<class 'str'>":
                Mods_ID: tuple = (Mods_ID,)
            case "<class 'list'>":
                Mods_ID: tuple = tuple(Mods_ID)
            case "<class 'tuple'>":
                Mods_ID: tuple = Mods_ID
            case _:
                return

        Mode_Name: str = ''
        try:
            match bool(Mode):
                case True:
                    Mode_Name = 'Disable'
                    DisEnable_Failed: list = self.__MAM__.Group_Addition(Group_ID='Disabled', Mods_ID=Mods_ID)
                case False:
                    Mode_Name = 'Enable'
                    DisEnable_Failed: list = self.__MAM__.Group_Remove(Group_ID='Disabled', Mods_ID=Mods_ID)
        except Exception as E:
            match type(E).__name__:
                case '___':
                    self.LogManage.LogOutput(Level='Warn', LogMessage=f'<Mod {Mode_Name}> {E}')
                case _:
                    self.LogManage.LogOutput(Level='Error', LogMessage=f'<Mod {Mode_Name}> Unexpected Error -> {E}')
        else:
            self.LogManage.LogOutput(Level='Normal', LogMessage=f'<Mod {Mode_Name}> Mod {Mode_Name} Succeeded')
            return DisEnable_Failed

class __Group__():
    def __init__(self, __MAM__: __ModsArchivesManager__):
        from Data.src.BackEnd.Instance import LogManager, LogManage

        self.LogManage: LogManager = LogManage
        self.__MAM__: __ModsArchivesManager__ = __MAM__

    def Create(self, Group_ID: str):
        try:
            self.__MAM__.Group_Create(Group_ID=Group_ID)
        except Exception as E:
            match type(E).__name__:
                case '___':
                    self.LogManage.LogOutput(Level='Warn', LogMessage=f'<Group Create> {E}')
                case _:
                    self.LogManage.LogOutput(Level='Error', LogMessage=f'<Group Create> Unexpected Error -> {E}')
        else:
            self.LogManage.LogOutput(Level='Normal', LogMessage=f'<Group Create> Group Create Succeeded')
            return True

    def Delete(self, Group_ID: str):
        try:
            self.__MAM__.Group_Delete(Group_ID=Group_ID)
        except Exception as E:
            match type(E).__name__:
                case '___':
                    self.LogManage.LogOutput(Level='Warn', LogMessage=f'<Group Delete> {E}')
                case _:
                    self.LogManage.LogOutput(Level='Error', LogMessage=f'<Group Delete> Unexpected Error -> {E}')
        else:
            self.LogManage.LogOutput(Level='Normal', LogMessage=f'<Group Delete> Group Delete Succeeded')
            return True

    def ReName(self, Group_ID: str, Group_Name: str):
        try:
            self.__MAM__.Mods_Archives.Set_Value(Key_Locate=f'Groups.{Group_ID}.GroupName', Value=Group_Name)
        except Exception as E:
            match type(E).__name__:
                case '___':
                    self.LogManage.LogOutput(Level='Warn', LogMessage=f'<Group ReName> {E}')
                case _:
                    self.LogManage.LogOutput(Level='Error', LogMessage=f'<Group ReName> Unexpected Error -> {E}')
        else:
            self.LogManage.LogOutput(Level='Normal', LogMessage=f'<Group ReName> Group ReName Succeeded')
            return True

    def Addition(self, Group_ID: str, Mods_ID: list[str] | tuple[str] | str):
        match str(type(Mods_ID)):
            case "<class 'str'>":
                Mods_ID: tuple = (Mods_ID,)
            case "<class 'list'>":
                Mods_ID: tuple = tuple(Mods_ID)
            case "<class 'tuple'>":
                Mods_ID: tuple = Mods_ID
            case _:
                return

        try:
            Addition_Failed: list = self.__MAM__.Group_Addition(Group_ID=Group_ID ,Mods_ID=Mods_ID)
        except Exception as E:
            match type(E).__name__:
                case '___':
                    self.LogManage.LogOutput(Level='Warn', LogMessage=f'<Group Addition> {E}')
                case _:
                    self.LogManage.LogOutput(Level='Error', LogMessage=f'<Group Addition> Unexpected Error -> {E}')
        else:
            self.LogManage.LogOutput(Level='Normal', LogMessage=f'<Group Addition> Group Addition Succeeded')
            return Addition_Failed

    def Remove(self, Group_ID: str, Mods_ID: list[str] | tuple[str] | str):
        match str(type(Mods_ID)):
            case "<class 'str'>":
                Mods_ID: tuple = (Mods_ID,)
            case "<class 'list'>":
                Mods_ID: tuple = tuple(Mods_ID)
            case "<class 'tuple'>":
                Mods_ID: tuple = Mods_ID
            case _:
                return

        try:
            Remove_Failed: list = self.__MAM__.Group_Remove(Group_ID=Group_ID ,Mods_ID=Mods_ID)
        except Exception as E:
            match type(E).__name__:
                case '___':
                    self.LogManage.LogOutput(Level='Warn', LogMessage=f'<Group Remove> {E}')
                case _:
                    self.LogManage.LogOutput(Level='Error', LogMessage=f'<Group Remove> Unexpected Error -> {E}')
        else:
            self.LogManage.LogOutput(Level='Normal', LogMessage=f'<Group Remove> Group Remove Succeeded')
            return Remove_Failed

class ModsManager():
    def __init__(self, Project_ID: str, Project_Info: dict):
        self.__MAM__: __ModsArchivesManager__ = __ModsArchivesManager__(Project_ID=Project_ID, Project_Info=Project_Info)
        
        self.Mod: __Mod__ = __Mod__(__MAM__=self.__MAM__)
        self.Group: __Mod__ = __Mod__(__MAM__=self.__MAM__)

if __name__ == '__main__':
    pass