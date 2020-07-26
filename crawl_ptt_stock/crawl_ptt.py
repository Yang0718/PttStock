#%%
import json
import requests 
import time
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from bs4.element import NavigableString
from tqdm import tqdm
import pickle
import os
pd.options.mode.chained_assignment = None #讓pandas不會在修改df裡的值時一直出現warning

#%%
session=requests.session()
requests.packages.urllib3.disable_warnings()
article_urls = []
url = 'https://www.ptt.cc/bbs/Stock/index'
raw = session.get('https://www.ptt.cc/bbs/Stock/index.html', verify=False)
soup = BeautifulSoup(raw.text, "lxml")

# 讀取parameters，看之前爬到哪
with open('./data/parameters.pickle', 'rb') as handle:
    parameters = pickle.load(handle)
# 手動輸入起始index就先跑下面這4行，再執行本程式
# import pickle
# parameters = {'current_index':2500, 'since_index':2500}
# with open('data/parameters.pickle', 'wb') as handle:
#     pickle.dump(parameters, handle)


START_IDX = int(soup.find_all(class_='btn wide')[1].get('href')[-9:-5])+1 # 找現在最新的頁面index
END_IDX = parameters['current_index']

# print ('Latest page index: {}'.format(START_IDX))
print ('Start crawling, there are '+str(START_IDX-END_IDX+1)+' new pages.')
for i in tqdm(range(np.abs(START_IDX - END_IDX) + 10)): # 額外多爬10頁，更新推噓數量資料
    page = url+str(START_IDX-i)+'.html'
    res  = session.get(page, verify=False)
    soup = BeautifulSoup(res.text, "lxml")
    for article in soup.select(".r-ent"):
        if '[標的]' in article.text:
            try:
                article_urls.append('https://www.ptt.cc'+ article.select(".title")[0].select("a")[0].get("href"))
            except:
                pass 

print ('Finish crawling.')

# print("url總數:",len(article_urls))
# np.save('data/urls_of_ptt.npy', article_urls)
#%%
import re
article_id, titles, dates, targets, labels, urls, authors, likes, dislikes, neutrals = [], [],[], [], [], [], [], [], [], []

print ('To dataframe...')

for url in tqdm(article_urls):
    raw  = session.get(url, verify=False)
    soup = BeautifulSoup(raw.text, "lxml")
    try:
        t = soup.select(".article-meta-value")[2].contents[0]
        author = soup.select(".article-meta-value")[0].contents[0].split(' (')[0]
        date = soup.select(".article-meta-value")[3].contents[0]
        # 算推噓
        like, dislike, neutral = 0, 0, 0 
        c = str(soup.select("#main-content")[0].find_all('span','push-tag'))
        like, dislike, neutral = c.count('推'), c.count('噓'), c.count('→')
        for tag in soup.select("#main-content")[0]:
            if type(tag) is NavigableString and tag !='\n':
                target = tag.split('標的：')[1].split('\n2')[0]
                label = tag.split('分類：')[1].split('\n3')[0]
                if '多/空/請益/心得' in label:
                    label = label.split('多/空/請益/心得')[1]
                if '空' in label:
                    label='空'
                elif '多' in label:
                    label='多'
                else:
                    continue # 如果是請益文或者是其他沒寫清楚的標題，就不要了
                # 確定都有抓到，再放進來
                if len(t)!=0 and len(target)!=0 and len(label)!=0 and len(author)!=0 and len(date)!=0 and like+dislike+neutral!=0:
                    article_id.append(url.split('/Stock/')[1][:-5])
                    titles.append(t)
                    targets.append(target)
                    labels.append(label)
                    urls.append(url)
                    authors.append(author)
                    dates.append(date)
                    likes.append(like)
                    dislikes.append(dislike)
                    neutrals.append(neutral)
                break
    except:
        pass
# print ('Done.')

#%%
print ('Cleaning...')
# 讀取台股代碼
with open('data/stockID.pickle', 'rb') as handle:
    stock_table = pickle.load(handle)
labels = [i.replace("\n",'').replace(" ","") for i in labels]
targets = [i.replace("\n",'').replace(" ","") for i in targets]

data = pd.DataFrame({'ArticleID':article_id, 'Title':titles, 'Author':authors, 'Target':targets,'Label':labels, 'Date':dates, 'Like':likes, 'Dislike':dislikes, 'Neutral': neutrals, 'url':urls})

# # 這筆資料爬到的日期沒有年份
# c = data[(data.Title=='[標的] 4958臻鼎my')  & (data.Author=='simultaneous')].index[0]

# 有幾筆資料的年份會不見，用上一筆的年份捕進來，不然pd.to_datetime會報錯
for i in range(len(data)):
    try:
        pd.to_datetime(data['Date'][i])
    except:
        data['Date'][i] = data['Date'][i] + data['Date'][i-1][-5:]
# 這筆資料怪怪的，個別處理
if 'M.1595285980.A.7C1' in data.ArticleID.values:
    data.loc[data.ArticleID=='M.1595285980.A.7C1','Title'] = '[標的] 00677U 富邦VIX 強力歐印空'
    data.loc[data.ArticleID=='M.1595285980.A.7C1','Date'] = 'Tue Jul 21 06:59:38 2020'
data['Date'] = pd.to_datetime(data['Date'])
print (data.Label.value_counts())
#%%
# 清理標的
remove_target_list = ['NASDAQ','道瓊','AMD','TSLA','本週股票','小納期','MINI標普500期','日本','石油','香港','ATVI']
remove_idx = []

# 找數字
def get_digits(str1):
    c = ""
    for i in str1:
        if i.isdigit():
            c += i
    return c

for i,j in enumerate(data.Target):
    try:
        try1 = str([int(s) for s in j.split('(')[1].split(')') if s.isdigit()][0])
    except:
        try:
            try1 = str([int(s) for s in j.split('（')[1].split('）') if s.isdigit()][0])
        except:
            try1 = ''

        
    for k in remove_target_list:
        if j.find(k)!=-1: # 表示j裡面有remove_target_list裡面的東西
            remove_idx.append(i)
            continue
    # 找股票代碼
    if get_digits(j) in stock_table.index and len(get_digits(j))==4:
        data.loc[i, 'Target'] = get_digits(j)
    elif get_digits(j)[:4] in stock_table.index: # 為了應付公司名稱剛好也有數字的情況(例：Target是6643 M31，此時get_digits會不小心把公司名稱也當成股票代號，就找不到了)
        data.loc[i, 'Target'] = get_digits(j)[:4]
    # 找公司名字
    elif j[:2] in stock_table.stock.values: 
        data.loc[i, 'Target'] = stock_table[stock_table.stock==j[:2]].index[0]
    elif j[:3] in stock_table.stock.values:
        data.loc[i, 'Target'] = stock_table[stock_table.stock==j[:3]].index[0]
    elif j in stock_table.stock.values:
        data.loc[i, 'Target'] = stock_table[stock_table.stock==j].index[0]
    elif try1.isdigit() and try1 in stock_table.index:
        data.loc[i, 'Target'] = try1
    # 如果target欄位還是找不到標的代號，就從title去找
    elif get_digits(data['Title'][i]) in stock_table.index and len(get_digits(data['Title'][i]))==4:
        data.loc[i, 'Target'] = get_digits(data['Title'][i])
    else:
        pass
data = data.drop(remove_idx, axis=0)
data.reset_index(drop=True, inplace=True)
#%%
# 處理內文沒寫標的仔
for i in data[data.Target.isnull()].index:
    if data.Title[i][-3:] in stock_table.stock.values:
        data.Target[i] = stock_table[stock_table.stock==data.Title[i][-3:]].index[0]
    elif data.Title[i][-2:] in stock_table.stock.values:
        data.Target[i] = stock_table[stock_table.stock==data.Title[i][-2:]].index[0]
    elif data.Title[i][5:7] in stock_table.stock.values:
        data.Target[i] = stock_table[stock_table.stock==data.Title[i][5:7]].index[0]

# 處理例外target
taiwan_index = ['大盤','台指期','加權指數','台指','台北股市']
vix = ['vix','VIX','富邦Vix','00677U','Vix']
ts = ['台新','台新金','台新銀']
tsmc = ['台積','台GG']
for i,j in enumerate(data.Target):
    if not j.isdigit():
        for k in taiwan_index:
            if j.find(k)!=-1:
                data['Target'][i] = '^TWII'
                break
        for k in vix:
            if j.find(k)!=-1:
                data['Target'][i] = '00677U'
                break
        for k in ts:
            if j.find(k)!=-1:
                data['Target'][i] = '2887'
                break
        for k in tsmc:
            if j.find(k)!=-1:
                data['Target'][i] = '2330'
                break

# 移除空的target值
data.dropna(subset=['Target'], inplace=True)
data.reset_index(drop=True)

## [先不要] 移除不是4位數股票代碼的資料
# remove_list = []
# for i,j in enumerate(data.Target):
#     if not j.isdigit() or len(j)!=4:
#         remove_list.append(i)
# data.drop(data.index[remove_list], axis=0, inplace=True)

data.reset_index(drop=True, inplace=True)
#%%
data = data[data.Target.str.len()<=10]

if 'ROI_1d' not in data.columns:
    data['ROI_1d'] = None
if 'ROI_overall' not in data.columns:
    data['ROI_overall'] = None
data['發文時間'] = -1
data['Price'] = -1
#%%
# Reverse data
# 為了以後能直接把新的標的文append到最後面
data = data.iloc[::-1].reset_index(drop=True)

if 'data' not in os.listdir():
    os.mkdir('data')

if 'ptt_table.pickle' in os.listdir('data/'):
    print ('ptt_table.pickle already existed, merging...')
    with open('data/ptt_table.pickle', 'rb') as handle:
        _ = pickle.load(handle)
    _ = _[~_.ArticleID.isin(data.ArticleID.values)]
    data = pd.concat([data, _], axis=0)
    data.drop_duplicates(inplace=True)
    print ('done.')
data.sort_values(by='Date',ascending=False, inplace=True)
# 表格裡面的文字會搞事，出現遞迴error(bf4在搞怪)，故一定要先轉成字串否則沒法存成pickle
data[['ArticleID','Title','Author','Target','Label']] = data[['ArticleID','Title','Author','Target','Label']].astype('str')

# 存檔
print ('Saving pickle and csv file...')
data.reset_index(drop=True, inplace=True)
data.to_pickle('data/ptt_table.pickle')
data.to_csv('data/ptt_table.csv',index=False)

# 最後一步，存到SQL中
# from save_to_db import toDB
# toDB(data, stock_table)

# %%
print ('Saving to db...')
import sqlite3 as lite
from pandas.io import sql
db = lite.connect('/Users/mac/PttStockProject/ptt_stock_django/db.sqlite3')
data.index.name='id' 
sql.to_sql(data, name='Ptt_db', con=db, if_exists='replace')
print ('All done!')

# 確定全都OK，再存回去parameters
parameters['current_index'] = START_IDX
with open('data/parameters.pickle', 'wb') as handle:
    pickle.dump(parameters, handle)
