@echo off
REM userTableに対象ユーザを追加

sqlite3 main.db "INSERT INTO userTable VALUES(0, \"%1\", 0, 0, 0)"