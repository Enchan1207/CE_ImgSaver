@echo off
sqlite3 main.db "select * from imageTable WHERE localPath='Nodata' ORDER BY post DESC LIMIT 20;"