#ifndef SERVO_CTRL_H
#define SERVO_CTRL_H

#include <Arduino.h>

namespace SmartSpray {

class ServoController {
public:
    void init();
    bool setAngle(int angle);
    int getAngle() const;
    bool isValidAngle(int angle) const;
    void disable();

private:
    int _currentAngle = -1;
    bool _initialized = false;
};

} // namespace SmartSpray

#endif // SERVO_CTRL_H
