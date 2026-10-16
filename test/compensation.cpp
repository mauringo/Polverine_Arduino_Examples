#include <cassert>
#include <cmath>
#include "polverine_compensation.h"

int main() {
    // Reference demo selects client 1 / 30 seconds: table cfg3.
    assert(TEMPERATURE_PROFILE == 1 && BMV080_CYCLE_SECONDS == 30);
    assert(std::fabs(polverineTemperatureOffset(0) - 9.08f) < 0.0001f);
    assert(std::fabs(polverineTemperatureOffset(20) - 9.24f) < 0.0001f);
    assert(std::fabs(polverineTemperatureOffset(40) - 9.874f) < 0.0001f);
    assert(std::fabs(polverineTemperatureOffset(60) - 12.02f) < 0.001f);
    assert(std::fabs(polverineTemperatureOffset(80) - 11.86f) < 0.0001f);
    assert(polverineTemperatureOffset(-46) == 0);
    assert(polverineTemperatureOffset(86) == 0);
    // Shared range endpoints use the first matching row, as in BlackIoT's code.
    assert(std::fabs(polverineTemperatureOffset(15) - 9.08f) < 0.0001f);
    assert(std::fabs(polverineTemperatureOffset(28) - (6.61f + 0.0315f * 28 + 2)) < 0.0001f);
    assert(std::fabs(polverineTemperatureOffset(50) - (6.07f + 0.0451f * 50 + 2)) < 0.0001f);
}
