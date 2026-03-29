import sqlite3
import paho.mqtt.client as mqtt
from datetime import datetime

# Create database
conn = sqlite3.connect("sensor_data.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS sensor_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id INTEGER,
    temperature REAL,
    error REAL,
    health REAL,
    timestamp TEXT
)
""")
conn.commit()

# MQTT settings
broker = "localhost"
port = 1883

sensor_values = {}

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker")
    client.subscribe("sensor/+/temp")
    client.subscribe("sensor/+/error")
    client.subscribe("sensor/+/health")

def on_message(client, userdata, msg):
    topic = msg.topic

    try:
        value = float(msg.payload.decode())
    except:
        return

    parts = topic.split("/")
    sensor_id = int(parts[1])
    data_type = parts[2]

    if sensor_id not in sensor_values:
        sensor_values[sensor_id] = {}

    sensor_values[sensor_id][data_type] = value

    if len(sensor_values[sensor_id]) == 3:
        temp = sensor_values[sensor_id]["temp"]
        error = sensor_values[sensor_id]["error"]
        health = sensor_values[sensor_id]["health"]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(
            "INSERT INTO sensor_data (sensor_id, temperature, error, health, timestamp) VALUES (?, ?, ?, ?, ?)",
            (sensor_id, temp, error, health, timestamp)
        )
        conn.commit()

        print(f"Stored -> Sensor {sensor_id}")

        sensor_values[sensor_id] = {}

client = mqtt.Client()
client.username_pw_set("root", "coreflux")
client.on_connect = on_connect
client.on_message = on_message

print("Logging data to database...")
client.connect(broker, port, 60)
client.loop_forever()