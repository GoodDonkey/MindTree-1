# init a base image
FROM python:3.8.12-buster

# install VIM
RUN apt-get update && apt-get install -y vim

# install default jvm
RUN apt-get install -y default-jdk

# define the present working directory
WORKDIR /MindTree

# copy the contents into the working dir
ADD . .

# dlib 설치시 이슈가 있어 미리 cmake를 설치해둔다.
RUN pip3 install cmake

# run pip to install the dependencies of the flask app
RUN pip3 install -r requirements.txt

## install py-hanspell
# run git clone to get py-hanspell
RUN git clone https://github.com/ssut/py-hanspell.git

# cp py-hanspell package
RUN cp -r py-hanspell/hanspell .
