from Data.src.BackEnd.Instance import INET_Switch

from Data.src.BackEnd.Class.Manager_Projects import ProjectsManager
from Data.src.BackEnd.Class.Manager_ModsArchives import ModsManager

from time import sleep as Time_Sleep
from pprint import pprint




INET_Switch.Switch(Target= 'IPV4')
ProjectManage: ProjectsManager = ProjectsManager()

print(f'Now, Trying to Create New Projects -> [ID: Test_01], [ID: Test_02]')
ProjectManage.Create(Project_ID='Test_01', Project_Name='测试_01', Mods_Location=r'Test\Mods\Mods_01', BasicMsg=('1.19.1', 'forge'))
ProjectManage.Create(Project_ID='Test_02', Project_Name='测试_02', Mods_Location=r'Test\Mods\Mods_02', BasicMsg=('1.21.4', 'fabric'))

Time_Sleep(1)

print(f'All the Project ID:')
for Project_ID in ProjectManage.Projects.Get_Keys():
    print(f"\tProject ID: {Project_ID} -> Project_Name: {ProjectManage.Projects.Get_Value(f'{Project_ID}.Project_Name')}")

Time_Sleep(1)

print(f'Now, Trying to Delete the Project -> [ID: Test_01]')
ProjectManage.Delete(Project_ID='Test_01')

Time_Sleep(1)

print(f'All the Project ID:')
for Project_ID in ProjectManage.Projects.Get_Keys():
    print(f"\tProject ID: {Project_ID} -> Project_Name: {ProjectManage.Projects.Get_Value(f'{Project_ID}.Project_Name')}")

Time_Sleep(1)

ModsManage: ModsManager = ModsManager(Project_ID='Test_02', Project_Info=ProjectManage.Project_Info(Project_ID='Test_02'))
print(f'Now, Trying to Search Mod By Mod Name -> [Mod Name: Carpet]')
HitsMods_Info, Pagination = ModsManage.Mod.Search(Mod_Name='Carpet', Platform='Modrinth')
pprint(HitsMods_Info)

Time_Sleep(1)

print(f'Now, Trying to Add Mod to the Project -> [Project ID: Test_01] [Mod ID: carpet]')
ModsManage.Mod.Addition(Mod_ID='carpet', Platform='Modrinth')

Time_Sleep(1)

print(f'Now, Trying to Disable Mod from the Project -> [Project ID: Test_01] [Mod ID: carpet]')
ModsManage.Mod.Disable(Mode=1, Mods_ID='carpet')

Time_Sleep(1)

print(f'Now, Trying to Enable Mod from the Project -> [Project ID: Test_01] [Mod ID: carpet]')
ModsManage.Mod.Disable(Mode=0, Mods_ID='carpet')

Time_Sleep(1)

print(f'Now, Trying to Update All Mods in the Project -> [Project ID: Test_01]')
ModsManage.Mod.UpDate(Mods_ID='__ALL__')

Time_Sleep(1)

print(f'Now, Delete One Last Mod -> [Project ID: Test_01] [Mod ID: carpet]')
ModsManage.Mod.Remove(Mods_ID='carpet')

Time_Sleep(1)

print(f'Now, Delete One Last Project -> [Project ID: Test_02]')
ProjectManage.Delete(Project_ID='Test_02')