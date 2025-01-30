#include "Wire.h"
#include "Adafruit_MPRLS.h"

unsigned long previousTime = 0;      // Store the last time the loop executed
const unsigned long interval = 10;   // 10 ms delay

// --------------------------------------- Pressure Sensors --------------------------------------
#define PCAADDR 0x70
#define RESET_PIN  -1
#define EOC_PIN    -1

Adafruit_MPRLS mpr_sensors[8];       // Array for each sensor instance
float sensor_offsets[8];             // Calibration offsets for each sensor

unsigned long startTime;
bool calibration_complete = false;

// --------------------------------------- Actuators --------------------------------------
int solenoidPins[12] = {13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2};

// PCA9548A channels: Using all 8 channels (0 to 7)
uint8_t sensor_channels[8] = {0, 1, 2, 3, 4, 5, 6, 7};

void pcaselect(uint8_t i) {
  if (i > 7) return;  // Ensure channel index is within range
  Wire.beginTransmission(PCAADDR);
  Wire.write(1 << i);
  Wire.endTransmission();  
}

void setup() {
  Serial.begin(115200);
  while (!Serial);
  delay(1000);

  Wire.begin();
  Serial.println("Starting sensor calibration...");

  startTime = millis();

  for (uint8_t t = 0; t < 8; t++) {
    pcaselect(sensor_channels[t]);
    if (!mpr_sensors[t].begin()) {
      Serial.print("Failed to find MPRLS sensor on channel ");
      Serial.println(sensor_channels[t]);
    } else {
      Serial.print("Found MPRLS sensor on channel ");
      Serial.println(sensor_channels[t]);
      sensor_offsets[t] = mpr_sensors[t].readPressure();
      Serial.print("Calibrating sensor on channel "); 
      Serial.print(sensor_channels[t]);
      Serial.print(", Offset: "); 
      Serial.println(sensor_offsets[t]);
    }
  }
  Serial.println("Calibration complete.");
  calibration_complete = true;

  for (uint8_t i = 0; i < 12; i++) {
    pinMode(solenoidPins[i], OUTPUT);
  }
}

void loop() {
  unsigned long currentTime = millis();
  if (currentTime - previousTime >= interval) {
    previousTime = currentTime;  // Update the last executed time

    // ------------------------- Actuators ------------------------------------
    if (Serial.available() > 0) {
      String input = Serial.readStringUntil('\n');
      input.trim();

      // Process binary string for valve control
      if (input.length() == 12) { // Expect a 12-bit binary string
          bool isValid = true;

          // Validate the binary string contains only '0' or '1'
          for (char c : input) {
            if (c != '0' && c != '1') {
              isValid = false;
              break;
            }
          }

          if (isValid) {
              // Update valve states based on the binary string
              for (uint8_t i = 0; i < 12; i++) {
                  bool state = (input[i] == '1');
                  digitalWrite(solenoidPins[i], state ? HIGH : LOW);
              }
              Serial.println("Updated valve states from binary string.");
          } else {
              Serial.println("Invalid binary string received.");
          }
      } else {
          Serial.println("Invalid input length received.");
      }
    }

    // ------------------- Send sensor data to Pi --------------------------------
    if (!calibration_complete) {
      return;
    }

    unsigned long loopCurrentTime = millis() - startTime;

    Serial.print(loopCurrentTime);
    Serial.print(",");

    float veab_sensor = 0.0;  // Placeholder for VEAB sensor data
    Serial.print(veab_sensor);
    Serial.print(",");

    for (uint8_t t = 0; t < 8; t++) {
      pcaselect(sensor_channels[t]);
      float pressure_hPa = mpr_sensors[t].readPressure();
      float calibrated_pressure = (pressure_hPa - sensor_offsets[t]) * 100;

      Serial.print(calibrated_pressure);
      if (t < 7) Serial.print(",");
    }

    Serial.println();
  }
}
