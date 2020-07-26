#%%
# 計算各個標的文之績效
import numpy as np
import pandas as pd
import pickle 

with open('data/ptt_table.pickle', 'rb') as handle:
    ptt = pickle.load(handle)
    ptt.reset_index(inplace=True, drop=True)
with open('data/stock_db.pickle', 'rb') as handle:
    stock = pickle.load(handle)
    stock.dropna(inplace=True, how='all', thresh=2) # 留下有開盤的日期
    # stock = stock.set_index('date')
    stock.date = pd.to_datetime(stock.date)

#%%
# # 把盤後發文的算隔天
import datetime
# from datetime import timedelta
close_time = datetime.time(13, 30) 
start_time = datetime.time(9, 30) 
# for i,j in enumerate(data.Date):
#     if j.time() > closetime:
#         fixed_date = j + timedelta(days=1)
#         data['Date'][i] = fixed_date.date()
#     else:
#         data['Date'][i] = j.date()

# 算發文價格
for i in ptt[ptt['Price']==-1].index:
    post_date, post_target = ptt['Date'][i], ptt['Target'][i]

    if post_target not in stock.columns:
        # print (ptt['Target'][i],'不在股價資料庫中.')
        continue
    # 是否是在有開盤的日子發文
    if post_date.date() in list(stock.date):
        # 當日盤中發文，則發文價格為當日收盤價
        if (post_date.time() > start_time) and (post_date.time() < close_time):
            ptt.loc[i, '發文時間'] = '盤中'
            try:
                price = list(stock[stock.date==post_date.date()][post_target].str.split(':'))
                price = float(price[0][1])
                ptt.loc[i, 'Price'] = price
            except:
                print ('發文當天股市有開盤，但是'+str(post_target)+'沒有收盤價紀錄')
                continue
        # 當日盤前發文，則發文價格為當天開盤價
        elif post_date.time() <= start_time:
            ptt.loc[i, '發文時間'] = '當天盤前'
            try:
                ptt.loc[i, 'Price'] = float(list(stock[stock.date==post_date.date()][post_target].str.split(':'))[0][0])
            except:
                print ('發文當天股市有開盤，但是'+str(post_target)+'沒有開盤價紀錄')
                continue
        # 當日盤後發文，則發文價格為下一個交易日之開盤價
        elif post_date.time() >= close_time:
            ptt.loc[i, '發文時間'] = '盤後'
            price_after_post = stock[stock.date > post_date][[post_target]].values
            try:
                ptt.loc[i, 'Price'] = float([x.split(':')[0] for x in price_after_post[0]][0])
            except:
                print (str(post_target)+'還沒有下一個交易日之開盤價')
                continue
                

    else:
        ptt.loc[i, '發文時間'] = '盤後'
        price_after_post = stock[stock.date > post_date][[post_target]].dropna().values
        try:
            ptt.loc[i, 'Price'] = float([x.split(':')[0] for x in price_after_post[0]][0])
        except:
            print (str(post_target)+'還沒有下一個交易日之開盤價')
            continue
#%%
def roi(cost, now):
    return round(((now-cost)/cost)*100, 2)

for i in ptt[ptt['Price']!=-1].index:
    post_date, post_target = ptt['Date'][i], ptt['Target'][i]
    if post_target not in stock.columns:
        continue

    price_after_post = stock[stock.date > post_date][[post_target]].dropna().values
    # 隔日&至今ROI
    if len(price_after_post) >= 1:
        ptt.loc[i, 'ROI_overall'] = roi(ptt.loc[i, 'Price'], float([x.split(':')[1] for x in price_after_post[-1]][0]))
        ptt.loc[i, 'ROI_1d'] = roi(ptt.loc[i, 'Price'], float([x.split(':')[1] for x in price_after_post[0]][0]))

ptt.loc[:,'Price'] = round(ptt.Price, 2)
#%%
with open('data/ptt_table.pickle', 'wb') as handle:
    pickle.dump(ptt, handle)
ptt.sort_values(by='ROI_overall', ascending=False)[['Title','Author','Label','ROI_overall']]
# %%
print ('Saving to db...')
import sqlite3 as lite
from pandas.io import sql
db = lite.connect('/Users/mac/PttStockProject/ptt_stock_django/db.sqlite3')
ptt.index.name='id' 
sql.to_sql(ptt, name='Ptt_db', con=db, if_exists='replace')

print ('All done!')

# %%
