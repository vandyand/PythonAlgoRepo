

import pandas as pd
import numpy as np
import sys
import os
import matplotlib.pyplot as plt
import scipy.stats as st

try:
    hyper_iterator = int(sys.argv[1])
except Exception:
    hyper_iterator = 0

if sum(1 for line in open('hyperparameters.txt'))==40:
    hyper_iterator = 0

hyper_lines_per_iterator = 40

contents = open('hyperparameters.txt','r+').read()
content = []
for i in contents.split('\n'):
    content.append(i.split(' = '))

symbol       = content[8+hyper_lines_per_iterator*hyper_iterator][1]
spread       = int(content[9+hyper_lines_per_iterator*hyper_iterator][1])
data_set_num = int(content[17+hyper_lines_per_iterator*hyper_iterator][1])

data_hub_file_path = 'C:\\Users\\Dell\\Desktop\\PythonAlgoFolder\\DataHub'
data_file_path = '{}\\Set{}'.format(data_hub_file_path,data_set_num)

os.chdir(data_file_path)
num_files = len([x for x in os.listdir() if '.csv' in x])


cols = ['profit','bprofit_','fprofit_',
        'bprofit','bgross_profit','bgross_loss',
        'bnum_trades','bnum_long_trades','bnum_short_trades',
        'bprofit_factor','bexpected_payoff','brecovery_factor',
        'bdrawdown_dol','bdrawdown_pct',
        'bsharpe','bsortino',
        'fprofit','fgross_profit','fgross_loss',
        'fnum_trades','fnum_long_trades','fnum_short_trades',
        'fprofit_factor','fexpected_payoff','frecovery_factor',
        'fdrawdown_dol','fdrawdown_pct',
        'fsharpe','fsortino',
        'num_trades',
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


datas = [import_data(r'C:\Users\dell\Desktop\PythonAlgoFolder\DataHub\Set{}\{}'.format(data_set_num,f)) for f in os.listdir() if '.csv' in f]

print("\n",np.mean(mean_returns),np.std(mean_returns))



# Feature engineering
for data in datas:
    data['Long_Back_Range'] = data['Long_Back_1'] - data['Long_Back_2']
    data['Short_Back_Range'] = data['Short_Back_1'] - data['Short_Back_2']
    data['bdrawdown_pct_useful'] = 1 - data['bdrawdown_pct']
    data['bstd'] = np.where(data['bsharpe']==0,0,data['bexpected_payoff'] / data['bsharpe'])
    data['fstd'] = np.where(data['fsharpe']==0,0,data['fexpected_payoff'] / data['fsharpe'])


# Score engineering
properties = np.array(['bprofit','bprofit_factor','bexpected_payoff','bnum_trades',
              'bsharpe','bsortino','brecovery_factor','bdrawdown_pct_useful','bstd'])
num_combinations = 2**len(properties) - 1
for i in range(1,num_combinations):
    for data in datas:
        lookups = properties[[bool(int(x)) for x in bin(i)[2:].zfill(len(properties))]]
        product = 1
        for j in lookups:
            product *= data[j]
        data['bscore{}'.format(i)] = product


# Set metaparameters
back_sets = 2 # How many previous datasets to train on?
iterations = num_files - back_sets # How many times to train and test (for i in range(iterations))?
sample_size = 1 # How many of the top predictions to take for final stats (mean and std)?
sample_start = 1 # Start at 1 for normal operation. If you only want the second recommendation set this to two and 
                 # sample_size to one.
master_preds = []


# Go through the possible combinations of sample_starts and score_numbers and 
# set best results to results.txt

sample_starts = list(range(1,11)) # Start at 1 for normal operation. If you only want the second recommendation set this to two and 
                 # sample_size to one.
score_nums = list(range(1,num_combinations))
all_means = []
all_stds = []
if 'results.txt' not in os.listdir():
    a = open('results.txt','w')
    a.close()
results_file = open('results.txt','a')
for sample_start in sample_starts:
    for score_num in score_nums:
        model_best_preds = []
        model_num_trades = []
        model_means      = []
        model_stds       = []
        for i in range(num_files):
            holdout_preds = datas[i][['bscore{}'.format(score_num),'fprofit','fnum_trades','fexpected_payoff','fstd']]
            sortd = holdout_preds.sort_values('bscore{}'.format(score_num),ascending=False).iloc[sample_start-1:sample_start-1+sample_size]
            fprofits = sortd['fprofit']
            fnum_trades = sortd['fnum_trades']
            fmeans = sortd['fexpected_payoff']
            fstds = sortd['fstd']
            
            [model_best_preds.append(fprofits.iloc[x]) for x in range(sample_size)]
            [model_num_trades.append(fnum_trades.iloc[x]) for x in range(sample_size)]
            [model_means.append(fmeans.iloc[x]) for x in range(sample_size)]
            [model_stds.append(fstds.iloc[x]) for x in range(sample_size)]
        
        agg_num_trades = np.sum(model_num_trades)
        first_term = 0
        if agg_num_trades!=0:
            first_term = 1/agg_num_trades
        agg_mean = first_term*(sum([model_num_trades[x]*model_means[x] for x in range(len(model_num_trades))]))
        second_term = sum([model_num_trades[x]*model_stds[x]**2 for x in range(len(model_num_trades))])
        third_term = sum([model_num_trades[x]*(model_means[x] - agg_mean)**2 for x in range(len(model_num_trades))])
        agg_std = (first_term*(second_term + third_term))**0.5
        
        
        [all_means.append(agg_mean)]
        [all_stds.append(agg_std)]
        
        if (agg_num_trades>1 and agg_std!=0 and st.norm.cdf((agg_mean-(-0.15))/agg_std*agg_num_trades**0.5)>0.95):#st.norm.cdf(np.mean(model_best_preds)/np.std(model_best_preds)*num_files**0.5)>0.95):
            results_file.write("Item: {0: >2}, Score num: {1: >3}, mean: {2: <6}, std: {3: <6}, sharpe: {4: <6}, num_trades: {5: >3}, z_score: {6: <6}, p_value: {7: <6}\n".format(
                sample_start,score_num,
                round(agg_mean,4),
                round(agg_std,4),
                round(agg_mean/agg_std,4),
                round(agg_num_trades,4),
                round((agg_mean-(-0.15))/agg_std*agg_num_trades**0.5,4),
                round(st.norm.cdf((agg_mean-(-0.15))/agg_std*agg_num_trades**0.5),4)))
results_file.close()
print("\navg_mean: {}, avg_std: {}".format(np.mean(all_means),np.mean(all_stds)))
   






#
## Visualization here
#
#sample_start = 3
#score_num = 32
#
#print('\n\n\n\n\n')
#print('{},{}'.format(sample_start, score_num))
#
#
#model_best_preds = []
#model_num_trades = []
#model_means      = []
#model_stds       = []
#for i in range(num_files):
#    holdout_preds = datas[i][['bscore{}'.format(score_num),'fprofit','fnum_trades','fexpected_payoff','fstd']]
#    sortd = holdout_preds.sort_values('bscore{}'.format(score_num),ascending=False).iloc[sample_start-1:sample_start-1+sample_size]
#    fprofits = sortd['fprofit']
#    fnum_trades = sortd['fnum_trades']
#    fmeans = sortd['fexpected_payoff']
#    fstds = sortd['fstd']
#    
#    [model_best_preds.append(fprofits.iloc[x]) for x in range(sample_size)]
#    [model_num_trades.append(fnum_trades.iloc[x]) for x in range(sample_size)]
#    [model_means.append(fmeans.iloc[x]) for x in range(sample_size)]
#    [model_stds.append(fstds.iloc[x]) for x in range(sample_size)]
#
#
#agg_num_trades = np.sum(model_num_trades)
#first_term = 1/agg_num_trades
#agg_mean = first_term*(sum([model_num_trades[x]*model_means[x] for x in range(len(model_num_trades))]))
#second_term = sum([model_num_trades[x]*model_stds[x]**2 for x in range(len(model_num_trades))])
#third_term = sum([model_num_trades[x]*(model_means[x] - agg_mean)**2 for x in range(len(model_num_trades))])
#agg_std = (first_term*(second_term + third_term))**0.5
#
#
#print("Item: {0: >2}, Score num: {1: >3}, mean: {2: <6}, std: {3: <6}, sharpe: {4: <6}, num_trades: {5: >3}, z_score: {6: <6}, p_value: {7: <6}\n".format(
#    sample_start,score_num,
#    round(agg_mean,4),
#    round(agg_std,4),
#    round(agg_mean/agg_std,4),
#    round(agg_num_trades,4),
#    round((agg_mean-(-0.15))/agg_std*agg_num_trades**0.5,4),
#    round(st.norm.cdf((agg_mean-(-0.15))/agg_std*agg_num_trades**0.5),4)))
#
#
## Plot results
#
#a = [master_preds.append(model_best_preds[x]) for x in range(sample_size)]
#
#plt.plot(model_means[::-1])
#plt.title('Returns')
#plt.axhline(0,c='g')
#plt.axhline(np.mean(model_means),c='r')
#plt.show()
#model_equity = [1000]
#a = [model_equity.append(model_means[len(model_means)-x-1]*10+model_equity[x]) for x in range(len(model_means))]
#plt.plot(model_equity)
#plt.title('Equity with fixed size')
#plt.show()
#print("Final Equity: {}".format(round(model_equity[-1],2)))
#model_equity = [1000]
#a = [model_equity.append(model_means[len(model_means)-x-1]*model_equity[x]*0.01+model_equity[x]) for x in range(len(model_means))]
#plt.plot(model_equity)
#plt.title('Equity with percent size')
#plt.show()
#print("Final Equity: {}".format(round(model_equity[-1],2)))
#


