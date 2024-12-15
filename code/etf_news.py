from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# ETF 테마별 코드
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

def crawl_etf_news(theme_name, max_news=5):
    if theme_name not in themes:
        print(f"'{theme_name}' 테마는 존재하지 않습니다.")
        return

    etf_codes = themes[theme_name]
    print(f"선택한 테마: {theme_name} (ETF 코드: {etf_codes})")

    # 크롬 드라이버 설정
    
    driver = webdriver.Chrome()

    base_url = "https://finance.naver.com/item/main.nhn?code="  # ETF 상세 페이지 URL
    all_news_data = []

    try:
        for etf_code in etf_codes:
            print(f"\n=== ETF 코드: {etf_code} ===")
            driver.get(base_url + etf_code)  # ETF 상세 페이지로 이동
            time.sleep(2)

            # 뉴스/공시 탭 클릭
            try:
                news_tab = driver.find_element(By.CLASS_NAME, "tab5")  # "뉴스/공시" 탭 찾기
                driver.execute_script("arguments[0].click();", news_tab)  # 클릭 이벤트 강제 실행
                time.sleep(2)  # DOM 로드 대기
            except Exception as e:
                print(f"ETF 코드 {etf_code}의 '뉴스/공시' 탭 클릭 실패: {e}")
                continue

            # 뉴스 테이블 크롤링
            try:
                news_table = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "table.type5 tbody"))
                )
                news_rows = news_table.find_elements(By.TAG_NAME, "tr")
            except Exception as e:
                print(f"ETF 코드 {etf_code}의 뉴스 데이터를 찾을 수 없습니다: {e}")
                continue

            etf_news_data = []
            for row in news_rows[:max_news]:  # 최대 max_news만큼 크롤링
                try:
                    # 뉴스 제목과 링크 추출
                    title_element = row.find_element(By.CSS_SELECTOR, "td.title a")
                    title = title_element.text.strip()
                    link = title_element.get_attribute("href")

                    # 뉴스 날짜 및 제공자 추출
                    date = row.find_element(By.CLASS_NAME, "date").text.strip()
                    provider = row.find_element(By.CLASS_NAME, "info").text.strip()

                    print(f"뉴스: {title} ({link}) - {date} ({provider})")

                    etf_news_data.append({
                        "title": title,
                        "link": link,
                        "date": date,
                        "provider": provider,
                    })
                except Exception as e:
                    print(f"뉴스 크롤링 실패: {e}")

            all_news_data.append({etf_code: etf_news_data})

    except Exception as e:
        print("에러 발생:", e)
    finally:
        driver.quit()

    return all_news_data


# 실행 코드
if __name__ == "__main__":
    theme_name = input("ETF 테마 이름을 입력하세요: ").strip()  # 사용자로부터 테마 이름 입력받기
    max_news = int(input("크롤링할 뉴스 개수를 입력하세요 (예: 5): ").strip())

    # 크롤링 함수 실행
    news_results = crawl_etf_news(theme_name, max_news=max_news)

    # 크롤링 결과 출력
    if news_results:
        for etf in news_results:
            for etf_code, news_list in etf.items():
                print(f"\n[ETF 코드: {etf_code}]")
                for idx, news in enumerate(news_list, start=1):
                    print(f"\n[뉴스 {idx}]")
                    print(f"제목: {news['title']}")
                    print(f"링크: {news['link']}")
                    print(f"날짜: {news['date']}")
                    print(f"제공: {news['provider']}")