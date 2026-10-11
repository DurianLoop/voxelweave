@echo off
"D:\conda\envs\MRI\python.exe" -B -u "%~dp0bootstrap.py" %*
exit /b %ERRORLEVEL%
