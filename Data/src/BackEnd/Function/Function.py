def CheckValid_str(String: str, Format: str = r'[A-Za-z0-9_]+'):
    from re import fullmatch
    return bool(fullmatch(pattern=Format, string=String))

def HashFile(Path_File: str, HashMode: str) -> str:
    '''
    Path_File: str = 'PathFile'\n
    HashMode: str = 'sha1' | 'sha512'\n
    '''
    from hashlib import sha1, sha512

    match HashMode:
        case 'sha1':
            HashObjects = sha1()
        case 'sha512':
            HashObjects = sha512()

    with open(Path_File, "rb") as f:
        for Byte_Block in iter(lambda: f.read(4096), b""):
            HashObjects.update(Byte_Block)

    return HashObjects.hexdigest()

def Download(Path_Folder: str, File_Name: str, Download_URL: str, Hashes: dict = {}):
    from requests import get, Response
    from os import rename
    from Data.src.BackEnd.Class.LucasException import BadConnection, FileDownloadFailed

    Path_File = rf'{Path_Folder}\{File_Name}.Download'
    
    try:
        response: Response = get(Download_URL, stream=True)
        response.raise_for_status()
    except Exception as E:
        raise BadConnection(*E.args,
                            Address=Download_URL,
                            Status_Code=response.status_code)

    try:
        with open(Path_File, 'wb') as File:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk: File.write(chunk)
    except Exception as E:
        raise E
    else:
        HashTypes: tuple = ('sha1', 'sha512',)
        for HashType in HashTypes:
            if (HashType in Hashes) and (not Hashes["sha1"] == HashFile(Path_File=Path_File, HashMode='sha1')):
                raise FileDownloadFailed(FilePath=Path_File,
                                         Type=f'Hash Check Failed [{HashType}]')
        rename(Path_File, rf'{Path_Folder}\{File_Name}')

if __name__ == '__main__':
    pass