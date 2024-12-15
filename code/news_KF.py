from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time



# "원자재&ETF" 클릭
def navigate_to_news_list(driver, base_url):
    driver.get(base_url)
    time.sleep(2)  # 페이지 로드 대기
    try:
        # "원자재&ETF" 항목 클릭
        element = driver.find_element(By.XPATH, "//li[@class='title' and contains(text(), '원자재')]")
        element.click()
        time.sleep(2)  # 페이지 이동 대기
    except Exception as e:
        print(f"'원자재&ETF' 클릭 중 오류 발생: {e}")

# 뉴스 리스트 크롤링
def fetch_news_list(driver, max_news=10):
    news_list = []
    try:
        news_items = driver.find_elements(By.CSS_SELECTOR, "div.list ul")  # 뉴스 리스트

        for item in news_items[:max_news]:  # 최대 max_news 개수만 가져옴
            try:
                title_element = item.find_element(By.CSS_SELECTOR, "li.title")
                title = title_element.text.strip()  # 제목 추출
                date = item.find_element(By.CSS_SELECTOR, "li.date").text.strip()  # 날짜 추출
                # 링크 추출
                onclick_value = title_element.get_attribute("onclick")
                news_code = onclick_value.split("'")[1]
                link = f"https://www.wowtv.co.kr/NewsCenter/News/Read?articleId={news_code}"

                print(f"뉴스 제목: {title}, 날짜: {date}, 링크: {link}")
                news_list.append({"title": title, "date": date, "link": link})
            except Exception as e:
                print(f"뉴스 항목 처리 중 오류 발생: {e}")
    except Exception as e:
        print(f"뉴스 리스트 크롤링 중 오류 발생: {e}")

    return news_list

# 뉴스 본문 크롤링
def fetch_news_content(driver, news_link):
    try:
        driver.get(news_link)
        print(f"URL 접속 중: {news_link}")

        # 본문 로딩을 최대 30초까지 대기
        content_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div#divNewsContent"))
        )
        content = content_element.text.strip()
        return content
    except Exception as e:
        print(f"본문 크롤링 중 오류 발생: {e}")
        return None

# 전체 크롤링
def crawl_wowtv_news(max_news=10):
    base_url = "https://www.wowtv.co.kr/Opinion/SerialColumn/Index?subMenu=opinion&Class=G&menuSeq=79064"
    driver = webdriver.Chrome()
    news_data = []

    try:
        # "원자재&ETF" 클릭
        navigate_to_news_list(driver, base_url)

        # 뉴스 리스트 크롤링
        news_list = fetch_news_list(driver, max_news=max_news)

        for news in news_list:
            print(f"\n[뉴스 크롤링 시작] 제목: {news['title']}")
            content = fetch_news_content(driver, news['link'])

            if content:
                print("본문 내용 크롤링 성공")
                news_data.append({
                    "title": news["title"],
                    "date": news["date"],
                    "link": news["link"],
                    "content": content
                })
            else:
                print("본문 내용 크롤링 실패")

            time.sleep(1)  # 서버 부하 방지를 위한 딜레이
    finally:
        driver.quit()

    # 결과를 DataFrame으로 변환
    df = pd.DataFrame(news_data)
    return df

# 실행 코드
if __name__ == "__main__":
    
    news_df = crawl_wowtv_news(max_news=7)

    # 결과 출력 및 저장
    print("\n=== 크롤링 결과 ===")
    print(news_df)

    # 파일 저장
    news_df.to_csv("wowtv_news_list_selenium.csv", index=False, encoding="utf-8-sig")
    print("뉴스 데이터를 wowtv_news_list_selenium.csv 파일로 저장했습니다.")