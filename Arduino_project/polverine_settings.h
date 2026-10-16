#pragma once

// Matches POLVERINE_FULL_MQTT_DEMO/include/polverine_cfg.h.
// The BSEC profile (3.3 V, 3 seconds, 4 days) is selected at the top of Arduino_project.ino.
constexpr int BME690_SDA = 14;
constexpr int BME690_SCL = 21;
constexpr int BMV080_SCK = 12;
constexpr int BMV080_MISO = 13;
constexpr int BMV080_MOSI = 11;
constexpr int BMV080_CS = 10;
constexpr unsigned BMV080_CYCLE_SECONDS = 60;
constexpr unsigned TEMPERATURE_PROFILE = 0;
