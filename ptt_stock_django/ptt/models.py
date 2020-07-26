from django.db import models
import datetime
# Create your models here.
class Ptt(models.Model):
    # 根據db中的欄位名稱
    Title = models.TextField(default='default')
    Author = models.TextField(default='default')
    Target = models.TextField(default='default')
    Label = models.TextField(default='default')
    Date = models.DateTimeField(default=datetime.date(2020, 12, 30)) 
    Like = models.IntegerField(default=0)
    Dislike = models.IntegerField(default=0)
    Neutral = models.IntegerField(default=0)
    Url = models.TextField(default='default')
    ROI_1d = models.FloatField(default=0)
    ROI_overall = models.FloatField(default=0)
    Price = models.FloatField(default=0)
    # last_modify_date = models.DateTimeField(auto_now=True) # auto_now:資料有更新時會幚你自動加上更新的時間
    # created = models.DateTimeField(auto_now_add=True) # auto_now_add:新增時會幚你自動加上建立時間

    class Meta:
        db_table = "Ptt_db" # table名稱

# 歷史股價資料庫
class Stock(models.Model):
    stockID = models.TextField(default='default')
    date = models.DateTimeField(default=datetime.date(2020, 12, 30)) 
    close = models.FloatField(default=0.0)
    class Meta:
        db_table = "Stock_db"
        