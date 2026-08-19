#ifndef SAFETY_H
#define SAFETY_H

#include <Arduino.h>

namespace SmartSpray {

// Forward declarations
class PumpController;
class ServoController;

class SafetyManager {
public:
    void init(PumpController* pump, ServoController* servo);
    void update();  // Call in loop()

    bool isEmergencyStopped() const;
    void emergencyStop();
    void resetEmergencyStop();

    bool isSafeToSpray() const;
    unsigned long getLastCommandTime() const;
    void recordCommand();

private:
    PumpController* _pump = nullptr;
    ServoController* _servo = nullptr;

    volatile bool _eStopped = false;
    unsigned long _lastCommandTime = 0;

    static void IRAM_ATTR _estopISR();
    static SafetyManager* _instance;  // For ISR access
};

} // namespace SmartSpray

#endif // SAFETY_H
