@echo off
copy /Y ".env.friend" ".env" >nul
echo Active scout profile: FRIEND (.env.friend)
type .env
