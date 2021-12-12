import json
import os

import requests

from mindtree import APP_PATH, db
from mindtree.models import Post, SeriesPost
from mindtree.utils.DTO import PathDTO
from mindtree.utils.util import get_time_str

import pandas as pd
import matplotlib.pyplot as plt

# matplotlib을 서버 상에서 사용할 때 GUI 사용 관련 에러가 날 수 있으므로 아래의 옵션을 설정해준다.
plt.switch_backend('Agg')

key_path = os.path.join(APP_PATH, "key", "keys.json")
with open(key_path, "r") as keys:
    n_key = json.load(keys)


class SentimentAnalysis(PathDTO):
    # Naver sentiment API 요청 정보
    url = 'https://naveropenapi.apigw.ntruss.com/sentiment-analysis/v1/analyze'

    headers = {'X-NCP-APIGW-API-KEY-ID': n_key["NAVER_API_KEY_ID"],
               'X-NCP-APIGW-API-KEY': n_key["NAVER_API_KEY"],
               'Content-Type': 'application/json; charset=utf-8'
               }

    def __init__(self):
        # 빈 경로 변수 설정
        self.text_path = ''
        self.sentiment_path = ''

        # ocr 텍스트 파일
        self.ocr_text_data = ''

        self.res = ''  # post 요청 후 반응 객체
        self.json_response = ''  # response 객체의 json 데이터
        print(get_time_str(), "SentimentAnalysis initialized...")

    def sentiment_analysis(self, post_id):
    
        print("[sentiment_analysis] post_id: ", post_id)
        # 경로를 설정한다.
        self.text_path = super().get_user_ocr_file_path(post_id)  # 굳이 안해도됨. DB에 저장되어 있기 때문.
        self.sentiment_path = super().get_user_sentiment_path(post_id)

        # ocr text db에서 가져오기
        ocr_text = Post.query.get(post_id).ocr_text
        self.ocr_text_data = ocr_text

        if self._request():  # _request() 실패시 결과를 저장하지 않는다.
            self._save_response(post_id)
            self._create_stacked_bar_chart(post_id)

    def sentiment_analysis_series(self, series_post_id):
        self.ocr_text_data = SeriesPost.query.get(series_post_id).ocr_text_bulk

        if self._request():  # _request() 실패시 결과를 저장하지 않는다.
            self._save_response_series(series_post_id)
            # self.make_stacked_bar_chart(series_post_id)
        else:
            print('[sentiment_analysis_series] 요청 에러')

    def _request(self):
        self.res = requests.post(url=self.url,
                                 headers=self.headers,
                                 json={"content": self.ocr_text_data}
                                 )
        if self.res.json():
            self.json_response = self.res.json()
        else:
            print('[_request] self.res.json() == None....')

        if self.res.status_code == 200:
            return self.json_response
        else:
            print(f"{get_time_str()} SentimentAnalysis: request error! {self.res.status_code}")
            return None

    def _save_response(self, post_id):
        # sentiment 로컬 저장
        with open(self.sentiment_path, "w", encoding='utf-8') as f:
            json.dump(self.json_response, f, indent='\t', ensure_ascii=False)
            print(get_time_str(), "SentimentAnalysis: 감성분석 저장 완료")

        # sentiment DB 저장
        post = Post.query.get_or_404(post_id)
        post.sentiment = self.json_response
        db.session.commit()

    def _save_response_series(self, post_id):
        # sentiment DB 저장
        series_post = SeriesPost.query.get_or_404(post_id)
        series_post.sentiment = self.json_response
        db.session.commit()

    def _create_stacked_bar_chart(self, post_id):
        # 스택바 이미지 크기 설정
        plt.rcParams["figure.figsize"] = [7.50, 3.50]

        # 데이터 준비
        negative_ratio = self.json_response["document"]["confidence"]["negative"]
        positive_ratio = self.json_response["document"]["confidence"]["positive"]
        neutral_ratio = self.json_response["document"]["confidence"]["neutral"]
        emotion = ['emotion']

        # 그래프 생성
        df = pd.DataFrame({'negative_ratio': negative_ratio, 'positive_ratio': positive_ratio, 'neutral_ratio':neutral_ratio}, index=emotion)
        ax = df.plot.barh(stacked=True, color={'negative_ratio': 'red', 'positive_ratio': 'blue', 'neutral_ratio': 'gray'})
        ax.get_legend().remove() # 범례 제거
        plt.axis('off') # tic 제거

        # 이미지 저장
        # transparent = True 이 옵션은 이미지 저장할 때 배경을 투명으로 저장하겠다는 옵션
        plt.savefig(os.path.join(super().get_user_media_path(post_id), super().get_user_stacked_bar_chart_file_name(post_id)), transparent = True)


if __name__ == '__main__':
    """ 유닛 테스트 방법:
        MindTree (루트경로에서) 
        $ python mindtree/modules/sentiment_analysis.py  """
    sa = SentimentAnalysis()
    # sa.sentiment_analysis(2)
    # sa._create_stacked_bar_chart(13)
