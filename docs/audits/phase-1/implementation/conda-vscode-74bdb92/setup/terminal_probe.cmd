@call "E:\WORK\Anaconda\Scripts\activate.bat" "E:\WORK\Anaconda\envs\aqrp-p1"
@if errorlevel 1 exit /b %errorlevel%
@python -X utf8 "C:\Users\11638\AppData\Local\AQRP\runs\conda-vscode-1792572943050\runtime_probe.py"
@exit /b %errorlevel%
