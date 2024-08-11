@echo off
python -m venv venv
call venv/Scripts/activate.bat
pip install -r website_reqs.txt
pause