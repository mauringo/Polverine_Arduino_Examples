#!/usr/bin/env python3
"""Exercise the production BSEC scheduling methods against a delayed fake sensor."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root / 'lib/BSEC3_unofficial/src/bsec3.cpp').read_text()
start = source.index('bool Bsec3::run(void)')
end = source.index('\n/**', source.index('bool Bsec3::processFetchedData', start))
methods = source[start:end]
harness = r'''
#include <cassert>
#include <cstdint>
constexpr int BME69X_OK=0, BSEC_OK=0;
constexpr int BME69X_SLEEP_MODE=0, BME69X_FORCED_MODE=1, BME69X_PARALLEL_MODE=2;
constexpr int BME69X_GASM_VALID_MSK=0x20;
int64_t nowMs=0;
struct bme69xData { int status=BME69X_GASM_VALID_MSK; float pressure=101325; };
struct Settings {
    int64_t next_call=0;
    int op_mode=BME69X_SLEEP_MODE;
    bool trigger_measurement=false;
    int heater_duration=100;
};
struct FakeSensor {
    int status=0, reads=0, triggers=0;
    int64_t availableAt=0;
    bool fail=false;
    int fetchData() {
        ++reads;
        if (fail) { status=-1; return 0; }
        if (nowMs<availableAt) { status=2; return 0; }
        status=0; return 1;
    }
    int getData(bme69xData &data) { data=bme69xData{}; return 0; }
    int getMeasDur(int) { return 50000; }
    void setOpMode(int) {}
};
int bsec_sensor_control(void *, int64_t timestamp, Settings *settings) {
    settings->next_call=timestamp+INT64_C(3000000000);
    settings->op_mode=BME69X_FORCED_MODE;
    settings->trigger_measurement=true;
    return 0;
}
struct Bsec3 {
    FakeSensor sensor;
    Settings bmeConf;
    int opMode=BME69X_SLEEP_MODE, status=0, processed=0;
    void *bsecInstance=nullptr;
    bool measurementPending=false;
    int64_t measurementReadyNs=0;
    float pressure=0;
    int64_t getTimeMs() { return nowMs; }
    void setBme69xConfigForced() {
        ++sensor.triggers; sensor.availableAt=nowMs+150; opMode=BME69X_FORCED_MODE;
    }
    void setBme69xConfigParallel() {}
    bool processData(int64_t, const bme69xData &data) {
        ++processed; pressure=data.pressure; return true;
    }
    bool run();
    bool processFetchedData(int64_t);
};
'''
tests = r'''
int main() {
    Bsec3 sensor;
    assert(sensor.run()); // Trigger once; never read immediately.
    assert(sensor.sensor.triggers==1 && sensor.sensor.reads==0);
    nowMs=149; assert(sensor.run()); assert(sensor.sensor.reads==0);
    nowMs=150; assert(sensor.run()); assert(sensor.processed==1);
    assert(sensor.pressure==101325); // Preserve Pa for both BSEC and callbacks.
    nowMs=2999; assert(sensor.run()); assert(sensor.sensor.triggers==1);
    nowMs=3000; assert(sensor.run()); assert(sensor.sensor.triggers==2);
    nowMs=3150; assert(sensor.run()); assert(sensor.processed==2);

    // Retry a late sensor for a bounded interval, without retriggering it.
    nowMs=0; Bsec3 late; assert(late.run()); late.sensor.availableAt=1000;
    nowMs=150; assert(late.run()); assert(late.measurementPending);
    nowMs=649; assert(late.run()); assert(late.measurementPending);
    nowMs=650; assert(!late.run()); assert(!late.measurementPending);
    assert(late.sensor.triggers==1 && late.processed==0);

    nowMs=0; Bsec3 failed; assert(failed.run()); failed.sensor.fail=true;
    nowMs=150; assert(!failed.run()); assert(!failed.measurementPending);
}
'''
with tempfile.TemporaryDirectory(prefix='bsec-timing-') as directory:
    path = Path(directory)
    (path / 'check.cpp').write_text(harness + methods + tests)
    subprocess.run(['c++', '-std=c++11', '-Wall', '-Wextra', str(path / 'check.cpp'), '-o', str(path / 'check')], check=True)
    subprocess.run([str(path / 'check')], check=True)
print('PASS: delayed reads, no retriggers, bounded retries, errors, pressure in Pa')
