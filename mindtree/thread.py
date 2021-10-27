from concurrent import futures

from mindtree.modules.OCR import OCR
from mindtree.modules.sentiment_analysis import SentimentAnalysis
from mindtree.modules.text_analysis import TextAnalysis
from mindtree.utils.util import get_time_str

from mindtree import db
from mindtree.models import Post


class ThreadedAnalysis:
    def __init__(self):
        self._ocr = None
        self._text_analyzer = None
        self._sentiment_analyzer = None

        self.ocr = None
        self.text_analyzer = None
        self.sentiment_analyzer = None
        self.initialized = False

    def init_and_analyze(self, post_id: int):
        """main function"""
        self.init_analyzers()
        self.analysis(post_id)

    def is_initialized(self):
        print(f"{get_time_str()} is worker initialied? ----- {self.initialized}")
        return self.initialized

    def init_analyzers(self):
        with futures.ThreadPoolExecutor() as executor:
            # 각 객체를 초기화한다.
            self._ocr = executor.submit(OCR)
            self._text_analyzer = executor.submit(TextAnalysis)
            self._sentiment_analyzer = executor.submit(SentimentAnalysis)

            if futures.wait([self._ocr, self._text_analyzer, self._sentiment_analyzer]):
                """ 세 futures 객체가 일을 마칠때 까지 기다린다. 
                    실제로 위 wait 메서드의 return 값은 각 객체가 일을 마칠때 까지 반환되지 않기 때문에,
                    if 문으로 바로 검증되지 않고 wait()가 return 될때까지 기다린다. 
                    True가 리턴되면 아래와 같이 각 분석 객체를 변수에 담는다."""

                self.ocr = self._ocr.result()
                self.text_analyzer = self._text_analyzer.result()
                self.sentiment_analyzer = self._sentiment_analyzer.result()

                print("[init_analyzers] initialization 완료")
                self.initialized = True

            return self

    def analysis(self, post_id):
        print("thread.analysis", post_id)
        with futures.ThreadPoolExecutor() as executor:
            # 1. OCR 시작. 끝날때까지 기다린다.
            f1_m = executor.submit(self.ocr.ocr_main, post_id)
            futures.wait([f1_m])

            # 1-2. 완료 로그찍기
            if f1_m.done():
                print("f1_m 완료")
            else:
                print("f1_m 오류발생")
                f1_m.cancel()

            # 2. 감성분석, 텍스트 분석 모두 실행.
            f2_m = executor.submit(self.text_analyzer.text_analysis, post_id)
            f3_m = executor.submit(self.sentiment_analyzer.sentiment_analysis, post_id)

            # 2-2. 완료되면 로그찍기
            i = 2
            for f in futures.as_completed([f2_m, f3_m]):
                if f.done():
                    print(i, "완료")
                    i += 1
                    continue
                else:
                    f.cancel()

        # 분석이 끝난 후 db에 완료 했음을 저장.
        post = Post.query.get(post_id)
        post.completed = True
        db.session.commit()


if __name__ == '__main__':
    pass
