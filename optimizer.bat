
for /l %%x in (1, 1, 1000) do (
    call compete.bat
    timeout /t 1
    python analyzer.py
)