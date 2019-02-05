# Use an official Python runtime as a parent image
FROM python:3

# Copy the application directory contents into the container at /app
RUN mkdir -p /app

WORKDIR /app

COPY ./app ./

RUN pip install -r requirements.txt

# Run bot when the container launches
CMD ["/bin/sh", "-c", "python transmission_bot.py > /app/transmission_mgmt_bot.log 2>&1"]
