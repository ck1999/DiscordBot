FROM python:3.9
RUN pip install -U pip

COPY requirements.txt .

RUN pip install -r requirements.txt
RUN pip install git+https://github.com/iDevision/enhanced-discord.py

COPY . .
CMD [ "ls" ]