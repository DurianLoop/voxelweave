@echo off
setlocal
cd /d D:\MRI
set "PYTHONPATH=D:\MRI\pre;D:\MRI\baseline;D:\MRI\design;D:\MRI"
set "IXI_DATA_ROOT=D:\MRI\dataset\IXI"
"D:\conda\envs\MRI\python.exe" -u -B -m ixi_ecsinet_2p5d.one_click --through mini
set "EXIT_CODE=%ERRORLEVEL%"
echo.
if "%EXIT_CODE%"=="0" (
  echo ECSI-Net acceptance stages finished.
) else if "%EXIT_CODE%"=="2" (
  echo GPU is busy. Existing work was preserved; run this file again after the GPU is free.
) else (
  echo ECSI-Net acceptance stopped at a failed gate. Exit code: %EXIT_CODE%
)
pause
exit /b %EXIT_CODE%
