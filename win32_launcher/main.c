#include <windows.h>
#include <stdio.h>
#include "main.h"

int main() {
    SetConsoleTitle(MAIN_APP_NAME);
    SetConsoleCtrlHandler(NULL, TRUE); // ignore Ctrl-C

    // get command line combined string (ref:https://stackoverflow.com/a/36876057)
    char *s = GetCommandLine();
    if (*s == '"') {
        ++s;
        while (*s)
            if (*s++ == '"')
                break;
    } else {
        while (*s && *s != ' ' && *s != '\t')
            ++s;
    }
    while (*s == ' ' || *s == '\t')
        s++;

    // get app path
    char p[MAX_PATH];
    const int len = GetModuleFileName(NULL, p, MAX_PATH);
    int l = len-1;
    while (p[l] != '/' && p[l] != '\\')
        l--;
    p[l] = '\0';

    const int sc = 40+l*2+strlen(s);
    char c[sc];
#ifdef HAS_PYTHON_RUNTIME // whether to use user-defined python interpreter
    c[0] = '\0';
    strcat(c, "python \"");
    strcat(c, p);
    strcat(c, "\\src\\" MAIN_APP_NAME "\" ");
#else
    c[0] = '\"';
    c[1] = '\0';
    strcat(c, p);
    strcat(c, "\\" MAIN_PYTHON_FOLDER "\\python.exe\" \"");
    strcat(c, p);
    strcat(c, "\\bin\\" MAIN_APP_NAME ".pyc\" ");
#endif
    strcat(c, s);

    STARTUPINFOA si = {0};
    PROCESS_INFORMATION pi = {0};
    si.cb = sizeof(si);
    if (!CreateProcess(NULL, c, NULL, NULL, FALSE, CREATE_NEW_PROCESS_GROUP, NULL, NULL, &si, &pi)) // fail to start
        goto fail;
    WaitForSingleObject(pi.hProcess, INFINITE);
    DWORD exitCode = 0;
    GetExitCodeProcess(pi.hProcess, &exitCode);
    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);
    if (exitCode) { // python has thrown an error
fail:
        printf("Unable to execute: %s\n", c);
        system("pause");
        return 1;
    }
    return 0;
}
