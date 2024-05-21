@ECHO OFF
choice /c 456789ABCD /N /M "Compile launcher using Python version 3.x (4 <= x <= 13): Choose x = [4-D]? "
set /a PY_MINOR_VERSION=%errorlevel%+3
set MAIN_PYTHON_DIR=py3%PY_MINOR_VERSION%
set MAIN_PYTHON_DLL=python3%PY_MINOR_VERSION%.dll
set DIST_DIR=..\dist_py3%PY_MINOR_VERSION%
mkdir %DIST_DIR%

FOR %%X IN (readGPC subBkgd calcConv) DO (
	windres -D MAIN_APP_NAME=\\\"%%X\\\" main.rc res_%%X.o
	gcc -Wall -std=gnu99 -s -Os -g0 -DNDEBUG -D PY_MINOR_VERSION=%PY_MINOR_VERSION% -D MAIN_PYTHON_DIR=\"%MAIN_PYTHON_DIR%\" -D MAIN_PYTHON_DLL=\"%MAIN_PYTHON_DLL%\" -D MAIN_APP_NAME=\"%%X\" main_py.c res_%%X.o -o %DIST_DIR%\%%X.exe
)
