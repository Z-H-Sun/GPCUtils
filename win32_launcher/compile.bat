@ECHO OFF
FOR %%X IN (readGPC subBkgd calcConv) DO (
	windres -D MAIN_APP_NAME=\\\"%%X\\\" main.rc res_%%X.o
	gcc -Wall -std=gnu99 -s -Os -g0 -DNDEBUG -D MAIN_APP_NAME=\"%%X\" main.c res_%%X.o -o %%X.exe
)
