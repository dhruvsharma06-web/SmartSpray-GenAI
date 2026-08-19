#include "safety.h"
#include "config.h"
#include "pump.h"
#include "servo.h"

namespace SmartSpray {

// Static instance pointer for ISR
SafetyManager* SafetyManager::_instance = nullptr;

void IRAM_ATTR SafetyManager::_estopISR() {
    if (_instance) {
        _instance->_eStopped = true;
    }
}

void SafetyManager::init(PumpController* pump, ServoController* servo) {
    _pump = pump;
    _servo = servo;
    _eStopped = false;
    _instance = this;

    // E-stop pin: active LOW with internal pull-up
    pinMode(ESTOP_PIN, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(ESTOP_PIN), _estopISR, FALLING);

    // Check if e-stop is already pressed on boot
    if (digitalRead(ESTOP_PIN) == LOW) {
        _eStopped = true;
    }

    _lastCommandTime = millis();
    Serial.println("INFO,SAFETY_INIT,OK");
}

void SafetyManager::update() {
    // If e-stopped, ensure everything is shut down
    if (_eStopped) {
        if (_pump && _pump->isActive()) {
            _pump->stop();
            Serial.println("ACK,ESTOP_PUMP_KILLED");
        }
        return;
    }

    // Communication timeout: if no command in HEARTBEAT_TIMEOUT_MS, kill pump
    if (_pump && _pump->isActive()) {
        unsigned long timeSinceCommand = millis() - _lastCommandTime;
        if (timeSinceCommand > HEARTBEAT_TIMEOUT_MS) {
            _pump->stop();
            Serial.println("ACK,ERROR,COMM_TIMEOUT_SAFETY");
        }
    }
}

bool SafetyManager::isEmergencyStopped() const {
    return _eStopped;
}

void SafetyManager::emergencyStop() {
    _eStopped = true;
    if (_pump) _pump->stop();
    Serial.println("ACK,ESTOP_ACTIVATED");
}

void SafetyManager::resetEmergencyStop() {
    // Only reset if the physical button is released
    if (digitalRead(ESTOP_PIN) == HIGH) {
        _eStopped = false;
        Serial.println("ACK,ESTOP_RESET");
    } else {
        Serial.println("ACK,ERROR,ESTOP_STILL_PRESSED");
    }
}

bool SafetyManager::isSafeToSpray() const {
    if (_eStopped) return false;
    if (_pump && _pump->isActive()) return false;  // Already spraying
    return true;
}

unsigned long SafetyManager::getLastCommandTime() const {
    return _lastCommandTime;
}

void SafetyManager::recordCommand() {
    _lastCommandTime = millis();
}

} // namespace SmartSpray
