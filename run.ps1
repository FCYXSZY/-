$env:HTTP_PROXY = "http://127.0.0.1:7890"
$env:HTTPS_PROXY = "http://127.0.0.1:7890"
. .venv\Scripts\Activate
cd flask2
python reptile.py
pause
