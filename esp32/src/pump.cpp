#include "pump.h"
#include "config.h"

namespace SmartSpray {

void PumpController::init() {
    pinMode(PUMP_PIN, OUTPUT);
    digitalWrite(PUMP_PIN, LOW);  // Pump OFF on boot — SAFETY CRITICAL
    _active = false;
    _initialized = true;
    Serial.println("INFO,PUMP_INIT,OK");
}

bool PumpController::isValidDuration(int durationMs) const {
    return durationMs >= MIN_PUMP_DURATION_MS && durationMs <= MAX_PUMP_DURATION_MS;
}

bool PumpController::activate(int durationMs) {
    if (!_initialized) return false;
    if (_active) return false;  // Already spraying — reject duplicate
    if (!isValidDuration(durationMs)) return false;

    digitalWrite(PUMP_PIN, HIGH);
    _active = true;
    _startTime = millis();
    _targetDuration = durationMs;
    return true;
}

void PumpController::stop() {
    digitalWrite(PUMP_PIN, LOW);
    _active = false;
    _startTime = 0;
    _targetDuration = 0;
}

void PumpController::update() {
    if (!_active) return;

    unsigned long elapsed = millis() - _startTime;

    // Auto-shutoff: target duration reached
    if (elapsed >= (unsigned long)_targetDuration) {
        stop();
        Serial.println("ACK,SPRAY_COMPLETED");
        return;
    }

    // SAFETY: absolute max duration enforcement
    // Even if _targetDuration was somehow corrupted, this catches it
    if (elapsed >= MAX_PUMP_DURATION_MS) {
        stop();
        Serial.println("ACK,ERROR,PUMP_TIMEOUT_SAFETY");
        return;
    }
}

bool PumpController::isActive() const {
    return _active;
}

unsigned long PumpController::getRuntime() const {
    if (!_active) return 0;
    return millis() - _startTime;
}

} // namespace SmartSpray
