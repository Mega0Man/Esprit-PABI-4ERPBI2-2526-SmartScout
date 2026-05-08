@echo off
copy /Y ".env.me" ".env" >nul
echo Active scout profile: ME (.env.me)
type .env
