// Polverine serial JSON example — Mauro Riboni (@mauringo).
#include <Arduino.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <bsec3.h>
#include <config/bme690_profile.h>
#include "polverine_compensation.h"
Bsec3 sensor;
#ifdef USE_BMV080
#include <7Semi_BMV080.h>
BMV080_7Semi particulate;
bool pmReady = false;
#endif
bool ready = false;

void printJson(const JsonDocument &data) {
    serializeJson(data, Serial);
    Serial.println();
}

void status(const char *device, int code) {
    JsonDocument data;
    data["type"] = "status";
    data["device"] = device;
    data["code"] = code;
    printJson(data);
}

void onData(const bme69xData raw, const bsecOutputs outputs, const Bsec3) {
    if (!outputs.nOutputs) return;
    JsonDocument data;
    data["type"] = "bme690";
    data["time_ms"] = outputs.output[0].time_stamp / INT64_C(1000000);
    data["raw_temperature_c"] = raw.temperature;
    data["pressure_pa"] = raw.pressure;
    data["raw_humidity_pct"] = raw.humidity;
    data["gas_resistance_ohm"] = raw.gas_resistance;
    for (uint8_t i = 0; i < outputs.nOutputs; ++i) {
        const auto &o = outputs.output[i];
        switch (o.sensor_id) {
            case BSEC_OUTPUT_IAQ:
                data["iaq"] = o.signal;
                data["iaq_accuracy"] = o.accuracy;
                break;
            case BSEC_OUTPUT_SENSOR_HEAT_COMPENSATED_TEMPERATURE: data["temperature_c"] = o.signal; break;
            case BSEC_OUTPUT_SENSOR_HEAT_COMPENSATED_HUMIDITY: data["humidity_pct"] = o.signal; break;
            case BSEC_OUTPUT_STATIC_IAQ: data["static_iaq"] = o.signal; break;
            case BSEC_OUTPUT_CO2_EQUIVALENT: data["co2_equivalent_ppm"] = o.signal; break;
            case BSEC_OUTPUT_BREATH_VOC_EQUIVALENT: data["voc_equivalent_ppm"] = o.signal; break;
            case BSEC_OUTPUT_STABILIZATION_STATUS: data["stabilized"] = o.signal; break;
            case BSEC_OUTPUT_GAS_PERCENTAGE: data["gas_percentage"] = o.signal; break;
            case BSEC_OUTPUT_RUN_IN_STATUS: data["run_in"] = o.signal; break;
            default: break;
        }
    }
    printJson(data);
}

void setup() {
    Serial.begin(115200);
    const uint32_t start = millis();
    while (!Serial && millis() - start < 3000) delay(10);
    // 1. Start the board buses and BMV080 with the reference 30-second cycle.
    Wire.begin(BME690_SDA, BME690_SCL, 100000);
#ifdef USE_BMV080
    pmReady = particulate.begin(SPI, BMV080_CS, 1000000, BMV080_SCK, BMV080_MISO, BMV080_MOSI);
    if (pmReady) pmReady = particulate.setDutyCyclingPeriod(BMV080_CYCLE_SECONDS);
    if (pmReady) pmReady = particulate.startDutyCycling();
    status("bmv080", pmReady ? 0 : -1);
#endif
    // 2. Apply Polverine's BME690 profile and temperature compensation.
    ready = sensor.begin(BME69X_I2C_ADDR_LOW, Wire);
    if (ready) ready = sensor.setConfig(bsec3_profile_data, sizeof(bsec3_profile_data));
#ifdef USE_BMV080
    // Apply the board table only when its matching BMV080 heating mode is active.
    if (pmReady) sensor.setTemperatureOffsetCallback(polverineTemperatureOffset);
#endif
    // 3. Ask BSEC for the same IAQ outputs as the reference demo.
    bsecSensor outputs[] = {BSEC_OUTPUT_IAQ, BSEC_OUTPUT_RAW_TEMPERATURE,
        BSEC_OUTPUT_RAW_PRESSURE, BSEC_OUTPUT_RAW_HUMIDITY, BSEC_OUTPUT_RAW_GAS,
        BSEC_OUTPUT_STABILIZATION_STATUS, BSEC_OUTPUT_RUN_IN_STATUS,
        BSEC_OUTPUT_SENSOR_HEAT_COMPENSATED_TEMPERATURE,
        BSEC_OUTPUT_SENSOR_HEAT_COMPENSATED_HUMIDITY,
        BSEC_OUTPUT_STATIC_IAQ, BSEC_OUTPUT_CO2_EQUIVALENT, BSEC_OUTPUT_BREATH_VOC_EQUIVALENT,
        BSEC_OUTPUT_GAS_PERCENTAGE};
    if (ready) ready = sensor.updateSubscription(outputs, ARRAY_LEN(outputs), BSEC3_PROFILE_SAMPLE_RATE);
    sensor.attachCallback(onData);
    status("bme690", ready ? 0 : -1);
}

void loop() {
#ifdef USE_BMV080
    bmv080_output_t pm;
    if (pmReady && particulate.getSensorData(pm)) {
        JsonDocument data;
        data["type"] = "bmv080";
        data["time_ms"] = millis();
        data["cycle_seconds"] = BMV080_CYCLE_SECONDS;
        data["pm1_ug_m3"] = pm.pm1_mass_concentration;
        data["pm2_5_ug_m3"] = pm.pm2_5_mass_concentration;
        data["pm10_ug_m3"] = pm.pm10_mass_concentration;
        data["runtime_seconds"] = pm.runtime_in_sec;
        data["obstructed"] = particulate.isObstructed();
        data["out_of_range"] = particulate.isOutsideMeasurementRange();
        printJson(data);
    }
#endif
    if (ready && !sensor.run()) {
        status("bsec3", sensor.status);
        status("bme690", sensor.sensor.status);
        if (sensor.status < BSEC_OK || sensor.sensor.status < BME69X_OK) ready = false;
    }
    delay(10);
}
