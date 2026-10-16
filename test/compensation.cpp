#include <cassert>
#include <cmath>
#include "polverine_compensation.h"

int main() {
    // Wi-Fi/MQTT reference: client 0, 60-second BMV080 cycle -> cfg2.
    assert(TEMPERATURE_PROFILE == 0 && BMV080_CYCLE_SECONDS == 60);
    assert(std::fabs(polverineTemperatureOffset(0) - 3.62f) < 0.0001f);
    assert(std::fabs(polverineTemperatureOffset(20) - 5.26f) < 0.0001f);
    assert(std::fabs(polverineTemperatureOffset(40) - 5.902f) < 0.0001f);
    assert(std::fabs(polverineTemperatureOffset(60) - 10.8f) < 0.001f);
    assert(std::fabs(polverineTemperatureOffset(80) - 12.91f) < 0.0001f);
    assert(polverineTemperatureOffset(-46) == 0);
    assert(polverineTemperatureOffset(86) == 0);
    // Shared endpoints keep the first matching reference row.
    assert(std::fabs(polverineTemperatureOffset(15) - 3.62f) < 0.0001f);
    assert(std::fabs(polverineTemperatureOffset(28) -
        (-21.3f + 2.84f*28 - 0.108f*28*28 + 0.00137f*28*28*28 + 2)) < 0.0001f);
    assert(std::fabs(polverineTemperatureOffset(50) - (2.93f + 0.0243f*50 + 2)) < 0.0001f);
}
