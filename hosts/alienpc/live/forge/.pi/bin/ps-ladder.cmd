<# :
 batch-ladder helper: runs each listed PowerShell command against the 5slock ladder, in order,
 and stops on the first one that returns a number. Usage:
     cmd //c "C:\Users\derek\5slock\.pi\bin\ps-ladder.cmd 1 "Write-Host ok""
 The command is argv 2, so it carries no `;` and no `/` and needs no quoting on the inside.
 The first line is a polyglot: cmd treats `<# :` as a command and runs the batch block;
 PowerShell reads it as a `<# ... #>` comment and executes the Write-Host below.
 The marker check in the loop is what makes the ladder stop at the first number: 5 is a
 successful exit code, not a pid, so `IsNumeric` alone is not enough.
 Derived from C:\Users\derek\covenant\scripts\ps-ladder.cmd (2026-07-29); 5slock copy with the
 same 1..5 ladder. The 5th rung is `powershell.exe` (Windows PowerShell 5.1): the pi `powershell`
 tool runs 7 with a read-cwd gate at the profile layer, so the system powershell is the fallback
 that reads external directories.
#>
@echo off
setlocal enabledelayedexpansion
set "PS5=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
for %%n in (1 2 3 4 5) do (
    for /f "usebackq delims=" %%v in ("powershell" -NoProfile -NonInteractive -ExecutionPolicy Bypass -Number %%n --Command %2) do (
        set "OUT=%%v"
    )
    set "RC=!errorlevel!"
    echo !OUT! | findstr /r "^[0-9][0-9]*$" >nul
    if not "!RC!" == "5" if not "!RC!" == "1073807364" if not "!OUT:~0,8!" == "[written" if not "!OUT:~0,7!" == "[empty " if not "!OUT:~0,8!" == "[pending" if not "!OUT:~0,7!" == "[system" goto done
)
:done
1>&2 echo [ps-ladder] used !PS5!
exit /b !RC!
