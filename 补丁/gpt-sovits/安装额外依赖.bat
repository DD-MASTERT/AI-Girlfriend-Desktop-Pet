@echo off
"runtime/python.exe" -m pip cache purge
"runtime/python.exe" -m pip install --upgrade pip
"runtime/python.exe" -m pip install gradio==4.36.1
"runtime/python.exe" -m pip install numpy soundfile gradio_client==1.0.1
"runtime/python.exe" -m pip install requests==2.32.3
pause

