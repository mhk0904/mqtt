#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random
import time
import paho.mqtt.client as mqtt_client
import RPi.GPIO as GPIO 
import time
TRIG_PIN = 20 
ECHO_PIN = 21

def initUltrasonic():
    GPIO.setup(TRIG_PIN, GPIO.OUT)
    GPIO.setup(ECHO_PIN, GPIO.IN)

def controlUltrasonic():
    distance = 0.0
    GPIO.output(TRIG_PIN, False)
    time.sleep(0.5)
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, False)
    
    while GPIO.input(ECHO_PIN) == 0 :
        pulse_start = time.time()
    while GPIO.input(ECHO_PIN) == 1 :
        pulse_end = time.time()
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17000
    distance = round(distance, 2)
    return distance

# broker 정보 #1
broker_address = "localhost"
broker_port = 1883

topic = "/python/mqtt"

def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker")
        else:
            print(f"Failed to connect, Returned code: {rc}")

    def on_disconnect(client, userdata, flags, rc=0):
        print(f"disconnected result code {str(rc)}")

    def on_log(client, userdata, level, buf):
        print(f"log: {buf}")

    # client 생성 #2
    client_id = f"mqtt_client_{random.randint(0, 1000)}"
    client = mqtt_client.Client(client_id)

    # 콜백 함수 설정 #3
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_log = on_log

    # broker 연결 #4
    client.connect(host=broker_address, port=broker_port)
    return client

def publish(client: mqtt_client):
    GPIO.setmode(GPIO.BCM)                      # GPIO 모드 설정
    distance = 0.0                              # 거리 변수 설정
    initUltrasonic()                            # 초음파 센서 초기화
    print("Ultrasonic Operating ...")

    while True:
        time.sleep(1)
        distance = controlUltrasonic()
        msg = f"messages: {distance}"
        result = client.publish(topic, msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send `{distance}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")

def run():
    client = connect_mqtt()
    client.loop_start() #5
    print(f"connect to broker {broker_address}:{broker_port}")
    publish(client) #6

if __name__ == '__main__':
    run()