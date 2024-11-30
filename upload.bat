@echo off
:: 预检测是否存在所需工具
where python >nul 2>nul
if not %ERRORLEVEL% equ 0 (
    echo 未找到python!
    exit /b 127
)
where twine >nul 2>nul
if not %ERRORLEVEL% equ 0 (
    echo 未找到twine可执行文件!
    echo 如果你的环境没有安装构建工具, 请执行:
    echo pip install setuptools wheel
    echo 你是否忘记安装twine了? 请执行下面的命令:
    echo pip install twine
    exit /b 127
)
:: 开始构建并上传
python setup.py sdist bdist_wheel > nul
if not %ERRORLEVEL% equ 0 (
    echo === 编译失败 :( ===
    exit /b 1
)
echo ==请输入你的APIKEY==
twine upload dist/*
if %ERRORLEVEL% equ 0 (
    echo === 上传成功! ===
    exit /b 0
) else (
    echo === 上传失败 :( ===
    exit /b 1
)
