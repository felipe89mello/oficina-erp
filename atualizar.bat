@echo off
REM Roda este script DENTRO da pasta do projeto, no notebook do cliente,
REM depois de copiar os arquivos-fonte atualizados por cima dos antigos.
REM Ele reinstala dependencias (caso tenham mudado) e gera um novo .exe.
REM O banco de dados do usuario fica em %APPDATA%\OficinaERP e NAO e tocado.

echo Ativando ambiente virtual...
call venv\Scripts\activate

echo Instalando/atualizando dependencias...
pip install -r requirements.txt --quiet

echo Gerando novo executavel...
pyinstaller --onefile --noconfirm --add-data "app/templates;app/templates" --add-data "app/static;app/static" main.py

echo.
echo ==========================================
echo Build concluido! O novo .exe esta em dist\main.exe
echo Copie ele para onde o atalho da area de trabalho aponta.
echo ==========================================
pause
