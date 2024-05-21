#include <windows.h>
#include <stdio.h>
#include "main.h"

// Py_DecodeLocale() not yet available in Python 3.4; need to implement char* to wchar* conversion on our own (ref: https://stackoverflow.com/a/18353327)
// ==========
wchar_t *b2w_convert(char *str) { // string conversion
    int size_needed = MultiByteToWideChar(CP_ACP, 0, str, -1, NULL, 0);
    if (!size_needed) // fail
        return (wchar_t*) "\0";
    wchar_t *rtn = (wchar_t *) malloc(size_needed * sizeof(wchar_t));
    MultiByteToWideChar(CP_ACP, 0, str, -1, rtn, size_needed);
    return rtn;
}

wchar_t **b2w_array(int argc, char *argv[]) { // array of string conversion
    wchar_t **rtn = (wchar_t **) calloc(argc, sizeof(wchar_t *));
    for (int i=1; i < argc; i++) { // in our case here, argv0 should be separately processed; see comments in `main`
        rtn[i] = b2w_convert(argv[i]);
    }
    return rtn;
}

void b2w_dispose(int count, wchar_t ** array) { // tidy up
    for (int i=1; i < count; i++) { // array[0] need not to be freed (because it is not created by *alloc; see `b2w_array`)
        free(array[i]);
    }
    free(array);
}
// ==========

#if PY_MINOR_VERSION < 10
#define PY_FOPEN "_Py_fopen"
#else // _Py_fopen is no longer available for Python >= 3.10
#define PY_FOPEN "_Py_wfopen"
#endif

#define size(a) sizeof(a)/sizeof(a[0])

int main(int argc, char *argv[]) {
    int exit_code = 0;
    const char* const func_name[] = {"Py_SetProgramName", "Py_SetPythonHome", "Py_Initialize", "PySys_SetArgvEx", PY_FOPEN, "PyRun_SimpleFileExFlags", "Py_Finalize"};
    HINSTANCE h;
    FARPROC f[size(func_name)];

    SetConsoleTitle(MAIN_APP_NAME);

    // get app file name
    char p[MAX_PATH];
    wchar_t wp[MAX_PATH];
    int l = GetModuleFileName(NULL, p, MAX_PATH);
    MultiByteToWideChar(CP_ACP, 0, p, -1, wp, MAX_PATH); // wp is now argv[0]

    // get app path (by setting `p[l] = '\0'`)
    l--;
    while (p[l] != '/' && p[l] != '\\')
        l--;

    // get python package path
    const int lp = strlen(MAIN_PYTHON_DIR)+1;
    const int lt = l+lp;
    memcpy(&p[l], "\\" MAIN_PYTHON_DIR, lp+1); // p is now python package path (with tailing \0)

    // prepend python package folder to PATH
    char* path_env_old = getenv("PATH");
    int path_env_len = 0;
    if (path_env_old) // not NULL
        path_env_len = strlen(path_env_old);
    char path_env[MAX_PATH+path_env_len+8];
    memcpy(path_env, "PATH=", 5);
    memcpy(&path_env[5], p, lt);
    if (path_env_old) // not NULL
        path_env[lt+5] = ';';
        memcpy(&path_env[lt+6], path_env_old, path_env_len+1);
    _putenv(path_env);

    // dynamic load dlls so there will be no path-finding issues (so that they can be organized into subfolders rather than hanging around in the root folder)
#if PY_MINOR_VERSION > 4
    LoadLibrary("ucrtbase.dll"); // this seems necessary for Windows 7 when ucrtbase.dll is not initially included in PATH; otherwise, the following error will be thrown: ucrtbase.terminate could not be located in the dynamic link library api-ms-win-crt-runtime-l1-1-10.dll
#endif
    if (! (h = LoadLibrary(MAIN_PYTHON_DLL))) {
        puts("Unable to load " MAIN_PYTHON_DLL);
loaderror:
        system("pause");
        exit_code = 2;
        goto finalize;
    }
    for (int i=0; i < size(f); i++) {
        if (! (f[i] = GetProcAddress(h, func_name[i]))) {
            char err_str[50] = "Unable to get address for ";
            const int err_str_len = 26; // strlen(err_str);
            memcpy(&err_str[err_str_len], func_name[i], 24); // strlen(err_str_len));
            puts(err_str);
            goto loaderror;
        }
    }

    f[0](wp); // Py_SetProgramName argv[0]

    MultiByteToWideChar(CP_ACP, 0, p, -1, wp, MAX_PATH); // now `p` and `wp` are no longer argv[0] but rather python package path
    f[1](wp); // Py_SetPythonHome; will automatically append {this folder}/DLLs; {this folder}/Lib; {this folder}/Lib/site-packages to sys.path

    f[2](); //Py_Initialize

    // get main pyc file name
    const char* const pyc_name = "\\bin\\" MAIN_APP_NAME ".pyc";
    const int lpc = strlen(pyc_name)+1; // including the tailing \0
    memcpy(&p[l], pyc_name, lpc);
    MultiByteToWideChar(CP_ACP, 0, p, -1, wp, MAX_PATH); // now `p` and `wp` are no longer argv[0] but rather main pyc file name
    wchar_t **_argv = b2w_array(argc, argv);
    _argv[0] = wp; // need to set python's argv[0] as the main pyc file name; otherwise, its path will not be properly appended to the import path
    f[3](argc, _argv, TRUE); // PySys_SetArgvEx

#if PY_MINOR_VERSION < 10
    FILE *file = (FILE*) f[4](p, "rb"); // must use Python's own fopen wrapper; otherwise, the difference in compiler for Python library and client applications will give binary incompatible FILE structures and thus cause crash
#else // _Py_fopen got removed for Python >= 3.10; in such cases, use _Py_wfopen instead
    FILE* file = (FILE*) f[4](wp, (wchar_t*) "r\0b\0\0");
#endif
    if (file) {
        printf("Loading...\r");
        f[5](file, p, TRUE, NULL); // PyRun_SimpleFileExFlags; close file afterwards
    } else {
        char err_str[18+lpc];
        memcpy(err_str, "Unable to locate ", 17);
        memcpy(&err_str[17], p, l+lpc);
        puts(err_str);
        system("pause");
        exit_code = 1;
    }
    f[6](); // Py_Finalize
    b2w_dispose(argc, _argv);
finalize:
    FreeLibrary(h);
    return exit_code;
}
