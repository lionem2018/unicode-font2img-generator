import requests
import re
from bs4 import BeautifulSoup


def spider():
    url = 'https://ko.wikipedia.org/wiki/%EC%9C%A0%EB%8B%88%EC%BD%94%EB%93%9C_%EC%98%81%EC%97%AD'

    source_code = requests.get(url)
    if not source_code.ok:
        print("Site", url, "연결 실패")
        return

    plain_text = source_code.text
    soup = BeautifulSoup(plain_text, 'lxml')

    type_count = len(soup.find_all("span", {"class": re.compile("sortkey")}))

    print(type_count)

    count = 0
    for table_item in soup.select('tbody > tr'):
        count += 1

    print(count)

    ## type_count랑 count가 왜 다른가?
    # 실제 개수: 7959(전체 테이블 크기) - 184(마지막 레퍼런스 부분) / 27(리스트 하나의 크기) = 287개
    # count가 가장 근접함


if __name__ == '__main__':
    spider()
