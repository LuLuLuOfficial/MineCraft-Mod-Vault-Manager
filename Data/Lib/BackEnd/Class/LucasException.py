# Public
class UnFixedKnownBug(Exception):# 未被处理的已知Bug
    def __init__(self,
                 *args,
                 Message: str = 'Known Bugs That Have Not Been Addressed.',
                 BugDescribe: str = 'None'):
        self.Message = f'{Message}[BugDescribe: {BugDescribe}]'
        self.Message += f'-[Addition->{args}]'
        super().__init__(self.Message)

class UnKnownBug(Exception):# 未知Bug
    def __init__(self,
                 *args,
                 Message: str = 'Unknown Bug.',
                 BugDescribe: str = 'None'):
        self.Message = f'{Message}[BugDescribe: {BugDescribe}]'
        self.Message += f'-[Addition->{args}]'
        super().__init__(self.Message)

class StringFormatError(Exception):  # 不合法的字符串输入
    def __init__(self,
                 *args,
                 Message: str = 'String composition not as expected.',
                 String: str = 'None',
                 Format: str = 'None'):
        self.Message: str = f'{Message}[String: {String} - Format Rule: {Format}]'
        self.Message += f'-[Addition->{args}]'
        super().__init__(self.Message)

# Function
class FileDownloadFailed(Exception):# 下载文件失败
    def __init__(self,
                 *args,
                 Message: str = 'Failed To Download The File.',
                 FilePath: str = 'None',
                 Type: str = 'None'):
        self.Message = f'{Message}[{Type} -> {FilePath}]'
        self.Message += f'-[Addition->{args}]'
        super().__init__(self.Message)

# API_Modrinth | API_ | API_...
class BadConnection(Exception):     # 无法连接到目标地址
    def __init__(self,
                 *args,
                 Message: str = 'Unable to connect to target address.',
                 Address: str = 'None',
                 Status_Code: int = None):
        self.Message: str = f'{Message}[Address: {Address} - Status_Code: {Status_Code}]'
        self.Message += f'-[Addition->{args}]'
        super().__init__(self.Message)

class UnSupportedPlatform(Exception):   # 不支持的Mod平台
    def __init__(self,
                 *args,
                 Message: str = 'Requested an API with Unsupported platform.',
                 Platform: str = 'None'):
        self.Message = f'{Message}[Platform: {Platform}]'
        self.Message += f'-[Addition->{args}]'
        super().__init__(self.Message)

class UnSupportLoader(Exception):   # 不支持的MOD加载器
    def __init__(self,
                 *args,
                 Message: str = 'Requested UnSupported Mod Loader.',
                 ModLoader: str = 'None'):
        self.Message: str = f'{Message}[Target Loader: {ModLoader}]'
        self.Message += f'-[Addition->{args}]'
        super().__init__(self.Message)

class UnSupportVersion(Exception):  # 不支持的游戏版本
    def __init__(self,
                 *args,
                 Message: str = 'Requested UnSupported Game Version.',
                 GameVersion: str = 'None'):
        self.Message: str = f'{Message}[Target Version: {GameVersion}]'
        self.Message += f'-[Addition->{args}]'
        super().__init__(self.Message)

class NonExistentModVersion(Exception):# 无法定位到目标的Mod版本
    def __init__(self,
                 *args,
                 Message: str = 'Requested Mod Version does not exist on the target Platform.',
                 Platform: str = 'None',
                 Mod_ID: str = 'None',
                 Type: str = 'None'):
        self.Message = f'{Message}[Platform: {Platform} | Mod_ID: {Mod_ID} | Type: {Type}]'
        self.Message += f'-[Addition->{args}]'
        super().__init__(self.Message)

# Manager Projects & Mods Archives
class NonExistentObject(Exception):# 不存在的对象
    def __init__(self,
                 *args,
                 Message = 'The Requested Object Not Exist.',
                 Object_ID: str = 'None'):
        self.Message = f'{Message}[Object_ID: {Object_ID}]'
        self.Message += f'-[Addition->{args}]'
        super().__init__(self.Message)

class DuplicateObject(Exception):# 重复的对象
    def __init__(self,
                 *args,
                 Message: str = 'The Requested Object Already Exists.',
                 Object_ID: list[str] = ['Existing_Object_ID', 'Creating_Object_ID'],
                 Attribute: list[str] = ['Key', 'Value']):
        self.Message: str = f'{Message}[Object_ID: [Existing->{Object_ID[0]}, Creating->{Object_ID[1]}] - Attribute: [Key->{Attribute[0]}, Value->{Attribute[1]}]]'
        self.Message += f'-[Addition->{args}]'
        super().__init__(self.Message)

class ProtectedObject(Exception):# 受保护的对象
    def __init__(self,
                 *args,
                 Message: str = 'Target Object was Protected.',
                 Object_Locate: str = 'None'):
        self.Message: str = f'{Message}[Object Location: {Object_Locate}]'
        self.Message += f'-[Addition->{args}]'
        super().__init__(self.Message)

if __name__ == '__main__':
    try:
        raise BadConnection(Addition='400')
    except Exception as E:
        print(f"{type(E).__name__}")
        print(f"{E}")