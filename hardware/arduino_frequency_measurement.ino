#include <WiFi.h>
#include <PubSubClient.h>
#include "config.h"  // WiFi/MQTT credentials — see config.h.example

// === WiFi & MQTT Settings (loaded from config.h) ===
const char* ssid = WIFI_SSID;
const char* password = WIFI_PASSWORD;
const char* mqtt_server = MQTT_SERVER;
const int mqtt_port = MQTT_PORT;
const char* mqtt_topic = MQTT_TOPIC;

WiFiClient espClient;
PubSubClient client(espClient);

#define SENSOR_PIN 34
#define NUM_SAMPLES 400
#define ADC_MIDPOINT 2048
#define VOLTAGE_SCALING 0.5
#define CYCLES_TO_MEASURE 10

float frequency = 0;

// === Timing control ===
unsigned long lastMeasurementTime = 0;
const unsigned long measurementInterval = 60000; // 60 seconds

void setup_wifi() {
  delay(10);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
}

void reconnect() {
  while (!client.connected()) {
    if (client.connect(MQTT_CLIENT_ID)) {
      // Reconnected
    } else {
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long currentTime = millis();
  if (currentTime - lastMeasurementTime >= measurementInterval) {
    lastMeasurementTime = currentTime;

    float sumSquares = 0;
    int zeroCrossCount = 0;
    int lastVal = analogRead(SENSOR_PIN);
    unsigned long firstZeroTime = 0;
    unsigned long lastZeroTime = 0;

    for (int i = 0; i < NUM_SAMPLES; i++) {
      int val = analogRead(SENSOR_PIN);
      float centered = val - ADC_MIDPOINT;
      sumSquares += centered * centered;

      if (val < ADC_MIDPOINT && lastVal >= ADC_MIDPOINT) {
        zeroCrossCount++;
        if (zeroCrossCount == 1) {
          firstZeroTime = micros();
        }
        if (zeroCrossCount == CYCLES_TO_MEASURE + 1) {
          lastZeroTime = micros();
          break;
        }
      }
      lastVal = val;
      delayMicroseconds(500);
    }

    float rms = sqrt(sumSquares / NUM_SAMPLES);
    float voltage = rms * VOLTAGE_SCALING;

    if (zeroCrossCount >= CYCLES_TO_MEASURE + 1) {
      float timeElapsed = (lastZeroTime - firstZeroTime) / 1000000.0;
      frequency = CYCLES_TO_MEASURE / timeElapsed;
    }

    Serial.print("RMS Voltage: ");
    Serial.print(voltage, 2);
    Serial.print(" V\tFrequency: ");
    Serial.print(frequency, 2);
    Serial.println(" Hz");

    String payload = "{\"voltage\": ";
    payload += voltage;
    payload += ", \"frequency\": ";
    payload += frequency;
    payload += ", \"timestamp\": ";
    payload += millis();
    payload += "}";

    client.publish(mqtt_topic, payload.c_str());
  }
}
