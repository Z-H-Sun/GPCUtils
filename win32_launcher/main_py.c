#include <Python.h>
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
    const char* const dll_name[] = MAIN_PYTHON_DLL;
    const char* const func_name[] = {"Py_SetProgramName", "Py_SetPythonHome", "Py_Initialize", "PySys_SetArgvEx", PY_FOPEN, "PyRun_SimpleFileExFlags", "Py_Finalize"};
    HINSTANCE h[size(dll_name)] = {0};
    FARPROC f[size(func_name)] = {0};

    SetConsoleTitle(MAIN_APP_NAME);

    for (int i=0; i < size(h); i++) { // dynamic load dlls so there will be no path-finding issues (so that they can be organized into subfolders rather than hanging around in the root folder). mcvc runtime must be loaded before python dll because the latter is dependent on the former. mcvc++ runtime is also loaded here because qt and matplotlib libraries are dependent on it
        if (! (h[i] = LoadLibrary(dll_name[i]))) {
            printf("Unable to load %s\n", dll_name[i]);
loaderror:
            system("pause");
            exit_code = 2;
            goto finalize;
        }
    }
    for (int i=0; i < size(f); i++) {
        if (! (f[i] = GetProcAddress(h[size(h)-1], func_name[i]))) {
            printf("Unable to get address for %s\n", func_name[i]);
            goto loaderror;
        }
    }

    // get app file name
    char p[MAX_PATH];
    wchar_t wp[MAX_PATH];
    int l = GetModuleFileName(NULL, p, MAX_PATH);
    MultiByteToWideChar(CP_ACP, 0, p, -1, wp, MAX_PATH);
    f[0](wp); // Py_SetProgramName argv[0]

    // get app path
    l--;
    while (p[l] != '/' && p[l] != '\\')
        l--;
    p[l] = '\0';

    // get python package path
    strcat(p, "\\" MAIN_PYTHON_FOLDER);
    MultiByteToWideChar(CP_ACP, 0, p, -1, wp, MAX_PATH); // now `p` and `wp` are no longer argv[0] but rather python package path
    f[1](wp); // Py_SetPythonHome; will automatically append {this folder}/DLLs; {this folder}/Lib; {this folder}/Lib/site-packages to sys.path

    f[2](); //Py_Initialize

    // get main pyc file name
    p[l] = '\0';
    strcat(p, "\\bin\\" MAIN_APP_NAME ".pyc");
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
        printf("Unable to locate %s\n", p);
        system("pause");
        exit_code = 1;
    }
    f[6](); // Py_Finalize
    b2w_dispose(argc, _argv);
finalize:
    for (int i=0; i < 3; i++) {
        FreeLibrary(h[i]);
    }
    return exit_code;
}
