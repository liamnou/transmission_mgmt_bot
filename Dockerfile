# Use an official Python runtime as a parent image
FROM python:3.8

WORKDIR /app

COPY ./app/requirements.txt ./

RUN pip install -r requirements.txt

COPY ./app ./

# Run bot when the container launches
CMD ["python", "transmission_bot.py"]
