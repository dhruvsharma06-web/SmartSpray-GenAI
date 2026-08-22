#include "pump.h"
#include "config.h"

void PumpController::init() {
    pinMode(PUMP_PIN, OUTPUT);
    digitalWrite(PUMP_PIN, LOW);
    _active = false;
    _estopActive = false;
    _startTimeMs = 0;
    _durationMs = 0;
}

void PumpController::start(uint32_t durationMs) {
    if (_estopActive || durationMs == 0) {
        return;
    }

    _active = true;
    _startTimeMs = millis();
    _durationMs = durationMs;
    digitalWrite(PUMP_PIN, HIGH);
}

void PumpController::stop() {
    _active = false;
    _startTimeMs = 0;
    _durationMs = 0;
    digitalWrite(PUMP_PIN, LOW);
}

void PumpController::update() {
    if (!_active) {
        return;
    }

    if (millis() - _startTimeMs >= _durationMs) {
        stop();
    }
}

bool PumpController::isActive() const {
    return _active;
}

uint32_t PumpController::runtimeMs() const {
    if (!_active) {
        return 0;
    }

    return millis() - _startTimeMs;
}
