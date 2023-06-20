set "msg="
set /p msg="Please enter migration message or leave empty>"

if not defined msg (
    .\venv\Scripts\python.exe -m flask db migrate
    exit /b
)

.\venv\Scripts\python.exe -m flask db migrate -m "%msg%"
