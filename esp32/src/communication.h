#ifndef COMMUNICATION_H
#define COMMUNICATION_H

#include <Arduino.h>

namespace SmartSpray {

// Forward declarations
class ServoController;
class PumpController;
class SafetyManager;

enum class CommandType {
    SPRAY,
    STOP,
    STATUS,
    ESTOP,
    RESET_ESTOP,
    UNKNOWN,
    INVALID
};

struct ParsedCommand {
    CommandType type = CommandType::UNKNOWN;
    int servoAngle = 0;
    int durationMs = 0;
};

class CommandParser {
public:
    void init(ServoController* servo, PumpController* pump, SafetyManager* safety);
    void update();  // Call in loop() to check for serial data

private:
    ServoController* _servo = nullptr;
    PumpController* _pump = nullptr;
    SafetyManager* _safety = nullptr;

    char _buffer[64];
    int _bufferIndex = 0;

    ParsedCommand parseCommand(const char* line);
    void executeCommand(const ParsedCommand& cmd);
    void sendStatus();
};

} // namespace SmartSpray

#endif // COMMUNICATION_H
