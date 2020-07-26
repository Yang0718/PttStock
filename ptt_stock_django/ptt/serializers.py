from rest_framework import serializers
from ptt.models import Ptt, Stock


class PttSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ptt
        # fields = '__all__'
        fields = (['Title', 'Author', 'Target', 'Label', 'Date', 'Like', 'Dislike', 'Neutral', 'Url', 'ROI_1d','ROI_overall','Price'])

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        # fields = '__all__'
        fields = ('stockID', 'date','close')