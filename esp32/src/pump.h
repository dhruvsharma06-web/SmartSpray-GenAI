#ifndef PUMP_H
#define PUMP_H

#include <Arduino.h>

class PumpController {
public:
    void init();
    void start(uint32_t durationMs);
    void stop();
    void update();
    bool isActive() const;
    uint32_t runtimeMs() const;

private:
    bool _active = false;
    bool _estopActive = false;
    uint32_t _startTimeMs = 0;
    uint32_t _durationMs = 0;
};

#endif