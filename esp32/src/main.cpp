// ============================================================
// SmartSpray ESP32 Main
// ============================================================
// Firmware for handheld precision spraying system.
// Controls pump via serial commands from the backend.
// Safety is enforced independently of the host software.
// ============================================================

#include <Arduino.h>
#include "config.h"
#include "pump.h"
#include "safety.h"
#include "communication.h"

using namespace SmartSpray;

static PumpController pump;
static SafetyManager safety;
static CommandParser parser;

void setup() {
    Serial.begin(SERIAL_BAUD_RATE);
    while (!Serial) { delay(10); }

    Serial.println("=========================");
    Serial.print("SmartSpray FW ");
    Serial.println(FIRMWARE_VERSION);
    Serial.print("UID: ");
    Serial.println(DEVICE_UID);
    Serial.println("=========================");

    // Initialize subsystems — order matters
    pump.init();      // Pump OFF first (safety critical)
    safety.init(&pump);  // Safety monitors pump
    parser.init(&pump, &safety);  // Parser needs pump + safety

    Serial.println("INFO,BOOT_COMPLETE");
}

void loop() {
    // 1. Safety checks first (e-stop, comm timeout)
    safety.update();

    // 2. Pump auto-shutoff check
    pump.update();

    // 3. Process incoming serial commands
    parser.update();

    delay(LOOP_DELAY_MS);
}
