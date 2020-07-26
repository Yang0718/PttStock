#%%
import requests
import pandas as pd

def crawl_ID(url):
    res = requests.get(url)
    df = pd.read_html(res.text)[0]
    df.columns = df.iloc[0]
    df = df.dropna(thresh=3, axis=0).dropna(thresh=3, axis=1)
    df = df.loc[2:]
    new = df.有價證券代號及名稱.str.split("　",n=2,expand=True)
    df.insert(0,'stockID',new[0])
    df.insert(1,'stock',new[1])
    df.drop(['有價證券代號及名稱'], axis=1, inplace=True)
    return df[['stockID','stock','上市日','市場別','產業別']]


# 上市
df1 = crawl_ID('http://isin.twse.com.tw/isin/C_public.jsp?strMode=2')
# 上櫃
df2 = crawl_ID('https://isin.twse.com.tw/isin/C_public.jsp?strMode=4')
# 興櫃
df3 = crawl_ID('https://isin.twse.com.tw/isin/C_public.jsp?strMode=5')

#%%
df = pd.concat([df1, df2, df3], axis=0)

df.set_index('stockID', inplace=True)
df = df[['stock','市場別']]

# stock_table = df3[['stockID', 'stock']].set_index('stockID')['stock'].to_dict()

import pickle
# with open('data/stockID.pickle', 'wb') as handle:
#     pickle.dump(stock_table, handle, protocol=pickle.HIGHEST_PROTOCOL)
#     print ('Finish saving the stock ID table.')
other_target = pd.DataFrame({'stock':'大盤','市場別':'指數'}, index=['^TWII'])
df = pd.concat([df,other_target], axis=0)
# 存成dataframe
import os
if 'data' not in os.listdir():
    os.mkdir('data')
with open('data/stockID.pickle', 'wb') as handle:
    pickle.dump(df, handle, protocol=pickle.HIGHEST_PROTOCOL)
print ('Finish saving stock ID table.')