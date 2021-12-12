# init a base image (Alpine is small Linux distro)
FROM python:3.9-alpine
# define the present working directory
WORKDIR /MindTree
# copy the contents into the working dir
ADD . /MindTree

# run pip to install the dependencies of the flask app
RUN pip3 install -r requirements.txt

# run git clone to get py-hanspell
RUN git clone https://github.com/ssut/py-hanspell.git

# run setup.py to install py-hanspell
RUN python py-hanspell/setup.py install

# define the command to start the container
CMD ["python","app.py"]