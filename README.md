# Bash操作指南
## 一、打开方式
win+R，输入cmd或者powershell

# Git操作指南
## 一、下载git（浏览器直接搜），一路点到底
## 二、检查git是否在环境变量中生效以及登录git
1. 检查有效性：输入git后直接回车
```Bssh
git
```

2. 登录git：注意cmd是命令行要一条一条输入（多行输入最后一行之前的命令会被自动执行）
```Bash
git config --global user.name "你的名字"  #注意名字要加双引号，邮箱不用
git config --global user.email 你的邮箱   
```

3. 提交git版本更新时要写！日！志！，否则会卡在那不让你交（就是蓝色那个提交按钮上面的消息框要有写的内容才能提交到git）


# Github操作指南：(在VSCode里操作)
## 一、有不清楚的查AI，大部分命令行操作照着往终端输就行
## 二 、这里是日常开发中最标准、最稳健的 Git 命令行 操作流程。
请养成习惯：“早晨来了先拉取，晚上走前提交完”。
### 1. 每天开工第一步：拉取最新代码
防止你写了一天代码，最后发现和同事昨天改的冲突了。

```Bash
cd /d "你的项目路径"
git pull origin main  
#(注：如果你的分支叫 master，就把 main 改成 master)
```
### 2. 每天收工（或完成功能）三连击
写完代码准备提交时的标准操作。

- 第一步：暂存与提交 (Save)
```Bash
git add .
git commit -m "这里写清楚你今天干了啥（比如：修复了登录bug）"
```
- 第二步：再次拉取 (Safety Check) —— 最关键的一步！
在你 Push 之前，必须再拉一次。因为在你写代码的这几个小时里，可能同事已经提交了新代码。

```Bash
git pull origin main
```
如果提示 Already up to date：完美，直接进行第三步。

如果提示 CONFLICT (冲突)：停下来！去代码里解决冲突（手动修改那些 <<<<<<< 的地方），改完后重新 add 和 commit，再继续。

- 第三步：推送到云端 (Upload)
```Bash
git push origin main
```
💡 极简速查表 (可以直接复制)
```Bash
# 1. 进目录
cd /d "D:\你的项目文件夹"

# 2. 提交流程
git add .
git commit -m "日常更新"
git pull origin main
git push origin main
```

## 三、关于项目结构（后续也可扩充）
```text
MCM_Latex2026
│   .Rhistory
│   MCM-ICM_Summary.log
│   MCM-ICM_Summary.pdf
│   MCM-ICM_Summary.tex    //写摘要的tex文件
│   mcmthesis-demo-blx.bib
│   mcmthesis-demo.aux
│   mcmthesis-demo.bbl
│   mcmthesis-demo.log
│   mcmthesis-demo.out
│   mcmthesis-demo.pdf
│   mcmthesis-demo.run.xml
│   mcmthesis-demo.synctex.gz
│   mcmthesis-demo.tex    //这个是核心的tex编写文件！！！
│   mcmthesis-demo.toc
│   mcmthesis.cls
│   mcmthesis.synctex.gz
│   MCM_Latex2024.Rproj
│   README.md
│   table2latex.txt
│   texput.log
│
├───code
│   │   mcmthesis-matlab1.m       //放一些其他零零散散的小代码
│   │   mcmthesis-sudoku.cpp
│   │
│   ├───Python    //放python代码
│   │       func1.py
│   │       func2.py
│   │
│   └───SPSS     //放SPSS相关数据文件
│           todo - 副本.txt
│           todo.txt
│
└───figures
        fig1.jpg
        fig2.jpg
        fig24.JPG
        mcmthesis-aaa-eps-converted-to.pdf
        mcmthesis-logo.pdf
```

# VSCode操作指南
- 简介VSCode
1.本质是个记事本（编辑器），靠插件驱动顺着系统path路径（在设置-高级设置-环境变量里）找到的编译器.exe来实现各种程序代码的编译compile、运行run和调试debug等功能
  
2.和交流的语言一样，代码要有对应的“环境”才能被正确读取与运行。注意VSCode里右下角倒数第三个图标的环境是否正确（特别注意python中虚拟环境是否选择正确），然后注意编码格式不要乱码什么的

3.注意代码文件命名要清晰易懂，写注释。

- 先导入我的VSCode配置文件ychconfig.code-profile

(省去手写config的痛苦步骤...

点击左下角齿轮 ⚙️ -> 配置文件 (Profiles) -> 导入配置文件 (Import Profile)

- 再去点左侧边栏的第三个分支状图标

如果成功检测到了本地安装的git（没有的话重启下电脑再看看）则按上面的按钮将本文件夹设置为一处git仓库

- 再连接本地git仓库到网上的github项目仓库

仓库地址：https://github.com/M0onesy/CEM_MCM_2026.git

- 初次建立本地git仓库与平台github仓库联系的终端命令行
```Bash
git remote add origin https://github.com/M0onesy/CEM_MCM_2026.git  #关联到咱的项目（git可能此时要求你登录github，注意查看浏览器别卡在这里）

#以下命令仅供参考
#一定不要直接执行 git push -u origin main！！！这会强制覆盖掉github上当前的所有文件，要先pull拉下来解决完冲突确认无误后再push上去完成更新。
git remote -v  #查看当前的github关联
git remote remove origin  #删除错误的关联
git pull origin main --allow-unrelated-histories  允许不相关的历史合并（git和github仓库都非空有文件且目前无关联时使用）
```
