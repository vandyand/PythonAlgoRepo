

import pandas as pd
import numpy as np
import sys
import os
import matplotlib.pyplot as plt
import scipy.stats as st

try:
    set_number = int(sys.argv[1])
except Exception:
    set_number = 0

try:
    symbol = sys.argv[2]
except Exception:
    symbol = 'EURUSD'

data_hub_file_path = 'C:\\Users\\Dell\\Desktop\\PythonAlgoFolder\\DataHub'
data_file_path = '{}\\Set{}'.format(data_hub_file_path,set_number)

os.chdir(data_file_path)
num_files = len([x for x in os.listdir() if '.csv' in x])


cols = ['profit','bprofit_','fprofit_',
        'bprofit','bgross_profit','bgross_loss',
        'bnum_trades','bnum_long_trades','bnum_short_trades',
        'bprofit_factor','bexpected_payoff','brecovery_factor',
        'bdrawdown_dol','bdrawdown_pct',
        'bscore0','bscore1',
        'bscore2','bscore3',
        'bscore4','bscore5',
        'bscore6','bscore7',
        'bscore8','bscore9',
        'bscore10','bscore11',
        'bscore12','bscore13',
        'bscore14','bscore15',
        'bscore16','bscore17',
        'fprofit',
        'fprofit_factor','fexpected_payoff','frecovery_factor',
        'fdrawdown_dol','fdrawdown_pct',
#        'fscore0','fscore1',
#        'fscore2','fscore3',
#        'fscore4','fscore5',
#        'fscore6','fscore7',
#        'fscore8','fscore9',
#        'fscore10','fscore11',
#        'fscore12','fscore13',
#        'fscore14','fscore15',
#        'fscore16','fscore17',
        'num_trades',
        'fnum_trades',
        'Long_Back_1','Long_Back_2','Short_Back_1','Short_Back_2','Open_Bars']


mean_returns = []
#file_count = 0
def import_data(filepath):
    data = pd.read_csv(filepath,header=None)
    data.columns = cols
    data = data.drop_duplicates(['profit','bnum_trades','bprofit_factor','fprofit','fnum_trades']).reset_index(drop=True)
    mean_returns.append(data['fprofit'].mean())
#    global file_count
#    file_count += 1
#    print(file_count)
    return(data)


datas = [import_data(r'C:\Users\dell\Desktop\PythonAlgoFolder\DataHub\Set{}\{}_{}.csv'.format(set_number,x+1,symbol)) for x in range(num_files)]

print("\n",np.mean(mean_returns),np.std(mean_returns))





# Feature engineering - long and short back ranges
for data in datas:
    data['Long_Back_Range'] = data['Long_Back_1'] - data['Long_Back_2']
    data['Short_Back_Range'] = data['Short_Back_1'] - data['Short_Back_2']


# Get X and y columns (y is target)
X_cols = ['bprofit','bgross_profit','bgross_loss',
              'bnum_trades','bnum_long_trades','bnum_short_trades',
              'bprofit_factor','bexpected_payoff','brecovery_factor',
              'bdrawdown_dol','bdrawdown_pct',
              'bscore0','bscore1','bscore2','bscore3','bscore4','bscore5',
              'bscore6','bscore7','bscore8','bscore9','bscore10','bscore11','bscore12',
              'bscore13','bscore14','bscore15','bscore16','bscore17'
              'Long_Back_1','Long_Back_2','Short_Back_1','Short_Back_2','Open_Bars',
              'Long_Back_Range','Short_Back_Range']

target = 'fprofit'


# Set metaparameters
back_sets = 2 # How many previous datasets to train on?
iterations = num_files - back_sets # How many times to train and test (for i in range(iterations))?
sample_size = 1 # How many of the top predictions to take for final stats (mean and std)?
sample_start = 1 # Start at 1 for normal operation. If you only want the second recommendation set this to two and 
                 # sample_size to one.
master_preds = []


# Go through the possible combinations of sample_starts and score_numbers and 
# set best results to results.txt

sample_starts = [1,2,3,4,5,6,7,8,9,10] # Start at 1 for normal operation. If you only want the second recommendation set this to two and 
                 # sample_size to one.
score_nums = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]
all_means = []
if 'results.txt' not in os.listdir():
    a = open('results.txt','w')
    a.close()
results_file = open('results.txt','a')
for sample_start in sample_starts:
    for score_num in score_nums:
        model_best_preds = []
        model_num_trades = []
        for i in range(num_files):
            holdout_preds = datas[i][['bscore{}'.format(score_num),'fprofit','fnum_trades']]
            sortd = holdout_preds.sort_values('bscore{}'.format(score_num),ascending=False).iloc[sample_start-1:sample_start-1+sample_size]
            best_preds = sortd['fprofit']
            num_trades = sortd['fnum_trades']
            [model_best_preds.append(best_preds.iloc[x]) for x in range(sample_size)]
            [model_num_trades.append(num_trades.iloc[x]) for x in range(sample_size)]
#        mean = np.mean(model_best_preds)
#        std = np.std(model_best_preds)
#        sharpe = mean/std
#        z_score = mean/std*np.sum(model_num_trades)**0.5
#        p_value = st.norm.cdf(z_score)
#        print("Item: {0}, Score num: {1}, All best_params   mean:{2: >6}, std:{3: >6}, sharpe:{4: >6}, z_score:{5: >6}, p_value:{6: >6}".format(
#            sample_start,score_num,
#            round(np.mean(model_best_preds),3),
#            round(np.std(model_best_preds),3),
#            round(np.mean(model_best_preds)/np.std(model_best_preds),3),
#            round(np.mean(model_best_preds)/np.std(model_best_preds)*np.sum(model_num_trades)**0.5,3),
#            round(st.norm.cdf(np.mean(model_best_preds)/np.std(model_best_preds)*np.sum(model_num_trades)**0.5),3)))
        [all_means.append(np.mean(model_best_preds))]
        if (np.mean(model_best_preds)>0):#st.norm.cdf(np.mean(model_best_preds)/np.std(model_best_preds)*num_files**0.5)>0.95):
            results_file.write("Item: {0: >2}, Score num: {1: >2}, mean: {2: <6}, std: {3: <6}, sharpe: {4: <6}, num_trades: {5: >3}, z_score: {6: <6}, p_value: {7: <6}\n".format(
                sample_start,score_num,
                round(np.mean(model_best_preds),4),
                round(np.std(model_best_preds),4),
                round(np.mean(model_best_preds)/np.std(model_best_preds),4),
                round(np.sum(model_num_trades),4),
                round(np.mean(model_best_preds)/np.std(model_best_preds)*np.sum(model_num_trades)**0.5,4),
                round(st.norm.cdf(np.mean(model_best_preds)/np.std(model_best_preds)*np.sum(model_num_trades)**0.5),4)))
results_file.close()
print("\nmean: {}, std: {}".format(np.mean(all_means),np.std(all_means)))
   



# =============================================================================
# sample_start = 10
# score_num = 5
# 
# print('\n\n\n\n\n')
# print('{},{}'.format(sample_start, score_num))
# 
# 
# # # Just use some column name
# # 
# model_means = []
# model_stds = []
# model_best_preds_means = []
# model_best_preds = []
# 
# iterr = num_files
# for i in range(iterr):
# 
#     holdout_preds = datas[i]
#     best_preds = holdout_preds.sort_values('bscore{}'.format(score_num),ascending=False).iloc[sample_start-1:sample_start-1+sample_size]['fprofit']
# 
#     model_means.append(best_preds.mean())
#     model_stds.append(np.std(best_preds))
#     [model_best_preds.append(best_preds.iloc[x]) for x in range(sample_size)]
#     [model_best_preds_means.append(best_preds.mean())]
# #    print("Week {0: >2}, best {1: >3} mean:{2: >6}, std:{3: >6} {4: >6},{5: >6}, Cumulative mean:{6: >6}, Cumulative std:{7: >6}".format(
# #         i+1,sample_size,round(best_preds.mean(),2),round(np.std(best_preds),2),
# #         str(best_preds.mean()>0),str(best_preds.mean()>np.std(best_preds)), 
# #         round(np.mean(model_best_preds),2),round(np.std(model_best_preds),2)))
#  
# mean = np.mean(model_best_preds)
# std = np.std(model_best_preds)
# sharpe = mean/std
# z_score = mean/std*iterr**0.5
# p_value = st.norm.cdf(z_score)
# 
# print("All best_params   mean:{0: >6}, std:{1: >6}, sharpe: {2: >6}, z-score: {3: >6}, p_value {4: >6}".format(round(mean,3),round(std,3),
#                                                                            round(sharpe,4),
#                                                                            round(z_score,4),round(p_value,4)))
# 
# a = [master_preds.append(model_best_preds[x]) for x in range(iterr*sample_size)]
# 
# plt.plot(model_best_preds_means[::-1])
# plt.title('Returns')
# plt.axhline(0,c='g')
# plt.axhline(np.mean(model_means),c='r')
# plt.show()
# model_equity = [1000]
# a = [model_equity.append(model_best_preds_means[len(model_best_preds_means)-x-1]*10+model_equity[x]) for x in range(len(model_best_preds_means))]
# plt.plot(model_equity)
# plt.title('Equity with fixed size')
# plt.show()
# print("Final Equity: {}".format(round(model_equity[-1],2)))
# model_equity = [1000]
# a = [model_equity.append(model_best_preds_means[len(model_best_preds_means)-x-1]*model_equity[x]*0.01+model_equity[x]) for x in range(len(model_best_preds_means))]
# plt.plot(model_equity)
# plt.title('Equity with percent size')
# plt.show()
# print("Final Equity: {}".format(round(model_equity[-1],2)))
# =============================================================================






