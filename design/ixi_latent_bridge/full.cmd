@echo off
"D:\conda\envs\MRI\python.exe" -B -u "%~dp0launch.py" %*
exit /b %ERRORLEVEL%
