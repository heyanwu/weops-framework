# WeOPS-Framework

<img src="https://wedoc.canway.net/imgs/img/嘉为蓝鲸.jpg" >


#### 更多资料/工具包下载可见“蓝鲸 S-mart市场”
https://bk.tencent.com/s-mart/application/282/detail

#### 更多问题欢迎添加“小嘉”微信，加入官方沟通群

<img src="https://wedoc.canway.net/imgs/img/小嘉.jpg" width="30%" height="30%">


# 嘉为蓝鲸WeOPS基础框架使用说明

## 开发使用

### 产品 LOGO

请将你的产品 LOGO 命名为 "{APP_CODE}.png"（APP_CODE 是你的应用 ID），并分别放在最外层目录和 static/img 目录下。
最外层目录下的 LOGO 用于通过 "S-mart应用" 方式部署时自动识别产品 LOGO，避免实施团队的需要手动上传 LOGO。
static/img 目录下的 LOGO 用于浏览器标签页识别 icon，提升产品体验。

## 分支管理

- master

master 是主分支。

- release

release 作为部署和发包分支，在分支代码更新后，触发 GitLab CI 自动从 release 分支获取最新代码，并在 CI 中运行前端打包，然后推送到仓库。
该分支支持在蓝鲸开发者中心源码部署进行联调测试，后续可以考虑自动部署。
该分支作为发布分支，支持在实施时通过"一键打包"等工具拉取包含打包好的前端资源的产品代码，并在客户环境通过 "S-mart应用" 方式部署。

## 集成工具说明

### pre-commit

pre-commit 是基于 Git Hooks 的本地开发套件，支持通过插件扩展能力。目前支持 PEP8 规范检查、代码格式化、commit 信息检查、
requirements.txt 包检查等功能。
