from Data.Lib.PyLucas.Manager_Projects import ProjectsManager
from Data.Lib.PyLucas.Manager_Mods import ModsManager
from Data.Lib.PyLucas.Function.INET_Switcher import INET_Switch

from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Any

INET_Switch.Switch(Target= 'IPV4')
ProjectManage: ProjectsManager = ProjectsManager()

from flask import Flask, jsonify, render_template

class __ForntEndApp__:
    def __init__(self, __name__):
        self.app = Flask(__name__)
        CORS(self.app)

        self.ProjectManage: ProjectsManager = None
        self.ModsManage: ModsManager = None
        self.Alive_ProjectManage: bool = False
        self.Alive_ModsManage: bool = False

        self.Initialize()
    
    def Initialize(self):
        from os import getcwd

        self.app.template_folder = rf'{getcwd()}\Main\FrontEnd\Template'
        self.app.static_folder = rf'{getcwd()}\Main\FrontEnd\Static'

        self.Create_ProjectManage()
        
        self.Initialize_Routes_API()
        self.Initialize_Routes_WebPage()

    def Create_ProjectManage(self):
        if not self.Alive_ProjectManage:
            self.ProjectManage = ProjectsManager()
            self.Alive_ProjectManage = True
        return self.ProjectManage

    def Create_ModsManage(self, Project_ID: str):
        if not self.Alive_ModsManage:
            self.ModsManage = ModsManager(Project_ID, self.ProjectManage.Project_Info(Project_ID))
            self.Alive_ModsManage = True
        return self.ModsManage

    def Kill_ProjectManage(self):
        if self.Alive_ProjectManage:
            self.ProjectManage = None
            self.Alive_ProjectManage = False

    def Kill_ModsManage(self, ):
        if self.Alive_ModsManage:
            self.ModsManage = None
            self.Alive_ModsManage = False

    def Initialize_Routes_API(self):
        """初始化API路由"""
        @self.app.route('/API/Projects', methods=['GET'])
        def Projects():
            if self.Alive_ProjectManage:
                return self.ProjectManage.Projects
            else:
                return jsonify({"error": "ProjectManage 未创建."}), 404

        @self.app.route('/API/Projects/ID&Name', methods=['GET'])
        def Projects_ID_Name():
            if self.Alive_ProjectManage:
                Result: dict = {Project_ID: self.ProjectManage.Project_Info(Project_ID)["Project_Name"] for Project_ID in self.ProjectManage.Projects}
                return jsonify(Result)
            else:
                return jsonify({"error": "ProjectManage 未创建."}), 404

        @self.app.route('/API/Project/<Project_ID>', methods=['GET'])
        def Project_Info(Project_ID):
            if self.Alive_ProjectManage:
                return self.ProjectManage.Project_Info(Project_ID)
            else:
                return jsonify({"error": "ProjectManage 未创建."}), 404

        @self.app.route('/API/Project/<Project_ID>/ModsArchive/ID&Name', methods=['GET'])
        def Project_ModsID_Name(Project_ID):
            if self.Alive_ModsManage:
                Result: dict = {Mod_ID: self.ModsManage.Mod.Archive[Mod_ID]["ModName"] for Mod_ID in self.ModsManage.Mod.Archive}
                return jsonify(Result)
            else:
                return jsonify({"error": "ModsManage 未创建."}), 404

        @self.app.route('/API/Project/<Project_ID>/GroupsArchive/ID&Name', methods=['GET'])
        def Project_GroupsID_Name(Project_ID):
            if self.Alive_ModsManage:
                Result: dict = {Group_ID: self.ModsManage.Group.Archive[Group_ID]["GroupName"] for Group_ID in self.ModsManage.Group.Archive}
                return jsonify(Result)
            else:
                return jsonify({"error": "ModsManage 未创建."}), 404

        @self.app.route('/API/Project/<Project_ID>/ModsArchive', methods=['GET'])
        def Project_ModsArchive(Project_ID):
            if self.Alive_ModsManage:
                return jsonify(self.ModsManage.Mod.Archive)
            else:
                return jsonify({"error": "ModsManage 未创建."}), 404

        @self.app.route('/API/Project/<Project_ID>/ModsArchive', methods=['GET'])
        def Project_GroupsArchive(Project_ID):
            if self.Alive_ModsManage:
                return jsonify(self.ModsManage.Group.Archive)
            else:
                return jsonify({"error": "ModsManage 未创建."}), 404

        @self.app.route('/API/Project/<Project_ID>/ModsManager', methods=['GET'])
        def Project_ModsManager():
            pass

        @self.app.route('/API/Test', methods=['POST'])
        def Test():
            Data = request.json
            print(Data)
            return Data
            

    def Initialize_Routes_WebPage(self):
        """初始化WebPage路由"""
        @self.app.route('/', methods=['GET'])
        def Home():
            return 'Welcome to Minecraft Mod Manager!'
        
        @self.app.route('/Help', methods=['GET'])
        def Help():
            return '这里没啥...'

        @self.app.route('/ProjectsManager', methods=['GET'])
        def Manager_Projects():
            return render_template('Manager_Projects.html')

        @self.app.route('/ProjectsManager/<Project_ID>/ModsManager', methods=['GET'])
        def Manager_Project(Project_ID):
            if self.Alive_ProjectManage: 
                self.Kill_ModsManage()
                self.Create_ModsManage(Project_ID)
                return render_template('Manager_Mods.html', Project_ID=Project_ID)
            else:
                return 'ProjectManage 未创建.'

    def run(self,
            host: str | None = None,
            port: int | None = None,
            debug: bool | None = None,
            load_dotenv: bool = True,
            **options: Any):
        self.app.run(host=host,port=port,debug=debug,load_dotenv=load_dotenv,**options)

# 创建并运行 Flask 应用
if __name__ == '__main__':
    ForntEndApp = __ForntEndApp__(__name__)
    ForntEndApp.run(host='0.0.0.0', port=5000, debug=True)