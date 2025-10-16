/* USER CODE BEGIN Header */
/**
 ******************************************************************************
 * @file           : main.c
 * @brief          : Main program body for LoRa Gateway (RX, TX, TX_RX modes)
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2024 STMicroelectronics. // Copyright (c) 2024-2025 YourCompany.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file
 * in the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *
 ******************************************************************************
 */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "Gpio.hpp"
#include "GpioHandler.hpp" // GpioHandler might not be used if only LED toggling
#include "Lora.hpp"
#include "Memory.hpp"
#include "UartHandler.hpp"
#include "CommandMessage.hpp"
#include "Logger.hpp"
#include <vector>
#include <cstring> // For memcpy and memset
#include <stdio.h>  // For printf

// Include version information (auto-generated during build)
#ifdef __has_include
#if __has_include("version.h")
#include "version.h"
#endif
#endif

// Default version info if version.h is not available
#ifndef FIRMWARE_VERSION
#define FIRMWARE_VERSION "2.0.0"
#define BUILD_DATE "unknown"
#define BUILD_TIME "unknown"
#define GIT_HASH "unknown"
#define GIT_TAG "v2.0.0"
#define VERSION_STRING "v2.0.0 (unknown)"
#endif
#include <algorithm> // For std::min
#include <random>
#include <memory>
#include <cmath> // For sqrtf function
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

// Define el modo de operación del firmware.
// Cambiar esto para recompilar en un modo diferente.

enum class OperationMode {
  RX_MODE,
  TX_MODE,
  TX_RX_MODE
};


#define FIRMWARE_OPERATION_MODE OperationMode::TX_RX_MODE

// Identificador único para este dispositivo y su función de módulo esperada para comandos de configuración
#define DEVICE_ID 0x00
#define DEVICE_MODULE_FUNCTION MODULE_FUNCTION::SERVER // Asume que los comandos de config van a un "SERVER"

// Constantes para los modos de operación
#define MODE_OPERATION_RX 0x01
#define MODE_OPERATION_TX 0x02
#define MODE_OPERATION_TX_RX 0x03

// Constantes para simulación de Sniffer
#define CMD_ID_TRIGGER_SNIFFER_SIMULATION 0x30
#define SNIFFER_IO_DATA_SIZE 33
#define SNIFFER_TAG_DATA_SIZE 33 // Definido aquí para evitar errores de identificador no definido

// Constantes para simulación de tags basadas en el código Python
#define ONE_DETECTION 0x17
#define MULTIPLE_DETECTION 0x18
#define MAX_DISTANCE_A 40.0f
#define TRANSMITTER_DISTANCE 2.4f
#define MAX_DISTANCE_DIFF 0.5f
#define Y_CONST -3.0f
#define MAX_SNIFFERS 5
#define MAX_TAGS_PER_FRAME 24

// Estructura para datos de tag con distancias (Multiple Detection)
struct TagWithDistance {
    uint32_t tag_id;
    float distance_a;
    float distance_b;
    float battery;
    float x;
    float y;
};

// Estructura para datos de tag simple (One Detection)
struct TagSimple {
    uint32_t tag_id;
    uint8_t battery; // Battery * 10 (250-420 representa 2.5V-4.2V)
};

// Estructuras para simulación de datos de sniffer
struct SnifferDeviceConfig {
    uint8_t digital_output1;
    uint8_t digital_output2;
    uint8_t digital_input1;
    uint8_t digital_input2;
    uint8_t switch_output_20ma;
    uint8_t switch_input_20ma;
    uint8_t switch_serial;
    uint16_t analog_output_0_10v;
    uint16_t analog_output_x_20ma;
    uint16_t analog_input_0_10v;
    uint16_t analog_input6_x_20ma;
    uint16_t analog_input1_x_20ma;
    uint16_t analog_input2_x_20ma;
    uint16_t analog_input5_x_20ma;
};

struct DeviceSerialQueryConfigCpp {
    uint8_t query[16];
    uint8_t query_length;
    uint16_t response_size;
    uint16_t query_time_ms;
    uint32_t last_query_time_ms;
};

// Variables globales para simulación
bool simulationEnabled = false;
bool snifferTagSimulationEnabled = false; // Nueva bandera para simulación de sniffer tag
SnifferDeviceConfig deviceConfig;
DeviceSerialQueryConfigCpp serialQueryConfig;
uint32_t lastSimulationTime = 0;
uint32_t simulationInterval = 1000; // 1 segundo por defecto

// Variables para el estado de simulación de tags (matching Python logic)
uint32_t received_sniffer_id = 0;
uint32_t multiple_sniffer_id = 0;
uint32_t current_sniffer_id = 1;

// Array de UUIDs fijos para los sniffers
const char* device_uuids[] = {
    "f59422b3c7bb4fbc8d1893f1",  // UUIDs originales mantenidos
    "9e7a33fa404e2bc18986ceb4",
    "26870c502b927945422fc8ad",
    "a1b2c3d4e5f6a7b8c9d0e1f2",  // UUIDs fijos adicionales
    "b2c3d4e5f6a7b8c9d0e1f2a3",
    "c3d4e5f6a7b8c9d0e1f2a3b4",
    "d4e5f6a7b8c9d0e1f2a3b4c5",
    "e5f6a7b8c9d0e1f2a3b4c5d6",
    "f6a7b8c9d0e1f2a3b4c5d6e7",
    "a7b8c9d0e1f2a3b4c5d6e7f8",
    "b8c9d0e1f2a3b4c5d6e7f8a9",
    "c9d0e1f2a3b4c5d6e7f8a9b0",
    "d0e1f2a3b4c5d6e7f8a9b0c1",
    "e1f2a3b4c5d6e7f8a9b0c1d2",
    "f2a3b4c5d6e7f8a9b0c1d2e3",
    "a3b4c5d6e7f8a9b0c1d2e3f4",
    "b4c5d6e7f8a9b0c1d2e3f4a5",
    "c5d6e7f8a9b0c1d2e3f4a5b6",
    "d6e7f8a9b0c1d2e3f4a5b6c7",
    "e7f8a9b0c1d2e3f4a5b6c7d8"
};

#define NUM_DEVICE_UUIDS (sizeof(device_uuids) / sizeof(device_uuids[0]))

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
#ifndef MAX_LORA_BUFFER_SIZE
#define MAX_LORA_BUFFER_SIZE 255
#endif

#ifndef MAX_UART_BUFFER_SIZE
#define MAX_UART_BUFFER_SIZE 255 // Asegúrate que CommandMessage.hpp o main.h lo define
#endif
/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
ADC_HandleTypeDef hadc1;
CRC_HandleTypeDef hcrc;
I2C_HandleTypeDef hi2c1;
IWDG_HandleTypeDef hiwdg;
SPI_HandleTypeDef hspi1;
UART_HandleTypeDef huart1; // Available for debug or other purposes
UART_HandleTypeDef huart2; // Main UART for LoRa data and config commands
UART_HandleTypeDef huart3; // RS485 Logger output

/* USER CODE BEGIN PV */
// Punteros globales inicializados a nullptr
UartHandler* uartHandler = nullptr;
Memory* eepromMemory = nullptr;
Gpio* loraNssPin = nullptr;
Gpio* loraRstPin = nullptr;
Lora* lora = nullptr;
Gpio* loraRxLed = nullptr;
Gpio* loraTxLed = nullptr;
Gpio* keepAliveLed = nullptr;
CommandMessage* uartCommandParser = nullptr;
CommandMessage* loraCommandParser = nullptr;
CommandMessage* uartSimulatedCommandParse = nullptr;

// Define el modo de operación actual
OperationMode currentOperationMode = FIRMWARE_OPERATION_MODE;

// Buffers and state for LoRa communication
uint8_t loraReceiveBuffer[MAX_LORA_BUFFER_SIZE] = {0};
uint8_t loraReceivedBytes = 0;
uint8_t loraTransmitBuffer[MAX_LORA_BUFFER_SIZE] = {0};
uint8_t loraTransmitSizeBytes = 0;
bool pendingLoraTransmission = false;

// Buffers and state for UART communication
uint8_t uartReceiveBuffer[MAX_UART_BUFFER_SIZE] = {0};
uint16_t uartReceivedBytes = 0; // Renamed from bytes_reciv_software and bytes_reciv
bool newUartDataReceived = false;

// Control flag to stop LoRa reception during UART processing
bool blockLoraReception = false;
uint32_t blockStartTime = 0;
const uint32_t BLOCK_DURATION_MS = 1000; // 1 second blocking period

uint32_t keepAliveLastTick = 0;
uint32_t loggerHeartbeatLastTick = 0;
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_I2C1_Init(void);
static void MX_SPI1_Init(void);
static void MX_USART1_UART_Init(void);
static void MX_USART2_UART_Init(void);
static void MX_USART3_UART_Init(void);
static void MX_ADC1_Init(void);
static void MX_CRC_Init(void);
static void MX_IWDG_Init(void);
/* USER CODE BEGIN PFP */
void transmitLoraSettingResponse(Lora* loraDevice, UartHandler* uartComm, CommandMessage* cmdBuilder, uint8_t queryCommandId);
void processUartCommand(void);
void handleLoraReception(void);
void handleLoraTransmission(void);
// Prototipos para funcionalidad de simulación de sniffer
void initializeDefaultDeviceConfig(void);
void generateRandomSnifferIoDataCpp(uint8_t* buffer, size_t* dataSize, const SnifferDeviceConfig* config = nullptr);
void triggerSnifferSimulation(void);
void triggerSnifferTagSimulation(void); // Prototipo para nueva función
void handleSnifferSimulation(void);
bool buildAndSendSnifferFrame(const uint8_t* payload, size_t payloadSize, uint8_t commandId = 0x23);
bool buildAndSendTagSimulationFrame(uint8_t* buffer, size_t dataSize, bool isMultipleDetection);
uint32_t getRandomNumber(uint32_t min, uint32_t max);
void generateRandomSnifferTagDataCpp(uint8_t* buffer, size_t* dataSize); // Prototipo para generador de datos de sniffer tag
// Enhanced prototypes for Python-compatible tag simulation
void calculateXLimits(float y_const, float max_distance, float* x_min, float* x_max);
void generateDataConstantY(TagWithDistance* tags, uint8_t num_points);
void generateRandomMultipleDetectionData(TagWithDistance* tags, uint8_t num_tags);
void generateRandomOneDetectionData(TagSimple* tags, uint8_t num_tags);
void buildMultipleDetectionFrame(uint32_t sniffer_id, TagWithDistance* tags, uint8_t num_tags, uint8_t* buffer, size_t* dataSize);
void buildOneDetectionFrame(uint32_t sniffer_id, TagSimple* tags, uint8_t num_tags, uint8_t* buffer, size_t* dataSize);
void enhancedTagSimulation(uint8_t* buffer, size_t* dataSize, uint8_t* commandId); // Main enhanced simulation function
/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart) {
    if (huart == &huart2 && uartHandler != nullptr) {
        // Block LoRa reception when UART data is being received
        blockLoraReception = true;
        
        // Get the received byte from the buffer
        uint8_t received_byte = uartReceiveBuffer[0];
        
        // Process the received byte using the improved method
        uartReceivedBytes = uartHandler->process_received_byte(received_byte, uartReceiveBuffer);
        
        // Set flag if a complete frame was received
        if (uartReceivedBytes > 0) {
            newUartDataReceived = true;
        }
        
        // Continue reception for next byte
        HAL_UART_Receive_IT(huart, uartReceiveBuffer, 1);
    }
}

// Función para cambiar el modo de operación dinámicamente
bool changeOperationMode(uint8_t newMode) {
    switch(newMode) {
        case MODE_OPERATION_RX:
            currentOperationMode = OperationMode::RX_MODE;
            break;
        case MODE_OPERATION_TX:
            currentOperationMode = OperationMode::TX_MODE;
            break;
        case MODE_OPERATION_TX_RX:
            currentOperationMode = OperationMode::TX_RX_MODE;
            break;
        default:
            return false; // Modo no reconocido
    }

    // Limpiar buffers y estados
    memset(loraReceiveBuffer, 0, MAX_LORA_BUFFER_SIZE);
    memset(loraTransmitBuffer, 0, MAX_LORA_BUFFER_SIZE);
    loraReceivedBytes = 0;
    loraTransmitSizeBytes = 0;
    pendingLoraTransmission = false;

    // Se podría añadir indicación visual del cambio (LEDs)
    return true;
}

// ============================================================================
// IMPLEMENTACIÓN DE FUNCIONALIDAD DE SIMULACIÓN DE SNIFFER
// ============================================================================

/**
 * @brief Calcula CRC-16/MODBUS para un array de datos
 * @param data: Puntero a los datos
 * @param length: Longitud de los datos
 * @return CRC-16 calculado
 */
/**
 * @brief Inicializa la configuración por defecto del dispositivo sniffer
 */
void initializeDefaultDeviceConfig(void) {
    // Configuración digital por defecto
    deviceConfig.digital_output1 = 0;
    deviceConfig.digital_output2 = 0;
    deviceConfig.digital_input1 = 1;
    deviceConfig.digital_input2 = 0;
    deviceConfig.switch_output_20ma = 1;
    deviceConfig.switch_input_20ma = 0;
    deviceConfig.switch_serial = 1;
    
    // Configuración analógica por defecto (valores típicos entre 1000-4095)
    deviceConfig.analog_output_0_10v = 2500;
    deviceConfig.analog_output_x_20ma = 3000;
    deviceConfig.analog_input_0_10v = 2000;
    deviceConfig.analog_input6_x_20ma = 2800;
    deviceConfig.analog_input1_x_20ma = 3200;
    deviceConfig.analog_input2_x_20ma = 1800;
    deviceConfig.analog_input5_x_20ma = 3500;
    
    // Configuración de query serie por defecto
    memset(&serialQueryConfig, 0, sizeof(DeviceSerialQueryConfigCpp));
    serialQueryConfig.query_length = 0;
    serialQueryConfig.response_size = 0;
    serialQueryConfig.query_time_ms = 1000;
    serialQueryConfig.last_query_time_ms = 0;
}

/**
 * @brief Convierte un UUID en formato string hexadecimal a bytes
 * @param uuidStr: String del UUID (24 caracteres hex)
 * @param buffer: Buffer donde escribir los 12 bytes del UUID
 * @return true si la conversión fue exitosa, false en caso de error
 */
bool hexStringToBytes(const char* uuidStr, uint8_t* buffer) {
    if (!uuidStr || !buffer) return false;
    
    // Verificar que el string tenga exactamente 24 caracteres (12 bytes * 2)
    size_t len = strlen(uuidStr);
    if (len != 24) return false;
    
    for (int i = 0; i < 12; i++) {
        char highNibble = uuidStr[i * 2];
        char lowNibble = uuidStr[i * 2 + 1];
        
        // Convertir caracteres hex a valores numéricos
        uint8_t high = 0, low = 0;
        
        if (highNibble >= '0' && highNibble <= '9') high = highNibble - '0';
        else if (highNibble >= 'a' && highNibble <= 'f') high = highNibble - 'a' + 10;
        else if (highNibble >= 'A' && highNibble <= 'F') high = highNibble - 'A' + 10;
        else return false;
        
        if (lowNibble >= '0' && lowNibble <= '9') low = lowNibble - '0';
        else if (lowNibble >= 'a' && lowNibble <= 'f') low = lowNibble - 'a' + 10;
        else if (lowNibble >= 'A' && lowNibble <= 'F') low = lowNibble - 'A' + 10;
        else return false;
        
        buffer[i] = (high << 4) | low;
    }
    
    return true;
}

/**
 * @brief Genera un número aleatorio en un rango específico
 * @param min: Valor mínimo
 * @param max: Valor máximo
 * @return Número aleatorio generado
 */
uint32_t getRandomNumber(uint32_t min, uint32_t max) {
    static bool initialized = false;
    static std::mt19937 generator;
    
    if (!initialized) {
        generator.seed(HAL_GetTick());
        initialized = true;
    }
    
    std::uniform_int_distribution<uint32_t> distribution(min, max);
    return distribution(generator);
}

/**
 * @brief Genera datos aleatorios para Sniffer IO (equivalente a la función Python)
 * @param buffer: Buffer donde escribir los datos
 * @param dataSize: Puntero al tamaño de los datos generados
 * @param config: Configuración opcional (si es nullptr, usa valores aleatorios)
 */
void generateRandomSnifferIoDataCpp(uint8_t* buffer, size_t* dataSize, const SnifferDeviceConfig* config) {
    if (!buffer || !dataSize) return;
    
    *dataSize = SNIFFER_IO_DATA_SIZE; // 33 bytes
    memset(buffer, 0, SNIFFER_IO_DATA_SIZE);
    
    // Seleccionar un UUID fijo aleatorio de la lista (12 bytes)
    uint32_t uuidIndex = getRandomNumber(0, NUM_DEVICE_UUIDS - 1);
    const char* selectedUuid = device_uuids[uuidIndex];
    
    // Convertir UUID de string hex a bytes
    if (!hexStringToBytes(selectedUuid, buffer)) {
        // Si falla la conversión, generar UUID aleatorio como fallback
        for (int i = 0; i < 12; i++) {
            buffer[i] = getRandomNumber(0, 255);
        }
    }
    
    // Valores digitales (7 bytes) - usar configuración si está disponible
    if (config) {
        buffer[12] = config->digital_output1;
        buffer[13] = config->digital_output2;
        buffer[14] = config->digital_input1;
        buffer[15] = config->digital_input2;
        buffer[16] = config->switch_output_20ma;
        buffer[17] = config->switch_input_20ma;
        buffer[18] = config->switch_serial;
    } else {
        // Valores aleatorios para salidas digitales
        buffer[12] = getRandomNumber(0, 1); // Digital Output 1
        buffer[13] = getRandomNumber(0, 1); // Digital Output 2
        buffer[14] = getRandomNumber(0, 1); // Digital Input 1
        buffer[15] = getRandomNumber(0, 1); // Digital Input 2
        buffer[16] = getRandomNumber(0, 1); // Switch Output x 20mA
        buffer[17] = getRandomNumber(0, 1); // Switch Input x 20mA
        buffer[18] = getRandomNumber(0, 1); // Switch Serial
    }
    
    // Valores analógicos (14 bytes) - 7 valores de 2 bytes cada uno en big-endian
    uint16_t analogValues[7];
    
    if (config) {
        analogValues[0] = config->analog_output_0_10v;
        analogValues[1] = config->analog_output_x_20ma;
        analogValues[2] = config->analog_input_0_10v;
        analogValues[3] = config->analog_input6_x_20ma;
        analogValues[4] = config->analog_input1_x_20ma;
        analogValues[5] = config->analog_input2_x_20ma;
        analogValues[6] = config->analog_input5_x_20ma;
    } else {
        // Valores aleatorios entre 1000 y 4095 (12-bit ADC)
        for (int i = 0; i < 7; i++) {
            analogValues[i] = getRandomNumber(1000, 4095);
        }
    }
    
    // Escribir valores analógicos en formato big-endian
    for (int i = 0; i < 7; i++) {
        buffer[19 + i * 2] = (analogValues[i] >> 8) & 0xFF; // Byte alto
        buffer[20 + i * 2] = analogValues[i] & 0xFF;        // Byte bajo
    }
}

/**
 * @brief Genera datos aleatorios para Sniffer Tag (nueva función)
 * Simula el formato de "One Detection" (0x17) con múltiples tags
 * Estructura: Sniffer ID (12 bytes UUID) + Total Tags (1) + Frame Tags (1) + [Tag ID (4) + Battery (1)] * N
 * @param buffer: Buffer donde escribir los datos (hasta MAX_LORA_BUFFER_SIZE = 255 bytes)
 * @param dataSize: Puntero al tamaño de los datos generados
 */
void generateRandomSnifferTagDataCpp(uint8_t* buffer, size_t* dataSize) {
    if (!buffer || !dataSize) return;
    
    // Limpiar buffer con el tamaño máximo
    memset(buffer, 0, MAX_LORA_BUFFER_SIZE);
    
    // Calcular máximo número de tags basado en LoRa frame size (255 bytes)
    // Header: 12 bytes UUID + 1 byte total tags + 1 byte frame tags = 14 bytes
    // Cada tag: 4 bytes ID + 1 byte battery = 5 bytes por tag
    // Máximo tags: (255 - 14) / 5 = 48 tags
    const size_t header_size = 14; // 12 bytes UUID + 2 bytes counts
    const size_t bytes_per_tag = 5;
    const size_t max_tags = (MAX_LORA_BUFFER_SIZE - header_size) / bytes_per_tag;
    
    // Generar número aleatorio de tags (1 hasta máximo posible)
    uint8_t num_tags = getRandomNumber(1, max_tags);
    
    // Calcular tamaño final del frame
    *dataSize = header_size + (num_tags * bytes_per_tag);
    
    // Bytes 0-11: Sniffer ID usando UUID de la lista (mismo método que generateRandomSnifferIoDataCpp)
    uint32_t uuidIndex = getRandomNumber(0, NUM_DEVICE_UUIDS - 1);
    const char* selectedUuid = device_uuids[uuidIndex];
    
    // Convertir UUID de string hex a bytes (primeros 12 bytes)
    if (!hexStringToBytes(selectedUuid, buffer)) {
        // Si falla la conversión, generar UUID aleatorio como fallback
        for (int i = 0; i < 12; i++) {
            buffer[i] = getRandomNumber(0, 255);
        }
    }
    
    // Byte 12: Total tags registrados (mismo que frame tags para simplicidad)
    buffer[12] = num_tags;
    
    // Byte 13: Tags en este frame
    buffer[13] = num_tags;
    
    // Bytes 14+: Datos de cada tag (5 bytes por tag)
    size_t offset = 14;
    for (uint8_t i = 0; i < num_tags && offset + bytes_per_tag <= MAX_LORA_BUFFER_SIZE; ++i) {
        // Tag ID (4 bytes, little-endian) - rango 0-200 como en Python
        uint32_t tag_id = getRandomNumber(0, 200);
        buffer[offset] = tag_id & 0xFF;
        buffer[offset + 1] = (tag_id >> 8) & 0xFF;
        buffer[offset + 2] = (tag_id >> 16) & 0xFF;
        buffer[offset + 3] = (tag_id >> 24) & 0xFF;
        
        // Battery (1 byte) - rango 25-42 como en Python, pero multiplicado por 10 para el protocolo
        uint8_t battery = getRandomNumber(25, 42) * 10; // 250-420 (representa 2.5V-4.2V)
        buffer[offset + 4] = battery;
        
        offset += bytes_per_tag;
    }
}

/**
 * @brief Activa la simulación de sniffer
 */
void triggerSnifferSimulation(void) {
    simulationEnabled = true;
    snifferTagSimulationEnabled = false; // Por defecto, solo sniffer IO
}

/**
 * @brief Activa la simulación de sniffer tag
 */
void triggerSnifferTagSimulation(void) {
    snifferTagSimulationEnabled = true;
    simulationEnabled = false; // Solo uno activo a la vez
}

/**
 * @brief Maneja la lógica de simulación de sniffer (llamar desde el loop principal)
 */
void handleSnifferSimulation(void) {
    static uint32_t lastSimTime = 0;
    uint32_t now = HAL_GetTick();
    if (now - lastSimTime < simulationInterval) return;
    lastSimTime = now;

    // Buffer para datos de simulación - usar tamaño máximo de LoRa frame
    uint8_t simData[MAX_LORA_BUFFER_SIZE];
    size_t simDataSize = 0;
    
    if (simulationEnabled) {
        // Simulación IO: LED RX y TX alternan (patrón existente)
        generateRandomSnifferIoDataCpp(simData, &simDataSize, &deviceConfig);
        buildAndSendSnifferFrame(simData, simDataSize);
        
        // Indicador visual para simulación IO (patrón rápido)
        if (loraRxLed && loraTxLed) {
            HAL_GPIO_WritePin(loraRxLed->get_port(), loraRxLed->get_pin(), GPIO_PIN_SET);
            HAL_Delay(50);
            HAL_GPIO_WritePin(loraRxLed->get_port(), loraRxLed->get_pin(), GPIO_PIN_RESET);
            HAL_GPIO_WritePin(loraTxLed->get_port(), loraTxLed->get_pin(), GPIO_PIN_SET);
            HAL_Delay(50);
            HAL_GPIO_WritePin(loraTxLed->get_port(), loraTxLed->get_pin(), GPIO_PIN_RESET);
        }
        } else if (snifferTagSimulationEnabled) {
        // Enhanced TAG simulation: use new Python-compatible logic
        uint8_t frameCommandId = ONE_DETECTION; // Default
        enhancedTagSimulation(simData, &simDataSize, &frameCommandId);
        if (simDataSize > 0) {
            buildAndSendSnifferFrame(simData, simDataSize, frameCommandId);
        }
        
        // Indicador visual para simulación TAG (patrón doble)
        if (loraRxLed && loraTxLed) {
            // Doble parpadeo RX para indicar simulación TAG
            HAL_GPIO_WritePin(loraRxLed->get_port(), loraRxLed->get_pin(), GPIO_PIN_SET);
            HAL_GPIO_WritePin(loraTxLed->get_port(), loraTxLed->get_pin(), GPIO_PIN_SET);
            HAL_Delay(100);
            HAL_GPIO_WritePin(loraRxLed->get_port(), loraRxLed->get_pin(), GPIO_PIN_RESET);
            HAL_GPIO_WritePin(loraTxLed->get_port(), loraTxLed->get_pin(), GPIO_PIN_RESET);
            HAL_Delay(50);
            HAL_GPIO_WritePin(loraRxLed->get_port(), loraRxLed->get_pin(), GPIO_PIN_SET);
            HAL_GPIO_WritePin(loraTxLed->get_port(), loraTxLed->get_pin(), GPIO_PIN_SET);
            HAL_Delay(100);
            HAL_GPIO_WritePin(loraRxLed->get_port(), loraRxLed->get_pin(), GPIO_PIN_RESET);
            HAL_GPIO_WritePin(loraTxLed->get_port(), loraTxLed->get_pin(), GPIO_PIN_RESET);
        }
    }
}

/**
 * @brief Construye y envía un frame de sniffer completo con headers y CRC
 * @param payload: Datos del payload (33 bytes de IO + datos serie opcionales)
 * @param payloadSize: Tamaño del payload
 * @param commandId: Command ID to use (0x17 for One Detection, 0x18 for Multiple Detection, 0x23 for IO)
 * @return true si se envió correctamente, false en caso de error
 */
bool buildAndSendSnifferFrame(const uint8_t* payload, size_t payloadSize, uint8_t commandId) {
    if (!payload || payloadSize == 0 || !uartHandler || !uartSimulatedCommandParse) {
        return false;
    }

    // Configurar el comando dinámicamente
    uartSimulatedCommandParse->setCommandId(commandId);
    
    // Usar el nuevo protocolo FrameBuilder a través de composeAndSendMessage
    bool success = uartSimulatedCommandParse->composeAndSendMessage(
        uartHandler,
        const_cast<uint8_t*>(payload),
        static_cast<uint8_t>(payloadSize)
    );
    
    return success;
}

/**
 * @brief Build and send tag simulation frame with appropriate command ID
 * Determines the command ID based on frame content and sends the frame
 * @param buffer: Frame data buffer
 * @param dataSize: Size of frame data
 * @param isMultipleDetection: true for Multiple Detection (0x18), false for One Detection (0x17)
 * @return true if sent successfully, false otherwise
 */
bool buildAndSendTagSimulationFrame(uint8_t* buffer, size_t dataSize, bool isMultipleDetection) {
    if (!buffer || dataSize == 0) return false;
    
    uint8_t commandId = isMultipleDetection ? MULTIPLE_DETECTION : ONE_DETECTION;
    return buildAndSendSnifferFrame(buffer, dataSize, commandId);
}


// Optimized helper function to send LoRa setting responses via UART
// Uses cached values directly for maximum speed
void transmitLoraSettingResponse(Lora* loraDevice, UartHandler* uartComm, CommandMessage* cmdBuilder,
                                 uint8_t queryCommandId) {
    if (!loraDevice || !uartComm || !cmdBuilder) return;
    
    uint8_t dataArray[4];
    size_t dataSize = 0;

    // Use cached values directly - no EEPROM reads needed
    // Settings are loaded during initialization
    switch (queryCommandId) {
        case static_cast<uint8_t>(CommandType::QUERY_RX_FREQ): {
            float freqOut = loraDevice->get_rx_frequency() / 1000000.0f;
            memcpy(dataArray, &freqOut, sizeof(float));
            dataSize = sizeof(float);
            break;
        }
        case static_cast<uint8_t>(CommandType::QUERY_TX_FREQ): {
            float freqOut = loraDevice->get_tx_frequency() / 1000000.0f;
            memcpy(dataArray, &freqOut, sizeof(float));
            dataSize = sizeof(float);
            break;
        }
        case static_cast<uint8_t>(CommandType::QUERY_SPREAD_FACTOR): {
            uint8_t sf = loraDevice->get_spread_factor();
            memcpy(dataArray, &sf, sizeof(uint8_t));
            dataSize = sizeof(uint8_t);
            break;
        }
        case static_cast<uint8_t>(CommandType::QUERY_CODING_RATE): {
            uint8_t cr = loraDevice->get_coding_rate();
            memcpy(dataArray, &cr, sizeof(uint8_t));
            dataSize = sizeof(uint8_t);
            break;
        }
        case static_cast<uint8_t>(CommandType::QUERY_BANDWIDTH): {
            uint8_t bw = loraDevice->get_bandwidth();
            memcpy(dataArray, &bw, sizeof(uint8_t));
            dataSize = sizeof(uint8_t);
            break;
        }
        default:
            return;
    }

    // Send response immediately
    cmdBuilder->composeAndSendMessage(uartComm, dataArray, dataSize);
}

void processUartCommand() {
    if (!newUartDataReceived || uartReceivedBytes == 0 || !uartCommandParser || !lora || !uartHandler) {
        return;
    }

    // Log incoming UART data
    LOG_UART2_HEX("RX", uartReceiveBuffer, uartReceivedBytes);

    STATUS frameStatus = uartCommandParser->validate(uartReceiveBuffer, uartReceivedBytes);

    if (frameStatus == STATUS::CONFIG_FRAME) {
        uint8_t commandId = uartCommandParser->getCommandId();
        
        LOG_COMMAND("Processing command 0x%02X", commandId);
        
        // Convertir commandId a CommandType para comparación más clara en el switch
        switch (commandId) {
            // Casos para comandos de consulta
            case static_cast<uint8_t>(CommandType::QUERY_RX_FREQ):
            case static_cast<uint8_t>(CommandType::QUERY_TX_FREQ):
            case static_cast<uint8_t>(CommandType::QUERY_SPREAD_FACTOR):
            case static_cast<uint8_t>(CommandType::QUERY_CODING_RATE):
            case static_cast<uint8_t>(CommandType::QUERY_BANDWIDTH):
                transmitLoraSettingResponse(lora, uartHandler, uartCommandParser, commandId);
                break;

            // Casos para comandos de configuración
            case static_cast<uint8_t>(CommandType::SET_TX_FREQ): {
                int freqInt = uartCommandParser->freqDecode();
                lora->set_tx_freq(static_cast<uint32_t>(freqInt));
                // Send immediate response with new value
                transmitLoraSettingResponse(lora, uartHandler, uartCommandParser, static_cast<uint8_t>(CommandType::QUERY_TX_FREQ));
                // Defer slow operations to improve response time
                lora->save_settings();
                lora->configure_modem();
                break;
            }
            case static_cast<uint8_t>(CommandType::SET_RX_FREQ): {
                int freqInt = uartCommandParser->freqDecode();
                lora->set_rx_freq(static_cast<uint32_t>(freqInt));
                // Send immediate response with new value
                transmitLoraSettingResponse(lora, uartHandler, uartCommandParser, static_cast<uint8_t>(CommandType::QUERY_RX_FREQ));
                // Defer slow operations to improve response time
                lora->save_settings();
                lora->configure_modem();
                break;
            }
            case static_cast<uint8_t>(CommandType::SET_BANDWIDTH): {
                uint8_t bw = uartCommandParser->getDataAsUint8();
                lora->set_bandwidth(bw);
                // Send immediate response with new value
                transmitLoraSettingResponse(lora, uartHandler, uartCommandParser, static_cast<uint8_t>(CommandType::QUERY_BANDWIDTH));
                // Defer slow operations to improve response time
                lora->save_settings();
                lora->configure_modem();
                break;
            }
            case static_cast<uint8_t>(CommandType::SET_SPREAD_FACTOR): {
                uint8_t sf = uartCommandParser->getDataAsUint8();
                lora->set_spread_factor(sf);
                // Send immediate response with new value
                transmitLoraSettingResponse(lora, uartHandler, uartCommandParser, static_cast<uint8_t>(CommandType::QUERY_SPREAD_FACTOR));
                // Defer slow operations to improve response time
                lora->save_settings();
                lora->configure_modem();
                break;
            }
            case static_cast<uint8_t>(CommandType::SET_CODING_RATE): {
                uint8_t cr = uartCommandParser->getDataAsUint8();
                lora->set_coding_rate(cr);
                // Send immediate response with new value
                transmitLoraSettingResponse(lora, uartHandler, uartCommandParser, static_cast<uint8_t>(CommandType::QUERY_CODING_RATE));
                // Defer slow operations to improve response time
                lora->save_settings();
                lora->configure_modem();
                break;
            }
            case static_cast<uint8_t>(CommandType::SET_UART_BAUDRATE): {
                lora->set_default_parameters();
                // Defer slow operations to improve response time
                lora->save_settings();
                lora->configure_modem();
                break;
            }
            case static_cast<uint8_t>(CommandType::SET_OPERATION_MODE): {
                uint8_t newMode = uartCommandParser->getDataAsUint8();
                LOG_CONFIG("Changing operation mode to: %d", newMode);
                if (changeOperationMode(newMode)) {
                    LOG_CONFIG("Operation mode changed successfully to: %s", 
                              (currentOperationMode == OperationMode::RX_MODE) ? "RX" :
                              (currentOperationMode == OperationMode::TX_MODE) ? "TX" : "TX_RX");
                    // Responder con confirmación
                    uint8_t response = static_cast<uint8_t>(currentOperationMode);
                    uartCommandParser->composeAndSendMessage(uartHandler, &response, 1);
                    
                    // Indicar visualmente el cambio de modo (opcional)
                    if (loraRxLed && loraTxLed) {
                        // Patrón de parpadeo para indicar el modo
                        switch (currentOperationMode) {
                            case OperationMode::RX_MODE:
                                // Parpadear solo el LED RX
                                HAL_GPIO_WritePin(loraRxLed->get_port(), loraRxLed->get_pin(), GPIO_PIN_SET);
                                HAL_Delay(200);
                                HAL_GPIO_WritePin(loraRxLed->get_port(), loraRxLed->get_pin(), GPIO_PIN_RESET);
                                break;
                            case OperationMode::TX_MODE:
                                // Parpadear solo el LED TX
                                HAL_GPIO_WritePin(loraTxLed->get_port(), loraTxLed->get_pin(), GPIO_PIN_SET);
                                HAL_Delay(200);
                                HAL_GPIO_WritePin(loraTxLed->get_port(), loraTxLed->get_pin(), GPIO_PIN_RESET);
                                break;
                            case OperationMode::TX_RX_MODE:
                                // Parpadear ambos LEDs
                                HAL_GPIO_WritePin(loraRxLed->get_port(), loraRxLed->get_pin(), GPIO_PIN_SET);
                                HAL_GPIO_WritePin(loraTxLed->get_port(), loraTxLed->get_pin(), GPIO_PIN_SET);
                                HAL_Delay(200);
                                HAL_GPIO_WritePin(loraRxLed->get_port(), loraRxLed->get_pin(), GPIO_PIN_RESET);
                                HAL_GPIO_WritePin(loraTxLed->get_port(), loraTxLed->get_pin(), GPIO_PIN_RESET);
                                break;
                        }
                    }
                }
                break;
            }
            case CMD_ID_TRIGGER_SNIFFER_SIMULATION: {
                // Comando para activar/desactivar simulación de sniffer
                uint8_t enable = uartCommandParser->getDataAsUint8();
                if (enable == 1) {
                    triggerSnifferSimulation();
                    // Responder con confirmación
                    uint8_t response = 0x01;
                    uartCommandParser->composeAndSendMessage(uartHandler, &response, 1);
                } else if (enable == 2) {
                    triggerSnifferTagSimulation();
                    uint8_t response = 0x02; // Simulación de sniffer tag activada
                    uartCommandParser->composeAndSendMessage(uartHandler, &response, 1);
                } else {
                    simulationEnabled = false;
                    snifferTagSimulationEnabled = false;
                    uint8_t response = 0x00;
                    uartCommandParser->composeAndSendMessage(uartHandler, &response, 1);
                }
                break;
            }
            default:
                break;
        }
    } else if (frameStatus == STATUS::RETRANSMIT_FRAME) {
        if (currentOperationMode == OperationMode::TX_MODE || currentOperationMode == OperationMode::TX_RX_MODE) {
            if (uartReceivedBytes <= MAX_LORA_BUFFER_SIZE) {
                memcpy(loraTransmitBuffer, uartReceiveBuffer, uartReceivedBytes);
                loraTransmitSizeBytes = uartReceivedBytes;
                pendingLoraTransmission = true;
            }
        }
    }

    memset(uartReceiveBuffer, 0, MAX_UART_BUFFER_SIZE);
    uartReceivedBytes = 0;
    newUartDataReceived = false;
    uartCommandParser->reset(1);
    
    // Start 1-second blocking period after UART command processing
    blockStartTime = HAL_GetTick();
    
    // Restart UART reception for next byte - reinitialize interrupt
    HAL_UART_Receive_IT(&huart2, uartReceiveBuffer, 1);
    
    // blockLoraReception remains true for 1 second
}


void handleLoraReception() {
    if (!lora || !loraRxLed || !uartHandler) return;
    
    if (currentOperationMode == OperationMode::TX_MODE && !pendingLoraTransmission) {
        return;
    }

    loraReceivedBytes = lora->receive(loraReceiveBuffer, LinkMode::UPLINK);

    if (loraReceivedBytes > 0) {
        HAL_GPIO_WritePin(loraRxLed->get_port(), loraRxLed->get_pin(), GPIO_PIN_SET);
        
        // Log LoRa received data
        LOG_LORA_RX_HEX("Received", loraReceiveBuffer, loraReceivedBytes);

        if (loraCommandParser) {
            STATUS loraFrameStatus = loraCommandParser->validate(loraReceiveBuffer, loraReceivedBytes);
            
            LOG_LORA_RX("Frame validation: %s", 
                       (loraFrameStatus == STATUS::RETRANSMIT_FRAME) ? "RETRANSMIT" :
                       (loraFrameStatus == STATUS::VALID_FRAME) ? "VALID" :
                       (loraFrameStatus == STATUS::CONFIG_FRAME) ? "CONFIG" : "INVALID");

            if (loraFrameStatus == STATUS::RETRANSMIT_FRAME || loraFrameStatus == STATUS::VALID_FRAME || loraFrameStatus == STATUS::CONFIG_FRAME) {
                uartHandler->transmitMessage(loraReceiveBuffer, loraReceivedBytes);
                LOG_UART2_HEX("TX", loraReceiveBuffer, loraReceivedBytes);
            }
        }

        memset(loraReceiveBuffer, 0, MAX_LORA_BUFFER_SIZE);
        loraReceivedBytes = 0;
        if (loraCommandParser) loraCommandParser->reset(1);
        HAL_GPIO_WritePin(loraRxLed->get_port(), loraRxLed->get_pin(), GPIO_PIN_RESET);
    }
}

void handleLoraTransmission() {
    if (!lora || !loraTxLed) return;
    
    if (pendingLoraTransmission && (currentOperationMode == OperationMode::TX_MODE || currentOperationMode == OperationMode::TX_RX_MODE)) {
        if (loraTransmitSizeBytes > 0) {
            HAL_GPIO_WritePin(loraTxLed->get_port(), loraTxLed->get_pin(), GPIO_PIN_SET);
            
            // Log LoRa transmit data
            LOG_LORA_TX_HEX("Transmitting", loraTransmitBuffer, loraTransmitSizeBytes);
            
            if (lora->transmit(loraTransmitBuffer, loraTransmitSizeBytes, LinkMode::DOWNLINK) == HAL_OK) {
                LOG_LORA_TX("Transmission successful");
                HAL_Delay(10);
                HAL_GPIO_WritePin(loraTxLed->get_port(), loraTxLed->get_pin(), GPIO_PIN_RESET);
            } else {
                HAL_GPIO_WritePin(loraTxLed->get_port(), loraTxLed->get_pin(), GPIO_PIN_RESET);
            }
            memset(loraTransmitBuffer, 0, MAX_LORA_BUFFER_SIZE);
            loraTransmitSizeBytes = 0;
            pendingLoraTransmission = false;
        }
    }
}

// ============================================================================
// ENHANCED TAG SIMULATION FUNCTIONS (Python-compatible implementation)
// ============================================================================

/**
 * @brief Calculate valid x range where both distances are <= max_distance
 * Equivalent to Python's calculate_x_limits function
 * @param y_const: Constant Y value 
 * @param max_distance: Maximum allowed distance
 * @param x_min: Output minimum X value
 * @param x_max: Output maximum X value
 */
void calculateXLimits(float y_const, float max_distance, float* x_min, float* x_max) {
    if (!x_min || !x_max) return;
    
    // From distance_b equation: sqrt(x² + y_const²) <= max_distance
    float x_max_b = sqrtf(max_distance * max_distance - y_const * y_const);
    
    // From distance_a equation: sqrt((x + TRANSMITTER_DISTANCE)² + y_const²) <= max_distance
    float x_max_a = sqrtf(max_distance * max_distance - y_const * y_const) - TRANSMITTER_DISTANCE;
    
    // Take the minimum of both limits
    float x_limit = (x_max_b < x_max_a) ? x_max_b : x_max_a;
    *x_min = -x_limit;
    *x_max = x_limit;
}

/**
 * @brief Generate data points with distances <= MAX_DISTANCE_A (constant Y)
 * Equivalent to Python's generate_data_constant_y function
 * @param tags: Array to store generated tag data
 * @param num_points: Number of points to generate
 */
void generateDataConstantY(TagWithDistance* tags, uint8_t num_points) {
    if (!tags || num_points == 0) return;
    
    float x_min, x_max;
    calculateXLimits(Y_CONST, MAX_DISTANCE_A, &x_min, &x_max);
    
    uint8_t generated = 0;
    uint16_t attempts = 0;
    const uint16_t max_attempts = num_points * 10; // Prevent infinite loop
    
    while (generated < num_points && attempts < max_attempts) {
        attempts++;
        
        // Generate random X within valid range
        float x = ((float)getRandomNumber(0, 10000) / 10000.0f) * (x_max - x_min) + x_min;
        
        // Calculate distances
        float distance_a = sqrtf((x + TRANSMITTER_DISTANCE) * (x + TRANSMITTER_DISTANCE) + Y_CONST * Y_CONST);
        float distance_b = sqrtf(x * x + Y_CONST * Y_CONST);
        
        // Verify distances are within limit
        if (distance_a <= MAX_DISTANCE_A && distance_b <= MAX_DISTANCE_A) {
            tags[generated].tag_id = getRandomNumber(0xAAAAAAAA, 0xFFFFFFFF);
            tags[generated].distance_a = distance_a;
            tags[generated].distance_b = distance_b;
            tags[generated].battery = ((float)getRandomNumber(250, 420)) / 100.0f; // 2.5V to 4.2V
            tags[generated].x = x;
            tags[generated].y = Y_CONST;
            generated++;
        }
    }
}

/**
 * @brief Generate random data for multiple detection with variable distances
 * Equivalent to Python's _generate_random_multiple_detection_data function
 * @param tags: Array to store generated tag data
 * @param num_tags: Number of tags to generate
 */
void generateRandomMultipleDetectionData(TagWithDistance* tags, uint8_t num_tags) {
    if (!tags || num_tags == 0) return;
    
    for (uint8_t i = 0; i < num_tags; i++) {
        float max_distance = MAX_DISTANCE_A;
        float distance_a, distance_b;
        
        // Randomly decide if distance_a is greater or less than distance_b
        if (getRandomNumber(0, 1)) {
            // distance_a first, then adjust distance_b
            distance_a = ((float)getRandomNumber(0, 10000) / 10000.0f) * max_distance;
            float min_b = (distance_a - MAX_DISTANCE_DIFF) > 0 ? (distance_a - MAX_DISTANCE_DIFF) : 0;
            float max_b = (distance_a + MAX_DISTANCE_DIFF) < max_distance ? (distance_a + MAX_DISTANCE_DIFF) : max_distance;
            distance_b = ((float)getRandomNumber(0, 10000) / 10000.0f) * (max_b - min_b) + min_b;
        } else {
            // distance_b first, then adjust distance_a
            distance_b = ((float)getRandomNumber(0, 10000) / 10000.0f) * max_distance;
            float min_a = (distance_b - MAX_DISTANCE_DIFF) > 0 ? (distance_b - MAX_DISTANCE_DIFF) : 0;
            float max_a = (distance_b + MAX_DISTANCE_DIFF) < max_distance ? (distance_b + MAX_DISTANCE_DIFF) : max_distance;
            distance_a = ((float)getRandomNumber(0, 10000) / 10000.0f) * (max_a - min_a) + min_a;
        }
        
        tags[i].tag_id = i; // Simple incremental ID
        tags[i].distance_a = distance_a;
        tags[i].distance_b = distance_b;
        tags[i].battery = ((float)getRandomNumber(250, 420)) / 100.0f; // 2.5V to 4.2V
        tags[i].x = 0.0f; // Not calculated for this mode
        tags[i].y = 0.0f; // Not calculated for this mode
    }
}

/**
 * @brief Generate random data for one detection (alerts)
 * Equivalent to Python's _generate_random_one_detection_data function
 * @param tags: Array to store generated tag data
 * @param num_tags: Number of tags to generate
 */
void generateRandomOneDetectionData(TagSimple* tags, uint8_t num_tags) {
    if (!tags || num_tags == 0) return;
    
    for (uint8_t i = 0; i < num_tags; i++) {
        tags[i].tag_id = getRandomNumber(0, 200); // Tag ID range 0-200 as in Python
        tags[i].battery = getRandomNumber(25, 42); // Battery 2.5V-4.2V (stored as 25-42)
    }
}

/**
 * @brief Build Multiple Detection frame (0x18)
 * Equivalent to Python's build_multiple_detection_frame function
 * @param sniffer_id: Sniffer identifier (1-5)
 * @param tags: Array of tag data with distances
 * @param num_tags: Number of tags in the frame
 * @param buffer: Output buffer for the frame
 * @param dataSize: Output size of the generated frame
 */
void buildMultipleDetectionFrame(uint32_t sniffer_id, TagWithDistance* tags, uint8_t num_tags, uint8_t* buffer, size_t* dataSize) {
    if (!buffer || !dataSize || !tags || num_tags == 0) return;
    
    memset(buffer, 0, MAX_LORA_BUFFER_SIZE);
    
    size_t offset = 0;
    
    // Write sniffer_id directly as 4 bytes (little-endian)
    buffer[offset++] = sniffer_id & 0xFF;
    buffer[offset++] = (sniffer_id >> 8) & 0xFF;
    buffer[offset++] = (sniffer_id >> 16) & 0xFF;
    buffer[offset++] = (sniffer_id >> 24) & 0xFF;

    // Total tags registered (1 byte)
    buffer[offset++] = num_tags;
    
    // Tags in this frame (1 byte)
    buffer[offset++] = num_tags;
    
    // Tag data: each tag = 4 bytes ID + 2 bytes distance_a + 2 bytes distance_b + 1 byte battery = 9 bytes per tag
    for (uint8_t i = 0; i < num_tags && offset + 9 <= MAX_LORA_BUFFER_SIZE; i++) {
        // Tag ID (4 bytes, little-endian)
        buffer[offset++] = tags[i].tag_id & 0xFF;
        buffer[offset++] = (tags[i].tag_id >> 8) & 0xFF;
        buffer[offset++] = (tags[i].tag_id >> 16) & 0xFF;
        buffer[offset++] = (tags[i].tag_id >> 24) & 0xFF;
        
        // Distance A (2 bytes, centimeters)
        uint16_t dist_a_cm = (uint16_t)(tags[i].distance_a * 100); // Convert to centimeters
        buffer[offset++] = dist_a_cm & 0xFF;
        buffer[offset++] = (dist_a_cm >> 8) & 0xFF;
        
        // Distance B (2 bytes, centimeters)
        uint16_t dist_b_cm = (uint16_t)(tags[i].distance_b * 100); // Convert to centimeters
        buffer[offset++] = dist_b_cm & 0xFF;
        buffer[offset++] = (dist_b_cm >> 8) & 0xFF;
        
        // Battery (1 byte, multiplied by 10)
        uint8_t battery = (uint8_t)(tags[i].battery * 10); // Convert 2.5V-4.2V to 25-42
        buffer[offset++] = battery;
    }

    *dataSize = offset;
}

/**
 * @brief Build One Detection frame (0x17)
 * Equivalent to Python's build_one_detection_frame function
 * @param sniffer_id: Sniffer identifier (32-bit integer)
 * @param tags: Array of simple tag data
 * @param num_tags: Number of tags in the frame
 * @param buffer: Output buffer for the frame
 * @param dataSize: Output size of the generated frame
 */
void buildOneDetectionFrame(uint32_t sniffer_id, TagSimple* tags, uint8_t num_tags, uint8_t* buffer, size_t* dataSize) {
    if (!buffer || !dataSize || !tags || num_tags == 0) return;
    
    memset(buffer, 0, MAX_LORA_BUFFER_SIZE);
    
    size_t offset = 0;
    
    // Write sniffer_id directly as 4 bytes (little-endian)
    buffer[offset++] = sniffer_id & 0xFF;
    buffer[offset++] = (sniffer_id >> 8) & 0xFF;
    buffer[offset++] = (sniffer_id >> 16) & 0xFF;
    buffer[offset++] = (sniffer_id >> 24) & 0xFF;
    
    // Total tags registered (1 byte)
    buffer[offset++] = num_tags;

    // Tags in this frame (1 byte)
    buffer[offset++] = num_tags;
    
    // Tag data: each tag = 4 bytes ID + 1 byte battery = 5 bytes per tag
    for (uint8_t i = 0; i < num_tags && offset + 5 <= MAX_LORA_BUFFER_SIZE; i++) {
        // Tag ID (4 bytes, little-endian)
        buffer[offset++] = tags[i].tag_id & 0xFF;
        buffer[offset++] = (tags[i].tag_id >> 8) & 0xFF;
        buffer[offset++] = (tags[i].tag_id >> 16) & 0xFF;
        buffer[offset++] = (tags[i].tag_id >> 24) & 0xFF;
        
        // Battery (1 byte, already in correct format)
        buffer[offset++] = tags[i].battery;
    }

    *dataSize = offset;
}

/**
 * @brief Main enhanced simulation function matching Python logic
 * Implements the same logic as Python's main() function
 * @param buffer: Output buffer for the frame
 * @param dataSize: Output size of the generated frame
 * @param commandId: Output command ID for the generated frame (0x17 or 0x18)
 */
void enhancedTagSimulation(uint8_t* buffer, size_t* dataSize, uint8_t* commandId) {
    if (!buffer || !dataSize || !commandId) return;
    
    // Generate random sniffer ID (1-5)
    uint32_t sniffer_id = getRandomNumber(1, MAX_SNIFFERS);
    
    // Generate random number of tags (0-24)
    uint8_t num_tags = getRandomNumber(0, MAX_TAGS_PER_FRAME);
    
    if (num_tags == 0) {
        *dataSize = 0;
        *commandId = ONE_DETECTION; // Default
        return;
    }

    // Python logic: if multiple_sniffer_id == sniffer_id, use multiple detection
    if (multiple_sniffer_id == sniffer_id) {
        // Multiple Detection with constant Y positioning
        TagWithDistance tags[MAX_TAGS_PER_FRAME];
        generateDataConstantY(tags, num_tags);
        buildMultipleDetectionFrame(sniffer_id, tags, num_tags, buffer, dataSize);
        *commandId = MULTIPLE_DETECTION;
    } else {
        // One Detection (simple alerts)
        TagSimple tags[MAX_TAGS_PER_FRAME];
        generateRandomOneDetectionData(tags, num_tags);
        buildOneDetectionFrame(sniffer_id, tags, num_tags, buffer, dataSize);
        *commandId = ONE_DETECTION;
    }
    
    // Update state variables (Python logic)
    received_sniffer_id = sniffer_id;
    if (multiple_sniffer_id == received_sniffer_id) {
        multiple_sniffer_id = 0; // Reset for next cycle
    } else {
        // Randomly set multiple_sniffer_id for next iteration
        if (getRandomNumber(0, 3) == 0) { // 25% chance
            multiple_sniffer_id = sniffer_id;
        }
    }
}

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_I2C1_Init();
  MX_SPI1_Init();
  MX_USART1_UART_Init(); // Assuming USART1 is for debug/other
  MX_USART2_UART_Init(); // Main communication UART
  MX_USART3_UART_Init(); // Assuming USART3 is for other
  MX_ADC1_Init();
  MX_CRC_Init();
 // MX_IWDG_Init(); // Independent Watchdog, enable if needed
  /* USER CODE BEGIN 2 */
    // Initialize Logger first (needs UART3 to be initialized)
    Logger& logger = Logger::getInstance();
    logger.init();
    
    // Print version information at startup
    LOG_SYSTEM("=== LoRa Gateway Starting ===");
    LOG_SYSTEM("Version: %s", FIRMWARE_VERSION);
    LOG_SYSTEM("Build: %s %s", BUILD_DATE, BUILD_TIME);
    LOG_SYSTEM("Operation Mode: %s", 
               (FIRMWARE_OPERATION_MODE == OperationMode::RX_MODE) ? "RX" :
               (FIRMWARE_OPERATION_MODE == OperationMode::TX_MODE) ? "TX" : "TX_RX");
    LOG_SYSTEM("Main communication: UART2 (USART2)");
    LOG_SYSTEM("Logger output: UART3 (USART3) RS485");

    // Crear instancias de todos los objetos después de que se haya inicializado el hardware
    uartHandler = new UartHandler(&huart2);
    eepromMemory = new Memory(&hi2c1);
    
    loraNssPin = new Gpio(LORA_NSS_GPIO_Port, LORA_NSS_Pin);
    loraRstPin = new Gpio(LORA_RST_GPIO_Port, LORA_RST_Pin);
    
    // Lora necesita ser inicializada después de sus dependencias Gpio y Memory
    lora = new Lora(*loraNssPin, *loraRstPin, &hspi1, eepromMemory);
    
    loraRxLed = new Gpio(LORA_RX_OK_GPIO_Port, LORA_RX_OK_Pin);
    loraTxLed = new Gpio(LORA_TX_OK_GPIO_Port, LORA_TX_OK_Pin);
    keepAliveLed = new Gpio(KEEP_ALIVE_GPIO_Port, KEEP_ALIVE_Pin);
    
    uartCommandParser = new CommandMessage(static_cast<uint8_t>(DEVICE_MODULE_FUNCTION), DEVICE_ID);
    loraCommandParser = new CommandMessage(static_cast<uint8_t>(MODULE_FUNCTION::SNIFFER), 0x00);
    uartSimulatedCommandParse = new CommandMessage(0x00, 0x00); // MODULE_FUNCTION=0x00, MODULE_ID=0x00 para simulación

    

    // Configurar los objetos ahora que están creados
    lora->check_already_store_data();
    
    // FIXED: Proper UART interrupt setup for single-byte reception
    // Start with single byte reception instead of multi-byte
    // This allows proper frame assembly with start/end delimiter detection
    HAL_UART_Receive_IT(&huart2, uartReceiveBuffer, 1);
    // uartHandler->enable_receive_interrupt(1); // Replaced with direct HAL call
    
    // Inicializar configuración por defecto para simulación de sniffer
    initializeDefaultDeviceConfig();

  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
    while (1) {
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
        // 1. Process any new UART data
        if (newUartDataReceived) {
            processUartCommand();
        }

        // Check if 1-second blocking period has expired
        if (blockLoraReception && (HAL_GetTick() - blockStartTime >= BLOCK_DURATION_MS)) {
            blockLoraReception = false;
        }
        
        // Block all other functions if UART processing is active
        if (!blockLoraReception) {
            // 2. Handle LoRa Transmission if data is pending and mode allows
            if (pendingLoraTransmission) {
                if (currentOperationMode == OperationMode::TX_MODE || currentOperationMode == OperationMode::TX_RX_MODE) {
                    handleLoraTransmission();
                }
            }
            
            // 3. Handle LoRa Reception if mode allows
            if (!pendingLoraTransmission && (currentOperationMode == OperationMode::RX_MODE || currentOperationMode == OperationMode::TX_RX_MODE)) {
                handleLoraReception();
            }
            
            // 4. Handle Sniffer Simulation if enabled
            handleSnifferSimulation();

            // Keep-alive LED blinking
            if (keepAliveLed) {
                if (HAL_GetTick() - keepAliveLastTick > 1000) {
                    keepAliveLastTick = HAL_GetTick();
                    HAL_GPIO_WritePin(keepAliveLed->get_port(), keepAliveLed->get_pin(), GPIO_PIN_SET);
                } else {
                    if (HAL_GetTick() - keepAliveLastTick > 500) {
                        HAL_GPIO_WritePin(keepAliveLed->get_port(), keepAliveLed->get_pin(), GPIO_PIN_RESET);
                    }
                }
            }
            
            // Logger heartbeat every 30 seconds
            if (HAL_GetTick() - loggerHeartbeatLastTick > 30000) {
                loggerHeartbeatLastTick = HAL_GetTick();
                Logger::getInstance().logHeartbeat();
            }
        }
        //HAL_IWDG_Refresh(&hiwdg);
    }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};
  RCC_PeriphCLKInitTypeDef PeriphClkInit = {0};

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_LSI|RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.HSEPredivValue = RCC_HSE_PREDIV_DIV1;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON; // Keep HSI on if needed, otherwise can be off if HSE is stable
  RCC_OscInitStruct.LSIState = RCC_LSI_ON; // For IWDG
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL2; // Example: 8MHz HSE * 2 = 16MHz PLLCLK
                                               // Adjust PLLMUL based on your HSE and desired SYSCLK
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2; // PCLK1 max typically 36MHz for STM32F1
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1; // PCLK2 can be higher

  // Adjust Flash Latency based on HCLK frequency
  // For HCLK <= 24MHz, LATENCY_0 is fine.
  // For 24MHz < HCLK <= 48MHz, LATENCY_1.
  // For 48MHz < HCLK <= 72MHz, LATENCY_2.
  // Example: if HSE=8MHz, PLLMUL=9 => SYSCLK=72MHz, HCLK=72MHz. Then FLASH_LATENCY_2.
  // If HSE=8MHz, PLLMUL=2 => SYSCLK=16MHz, HCLK=16MHz. Then FLASH_LATENCY_0.
  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_0) != HAL_OK) // Adjust FLASH_LATENCY if HCLK > 24MHz
  {
    Error_Handler();
  }
  PeriphClkInit.PeriphClockSelection = RCC_PERIPHCLK_ADC;
  PeriphClkInit.AdcClockSelection = RCC_ADCPCLK2_DIV2; // ADC Clock, e.g., PCLK2/2
                                                       // Ensure ADC clock doesn't exceed its max (e.g. 14MHz for STM32F1)
  if (HAL_RCCEx_PeriphCLKConfig(&PeriphClkInit) != HAL_OK)
  {
    Error_Handler();
  }
}

// ... (MX_ADC1_Init, MX_CRC_Init, MX_I2C1_Init, MX_IWDG_Init, MX_SPI1_Init,
//      MX_USART1_UART_Init, MX_USART2_UART_Init, MX_USART3_UART_Init, MX_GPIO_Init
//      remain largely the same as in the provided snippets, ensure they match your CubeMX configuration)
// ... (Error_Handler, assert_failed also remain the same)

/**
  * @brief ADC1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_ADC1_Init(void)
{

  /* USER CODE BEGIN ADC1_Init 0 */

  /* USER CODE END ADC1_Init 0 */

  ADC_ChannelConfTypeDef sConfig = {0};

  /* USER CODE BEGIN ADC1_Init 1 */

  /* USER CODE END ADC1_Init 1 */

  /** Common config
  */
  hadc1.Instance = ADC1;
  hadc1.Init.ScanConvMode = ADC_SCAN_ENABLE; // Or ADC_SCAN_DISABLE if single channel
  hadc1.Init.ContinuousConvMode = DISABLE;
  hadc1.Init.DiscontinuousConvMode = DISABLE;
  hadc1.Init.ExternalTrigConv = ADC_SOFTWARE_START;
  hadc1.Init.DataAlign = ADC_DATAALIGN_RIGHT;
  hadc1.Init.NbrOfConversion = 1; // Adjust if more conversions are needed in a scan
  if (HAL_ADC_Init(&hadc1) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure Regular Channel
  */
  sConfig.Channel = ADC_CHANNEL_0; // Example channel, configure as needed
  sConfig.Rank = ADC_REGULAR_RANK_1;
  sConfig.SamplingTime = ADC_SAMPLETIME_239CYCLES_5; // Adjust as needed
  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN ADC1_Init 2 */
  // Add other channels if NbrOfConversion > 1
  /* USER CODE END ADC1_Init 2 */

}

/**
  * @brief CRC Initialization Function
  * @param None
  * @retval None
  */
static void MX_CRC_Init(void)
{

  /* USER CODE BEGIN CRC_Init 0 */

  /* USER CODE END CRC_Init 0 */

  /* USER CODE BEGIN CRC_Init 1 */

  /* USER CODE END CRC_Init 1 */
  hcrc.Instance = CRC;
  if (HAL_CRC_Init(&hcrc) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN CRC_Init 2 */

  /* USER CODE END CRC_Init 2 */

}

/**
  * @brief I2C1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_I2C1_Init(void)
{

  /* USER CODE BEGIN I2C1_Init 0 */

  /* USER CODE END I2C1_Init 0 */

  /* USER CODE BEGIN I2C1_Init 1 */

  /* USER CODE END I2C1_Init 1 */
  hi2c1.Instance = I2C1;
  hi2c1.Init.ClockSpeed = 400000; // Fast mode
  hi2c1.Init.DutyCycle = I2C_DUTYCYCLE_2;
  hi2c1.Init.OwnAddress1 = 0;
  hi2c1.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;
  hi2c1.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;
  hi2c1.Init.OwnAddress2 = 0;
  hi2c1.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;
  hi2c1.Init.NoStretchMode = I2C_NOSTRETCH_DISABLE;
  if (HAL_I2C_Init(&hi2c1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN I2C1_Init 2 */

  /* USER CODE END I2C1_Init 2 */

}

/**
  * @brief IWDG Initialization Function
  * @param None
  * @retval None
  */
static void MX_IWDG_Init(void)
{

  /* USER CODE BEGIN IWDG_Init 0 */

  /* USER CODE END IWDG_Init 0 */

  /* USER CODE BEGIN IWDG_Init 1 */
  // IWDG timeout = (LSI_VALUE / Prescaler) * Reload_value
  // LSI_VALUE is typically 40kHz for STM32F1.
  // Timeout = (40000 / 128) * 1875 = 312.5 * 1875 = 585937.5 us approx 0.58 seconds
  // Max reload value is 0xFFF (4095).
  // For a longer timeout, increase prescaler (max 256) or reload.
  /* USER CODE END IWDG_Init 1 */
  hiwdg.Instance = IWDG;
  hiwdg.Init.Prescaler = IWDG_PRESCALER_256;
  hiwdg.Init.Reload = 782; // Results in ~0.58s timeout with 40kHz LSI
  if (HAL_IWDG_Init(&hiwdg) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN IWDG_Init 2 */

  /* USER CODE END IWDG_Init 2 */

}

/**
  * @brief SPI1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_SPI1_Init(void)
{

  /* USER CODE BEGIN SPI1_Init 0 */

  /* USER CODE END SPI1_Init 0 */

  /* USER CODE BEGIN SPI1_Init 1 */

  /* USER CODE END SPI1_Init 1 */
  /* SPI1 parameter configuration*/
  hspi1.Instance = SPI1;
  hspi1.Init.Mode = SPI_MODE_MASTER;
  hspi1.Init.Direction = SPI_DIRECTION_2LINES;
  hspi1.Init.DataSize = SPI_DATASIZE_8BIT;
  hspi1.Init.CLKPolarity = SPI_POLARITY_LOW; // LoRa modules usually CPOL=0, CPHA=0 (SPI_PHASE_1EDGE)
  hspi1.Init.CLKPhase = SPI_PHASE_1EDGE;
  hspi1.Init.NSS = SPI_NSS_SOFT; // NSS pin controlled by software
  // BaudRatePrescaler: PCLK2 / Prescaler. If PCLK2 is 16MHz (from PLLMUL=2, HCLK_DIV1)
  // SPI_BAUDRATEPRESCALER_16 => 16MHz/16 = 1MHz.
  // LoRa SX127x max SPI freq is 10MHz. Adjust if PCLK2 is different.
  hspi1.Init.BaudRatePrescaler = SPI_BAUDRATEPRESCALER_16;
  hspi1.Init.FirstBit = SPI_FIRSTBIT_MSB;
  hspi1.Init.TIMode = SPI_TIMODE_DISABLE;
  hspi1.Init.CRCCalculation = SPI_CRCCALCULATION_DISABLE;
  hspi1.Init.CRCPolynomial = 10;
  if (HAL_SPI_Init(&hspi1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN SPI1_Init 2 */

  /* USER CODE END SPI1_Init 2 */

}

/**
  * @brief USART1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART1_UART_Init(void)
{

  /* USER CODE BEGIN USART1_Init 0 */

  /* USER CODE END USART1_Init 0 */

  /* USER CODE BEGIN USART1_Init 1 */

  /* USER CODE END USART1_Init 1 */
  huart1.Instance = USART1;
  huart1.Init.BaudRate = 115200;
  huart1.Init.WordLength = UART_WORDLENGTH_8B;
  huart1.Init.StopBits = UART_STOPBITS_1;
  huart1.Init.Parity = UART_PARITY_NONE;
  huart1.Init.Mode = UART_MODE_TX_RX;
  huart1.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart1.Init.OverSampling = UART_OVERSAMPLING_16;
  if (HAL_UART_Init(&huart1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART1_Init 2 */

  /* USER CODE END USART1_Init 2 */

}

/**
  * @brief USART2 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART2_UART_Init(void)
{

  /* USER CODE BEGIN USART2_Init 0 */

  /* USER CODE END USART2_Init 0 */

  /* USER CODE BEGIN USART2_Init 1 */

  /* USER CODE END USART2_Init 1 */
  huart2.Instance = USART2;
  huart2.Init.BaudRate = 115200; // Main communication UART
  huart2.Init.WordLength = UART_WORDLENGTH_8B;
  huart2.Init.StopBits = UART_STOPBITS_1;
  huart2.Init.Parity = UART_PARITY_NONE;
  huart2.Init.Mode = UART_MODE_TX_RX;
  huart2.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart2.Init.OverSampling = UART_OVERSAMPLING_16;
  if (HAL_UART_Init(&huart2) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART2_Init 2 */

  /* USER CODE END USART2_Init 2 */

}

/**
  * @brief USART3 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART3_UART_Init(void)
{

  /* USER CODE BEGIN USART3_Init 0 */

  /* USER CODE END USART3_Init 0 */

  /* USER CODE BEGIN USART3_Init 1 */

  /* USER CODE END USART3_Init 1 */
  huart3.Instance = USART3;
  huart3.Init.BaudRate = 115200;
  huart3.Init.WordLength = UART_WORDLENGTH_8B;
  huart3.Init.StopBits = UART_STOPBITS_1;
  huart3.Init.Parity = UART_PARITY_NONE;
  huart3.Init.Mode = UART_MODE_TX_RX;
  huart3.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart3.Init.OverSampling = UART_OVERSAMPLING_16;
  if (HAL_UART_Init(&huart3) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART3_Init 2 */

  /* USER CODE END USART3_Init 2 */

}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};
/* USER CODE BEGIN MX_GPIO_Init_1 */
/* USER CODE END MX_GPIO_Init_1 */

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOD_CLK_ENABLE(); // For HSE if on PD0/PD1
  __HAL_RCC_GPIOA_CLK_ENABLE(); // For USARTs, SPI, Lora DIOs etc.
  __HAL_RCC_GPIOB_CLK_ENABLE(); // For I2C, Lora NSS/RST, LEDs etc.

  /*Configure GPIO pin Output Level */
  // Initialize all relevant output pins to a known state (e.g., RESET)
  // This includes LORA_NSS, LORA_RST, LEDs, RS485_DE, BUZZER
  HAL_GPIO_WritePin(GPIOB, LORA_NSS_Pin|LORA_RST_Pin|LORA_DIO3_Pin|LORA_DIO1_Pin // These DIOs might be inputs for LoRa lib
                          |LORA_BUSSY_Pin|LORA_TX_OK_Pin|LORA_RX_OK_Pin|KEEP_ALIVE_Pin
                          |RS485_DE_Pin|BUZZER_Pin, GPIO_PIN_RESET);
  // Ensure LORA_NSS is high (inactive) initially if not handled by LoRa class constructor
  HAL_GPIO_WritePin(LORA_NSS_GPIO_Port, LORA_NSS_Pin, GPIO_PIN_SET);


  /*Configure GPIO pins : LORA_NSS_Pin LORA_RST_Pin LORA_TX_OK_Pin LORA_RX_OK_Pin
                           KEEP_ALIVE_Pin RS485_DE_Pin BUZZER_Pin */
  GPIO_InitStruct.Pin = LORA_NSS_Pin|LORA_RST_Pin|LORA_TX_OK_Pin|LORA_RX_OK_Pin
                          |KEEP_ALIVE_Pin|RS485_DE_Pin|BUZZER_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOB, &GPIO_InitStruct); // Assuming all these are on GPIOB

  /* Configure LoRa DIO pins as Inputs (example, adjust based on actual LoRa library usage) */
  // DIO0 is typically IRQ for TxDone, RxDone, CadDone
  // DIO1, DIO2, DIO3, DIO4, DIO5 can have various functions.
  // The LoRa library should handle their configuration if it uses them.
  // If you manually check them, configure them as inputs.
  // Example for DIO0:
  // GPIO_InitStruct.Pin = LORA_DIO0_Pin; // Assuming LORA_DIO0_Pin is defined
  // GPIO_InitStruct.Mode = GPIO_MODE_IT_RISING; // Or GPIO_MODE_INPUT
  // GPIO_InitStruct.Pull = GPIO_NOPULL; // Or GPIO_PULLDOWN if required
  // HAL_GPIO_Init(LORA_DIO0_GPIO_Port, &GPIO_InitStruct); // Assuming LORA_DIO0_GPIO_Port is defined

  // LORA_BUSSY_Pin might be an input if it's reflecting the radio's busy state.
  // If LORA_DIO1_Pin, LORA_DIO3_Pin, LORA_BUSSY_Pin are actually inputs from LoRa module:
  GPIO_InitStruct.Pin = LORA_DIO1_Pin|LORA_DIO3_Pin|LORA_BUSSY_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_NOPULL; // Or specific pull-up/down if needed
  HAL_GPIO_Init(GPIOB, &GPIO_InitStruct); // Assuming these are also on GPIOB


/* USER CODE BEGIN MX_GPIO_Init_2 */
/* USER CODE END MX_GPIO_Init_2 */
}

/* USER CODE BEGIN 4 */
// Any other custom functions can go here
/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  
  // Try to log the error before disabling interrupts
  LOG_CRITICAL(LogSource::ERROR_SRC, "CRITICAL ERROR - System entering error handler");
  LOG_CRITICAL(LogSource::ERROR_SRC, "Device requires reset - Uptime: %lu ms", HAL_GetTick());
  
  __disable_irq(); // Disable interrupts to prevent further issues
  // Blink an error LED or send an error message via a debug UART if possible
  while (1)
  {
      // Infinite loop, device needs reset
      // Consider toggling an LED rapidly to indicate critical error
      HAL_GPIO_TogglePin(KEEP_ALIVE_GPIO_Port, KEEP_ALIVE_Pin); // Example: Use keep_alive_led for error
      HAL_Delay(100); // Fast blink
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  // For production, this might log to EEPROM or a non-volatile memory location.
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
