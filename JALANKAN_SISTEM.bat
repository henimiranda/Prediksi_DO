@echo off
title EduPredict AI Launcher
echo ==================================================
echo       EDUPREDICT AI - MEMULAI SISTEM...
echo ==================================================
echo.
echo [*] Mengecek dependensi...
echo [*] Menjalankan server Streamlit...
echo.
echo JANGAN TUTUP JENDELA INI SELAMA MENGGUNAKAN WEBSITE!
echo.
streamlit run frontend/main.py
pause
