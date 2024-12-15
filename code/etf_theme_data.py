from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from pykrx import stock
from datetime import datetime, timedelta
import pandas as pd
import time

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

# Selenium 기반 ETF 상세 정보 크롤링
def fetch_etf_data(ticker):
    
    driver = webdriver.Chrome()

    try:
        # KRX ETF 페이지 접속
        url = "http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201030105"
        driver.get(url)

        # 티커 입력 및 검색
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "tboxisuCd_finder_secuprodisu1_0"))
        )
        driver.execute_script(f"arguments[0].value='{ticker}';", search_box)

        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "btnisuCd_finder_secuprodisu1_0"))
        )
        search_button.click()
        time.sleep(3)

        # 조회 버튼 클릭
        lookup_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "jsSearchButton"))
        )
        lookup_button.click()
        time.sleep(5)

        # BeautifulSoup으로 HTML 파싱
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # 개요 일반 데이터 크롤링
        overview_table = soup.find('table', {'id': 'jsGrid_MDCSTAT047_1'})
        overview_data = []
        if overview_table:
            rows = overview_table.find_all('tr')
            for row in rows:
                cols = row.find_all(['th', 'td'])
                if len(cols) == 4:
                    overview_data.append([cols[0].text.strip(), cols[1].text.strip()])
                    overview_data.append([cols[2].text.strip(), cols[3].text.strip()])
                elif len(cols) == 2:
                    overview_data.append([cols[0].text.strip(), cols[1].text.strip()])
        overview_df = pd.DataFrame(overview_data, columns=['항목', '내용'])

        # PDF 상위 10종목 데이터 크롤링
        pdf_table = soup.find('table', {'id': 'jsGrid_MDCSTAT047_2'})
        pdf_data = []
        headers = []
        if pdf_table:
            headers = [th.text.strip() for th in pdf_table.find('thead').find_all('th')]
            rows = pdf_table.find('tbody').find_all('tr')
            for row in rows:
                cols = [td.text.strip() for td in row.find_all('td')]
                pdf_data.append(cols)
        pdf_df = pd.DataFrame(pdf_data, columns=headers)

        return overview_df, pdf_df

    except Exception as e:
        print(f"크롤링 중 오류 발생: {e}")
        return None, None

    finally:
        driver.quit()

# 1. 특정 기간 계산
def calculate_dates():
    end_date = datetime.now().strftime("%Y%m%d")
    date_ranges = {
        "1주일": (datetime.now() - timedelta(days=7)).strftime("%Y%m%d"),
        "1개월": (datetime.now() - timedelta(days=30)).strftime("%Y%m%d"),
        "6개월": (datetime.now() - timedelta(days=180)).strftime("%Y%m%d"),
        "1년": (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")
    }
    return end_date, date_ranges

# 2. 특정 테마의 ETF 데이터 반환
def get_etf_data_by_theme(theme_name):
    if theme_name not in themes:
        raise ValueError(f"'{theme_name}'는 유효한 테마가 아닙니다.")
    
    tickers = themes[theme_name]
    end_date, date_ranges = calculate_dates()

    # 전체 데이터를 저장할 딕셔너리
    theme_data = {}

    for ticker in tickers:
        try:
            # ETF 이름 가져오기
            etf_name = stock.get_etf_ticker_name(ticker)

            # 각 기간별 데이터 가져오기
            ticker_data = {}
            for period, start_date in date_ranges.items():
                df = stock.get_etf_ohlcv_by_date(start_date, end_date, ticker)
                ticker_data[period] = df

            # 상세 정보 크롤링
            overview_df, pdf_df = fetch_etf_data(ticker)


            # 티커별 데이터 저장
            theme_data[etf_name] = {
                "기간별 데이터": ticker_data,
                "개요 일반": overview_df,
                "PDF 상위 10종목": pdf_df
            }

        except Exception as e:
            print(f"티커 {ticker} 처리 중 오류 발생: {e}")
    
    return theme_data

# 3. 실행 코드 (테스트용)
if __name__ == "__main__":
    # 사용자 입력
    theme_name = input("ETF 테마를 입력하세요: ").strip()

    # 테마별 ETF 데이터 가져오기
    try:
        data = get_etf_data_by_theme(theme_name)
        for etf_name, details in data.items():
            print(f"\n=== {etf_name} ===")
            for period, df in details["기간별 데이터"].items():
                print(f"\n--- {period} 데이터 ---")
                print(df.head())
    except ValueError as ve:
        print(ve)