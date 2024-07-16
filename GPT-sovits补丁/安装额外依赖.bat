@echo off
"runtime/python.exe" -m pip cache purge
"runtime/python.exe" -m pip install --upgrade pip
"runtime/python.exe" -m pip install gradio==4.36.1
"runtime/python.exe" -m pip install numpy soundfile gradio_client==1.0.1
"runtime/python.exe" -m pip install selenium==4.3.0 webdriver_manager==4.0.1 tencentcloud-sdk-python
"runtime/python.exe" -m pip install pygame==2.5.2
"runtime/python.exe" -m pip install requests==2.32.3
"runtime/python.exe" -m pip install requests==2.32.3
"runtime/python.exe" -m pip install fastapi==0.111.0
"runtime/python.exe" -m pip install pydantic==2.7.4
"runtime/python.exe" -m pip install install uvicorn[standard]
"runtime/python.exe" -m pip install urllib3==1.26.19
pause

