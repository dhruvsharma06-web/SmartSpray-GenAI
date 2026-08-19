#include "communication.h"
#include "config.h"
#include "servo.h"
#include "pump.h"
#include "safety.h"
#include <string.h>
#include <stdlib.h>

namespace SmartSpray {

void CommandParser::init(ServoController* servo, PumpController* pump, SafetyManager* safety) {
    _servo = servo;
    _pump = pump;
    _safety = safety;
    _bufferIndex = 0;
    memset(_buffer, 0, sizeof(_buffer));
    Serial.println("INFO,COMM_INIT,OK");
}

void CommandParser::update() {
    while (Serial.available()) {
        char c = Serial.read();

        // End of command (newline or carriage return)
        if (c == '\n' || c == '\r') {
            if (_bufferIndex > 0) {
                _buffer[_bufferIndex] = '\0';

                ParsedCommand cmd = parseCommand(_buffer);
                _safety->recordCommand();
                executeCommand(cmd);

                _bufferIndex = 0;
                memset(_buffer, 0, sizeof(_buffer));
            }
            continue;
        }

        // Buffer overflow protection
        if (_bufferIndex < SERIAL_BUFFER_SIZE - 1) {
            _buffer[_bufferIndex++] = c;
        } else {
            // Buffer overflow — reset and report error
            _bufferIndex = 0;
            memset(_buffer, 0, sizeof(_buffer));
            Serial.println("ACK,ERROR,BUFFER_OVERFLOW");
        }
    }
}

ParsedCommand CommandParser::parseCommand(const char* line) {
    ParsedCommand cmd;

    // STOP command
    if (strcmp(line, "STOP") == 0) {
        cmd.type = CommandType::STOP;
        return cmd;
    }

    // STATUS command
    if (strcmp(line, "STATUS") == 0) {
        cmd.type = CommandType::STATUS;
        return cmd;
    }

    // ESTOP command
    if (strcmp(line, "ESTOP") == 0) {
        cmd.type = CommandType::ESTOP;
        return cmd;
    }

    // RESET_ESTOP command
    if (strcmp(line, "RESET_ESTOP") == 0) {
        cmd.type = CommandType::RESET_ESTOP;
        return cmd;
    }

    // SPRAY,<angle>,<duration> command
    if (strncmp(line, "SPRAY,", 6) == 0) {
        // Parse angle
        const char* angleStr = line + 6;
        char* commaPos = strchr(angleStr, ',');
        if (commaPos == nullptr) {
            cmd.type = CommandType::INVALID;
            return cmd;
        }

        // Extract angle
        char angleBuf[8];
        int angleLen = commaPos - angleStr;
        if (angleLen <= 0 || angleLen >= 8) {
            cmd.type = CommandType::INVALID;
            return cmd;
        }
        strncpy(angleBuf, angleStr, angleLen);
        angleBuf[angleLen] = '\0';
        cmd.servoAngle = atoi(angleBuf);

        // Extract duration
        const char* durationStr = commaPos + 1;
        if (strlen(durationStr) == 0) {
            cmd.type = CommandType::INVALID;
            return cmd;
        }
        cmd.durationMs = atoi(durationStr);

        cmd.type = CommandType::SPRAY;
        return cmd;
    }

    // Unknown command
    cmd.type = CommandType::UNKNOWN;
    return cmd;
}

void CommandParser::executeCommand(const ParsedCommand& cmd) {
    switch (cmd.type) {

        case CommandType::ESTOP:
            _safety->emergencyStop();
            // ACK sent inside emergencyStop()
            return;

        case CommandType::RESET_ESTOP:
            _safety->resetEmergencyStop();
            return;

        case CommandType::STOP:
            if (_pump->isActive()) {
                _pump->stop();
            }
            Serial.println("ACK,STOPPED");
            return;

        case CommandType::STATUS:
            sendStatus();
            return;

        case CommandType::SPRAY: {
            // Check e-stop first
            if (_safety->isEmergencyStopped()) {
                Serial.println("ACK,ERROR,ESTOP_ACTIVE");
                return;
            }

            // Check if safe to spray
            if (!_safety->isSafeToSpray()) {
                Serial.println("ACK,ERROR,NOT_SAFE");
                return;
            }

            // Validate servo angle
            if (!_servo->isValidAngle(cmd.servoAngle)) {
                Serial.print("ACK,ERROR,INVALID_ANGLE,");
                Serial.println(cmd.servoAngle);
                return;
            }

            // Validate pump duration
            if (!_pump->isValidDuration(cmd.durationMs)) {
                Serial.print("ACK,ERROR,INVALID_DURATION,");
                Serial.println(cmd.durationMs);
                return;
            }

            // Set servo angle
            if (!_servo->setAngle(cmd.servoAngle)) {
                Serial.println("ACK,ERROR,SERVO_FAIL");
                return;
            }

            // Small delay for servo to reach position
            delay(200);

            // Activate pump
            if (!_pump->activate(cmd.durationMs)) {
                Serial.println("ACK,ERROR,PUMP_FAIL");
                return;
            }

            Serial.print("ACK,SPRAY_STARTED,");
            Serial.print(cmd.servoAngle);
            Serial.print(",");
            Serial.println(cmd.durationMs);
            return;
        }

        case CommandType::INVALID:
            Serial.println("ACK,ERROR,MALFORMED_COMMAND");
            return;

        case CommandType::UNKNOWN:
        default:
            Serial.println("ACK,ERROR,UNKNOWN_COMMAND");
            return;
    }
}

void CommandParser::sendStatus() {
    Serial.print("STATUS,");
    Serial.print(_safety->isEmergencyStopped() ? "ESTOP" : "OK");
    Serial.print(",SERVO,");
    Serial.print(_servo->getAngle());
    Serial.print(",PUMP,");
    Serial.print(_pump->isActive() ? "ON" : "OFF");
    Serial.print(",RUNTIME,");
    Serial.print(_pump->getRuntime());
    Serial.print(",FW,");
    Serial.println(FIRMWARE_VERSION);
}

} // namespace SmartSpray
