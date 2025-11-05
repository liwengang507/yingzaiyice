@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Starting Streamlit application...
echo Working directory: %CD%
echo App file: app.py
streamlit run app.py --server.port 8511
pause

