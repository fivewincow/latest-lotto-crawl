import requests
import json
import datetime
from bs4 import BeautifulSoup
import re
import time

def fetch_lotto_data(draw_no):
    """회차 번호를 기준으로 당첨 번호와 당첨금 정보를 가져옵니다."""
    url = "https://dhlottery.co.kr/gameResult.do?method=byWin"
    data = {'drwNo': draw_no}
    response = requests.post(url, data=data)

    if response.status_code != 200:
        return None

    return response.text



def parse_lotto_data(html):
    """HTML에서 당첨 번호와 당첨금 정보를 파싱합니다."""
    soup = BeautifulSoup(html, 'html.parser')
    result = {}

    # 당첨 번호 및 보너스 번호 추출
    numbers = soup.select('.ball_645')
    if numbers:
        result['winning_numbers'] = [int(num.text) for num in numbers[:6]]
        result['bonus_number'] = int(numbers[6].text)
    else:
        print("Winning numbers not found")
        return None

    # 기타 정보 추출
    draw_no_element = soup.select_one('.win_result h4 strong')
    if draw_no_element:
        result['draw_no'] = int(draw_no_element.text.split(' ')[0][:-1])
    draw_date_element = soup.select_one('.desc')
    if draw_date_element:
        date_match = re.search(r'(\d{4})년 (\d{1,2})월 (\d{1,2})일', draw_date_element.text)
        if date_match:
            draw_date = datetime.datetime.strptime(date_match.group(0), '%Y년 %m월 %d일').strftime('%Y/%m/%d')
            result['draw_date'] = draw_date
        else:
            print("Draw date format does not match")
            return None

    # 당첨금 정보 및 당첨 게임 수, 1게임당 당첨금액 추출
    prize_infos = soup.select('.tbl_data.tbl_data_col tbody tr')
    for info in prize_infos:
        cells = info.find_all('td')
        if cells:
            # 등수
            rank = cells[0].text.strip()
            # 당첨금액
            prize_amount = int(cells[1].text.strip().replace('원', '').replace(',', '').replace(' ', ''))
            # 당첨 게임 수
            winners_count = int(cells[2].text.strip().replace('게임', '').replace(',', '').replace(' ', ''))
            # 1게임당 당첨 금액 계산
            per_game_prize = prize_amount // winners_count if winners_count > 0 else 0

            # 결과 딕셔너리에 추가
            rank_key = 'rank_' + rank.replace('등', '')
            result[rank_key] = {
                'prize_amount': prize_amount,
                'winners_count': winners_count,
                'per_game_prize': per_game_prize
            }

    return result


def main():
    lotto_data_list = []

    # start , end
    for draw_no in range(1, 1108):
        html = fetch_lotto_data(draw_no)
        if html:
            parsed_data = parse_lotto_data(html)
            lotto_data_list.append(parsed_data)
            print(f"Data fetched for draw number: {draw_no}")
        else:
            print(f"Failed to fetch data for draw number: {draw_no}")
        time.sleep(0.5)

    # 결과를 JSON 파일로 저장
    with open('lotto_data.json', 'w', encoding='utf-8') as f:
        json.dump(lotto_data_list, f, ensure_ascii=False, indent=4)
    print("Lotto data saved to JSON file successfully.")


if __name__ == '__main__':
    main()
