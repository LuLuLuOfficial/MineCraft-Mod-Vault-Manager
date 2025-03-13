from Data.Lib.PyLucas.Manager_Projects import ProjectsManager
from Data.Lib.PyLucas.Manager_Mods import ModsManager
from Data.Lib.PyLucas.Function.INET_Switcher import INET_Switch

if __name__ == '__main__':
    from time import sleep

    INET_Switch.Switch(Target= 'IPV4')
    ProjectManage: ProjectsManager = ProjectsManager()

    # ProjectManage.Create(Project_ID='Test_01', Mods_Location=r'Test\Mods_01', BasicMsg=('1.19.2', 'fabric'))
    # ProjectManage.Create(Project_ID='Test_02', Mods_Location=r'Test\Mods_02', BasicMsg=('1.20.1', 'fabric'))

    ModsManage: ModsManager = ModsManager(Project_ID='Test_01', Project_Info=ProjectManage.Project_Info('Test_01'))

    ModsManage.Mod.Addition('carpet')
    ModsManage.Mod.Addition('fabric-api')
    ModsManage.Mod.Disable(('carpet',))
    ModsManage.Group.Create('Group_01')
    ModsManage.Group.Create('Group_02')
    ModsManage.Group.ReName('Group_01', '组_01')
    ModsManage.Group.Addition('Group_01', ('fabric-api',))

    ModsManage: ModsManager = ModsManager(Project_ID='Test_02', Project_Info=ProjectManage.Project_Info('Test_02'))

    ModsManage.Mod.Addition('carpet')
    ModsManage.Mod.Addition('fabric-api')
    ModsManage.Mod.Disable(('carpet',))
    ModsManage.Group.Create('Group_11')
    ModsManage.Group.Create('Group_12')
    ModsManage.Group.ReName('Group_11', '组_11')
    ModsManage.Group.Addition('Group_11', ('fabric-api',))

