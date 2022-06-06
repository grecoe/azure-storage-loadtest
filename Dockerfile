# Python seems to be included in this image, but having two FROM lines
# side by side seemed to be an issue. 

FROM python:3.9

RUN mkdir /app
WORKDIR /app
ADD requirements.txt /app/
RUN pip install -r requirements.txt
ADD . /app/

ENTRYPOINT [ "python" ]
CMD [ "executemove.py" ]