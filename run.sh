
source /Users/mac/miniconda3/bin/activate y3.6
# source activate y3.6 會沒作用，要用上面那種寫法
echo "conda env activated."

cd /Users/mac/PttStockProject/crawl_ptt_stock/
python crawl_ptt.py
echo "************"
python crawl_yahoo.py
echo "************"
python ROI.py
echo "************"
cd ..