#include <cassert>
#include <cmath>
#include <initializer_list>
#include "polverine_compensation.h"

int main() {
    // Wi-Fi/MQTT reference: client 0, 60-second BMV080 cycle -> cfg2.
    assert(TEMPERATURE_PROFILE == 0 && BMV080_CYCLE_SECONDS == 60);
    assert(std::fabs(polverineReferenceTemperatureOffset(0) - 3.62f) < 0.0001f);
    assert(std::fabs(polverineReferenceTemperatureOffset(20) - 5.26f) < 0.0001f);
    assert(std::fabs(polverineReferenceTemperatureOffset(40) - 5.902f) < 0.0001f);
    assert(std::fabs(polverineReferenceTemperatureOffset(60) - 10.8f) < 0.001f);
    assert(std::fabs(polverineReferenceTemperatureOffset(80) - 12.91f) < 0.0001f);
    assert(polverineReferenceTemperatureOffset(-46) == 0);
    assert(polverineReferenceTemperatureOffset(86) == 0);
    // Shared endpoints keep the first matching reference row.
    assert(std::fabs(polverineReferenceTemperatureOffset(15) - 3.62f) < 0.0001f);
    assert(std::fabs(polverineReferenceTemperatureOffset(28) -
        (-21.3f + 2.84f*28 - 0.108f*28*28 + 0.00137f*28*28*28 + 2)) < 0.0001f);
    assert(std::fabs(polverineReferenceTemperatureOffset(50) - (2.93f + 0.0243f*50 + 2)) < 0.0001f);
    // Calibration adds 14 C to the heat input, rather than altering JSON afterward.
    assert(TEMPERATURE_CALIBRATION_EXTRA_C == 14.0f);
    for (float raw : {0.0f, 20.0f, 40.0f, 60.0f, 80.0f}) {
        assert(std::fabs(polverineTemperatureOffset(raw) -
            polverineReferenceTemperatureOffset(raw) - 14.0f) < 0.0001f);
    }
    assert(polverineTemperatureOffset(-46) == 0);
    assert(polverineTemperatureOffset(86) == 0);
}
