#pragma once
#include "polverine_settings.h"
#include "polverine_temperature_tables.h"

// Same table selection and polynomial as BlackIoT's BSEC integration.
// BSEC uses this heat-source offset to compensate BOTH temperature and humidity.
inline float polverineTemperatureOffset(float rawTemperatureC) {
    for (const auto &profile : temp_profile_tab) {
        if (profile.client_id != TEMPERATURE_PROFILE ||
            profile.map.bmv080_duty_cycle_period_s != BMV080_CYCLE_SECONDS) continue;

        for (unsigned i = 0; i < profile.map.tocp_len; ++i) {
            const auto &row = profile.map.tocp_cfg[i];
            if (rawTemperatureC < row.range_min || rawTemperatureC > row.range_max) continue;
            const float t = rawTemperatureC;
            return row.w[0] + row.w[1] * t + row.w[2] * t * t +
                   row.w[3] * t * t * t + row.offset_ref;
        }
    }
    return 0; // Outside the reference table's supported ranges.
}
