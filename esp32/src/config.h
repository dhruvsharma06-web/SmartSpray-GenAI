#ifndef CONFIG_H
#define CONFIG_H

// ============================================================
// SmartSpray ESP32 Configuration
// ============================================================

// --- Firmware ---
#define FIRMWARE_VERSION "0.1.0"
#define DEVICE_UID "smartspray-001"

// --- Serial ---
#define SERIAL_BAUD_RATE 115200
#define COMMAND_TIMEOUT_MS 5000
#define SERIAL_BUFFER_SIZE 64

// --- Pin Definitions ---
#define SERVO_PIN 13
#define PUMP_PIN 12
#define ESTOP_PIN 14  // Physical emergency stop button (active LOW, pull-up)

// --- Servo Limits ---
#define MIN_SERVO_ANGLE 20
#define MAX_SERVO_ANGLE 160
#define DEFAULT_SERVO_ANGLE 90

// --- Pump Safety ---
#define MAX_PUMP_DURATION_MS 3000
#define MIN_PUMP_DURATION_MS 100

// --- Timing ---
#define LOOP_DELAY_MS 10
#define STATUS_INTERVAL_MS 1000
#define HEARTBEAT_TIMEOUT_MS 10000

#endif // CONFIG_H
