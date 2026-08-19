#include "servo.h"
#include "config.h"
#include <ESP32Servo.h>

static Servo servoMotor;

namespace SmartSpray {

void ServoController::init() {
    servoMotor.attach(SERVO_PIN);
    servoMotor.write(DEFAULT_SERVO_ANGLE);
    _currentAngle = DEFAULT_SERVO_ANGLE;
    _initialized = true;
    Serial.println("INFO,SERVO_INIT,OK");
}

bool ServoController::isValidAngle(int angle) const {
    return angle >= MIN_SERVO_ANGLE && angle <= MAX_SERVO_ANGLE;
}

bool ServoController::setAngle(int angle) {
    if (!_initialized) return false;
    if (!isValidAngle(angle)) return false;

    servoMotor.write(angle);
    _currentAngle = angle;
    return true;
}

int ServoController::getAngle() const {
    return _currentAngle;
}

void ServoController::disable() {
    servoMotor.detach();
    _initialized = false;
}

} // namespace SmartSpray
