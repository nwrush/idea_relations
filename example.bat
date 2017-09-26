@echo off
Set MALLET_BIN_DIR=%MALLET_HOME%\bin
Set INPUT_FILE="..\data\acl\acl.jsonlist.gz"
Set BACKGROUND_FILE="..\data\nips\nips.jsonlist.gz"
Set DATA_OUPUT_DIR="acl_example\processing\"
Set FINAL_OUTPUT_DIR="acl_example\output\"
Set PREFIX="acl"

python main.py --input_file %INPUT_FILE% --data_output_dir %DATA_OUPUT_DIR% --final_output_dir %FINAL_OUTPUT_DIR% --mallet_bin_dir %MALLET_BIN_DIR% --option keywords --num_ideas 100 --prefix %PREFIX% --background_file %BACKGROUND_FILE% --objects_location banana.p
