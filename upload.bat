@echo off
:: Ԥ����Ƿ�������蹤��
where python >nul 2>nul
if not %ERRORLEVEL% equ 0 (
    echo δ�ҵ�python!
    exit /b 127
)
where twine >nul 2>nul
if not %ERRORLEVEL% equ 0 (
    echo δ�ҵ�twine��ִ���ļ�!
    echo �����Ļ���û�а�װ��������, ��ִ��:
    echo pip install setuptools wheel
    echo ���Ƿ����ǰ�װtwine��? ��ִ�����������:
    echo pip install twine
    exit /b 127
)
:: ��ʼ�������ϴ�
python setup.py sdist bdist_wheel > nul
if not %ERRORLEVEL% equ 0 (
    echo === ����ʧ�� :( ===
    exit /b 1
)
echo ==���������APIKEY==
twine upload dist/*
if %ERRORLEVEL% equ 0 (
    echo === �ϴ��ɹ�! ===
    exit /b 0
) else (
    echo === �ϴ�ʧ�� :( ===
    exit /b 1
)
