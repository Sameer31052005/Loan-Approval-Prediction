@echo off
cd /d "%~dp0"
title CrediPredict AI - Group 6 Demo
echo CrediPredict AI - Synthetic Loan Approval Classification
echo Keep this terminal open while presenting.
echo.
python -c "import flask, sklearn, pandas, numpy, joblib" 2>nul
if errorlevel 1 (
 echo Dependencies are missing. Run: python -m pip install -r requirements.txt
 pause
 exit /b 1
)
python scripts/demo_check.py
if errorlevel 1 (
 echo Preflight failed. Read the error above before starting.
 pause
 exit /b 1
)
set PORT=5000
echo Open http://127.0.0.1:5000 after the server starts.
echo If port 5000 is busy, use a terminal: set PORT=5001 then python app.py
python app.py
pause
