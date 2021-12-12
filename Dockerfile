
# init a base image (Alpine is small Linux distro)
FROM python:3.8.12

# define the present working directory
WORKDIR /MindTree
# copy the contents into the working dir
ADD . /MindTree

# dlib 설치시 이슈가 있어 미리 cmake를 설치해둔다.
RUN pip3 install cmake

# run pip to install the dependencies of the flask app
RUN pip3 install -r requirements.txt

## py-hanspell이 conda나 pip로 안받아짐. 그래서 깃에서 직접 다운로드 후 설치한다.


# run git clone to get py-hanspell
RUN git clone https://github.com/ssut/py-hanspell.git /MindTree

# run setup.py to install py-hanspell
RUN python /py-hanspell/setup.py install
