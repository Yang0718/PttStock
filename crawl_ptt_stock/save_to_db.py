import pandas as pd
import pickle 
import sys
# sys.setrecursionlimit(100000)
# pd.options.mode.chained_assignment = None
# END_IDX = 1000

def toDB(data, stock_table):
    # # 處理內文沒寫標的仔
    # for i in data[data.Target.isnull()].index:
    #     if data.Title[i][-3:] in stock_table.stock.values:
    #         data.Target[i] = stock_table[stock_table.stock==data.Title[i][-3:]].index[0]
    #     elif data.Title[i][-2:] in stock_table.stock.values:
    #         data.Target[i] = stock_table[stock_table.stock==data.Title[i][-2:]].index[0]
    #     elif data.Title[i][5:7] in stock_table.stock.values:
    #         data.Target[i] = stock_table[stock_table.stock==data.Title[i][5:7]].index[0]
            
    # # 處理例外target
    # taiwan_index = ['大盤','台指期','加權指數','台指','台北股市']
    # vix = ['vix','VIX']
    # ts = ['台新','台新金','台新銀']
    # tsmc = ['台積','台GG']
    # for i,j in enumerate(data.Target):
    #     if not j.isdigit():
    #         for k in taiwan_index:
    #             if j.find(k)!=-1:
    #                 data['Target'][i] = '大盤'
    #                 break
    #         for k in vix:
    #             if j.find(k)!=-1:
    #                 data['Target'][i] = 'vix'
    #                 break
    #         for k in ts:
    #             if j.find(k)!=-1:
    #                 data['Target'][i] = '2887'
    #                 break 
    #         for k in tsmc:
    #             if j.find(k)!=-1:
    #                 data['Target'][i] = '2330'
    #                 break



    # # 移除空的target值
    # data.dropna(subset=['Target'], inplace=True)
    # data.reset_index(drop=True)

    # ## [先不要] 移除不是4位數股票代碼的資料
    # # remove_list = []
    # # for i,j in enumerate(data.Target):
    # #     if not j.isdigit() or len(j)!=4:
    # #         remove_list.append(i)
    # # data.drop(data.index[remove_list], axis=0, inplace=True)
    
    # data.reset_index(drop=True, inplace=True)
    # print ('資料清洗完成，存入db')

    # import sqlite3 as lite
    # from pandas.io import sql
    # db = lite.connect('/Users/mac/PttStockProject/ptt_stock_django/db.sqlite3')
    # data.index.name='id' 
    # print ('Saving to DB...')
    # sql.to_sql(data, name='Ptt_db', con=db, if_exists='replace')
    # print ('Done!')

