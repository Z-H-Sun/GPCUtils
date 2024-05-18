@ECHO OFF
set PYTHON_DIR=C:\Python34
set MAIN_PYTHON_DIR=py34
set MAIN_PYTHON_DLL={\"py34\\Dlls\\msvcr100.dll\",\"py34\\Dlls\\msvcp100.dll\",\"py34\\Dlls\\python34.dll\"}

FOR %%X IN (readGPC subBkgd calcConv) DO (
	windres -D MAIN_APP_NAME=\\\"%%X\\\" main.rc res_%%X.o
	gcc -Wall -std=gnu99 -s -Os -g0 -DNDEBUG -D MAIN_PYTHON_FOLDER=\"%MAIN_PYTHON_DIR%\" -D MAIN_PYTHON_DLL=%MAIN_PYTHON_DLL% -D MAIN_APP_NAME=\"%%X\" -I "%PYTHON_DIR%\include" main_py.c res_%%X.o -o ..\dist\%%X.exe
)
