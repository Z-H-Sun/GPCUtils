#ifndef MAIN_APP_NAME // "readGPC" / "subBkgd" / "calcConv"
#define MAIN_APP_NAME "readGPC"
#endif

// macros below will only be used in main_py.c (i.e., when python interpreter is embedded)
#ifndef MAIN_PYTHON_FOLDER // relative path of the python package
#define MAIN_PYTHON_FOLDER "py34"
#endif

#ifndef MAIN_PYTHON_DLL // relative path of the python dlls (first two are c runtime libraries; python dll must be the last one)
#define MAIN_PYTHON_DLL {"py34\\Dlls\\msvcr100.dll", "py34\\Dlls\\msvcp100.dll", "py34\\Dlls\\python34.dll"}
#endif
