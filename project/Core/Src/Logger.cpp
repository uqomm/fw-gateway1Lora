/*
 * Logger.cpp
 *
 *  Created on: Oct 16, 2025
 *      Author: artur
 */

#include "Logger.hpp"
#include "Lora.hpp"
#include <cstdarg>
#include <algorithm>

// Include version information (same as main.cpp)
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

// External UART handle declarations (from main.cpp)
extern UART_HandleTypeDef huart3;

// Static instance for singleton
Logger* Logger::instance = nullptr;

Logger::Logger() : initialized(false), message_counter(0) {
    memset(buffer, 0, LOGGER_BUFFER_SIZE);
}

Logger& Logger::getInstance() {
    if (instance == nullptr) {
        instance = new Logger();
    }
    return *instance;
}

bool Logger::init() {
    if (initialized) {
        return true;
    }
    
    // Initialize RS485 DE pin as output
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    GPIO_InitStruct.Pin = RS485_DE_Pin;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(RS485_DE_GPIO_Port, &GPIO_InitStruct);
    
    // Ensure RS485 is in receive mode initially
    disableRS485TX();
    
    initialized = true;
    
    // Send startup message
    logStartup();
    
    return true;
}

void Logger::enableRS485TX() {
    HAL_GPIO_WritePin(RS485_DE_GPIO_Port, RS485_DE_Pin, GPIO_PIN_SET);
    // Small delay to ensure driver is enabled
    for (volatile uint32_t i = 0; i < LOGGER_RS485_DE_DELAY_US * 8; i++) {
        __NOP();
    }
}

void Logger::disableRS485TX() {
    HAL_GPIO_WritePin(RS485_DE_GPIO_Port, RS485_DE_Pin, GPIO_PIN_RESET);
}

void Logger::sendToUART3(const char* message, uint16_t length) {
    if (!initialized || length == 0) {
        return;
    }
    
    enableRS485TX();
    
    HAL_StatusTypeDef status = HAL_UART_Transmit(&huart3, (uint8_t*)message, length, LOGGER_UART_TIMEOUT);
    
    // Wait for transmission to complete
    while (HAL_UART_GetState(&huart3) != HAL_UART_STATE_READY) {
        HAL_Delay(1);
    }
    
    disableRS485TX();
    
    if (status == HAL_OK) {
        message_counter++;
    }
}

const char* Logger::getLevelString(LogLevel level) {
    switch (level) {
        case LogLevel::LOG_DEBUG:    return "DBG";
        case LogLevel::LOG_INFO:     return "INF";
        case LogLevel::LOG_WARNING:  return "WRN";
        case LogLevel::LOG_ERROR:    return "ERR";
        case LogLevel::LOG_CRITICAL: return "CRT";
        default: return "UNK";
    }
}

const char* Logger::getSourceString(LogSource source) {
    switch (source) {
        case LogSource::SYSTEM:   return "SYS";
        case LogSource::UART2:    return "U2 ";
        case LogSource::LORA_RX:  return "LRX";
        case LogSource::LORA_TX:  return "LTX";
        case LogSource::COMMAND:  return "CMD";
        case LogSource::CONFIG:   return "CFG";
        case LogSource::ERROR_SRC: return "ERR";
        default: return "UNK";
    }
}

uint32_t Logger::getCurrentTick() {
    return HAL_GetTick();
}

void Logger::log(LogLevel level, LogSource source, const char* format, ...) {
    if (!initialized) {
        return;
    }
    
    // Prepare timestamp and header
    uint32_t timestamp = getCurrentTick();
    int header_len = snprintf(buffer, LOGGER_BUFFER_SIZE, 
                             "[%08lu] %s:%s ", 
                             timestamp,
                             getLevelString(level),
                             getSourceString(source));
    
    if (header_len < 0 || header_len >= LOGGER_BUFFER_SIZE) {
        return;
    }
    
    // Format the actual message
    va_list args;
    va_start(args, format);
    int message_len = vsnprintf(buffer + header_len, 
                               LOGGER_BUFFER_SIZE - header_len - 2, 
                               format, args);
    va_end(args);
    
    if (message_len < 0) {
        return;
    }
    
    // Add newline and null terminator
    int total_len = header_len + message_len;
    if (total_len < LOGGER_BUFFER_SIZE - 2) {
        buffer[total_len] = '\r';
        buffer[total_len + 1] = '\n';
        total_len += 2;
    }
    
    sendToUART3(buffer, total_len);
}

void Logger::logHex(LogLevel level, LogSource source, const char* prefix, const uint8_t* data, uint16_t length) {
    if (!initialized || data == nullptr || length == 0) {
        return;
    }
    
    // Limit hex dump size to prevent buffer overflow
    uint16_t max_bytes = std::min(length, (uint16_t)((LOGGER_MAX_MESSAGE_SIZE - 50) / 3));
    
    // Prepare timestamp and header
    uint32_t timestamp = getCurrentTick();
    int header_len = snprintf(buffer, LOGGER_BUFFER_SIZE,
                             "[%08lu] %s:%s %s[%d]: ",
                             timestamp,
                             getLevelString(level),
                             getSourceString(source),
                             prefix ? prefix : "HEX",
                             length);
    
    if (header_len < 0 || header_len >= LOGGER_BUFFER_SIZE - 10) {
        return;
    }
    
    // Add hex data
    int pos = header_len;
    for (uint16_t i = 0; i < max_bytes && pos < LOGGER_BUFFER_SIZE - 5; i++) {
        int hex_len = snprintf(buffer + pos, LOGGER_BUFFER_SIZE - pos, "%02X ", data[i]);
        if (hex_len <= 0) break;
        pos += hex_len;
    }
    
    // Add truncation indicator if needed
    if (max_bytes < length && pos < LOGGER_BUFFER_SIZE - 5) {
        pos += snprintf(buffer + pos, LOGGER_BUFFER_SIZE - pos, "...");
    }
    
    // Add newline
    if (pos < LOGGER_BUFFER_SIZE - 2) {
        buffer[pos] = '\r';
        buffer[pos + 1] = '\n';
        pos += 2;
    }
    
    sendToUART3(buffer, pos);
}

// Convenience methods for different sources
void Logger::logUART2(LogLevel level, const char* format, ...) {
    if (!initialized) return;
    
    va_list args;
    va_start(args, format);
    
    uint32_t timestamp = getCurrentTick();
    int header_len = snprintf(buffer, LOGGER_BUFFER_SIZE,
                             "[%08lu] %s:U2  ",
                             timestamp,
                             getLevelString(level));
    
    if (header_len > 0 && header_len < LOGGER_BUFFER_SIZE - 2) {
        int message_len = vsnprintf(buffer + header_len,
                                   LOGGER_BUFFER_SIZE - header_len - 2,
                                   format, args);
        if (message_len > 0) {
            int total_len = header_len + message_len;
            if (total_len < LOGGER_BUFFER_SIZE - 2) {
                buffer[total_len] = '\r';
                buffer[total_len + 1] = '\n';
                total_len += 2;
            }
            sendToUART3(buffer, total_len);
        }
    }
    
    va_end(args);
}

void Logger::logLoRaRX(LogLevel level, const char* format, ...) {
    if (!initialized) return;
    
    va_list args;
    va_start(args, format);
    
    uint32_t timestamp = getCurrentTick();
    int header_len = snprintf(buffer, LOGGER_BUFFER_SIZE,
                             "[%08lu] %s:LRX ",
                             timestamp,
                             getLevelString(level));
    
    if (header_len > 0 && header_len < LOGGER_BUFFER_SIZE - 2) {
        int message_len = vsnprintf(buffer + header_len,
                                   LOGGER_BUFFER_SIZE - header_len - 2,
                                   format, args);
        if (message_len > 0) {
            int total_len = header_len + message_len;
            if (total_len < LOGGER_BUFFER_SIZE - 2) {
                buffer[total_len] = '\r';
                buffer[total_len + 1] = '\n';
                total_len += 2;
            }
            sendToUART3(buffer, total_len);
        }
    }
    
    va_end(args);
}

void Logger::logLoRaTX(LogLevel level, const char* format, ...) {
    if (!initialized) return;
    
    va_list args;
    va_start(args, format);
    
    uint32_t timestamp = getCurrentTick();
    int header_len = snprintf(buffer, LOGGER_BUFFER_SIZE,
                             "[%08lu] %s:LTX ",
                             timestamp,
                             getLevelString(level));
    
    if (header_len > 0 && header_len < LOGGER_BUFFER_SIZE - 2) {
        int message_len = vsnprintf(buffer + header_len,
                                   LOGGER_BUFFER_SIZE - header_len - 2,
                                   format, args);
        if (message_len > 0) {
            int total_len = header_len + message_len;
            if (total_len < LOGGER_BUFFER_SIZE - 2) {
                buffer[total_len] = '\r';
                buffer[total_len + 1] = '\n';
                total_len += 2;
            }
            sendToUART3(buffer, total_len);
        }
    }
    
    va_end(args);
}

void Logger::logSystem(LogLevel level, const char* format, ...) {
    if (!initialized) return;
    
    va_list args;
    va_start(args, format);
    
    uint32_t timestamp = getCurrentTick();
    int header_len = snprintf(buffer, LOGGER_BUFFER_SIZE,
                             "[%08lu] %s:SYS ",
                             timestamp,
                             getLevelString(level));
    
    if (header_len > 0 && header_len < LOGGER_BUFFER_SIZE - 2) {
        int message_len = vsnprintf(buffer + header_len,
                                   LOGGER_BUFFER_SIZE - header_len - 2,
                                   format, args);
        if (message_len > 0) {
            int total_len = header_len + message_len;
            if (total_len < LOGGER_BUFFER_SIZE - 2) {
                buffer[total_len] = '\r';
                buffer[total_len + 1] = '\n';
                total_len += 2;
            }
            sendToUART3(buffer, total_len);
        }
    }
    
    va_end(args);
}

void Logger::logCommand(LogLevel level, const char* format, ...) {
    if (!initialized) return;
    
    va_list args;
    va_start(args, format);
    
    uint32_t timestamp = getCurrentTick();
    int header_len = snprintf(buffer, LOGGER_BUFFER_SIZE,
                             "[%08lu] %s:CMD ",
                             timestamp,
                             getLevelString(level));
    
    if (header_len > 0 && header_len < LOGGER_BUFFER_SIZE - 2) {
        int message_len = vsnprintf(buffer + header_len,
                                   LOGGER_BUFFER_SIZE - header_len - 2,
                                   format, args);
        if (message_len > 0) {
            int total_len = header_len + message_len;
            if (total_len < LOGGER_BUFFER_SIZE - 2) {
                buffer[total_len] = '\r';
                buffer[total_len + 1] = '\n';
                total_len += 2;
            }
            sendToUART3(buffer, total_len);
        }
    }
    
    va_end(args);
}

void Logger::logConfig(LogLevel level, const char* format, ...) {
    if (!initialized) return;
    
    va_list args;
    va_start(args, format);
    
    uint32_t timestamp = getCurrentTick();
    int header_len = snprintf(buffer, LOGGER_BUFFER_SIZE,
                             "[%08lu] %s:CFG ",
                             timestamp,
                             getLevelString(level));
    
    if (header_len > 0 && header_len < LOGGER_BUFFER_SIZE - 2) {
        int message_len = vsnprintf(buffer + header_len,
                                   LOGGER_BUFFER_SIZE - header_len - 2,
                                   format, args);
        if (message_len > 0) {
            int total_len = header_len + message_len;
            if (total_len < LOGGER_BUFFER_SIZE - 2) {
                buffer[total_len] = '\r';
                buffer[total_len + 1] = '\n';
                total_len += 2;
            }
            sendToUART3(buffer, total_len);
        }
    }
    
    va_end(args);
}

// Hex data logging methods
void Logger::logUART2Hex(const char* prefix, const uint8_t* data, uint16_t length) {
    logHex(LogLevel::LOG_DEBUG, LogSource::UART2, prefix, data, length);
}

void Logger::logLoRaRXHex(const char* prefix, const uint8_t* data, uint16_t length) {
    logHex(LogLevel::LOG_INFO, LogSource::LORA_RX, prefix, data, length);
}

void Logger::logLoRaTXHex(const char* prefix, const uint8_t* data, uint16_t length) {
    logHex(LogLevel::LOG_INFO, LogSource::LORA_TX, prefix, data, length);
}

void Logger::logStartup() {
    if (!initialized) return;
    
    logSystem(LogLevel::LOG_INFO, "=== LoRa Gateway Logger Started ===");
    logSystem(LogLevel::LOG_INFO, "Firmware: %s", FIRMWARE_VERSION);
    logSystem(LogLevel::LOG_INFO, "Build: %s %s", BUILD_DATE, BUILD_TIME);
    logSystem(LogLevel::LOG_INFO, "RS485 Logger on UART3 @ 115200");
    logSystem(LogLevel::LOG_INFO, "DE Pin: PB8, TX: PB10, RX: PB11");
    logSystem(LogLevel::LOG_INFO, "===================================");
}

void Logger::logHeartbeat() {
    if (!initialized) return;
    
    uint32_t uptime_sec = HAL_GetTick() / 1000;
    uint32_t hours = uptime_sec / 3600;
    uint32_t minutes = (uptime_sec % 3600) / 60;
    uint32_t seconds = uptime_sec % 60;
    
    // Get LoRa parameters if LoRa object is available
    if (lora != nullptr) {
        uint32_t rx_freq = lora->get_rx_frequency();
        uint32_t tx_freq = lora->get_tx_frequency();
        uint8_t sf = lora->get_spread_factor();
        uint8_t cr = lora->get_coding_rate();
        uint8_t bw = lora->get_bandwidth();
        
        logSystem(LogLevel::LOG_INFO, "Heartbeat - Uptime: %02lu:%02lu:%02lu, Messages: %lu, LoRa[RX:%luHz TX:%luHz SF:%u CR:%u BW:%u]",
                  hours, minutes, seconds, message_counter, rx_freq, tx_freq, sf, cr, bw);
    } else {
        logSystem(LogLevel::LOG_INFO, "Heartbeat - Uptime: %02lu:%02lu:%02lu, Messages: %lu, LoRa[Not initialized]",
                  hours, minutes, seconds, message_counter);
    }
}