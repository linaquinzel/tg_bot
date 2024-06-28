# Start your image with a node base image
FROM python

# The /app directory should act as the main application directory
WORKDIR /tg_bot
ENV TG_TOKEN = 'your telegram token'

ENV HOST_REDIS 'redis_container'
ENV PORT_REDIS 6379
ENV PORT_MQTT 1883
ENV HOST_MQTT 'mqtt_container'
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY mqtt/mqtt.py ./
RUN chmod a+x mqtt.py
COPY subscriber/subscriber.py ./
RUN chmod a+x subscriber.py
COPY . .
CMD ["/bin/bash", "-c", "python main.py"]
