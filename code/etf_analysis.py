import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from etf_theme_data import get_etf_data_by_theme  # etf_theme_data.py에서 함수 가져오기
import os

plt.rcParams["font.family"] = "Noto Sans CJK KR"  # Noto Sans CJK 폰트 설정
plt.rcParams["axes.unicode_minus"] = False  # 마이너스 기호 깨짐 방지

# Seaborn 스타일 설정
sns.set(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

# 저장 디렉토리 설정
output_dir = "etf_visualizations"
os.makedirs(output_dir, exist_ok=True)  # 디렉토리 없으면 생성

# 기간별 데이터 시각화 함수
def visualize_etf_data(theme_name):
    # 테마별 데이터를 가져옵니다
    etf_data = get_etf_data_by_theme(theme_name)
    
    # 각 ETF에 대해 시각화
    for etf_name, details in etf_data.items():
        print(f"\n=== {etf_name} 데이터 시각화 ===")
        
        # 기간별 데이터를 가져옵니다
        period_data = details["기간별 데이터"]
        
        for period, df in period_data.items():
            if df is not None and not df.empty:
                df.reset_index(inplace=True)  # 인덱스 초기화
                df["날짜"] = pd.to_datetime(df["날짜"])  # 날짜 형식 변환
                
                # 시각화
                plt.figure(figsize=(10, 6))
                sns.lineplot(
                    data=df,
                    x="날짜", y="종가", marker="o"
                )
                # 제목과 축 제거
                plt.gca().set_title("")
                plt.gca().set_xlabel("")
                plt.gca().set_ylabel("")
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                # 이미지 저장
                output_file = os.path.join(output_dir, f"{etf_name}_{period}_종가_추이.png")
                plt.savefig(output_file, dpi=300)
                print(f"{etf_name} - {period} 그래프가 저장되었습니다: {output_file}")
                
                
            else:
                print(f"{etf_name} ({period})에 대한 시각화 가능한 데이터가 없습니다.")

# 실행 코드
if __name__ == "__main__":
    # 사용자 입력
    theme_name = input("ETF 테마를 입력하세요: ").strip()
    
    try:
        # 시각화 함수 호출
        visualize_etf_data(theme_name)
    except ValueError as ve:
        print(ve)