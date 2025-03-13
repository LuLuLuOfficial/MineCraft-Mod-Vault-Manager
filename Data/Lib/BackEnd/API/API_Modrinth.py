from requests import get, Response
from ..Class.LucasException import BadConnection, UnSupportLoader, UnSupportVersion, UnFixedKnownBug, NonExistentModVersion

def Check_APIAlive(URL: str = 'https://staging-api.modrinth.com/') -> int:
    '''API存活检测'''
    response: Response = get(url=URL, timeout=5)
    if response.status_code != 200:
        raise BadConnection(Address=URL,
                            Status_Code=response.status_code)
    return True

def Check_GameVersion(Game_Version: str) -> bool:
    '''版本存在检测'''
    API_GameVersions: str = 'https://api.modrinth.com/v2/tag/game_version'
    response: Response = get(url=API_GameVersions, timeout=5)
    if response.status_code != 200:
        raise BadConnection(Address=API_GameVersions,
                            Status_Code=response.status_code)
    
    Versions: list = response.json()
    Version_Found: bool = False
    for Version in Versions:
        if Version["version"] == Game_Version:
            Version_Found = True
            break

    return Version_Found

def Check_ModeLoader(Mods_Loader: str) -> bool:
    '''加载器存在检测'''

    API_ModeLoaders: str = 'https://api.modrinth.com/v2/tag/loader'
    response: Response = get(url=API_ModeLoaders, timeout=5)
    if response.status_code != 200:
        raise BadConnection(Address=API_ModeLoaders,
                            Status_Code=response.status_code)
    
    Loaders: list = response.json()
    Loader_Found: bool = False
    for Loader in Loaders:
        if Loader["name"] == Mods_Loader:
            Loader_Found = True
            break

    return Loader_Found

def Mod_Search(Mod_Name: str,
               Project_Info: dict,
               Params: dict = {"query": '',
                               "facets": [["project_type:mod"]],
                               "index": 'relevance',
                               "offset": 0,
                               "limit": 10}) -> list | dict:
    '''
    Project_Info: dict = {"Game_Version": '游戏版本',
                          "Mods_Loader": 'Mod加载器版本',
                          "Mods_Location": '不重要',
                          "Date_Created": '不重要',
                          "Date_Modified": '不重要'}
    Params: dict = {"query": '被用以搜索的关键字 即 Mod_Name',
                    "facets": [用于筛选结果的分类器],
                    "index": '用于对搜索结果进行排序的排序方法',
                    "offset": 搜索的偏移量 即跳过的结果数,
                    "limit": 搜索返回的结果数})
    '''
    Params["query"] = Mod_Name
    Params["facets"].append([f'versions:{Project_Info["Game_Version"]}'])
    Params["facets"].append([f'categories:{Project_Info["Mods_Loader"]}'])
        
    API_Search = 'https://api.modrinth.com/v2/search'
    response: Response = get(url=API_Search, timeout=5)
    if response.status_code != 200:
        raise BadConnection(Address=API_Search,
                            Status_Code=response.status_code)

    response_json: dict = response.json()
    del response

    Pagination: dict = {
        "Params": Params,
        "Total_Hits": response_json["total_hits"]
    }

    HitsMods: list = response_json["hits"]
    HitsMods_Info: list = []

    for HitMod in HitsMods:
        HitsMods_Info.append({
            "Mod_Name": HitMod.get("title"),
            "Mod_ID": HitMod.get("slug"),
            "URL_Icon": HitMod.get("icon_url"),
            "URL_Mod": f'https://modrinth.com/mod/{HitMod.get("slug")}',
            "Description": HitMod.get("description")
        })

    return HitsMods_Info, Pagination

def Mod_Locate(Mod_ID: str, Project_Info: dict, Cribble: bool = True) -> dict:
    '''
    Mod_ID: str = {Mod_ID}
    Project_Info: dict = {"Game_Version": '游戏版本',
                          "Mods_Loader": 'Mod加载器版本',
                          "Mods_Location": '不重要',
                          "Date_Created": '不重要',
                          "Date_Modified": '不重要'}
    Cribble: bool = True | False -> 是否执行初步筛查
    '''
    if Cribble:
        # Preliminary judgment on whether there is a Mod version corresponding to the expected one
        API_Locate_1 = f'https://api.modrinth.com/v2/project/{Mod_ID}'
        response: Response = get(url=API_Locate_1, timeout=5)
        if response.status_code != 200:
            raise BadConnection(Address=API_Locate_1,
                                Status_Code=response.status_code)

        response_json: dict = response.json()
        del response
        if not Project_Info["Game_Version"] in response_json["game_versions"]:
            raise NonExistentModVersion(Platform='Modrinth',
                                        Mod_ID=Mod_ID,
                                        Type=f'Unsupported Game Version: {Project_Info["Game_Version"]}')
        if not Project_Info["Mods_Loader"] in response_json["loaders"]:
            raise NonExistentModVersion(Platform='Modrinth',
                                        Mod_ID=Mod_ID,
                                        Type=f'Unsupported Mods Loader: {Project_Info["Mods_Loader"]}')
    else:
        API_Locate_2 = f'https://api.modrinth.com/v2/project/{Mod_ID}/version'
        response: Response = get(url=API_Locate_2, timeout=5)
        if response.status_code != 200:
            raise BadConnection(Address=API_Locate_1,
                                Status_Code=response.status_code)

        response_json: dict = response.json()
        Mod_Archive: dict = {}
        del response
        for Mod_Version in response_json:
            if not ((Project_Info['Game_Version'] in Mod_Version['game_versions']) and (Project_Info['Mods_Loader'] in Mod_Version['loaders'])): continue

            if len(Mod_Version["files"]) != 1:
                from inspect import currentframe
                CurrentFrame = currentframe()
                FilePath: str = f'File: {CurrentFrame.f_code.co_filename}'
                ErrorLine: str = f'Line: {CurrentFrame.f_lineno - 4}'
                raise UnFixedKnownBug(FilePath, ErrorLine,
                                      Message='A single version of the Mod has multiple downloadable files',
                                      BugDescribe=f'Expected: len(Mod_Version["files"]) == 1, Actual: len(Mod_Version["files"]) == {len(Mod_Version["files"])}')
            Mod_Archive = {
                "Platform": 'Modrinth',
                "ModName": Mod_ID,
                "Groups": [],
                "Downloaded": 0,
                "DownLoadURL": Mod_Version['files'][0]['url'],
                "version_type": Mod_Version['version_type'], # release | beta | ...
                "hashes": Mod_Version['files'][0]['hashes'],
                "filename": Mod_Version['files'][0]['filename']
            }
            break

        if not Mod_Archive:
            raise NonExistentModVersion(Platform='Modrinth',
                                        Mod_ID=Mod_ID,
                                        Type=f'Expected Mod Version Not Exist: {Project_Info["Mods_Loader"]}')

        return Mod_Archive

if __name__ == '__main__':
    print(Check_APIAlive())
    print(Check_GameVersion('1.21.1'))
    print(Check_ModeLoader('fabric'))
    print(Mod_Search(Mod_Name='Fabric API', Project_Info={"Game_Version": '1.21.1', "Mods_Loader": 'fabric'}))
    print(Mod_Locate(Mod_ID='fabric-api', Project_Info={"Game_Version": '1.21.1', "Mods_Loader": 'fabric'}))