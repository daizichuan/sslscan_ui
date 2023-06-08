@echo off
title 执行SSL Scan WebUI脚本

:: 脚本目录
cd /d C:\pycharm\run\ui-test\SSLScan_UI\test_cases

:begin
echo ************************************************
echo *
echo *	输入1：运行功能用例
echo *	输入2：运行站点扫描
echo *
echo ************************************************

set /p num=请输入：

if %num%==1 goto function
if %num%==2 (goto scan) else goto begin

:function
python test_detection_page.py
pause
exit

:scan
python test_websites_scan2.0.py
pause
exit