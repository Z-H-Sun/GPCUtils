@ECHO OFF
set PYTHON_DIR=C:\Python34
set PYTHON_LIB=python34
set MAIN_PYTHON_DIR=py34

FOR %%X IN (readGPC subBkgd calcConv) DO (
	windres -D MAIN_APP_NAME=\\\"%%X\\\" main.rc res_%%X.o
	gcc -Wall -std=gnu99 -s -Os -g0 -DNDEBUG -D MAIN_PYTHON_FOLDER=\"%MAIN_PYTHON_DIR%\" -D MAIN_APP_NAME=\"%%X\" -I "%PYTHON_DIR%\include" -L "%PYTHON_DIR%\libs" main_py.c res_%%X.o -o ..\dist\%%X.exe -l %PYTHON_LIB%
)
