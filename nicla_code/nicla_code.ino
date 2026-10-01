#include <Nicla-Motore-V2_inferencing.h>
#include <Wire.h>
#include <Arduino_LSM6DSOX.h>

#define FREQUENCY_HZ 100
#define INTERVAL_US (1000000 / FREQUENCY_HZ) 

const int STRIDE_SAMPLES = 20; 
const int STRIDE_FLOATS = STRIDE_SAMPLES * 6; 

static float inference_buffer[EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE];
static size_t buffer_index = 0;
bool is_buffer_full = false;

unsigned long last_sample_us = 0;

void setup() {
    Serial.begin(115200);
    
    unsigned long start_timeout = millis();
    while (!Serial && (millis() - start_timeout < 3000)); 

    if (!IMU.begin()) {
        Serial.println("{\"status\":\"error\", \"msg\":\"IMU init failed\"}");
        while (1);
    }
    
    last_sample_us = micros();
}

void loop() {
    unsigned long current_us = micros();
    
    if (current_us - last_sample_us >= INTERVAL_US) {
        last_sample_us += INTERVAL_US; 

        float ax, ay, az, gx, gy, gz;
        if (IMU.accelerationAvailable() && IMU.gyroscopeAvailable()) {
            IMU.readAcceleration(ax, ay, az);
            IMU.readGyroscope(gx, gy, gz);

            if (!is_buffer_full) {
                inference_buffer[buffer_index++] = ax * 9.80665f;
                inference_buffer[buffer_index++] = ay * 9.80665f;
                inference_buffer[buffer_index++] = az * 9.80665f;
                inference_buffer[buffer_index++] = gx;
                inference_buffer[buffer_index++] = gy;
                inference_buffer[buffer_index++] = gz;
                
                if (buffer_index >= EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE) {
                    is_buffer_full = true;
                }
            }
        }
    }

    if (is_buffer_full) {
        signal_t signal;
        numpy::signal_from_buffer(inference_buffer, EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE, &signal);
        
        ei_impulse_result_t result = { 0 };
        EI_IMPULSE_ERROR err = run_classifier(&signal, &result, false);

        if (err == EI_IMPULSE_OK) {
            float max_conf = 0.0;
            const char* best_class = "unknown";
            
            for (size_t ix = 0; ix < EI_CLASSIFIER_LABEL_COUNT; ix++) {
                if (result.classification[ix].value > max_conf) {
                    max_conf = result.classification[ix].value;
                    best_class = result.classification[ix].label;
                }
            }

            Serial.print("{\"status\":\"");
            Serial.print(best_class);
            Serial.print("\",\"confidence\":");
            Serial.print(max_conf);
            Serial.print(",\"dsp_ms\":");
            Serial.print(result.timing.dsp);
            Serial.print(",\"class_ms\":");
            Serial.print(result.timing.classification);
            Serial.println("}");
        }
        
        for (size_t i = 0; i < EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE - STRIDE_FLOATS; i++) {
            inference_buffer[i] = inference_buffer[i + STRIDE_FLOATS];
        }
        
        buffer_index = EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE - STRIDE_FLOATS;
        is_buffer_full = false; 

        last_sample_us = micros(); 
    }
}