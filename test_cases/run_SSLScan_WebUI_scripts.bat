@echo off
title ִ��SSL Scan WebUI�ű�

:: �ű�Ŀ¼
cd /d C:\pycharm\run\ui-test\SSLScan_UI\test_cases

:begin
echo ************************************************
echo *
echo *	����1�����й�������
echo *	����2������վ��ɨ��
echo *
echo ************************************************

set /p num=�����룺

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