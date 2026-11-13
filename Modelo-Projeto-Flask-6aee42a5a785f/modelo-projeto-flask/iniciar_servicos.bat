
@echo off
REM Abre 4 janelas, uma para cada servico (alternativa ao VS Code).
for %%P in (servico_1 servico_2 servico_3 servico_4) do (
  start "%%P" cmd /k "cd /d %~dp0%%P && py app.py"
)
