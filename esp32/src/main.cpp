#include <Arduino.h>
#include "config.h"

const uint32_t MAX_SPRAY_DURATION_MS = 30000UL;
const char FW_VERSION[] = "0.2.0";

bool pumpOn = false;
bool estopActive = false;
bool sprayActive = false;
uint32_t sprayStartMs = 0;
uint32_t sprayDurationMs = 0;

void setPumpState(bool on) {
  digitalWrite(PUMP_PIN, on ? HIGH : LOW);
  pumpOn = on;
}

void stopSpray(bool sendSprayStoppedAck) {
  sprayActive = false;
  sprayStartMs = 0;
  sprayDurationMs = 0;
  setPumpState(false);

  if (sendSprayStoppedAck) {
    Serial.println("ACK,SPRAY_STOPPED");
  }
}

void sendStatus() {
  uint32_t runtimeMs = 0;
  if (sprayActive) {
    runtimeMs = millis() - sprayStartMs;
  }

  Serial.print("STATUS,OK,PUMP,");
  Serial.print(pumpOn ? "ON" : "OFF");
  Serial.print(",RUNTIME,");
  Serial.print(runtimeMs);
  Serial.print(",FW,");
  Serial.println(FW_VERSION);
}

bool parseDurationValue(const String &rawValue, uint32_t &durationMs) {
  String value = rawValue;

  if (value.length() == 0 || value.indexOf(',') >= 0) {
    return false;
  }

  value.trim();
  if (value.length() == 0) {
    return false;
  }

  if (value.startsWith("+")) {
    value = value.substring(1);
  }

  if (value.length() == 0) {
    return false;
  }

  for (uint16_t i = 0; i < value.length(); ++i) {
    if (!isDigit(value.charAt(i))) {
      return false;
    }
  }

  durationMs = value.toInt();
  return true;
}

void handleSprayCommand(const String &command) {
  if (estopActive) {
    Serial.println("ACK,ERROR,ESTOP_ACTIVE");
    return;
  }

  if (!command.startsWith("SPRAY,")) {
    Serial.println("ACK,ERROR,MALFORMED_COMMAND");
    return;
  }

  String rawDuration = command.substring(6);
  rawDuration.trim();

  if (rawDuration.length() == 0 || rawDuration.indexOf(',') >= 0) {
    Serial.println("ACK,ERROR,MALFORMED_COMMAND");
    return;
  }

  uint32_t durationMs = 0;
  if (!parseDurationValue(rawDuration, durationMs)) {
    Serial.println("ACK,ERROR,MALFORMED_COMMAND");
    return;
  }

  if (durationMs == 0 || durationMs > MAX_SPRAY_DURATION_MS) {
    Serial.print("ACK,ERROR,INVALID_DURATION,");
    Serial.println(durationMs);
    return;
  }

  sprayActive = true;
  sprayStartMs = millis();
  sprayDurationMs = durationMs;
  setPumpState(true);

  Serial.print("ACK,SPRAY_STARTED,");
  Serial.println(durationMs);
}

void setup() {
  pinMode(PUMP_PIN, OUTPUT);
  setPumpState(false);

  Serial.begin(115200);
  Serial.println("READY");
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command.length() == 0) {
      return;
    }

    if (command == "STATUS") {
      sendStatus();
    } else if (command == "STOP") {
      stopSpray(false);
      Serial.println("ACK,STOPPED");
    } else if (command == "ESTOP") {
      stopSpray(false);
      estopActive = true;
      Serial.println("ACK,ESTOP_ACTIVATED");
    } else if (command == "RESET_ESTOP") {
      estopActive = false;
      setPumpState(false);
      sprayActive = false;
      sprayStartMs = 0;
      sprayDurationMs = 0;
      Serial.println("ACK,ESTOP_RESET");
    } else if (command.startsWith("SPRAY")) {
      handleSprayCommand(command);
    } else {
      Serial.println("ACK,ERROR,UNKNOWN_COMMAND");
    }
  }

  if (sprayActive && (millis() - sprayStartMs >= sprayDurationMs)) {
    stopSpray(true);
  }
}
