python ini_genetic_param.py 1
python copy_eas.py

python delete_files.py
python big_master_backtests_generator.py 0
start /wait "" "master_batch_file.bat"
python analysis.py 0 EURUSD

python delete_files.py
python big_master_backtests_generator.py 1
start /wait "" "master_batch_file.bat"
python analysis.py 1 EURUSD

