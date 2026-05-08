@echo off
setlocal

set "SRC=%~dp0"
set "BASE=%~dp0.."
set "ME_DIR=%BASE%\scout_forecast_me"
set "FRIEND_DIR=%BASE%\scout_forecast_friend"

if exist "%ME_DIR%" rmdir /s /q "%ME_DIR%"
if exist "%FRIEND_DIR%" rmdir /s /q "%FRIEND_DIR%"

robocopy "%SRC%" "%ME_DIR%" /E /XD "__pycache__" ".pytest_cache" "mlruns" "mlartifacts" >nul
robocopy "%SRC%" "%FRIEND_DIR%" /E /XD "__pycache__" ".pytest_cache" "mlruns" "mlartifacts" >nul

copy /Y "%ME_DIR%\.env.me" "%ME_DIR%\.env" >nul
copy /Y "%FRIEND_DIR%\.env.friend" "%FRIEND_DIR%\.env" >nul

echo Created:
echo   %ME_DIR%
echo   %FRIEND_DIR%
echo.
echo Zip each folder and send the friend folder.

endlocal
