from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# 다운로드 폴더 설정
download_dir = r"result"
log_file = r"log.txt"
os.makedirs(download_dir, exist_ok=True)

# log.txt 초기화
with open(log_file, 'w', encoding='utf-8') as log:
    log.write("다운로드 시작\n")

# WebDriver 설정
options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "safebrowsing.enabled": True
}
options.add_experimental_option("prefs", prefs)

# 드라이버 생성
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    # 1. 페이지 열기
    url = "https://law.go.kr/precSc.do?menuId=7&subMenuId=47&tabMenuId=213&eventGubun=060117"
    driver.get(url)
    time.sleep(2)

    # 2. 상세검색 열기
    detail_search_button = driver.find_element(By.XPATH, "//a[@onclick=\"dtlSchEtcOpen('sub7');return false;\"]")
    detail_search_button.click()
    time.sleep(2)

    # 3. 민사 사건 선택
    civil_checkbox = driver.find_element(By.ID, "evtKnd1")
    if not civil_checkbox.is_selected():
        civil_checkbox.click()
    time.sleep(1)

    # 4. 정렬 방식 변경 (오름차순)
    sort_dropdown = Select(driver.find_element(By.ID, "sortPrnlYd"))
    sort_dropdown.select_by_value("20,10,30")
    time.sleep(1)

    # 5. 검색 버튼 클릭
    search_button = driver.find_element(By.XPATH, "//a[@onclick=\"javascript:newDtlEtcSearch('precEvtNm'); return false;\"]")
    search_button.click()
    time.sleep(5)

    # 6. 처음 케이스 다운로드 처리(코드 실행 시 한번만 실행됨)
    case_links = driver.find_elements(By.XPATH, "//a[contains(@onclick, 'lsEmpViewWideAll')]")
    if case_links:
        case_links[0].click()  # 첫 번째 케이스 열기
        time.sleep(3)

        # doc 파일 다운로드 로직
        save_button = driver.find_element(By.ID, "bdySaveBtn")
        save_button.click()
        time.sleep(2)

        doc_radio_button = driver.find_element(By.ID, "FileSaveDoc")
        doc_radio_button.click()
        time.sleep(1)

        final_save_button = driver.find_element(By.ID, "aBtnOutPutSave")
        final_save_button.click()
        time.sleep(3)

        # 로그 기록
        with open(log_file, 'a', encoding='utf-8') as log:
            log.write("첫 번째 케이스 다운로드 완료\n")

        # 팝업 닫기
        driver.switch_to.window(driver.window_handles[0])
  
    current_page = 10  # 원하는 페이지부터 다운 가능
    idx = 1  # 페이지 번호 초기값
  
    for _ in range(0, current_page - 1):
        try:
            if idx % 5 == 0:  # 5의 배수일 경우 "다음으로" 버튼 클릭
                next_page_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(@onclick, 'movePage')]//img[contains(@alt, '다음으로')]")
                ))
                next_page_button.click()
            else:  # 그 외에는 다음 페이지 번호 클릭
                next_page_link = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f"//ol[@start='1']/li/a[@onclick=\"javascript:movePage('{idx + 1}');\"]")
                ))
                next_page_link.click()
    
            # 페이지 로드 대기 (활성 페이지 변경 대기)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f"//li[@class='on' and text()='{idx + 1}']"))
            )
            print(f"페이지 {idx + 1} 로드 완료")
    
            idx += 1
        except Exception as e:
            print(f"오류 발생: {e}")
            break
  
    while True:
        print(f"Processing page: {current_page}")

        # 7. left_list_bx 내 모든 항목 처리
        list_items = driver.find_elements(By.XPATH, "//ul[@class='left_list_bx']/li/a")
        for item in list_items:
            try:
                case_name = item.find_element(By.XPATH, "./span[@class='tx']").text  # 케이스 이름 가져오기
                item.click()
                time.sleep(3)

                # doc 파일 다운로드 로직
                save_button = driver.find_element(By.ID, "bdySaveBtn")
                save_button.click()
                time.sleep(2)

                doc_radio_button = driver.find_element(By.ID, "FileSaveDoc")
                doc_radio_button.click()
                time.sleep(1)

                final_save_button = driver.find_element(By.ID, "aBtnOutPutSave")
                final_save_button.click()
                time.sleep(3)

                # 로그 기록
                with open(log_file, 'a', encoding='utf-8') as log:
                    log.write(f"페이지 {current_page} - 케이스: {case_name} 다운로드 완료\n")

                # 팝업 닫기
                driver.switch_to.window(driver.window_handles[0])
            except Exception as e:
                print(f"Error processing item: {e}")
                with open(log_file, 'a', encoding='utf-8') as log:
                    log.write(f"페이지 {current_page} - 에러: {e}\n")
                continue

        # 8. 다음 페이지로 이동 로직
        try:
            if current_page % 5 == 0:  # 5의 배수일 경우 "다음으로" 버튼 클릭
                next_page_button = driver.find_element(By.XPATH, "//a[contains(@onclick, 'movePage')]//img[contains(@alt, '다음으로')]")
                next_page_button.click()
            else:  # 그 외에는 다음 페이지 번호 클릭
                next_page_link = driver.find_element(By.XPATH, f"//ol[@start='1']/li/a[@onclick=\"javascript:movePage('{current_page + 1}');\"]")
                next_page_link.click()

            current_page += 1
            time.sleep(5)
        except Exception as e:
            print("No more pages to process or next page button not found.")
            with open(log_file, 'a', encoding='utf-8') as log:
                log.write("페이지 이동 불가 또는 다음 버튼 없음\n")
            break

finally:
    # 브라우저 종료
    driver.quit()

# 다운로드된 파일 확인
with open(log_file, 'a', encoding='utf-8') as log:
    log.write("다운로드 완료 파일 목록:\n")

downloaded_files = os.listdir(download_dir)
for file in downloaded_files:
    with open(log_file, 'a', encoding='utf-8') as log:
        log.write(f"{file}\n")

print("다운로드 완료 파일 목록:")
for file in downloaded_files:
    print(file)
