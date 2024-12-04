from pykrx import stock
from pykrx import bond
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt

# 테마별 ETF 티커 목록
themes = {
    "농산물": ["137610", "271060", "138920"],
    "원유": ["271050", "217770", "261220", "130680"],
    "금": ["411060", "225130", "139320", "132030", "319640"],
    "은": ["144600", "139320"],
    "기타 귀금속": ["334690", "334700"],
    "구리": ["138910", "160580"],
    "기타 산업금속": ["139310"],
    "탄소배출권": ["400570", "400580", "401590", "459370", "400590"]
}

# 각 테마별 ETF 정보 가져오기
def get_etf_info_by_theme(theme_name, tickers):
    print(f"\n=== {theme_name} ===")
    for ticker in tickers:
        etf_name = stock.get_etf_ticker_name(ticker)
        print(f"티커: {ticker}, 이름: {etf_name}")

      
end_date = input("해당 날짜를 입력하세요 (YYYYMMDD 형식): ")
ticker = input("티커를 입력하세요: ")  

# 시작 날짜를 종료 날짜의 일주일 전으로 설정
end_date_obj = datetime.strptime(end_date, "%Y%m%d")
start_date_obj = end_date_obj - timedelta(days=7)
start_date = start_date_obj.strftime("%Y%m%d")


#기준가
df_ohlcv = stock.get_etf_ohlcv_by_date(start_date, end_date, ticker)

#투자자별 거래실적
df_trading_volume = stock.get_etf_trading_volume_and_value(start_date, end_date, ticker)

#구성종목
df_pdf = stock.get_etf_portfolio_deposit_file(ticker)
print(df_ohlcv)