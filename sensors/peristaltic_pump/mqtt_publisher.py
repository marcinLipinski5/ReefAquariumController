import os

from paho.mqtt import client as mqtt_client
import logging


class MqttPublisher:

    def __init__(self):
        self.__host = "127.0.0.1"
        self.__port = 1883
        self.__topic = "reefAquariumController/PeristalticPump"
        self.__client_id = 'ReefAquariumController'
        self.__username = os.getenv("MQTT_USERNAME", "user")
        self.__password = os.getenv("MQTT_PASSWORD", "password")

    def __connect_mqtt(self):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                logging.debug("Connected to MQTT Broker!")
            else:
                logging.error("Failed to connect, return code %d\n", rc)

        client = mqtt_client.Client(self.__client_id)
        client.username_pw_set(self.__username, self.__password)
        client.on_connect = on_connect
        client.connect(self.__host, self.__port)
        return client

    def __publish(self, client, message: str):
        msg_count = 1
        while True:
            result = client.publish(self.__topic, message)
            if result[0] == 0:
                logging.debug(f"Send: `{message}` to topic `{self.__topic}`")
            else:
                logging.error(f"Failed to send: {message} to topic {self.__topic}")
            msg_count += 1
            if msg_count > 5:
                break

    def send_message(self, message: str):
        client = self.__connect_mqtt()
        client.loop_start()
        self.__publish(client, message)
        client.loop_stop()
