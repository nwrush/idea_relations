@echo off

Set BIN_DIR=%~f1
Set DIRECTORY=%~f2
Set TOPICS=%3
echo "Current directory is" %CD%
echo "Data directory is" %DIRECTORY%
echo "Number of topics is" %TOPICS%

cd %DIRECTORY%

echo "a"
call %BIN_DIR%\mallet import-file --input %DIRECTORY%\data.input --output %DIRECTORY%\data.mallet --keep-sequence --token-regex "\w+"
echo "b"
call %BIN_DIR%\mallet train-topics --input %DIRECTORY%\data.mallet^
 --num-topics %TOPICS% --output-state %DIRECTORY%\topic-state.gz^
 --output-doc-topics %DIRECTORY%\doc-topics.gz^
 --output-topic-keys %DIRECTORY%\topic-words.gz --num-top-words 500 > test.txt
echo "c"


