#ifndef MAIN_APP_NAME // "readGPC" / "subBkgd" / "calcConv"
#define MAIN_APP_NAME "readGPC"
#endif

// macros below will only be used in main_py.c (i.e., when python interpreter is embedded)
#ifndef PY_MINOR_VERSION // python version 3.x
#define PY_MINOR_VERSION 4
#endif

#ifndef MAIN_PYTHON_DIR // relative path of the python package
#define MAIN_PYTHON_DIR "py34"
#endif

#ifndef MAIN_PYTHON_DLL // relative path of the python dlls (first two are c runtime libraries; python dll must be the last one)
#define MAIN_PYTHON_DLL "python34.dll"
#endif
