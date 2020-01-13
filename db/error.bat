@echo off
sqlite3 main.db "select * from errorTable ORDER BY errorTime DESC LIMIT 20;"