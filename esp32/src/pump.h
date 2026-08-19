#ifndef PUMP_CTRL_H
#define PUMP_CTRL_H

#include <Arduino.h>

namespace SmartSpray {

class PumpController {
public:
    void init();
    bool activate(int durationMs);
    void stop();
    void update();  // Call in loop() for auto-shutoff
    bool isActive() const;
    unsigned long getRuntime() const;
    bool isValidDuration(int durationMs) const;

private:
    bool _active = false;
    unsigned long _startTime = 0;
    int _targetDuration = 0;
    bool _initialized = false;
};

} // namespace SmartSpray

#endif // PUMP_CTRL_H
