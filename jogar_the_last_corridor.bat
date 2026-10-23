@echo off
title THE LAST CORRIDOR
cls
echo ===================================================================
echo                     THE LAST CORRIDOR
echo          JOGO DE TERROR PSICOLOGICO COM DESKTOP SIMULADO
echo ===================================================================
echo.
echo Escolha como deseja executar:
echo.
echo  [1] Jogar  (aplicativo .EXE - recomendado)
echo  [2] Modo Desenvolvedor  (Python direto, requer dependencias)
echo  [3] Executar testes automatizados
echo  [4] Sair
echo.
set /p opcao="Digite a opcao desejada (1, 2, 3 ou 4): "

if "%opcao%"=="1" (
    if exist "dist\TheLastCorridor\TheLastCorridor.exe" (
        echo Iniciando The Last Corridor...
        start "" "dist\TheLastCorridor\TheLastCorridor.exe"
        exit
    ) else (
        echo [ERRO] Executavel nao encontrado em dist\TheLastCorridor\TheLastCorridor.exe
        echo Por favor, compile novamente com: pyinstaller TheLastCorridor.spec -y
        pause
        exit
    )
)

if "%opcao%"=="2" (
    echo Iniciando em modo desenvolvedor via Python...
    cd the_last_corridor
    python main.py
    cd ..
    exit
)

if "%opcao%"=="3" (
    echo Executando testes unitarios...
    python -m unittest discover -s the_last_corridor\tests
    pause
    exit
)

if "%opcao%"=="4" (
    exit
)

echo Opcao invalida. Iniciando versao executavel por padrao...
start "" "dist\TheLastCorridor\TheLastCorridor.exe"
