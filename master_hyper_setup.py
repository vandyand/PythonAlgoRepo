
# Hyperparameters:
num_iterations = 24
back_step_sizes = [1]#[20,10,5,1]
back_stepss = [3]#[3,4,5]
fore_stepss = [1]#[1,2]
start_year = 2018
start_month = 5
start_day = 25
EA = "DiscreteModelMaker\FoxtrotDiscreteModelMaker"
symbol = 'EURUSD'
spread = 15


# EA Parameters
lookback_time_dayss = [4]#[50,10,5,2]
holding_time_dayss = [1]#[5,1,0.5]
timeframe = 60
Chart_Timeframe = 'H1'
optimization_score_nums = [0]
file_name_prefix_vers = 0
threshold = 24
data_set_num = 2
num_backtests_per_set = 3
Long_Back_1_Start = 1
Long_Back_1_Step = 1
Long_Back_2_Start = 1
Long_Back_2_Step = 1
Short_Back_1_Start = 1
Short_Back_1_Step = 1
Short_Back_2_Start = 1
Short_Back_2_Step = 1
Open_Bars_Start = 1
Open_Bars_Step = 1
Lots_Value = 0.01
get_random_results = 1
only_positive_results = 1


# File parameters
hyper_lines_per_iterator = 40



import os
try:
    os.remove('C:\\Users\\Dell\\Desktop\\PythonAlgoFolder\\DataHub\\mamamamaster.bat')
except Exception:
    pass
try:
    os.remove('C:\\Users\\Dell\\Desktop\\PythonAlgoFolder\\DataHub\\hyperparameters.txt')
except Exception:
    pass

mamamamaster_file = open('mamamamaster.bat', 'a')
mamamamaster_file.write('''python ini_genetic_param.py 1
python copy_eas.py

''')


hyperparameters_file = open('hyperparameters.txt','a')



count = data_set_num
for optimization_score_num in optimization_score_nums:
    for holding_time_days in holding_time_dayss:
        for lookback_time_days in lookback_time_dayss:
            for fore_steps in fore_stepss:
                for back_steps in back_stepss:
                    for back_step_size in back_step_sizes:
                        data_set_num = count
                        count += 1
                        hyperparameters_file.write('''num_iterations = {}
back_step_size = {}
back_steps = {}
fore_steps = {}
start_year = {}
start_month = {}
start_day = {}
EA = {}
symbol = {}
spread = {}
lookback_time_days = {}
holding_time_days = {}
timeframe = {}
Chart_Timeframe = {}
optimization_score_num = {}
file_name_prefix_vers = {}
threshold = {}
data_set_num = {}
num_backtests_per_set = {}
Long_Back_1_Start = {}
Long_Back_1_Step = {}
Long_Back_2_Start = {}
Long_Back_2_Step = {}
Short_Back_1_Start = {}
Short_Back_1_Step = {}
Short_Back_2_Start = {}
Short_Back_2_Step = {}
Open_Bars_Start = {}
Open_Bars_Step = {}
Lots_Value = {}
get_random_results = {}
only_positive_results = {}
holder = 0
holder = 0
holder = 0
holder = 0
holder = 0
holder = 0
holder = 0
holder = 0
'''.format(
num_iterations,
back_step_size,
back_steps,
fore_steps,
start_year,
start_month,
start_day,
EA,
symbol,
spread,
lookback_time_days,
holding_time_days,
timeframe,
Chart_Timeframe,
optimization_score_num,
file_name_prefix_vers,
threshold,
data_set_num,
num_backtests_per_set,
Long_Back_1_Start,
Long_Back_1_Step,
Long_Back_2_Start,
Long_Back_2_Step,
Short_Back_1_Start,
Short_Back_1_Step,
Short_Back_2_Start,
Short_Back_2_Step,
Open_Bars_Start,
Open_Bars_Step,
Lots_Value,
get_random_results,
only_positive_results))

                        mamamamaster_file.write('''python delete_files.py
python big_master_backtests_generator.py {}
start /wait "" "master_batch_file.bat"
python analysis.py {}

'''.format(data_set_num,data_set_num))



mamamamaster_file.close()
hyperparameters_file.close()



