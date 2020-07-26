from django.shortcuts import render

# Create your views here.
from ptt.models import Ptt, Stock
from ptt.serializers import PttSerializer, StockSerializer
from rest_framework import viewsets
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator


# Create your views here.
class PttViewSet(viewsets.ModelViewSet):
    queryset = Ptt.objects.all()
    serializer_class = PttSerializer

class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer

def home(request):
    import requests
    if request.method=='POST':
        if request.POST.get('pttIDquery'):
            q = request.POST.get('pttIDquery').strip()
            selected_data = list(reversed(Ptt.objects.filter(Author=q)))
            return render(request, 'home.html', {'selected_data': selected_data,'query':q, 'query_type':'pttID'})
        elif request.POST.get('stockIDquery'):
            q = request.POST.get('stockIDquery').strip()
            selected_data = list(reversed(Ptt.objects.filter(Target=q)))
            return render(request, 'home.html', {'selected_data': selected_data,'query':q, 'query_type':'stockID'})
    # 預設顯示陳爸的標的文
    else:
        q = 'zesonpso'
        obj = Ptt.objects.filter(Author=q)
        # order_by = request.GET.get('order_by', 'like')
        # obj = obj.order_by(order_by)
        selected_data = list(reversed(obj))
        return render(request, 'home.html', {'selected_data': selected_data,'query':q, 'query_type':'pttID'})
    

def db(request):
    ptt_item = list(reversed(Ptt.objects.all()))  # 如果沒有要reverse，就寫Ptt.objects.all()就好

    # 下面這段是在寫讓表格分頁．結果後來發現datatable可以直接做好，所以就都註解掉了
    # page = request.GET.get('page', 1)

    # paginator = Paginator(ptt_item, 20) # 設定一頁幾筆
    # try:
    #     items = paginator.page(page)
    # except PageNotAnInteger:
    #     items = paginator.page(1)
    # except EmptyPage:
    #     items = paginator.page(paginator.num_pages)
    # return render(request, 'db.html', {'output' : items})

    return render(request, 'db.html', {'output' : ptt_item})
    # 這樣就可以在db.html裡面使用傳進dict裡面的變數

def about(request):
    return render(request, 'about.html', {})