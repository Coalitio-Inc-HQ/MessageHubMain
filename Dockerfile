FROM python:3.12
RUN mkdir /app
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN chmod a+x *.sh
CMD ["bash","app.sh"]