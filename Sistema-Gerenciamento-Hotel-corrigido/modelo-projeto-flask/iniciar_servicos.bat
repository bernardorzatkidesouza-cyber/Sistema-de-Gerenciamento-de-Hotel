@echo off
setlocal
REM Execute este arquivo a partir da pasta modelo-projeto-flask.
for %%S in (servico_hospedes servico_quartos servico_reservas servico_pagamento) do (
  start "%%S" cmd /k "cd /d ""%~dp0%%S"" && py app.py"
)
endlocal
