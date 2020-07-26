# https://ushluap.github.io/2019-06-26-crawler-1/<br>
# https://finance.yahoo.com/<br>
# https://twstock.readthedocs.io/zh_TW/latest/quickstart.html#id2<br>
# https://finance.yahoo.com/quote/1608.TW/history?period1=1419264000&period2=1577030400&interval=1d&filter=history&frequency=1d <br>
# In[1]:
import requests
import pandas as pd
import numpy as np
from io import StringIO
import time
import pickle
import datetime
import os

# ptt標的文爬蟲結果
stock_in_ptt = pd.read_pickle('data/ptt_table.pickle')
for i,j in enumerate(stock_in_ptt.Date):
    stock_in_ptt.loc[i, 'Date'] = j.date()
# 所有股票代碼
with open('data/stockID.pickle', 'rb') as handle:
    stockID = pickle.load(handle)
# 選出有在標的文裡面的股票代號
stockID = stockID[np.isin(stockID.index,stock_in_ptt.Target)]

# s = [x for x in stockID.index if len(x)==4]
# stockID = stockID.loc[s,:] # 只取股票代碼長度是4的
# # 1795美時已經上市了，但是yahoo finance還沒改，所以要先改成上櫃
# stockID.loc['1795']['市場別']='上櫃'
from datetime import date, timedelta
TODAY = date.today().strftime("%Y-%m-%d") # 獲取今天的日期(在爬的時候會多加一天，確保股價會爬到最新ㄉ)
TOMORROW = date.today() + timedelta(days=1)
TOMORROW = TOMORROW.strftime("%Y-%m-%d")

SINCE_DATE = stock_in_ptt.iloc[-1,5]- datetime.timedelta(days=30)
SINCE_DATE = SINCE_DATE.strftime("%Y-%m-%d")
# EARLIEST_DATE = (stock_in_ptt.Date[len(stock_in_ptt)-1]-timedelta(days=10)).strftime("%Y-%m-%d") # 全部標的文中，最早的日期再減十天
date_range = pd.date_range(start = SINCE_DATE,end=TODAY, freq='D')
stock_df = pd.DataFrame(index = date_range)
stock_df.index.name='date'

#%%
# 爬蟲不太穩定，有些人爬一次沒爬到，爬三次就爬到了
# https://query1.finance.yahoo.com/v7/finance/download/3030.TW?period1=1563987677&period2=1595610077&interval=1d&events=history
def crawl_yahoo(s, m, since, due):
    global stock_df
    succ, fail = 0, 0
    fail_list = []
    for i in set(s.index):
        try:
            # https://query1.finance.yahoo.com/v7/finance/download/2890.TW?period1=1587916800&period2=1595520000&interval=1d&events=history&crumb=hP2rOschxO0
            site = 'https://query1.finance.yahoo.com/v7/finance/download/'+i+m+'?period1='+since+'&period2='+due+'&interval=1d&events=history&crumb=hP2rOschxO0'
            response = requests.get(site) # 之前都用post爬，但後來改成get才可以
            df = pd.read_csv(StringIO(response.text))

            if df.shape[0]==0:
#                 print (i, stockID.loc[i][0], 'error, shape is 0')
                fail+=1
                fail_list.append(i)
            else:
                df.Date = pd.to_datetime(df.Date)
                # 開盤價:收盤價
                df['Price'] = df.apply(lambda x: str(x['Open'])+':'+str(x['Close']), axis=1)
                df = df[['Date','Price']]
                df.columns = ['date', i]
                df.set_index('date')
                
                stock_df = stock_df.merge(df, on='date',how='left')

#                 stock_df = np.vstack([stock_df, df.values])
                succ+=1
        except Exception as e:
            print (i, stockID.loc[i][0], ' error：', e)
            
    print ('success',succ, ' fail',fail)
    return fail_list

# 第一次開爬
since = str(int(time.mktime(time.strptime(SINCE_DATE, "%Y-%m-%d")))) # 起始日

due = str(int(time.mktime(time.strptime(TOMORROW, "%Y-%m-%d"))))

start = time.time()
print ('start crawling stock price...')
# function會回傳爬失敗的股票列表
f1 = crawl_yahoo(stockID[stockID.市場別=='上市'],'.TW', since, due)
f2 = crawl_yahoo(stockID[stockID.市場別=='上櫃'],'.TWO', since, due) # 上櫃的話要改成TWO
f3 = crawl_yahoo(stockID[stockID.市場別=='興櫃'],'.TWO', since, due) # 興櫃的話要改成TWO
f4 = crawl_yahoo(stockID[stockID.stock=='大盤'], '', since, due) 
print ('finish 1st crawling, cost ', str(datetime.timedelta(seconds=int(time.time()-start))))
print ('failed: ',len(f1), len(f2), len(f3), len(f4))

# 重複爬剛剛爬失敗的
if (len(f1)+len(f2)+len(f3)+len(f4))!=0:
    start = time.time()
    repeat = 0
    while (len(f1)>50) and (repeat<10):
        f1 = crawl_yahoo(stockID[stockID.index.isin(np.array(f1))],'', since, due)
        f2 = crawl_yahoo(stockID[stockID.index.isin(np.array(f2))],'O', since, due)
        f3 = crawl_yahoo(stockID[stockID.index.isin(np.array(f3))],'O', since, due)
        repeat+=1
    print ('finish repeat crawling, cost:', str(datetime.timedelta(seconds=int(time.time()-start))))
    print ('failed: ',len(f1), len(f2), len(f3), len(f4))
if stock_df.index.name != 'date':
    stock_df = stock_df.set_index('date')
# stock_df.index.name = 'id'
# 去掉未開盤的日期
# stock_df.dropna(subset=stock_df.columns[1:],axis=0, how='all', inplace=True)
stock_df.tail(5)
#%%
print ('Saving to local...')
if 'stock_db.pickle' in os.listdir('data/'):
    print ('stock_db.pickle already existed, merging...')
    with open('data/stock_db.pickle', 'rb') as handle:
        stock_db = pickle.load(handle)
        stock_db = stock_db.set_index('date')
    old_col = stock_db.columns
    new_col = stock_df.columns
    same_col = old_col.intersection(new_col)
    diff_col = list(set(new_col)-set(old_col))
    idx = stock_df.index
    diff_idx_df = pd.DataFrame(index=idx.difference(stock_db.index)) # 舊的db裡面沒有的datetime index
    stock_db = pd.concat([stock_db, diff_idx_df], axis=0)
    # 把相同欄位的塞入
    stock_db.loc[idx,same_col] = stock_df[same_col]
    # 把新的欄位併入
    stock_db = pd.concat([stock_db, pd.DataFrame(columns = diff_col)], axis=1) # 先製作空的新欄位
    stock_db.loc[idx,diff_col] = stock_df[diff_col]
    print ('done.')
    stock_df = stock_db

if type(stock_db.index[0]) != float:
    stock_df.index.name = 'date'
# 存進去的時候，要記得把index重設並命名成id
import sqlite3 as lite
from pandas.io import sql
print ('Saving price to db and pickle file...')
db = lite.connect('/Users/mac/PttStockProject/ptt_stock_django/db.sqlite3')

with open('data/stock_db.pickle', 'wb') as handle:
    if stock_df.index.name == 'date':
        stock_df_ = stock_df.reset_index() 
        stock_df_.index.name = 'id'
        pickle.dump(stock_df_, handle, protocol=pickle.HIGHEST_PROTOCOL)
        sql.to_sql(stock_df_, name='Stock_db', con=db, if_exists='replace')
    elif stock_df.index.name == 'id':
        pickle.dump(stock_df, handle, protocol=pickle.HIGHEST_PROTOCOL)
        sql.to_sql(stock_df, name='Stock_db', con=db, if_exists='replace')
    else:
        print ('error! check it out!')
print ('done.')