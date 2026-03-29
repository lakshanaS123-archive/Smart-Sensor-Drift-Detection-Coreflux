import random
import time
import paho.mqtt.client as mqtt

print("Starting simulator...")

broker = "localhost"
port = 1883

try:
    client = mqtt.Client()
    client.username_pw_set("root", "coreflux")
    client.connect(broker, port, 60)
    client.loop_start()   # VERY IMPORTANT
    print("Connected to MQTT broker")
except Exception as e:
    print("MQTT Connection Failed:", e)
    exit()

def generate_temp():
    return round(random.uniform(24, 35), 2)

while True:
    print("Sending data...")
    for sensor_id in [1, 2, 3]:
        temp = generate_temp()
        reference = 28
        
        error = temp - reference
        health = 100 - abs(error * 10)

        client.publish(f"sensor/{sensor_id}/temp", temp, retain=True)
        client.publish(f"sensor/{sensor_id}/error", error, retain=True)
        client.publish(f"sensor/{sensor_id}/health", health, retain=True)

        print(f"Sensor {sensor_id}: Temp={temp}, Error={error}, Health={health}")

    print("---------------------------")
    time.sleep(5)