@echo off

virtualenv venv
call .\venv\Scripts\activate.bat

pscp -P 1255 nikko@zin.cs.washington.edu:/home/nikko/storage/*.whl .

pip install "numpy-1.13.1+mkl-cp35-cp35m-win_amd64.whl"
pip install "scipy-0.19.1-cp35-cp35m-win_amd64.whl"

pip install -r requirements.txt