# Github操作指南：
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
