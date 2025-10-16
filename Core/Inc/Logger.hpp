/*
 * Logger.hpp
 *
 *  Created on: Oct 16, 2025
 *      Author: artur
 */

#ifndef INC_LOGGER_HPP_
#define INC_LOGGER_HPP_

#include "main.h"
#include <cstdint>
#include <cstring>
#include <cstdio>

// Forward declaration
class Lora;

// External reference to global LoRa object
extern Lora* lora;

// Logger configuration
#define LOGGER_BUFFER_SIZE 256
#define LOGGER_MAX_MESSAGE_SIZE 200
#define LOGGER_UART_TIMEOUT 100
#define LOGGER_RS485_DE_DELAY_US 10

// Logger levels
enum class LogLevel : uint8_t {
    LOG_DEBUG = 0,
    LOG_INFO = 1,
    LOG_WARNING = 2,
    LOG_ERROR = 3,
    LOG_CRITICAL = 4
};

// Logger message types
enum class LogSource : uint8_t {
    SYSTEM = 0,
    UART2 = 1,
    LORA_RX = 2,
    LORA_TX = 3,
    COMMAND = 4,
    CONFIG = 5,
    ERROR_SRC = 6
};

class Logger {
private:
    static Logger* instance;
    char buffer[LOGGER_BUFFER_SIZE];
    bool initialized;
    uint32_t message_counter;
    
    // Private constructor for singleton
    Logger();
    
    // Helper methods
    void enableRS485TX();
    void disableRS485TX();
    void sendToUART3(const char* message, uint16_t length);
    const char* getLevelString(LogLevel level);
    const char* getSourceString(LogSource source);
    uint32_t getCurrentTick();
    
public:
    // Singleton access
    static Logger& getInstance();
    
    // Initialization
    bool init();
    
    // Main logging methods
    void log(LogLevel level, LogSource source, const char* format, ...);
    void logHex(LogLevel level, LogSource source, const char* prefix, const uint8_t* data, uint16_t length);
    
    // Convenience methods for different sources
    void logUART2(LogLevel level, const char* format, ...);
    void logLoRaRX(LogLevel level, const char* format, ...);
    void logLoRaTX(LogLevel level, const char* format, ...);
    void logSystem(LogLevel level, const char* format, ...);
    void logCommand(LogLevel level, const char* format, ...);
    void logConfig(LogLevel level, const char* format, ...);
    
    // Hex data logging for communication monitoring
    void logUART2Hex(const char* prefix, const uint8_t* data, uint16_t length);
    void logLoRaRXHex(const char* prefix, const uint8_t* data, uint16_t length);
    void logLoRaTXHex(const char* prefix, const uint8_t* data, uint16_t length);
    
    // Status and diagnostics
    void logStartup();
    void logHeartbeat();
    uint32_t getMessageCount() const { return message_counter; }
    
    // Disable copy constructor and assignment operator
    Logger(const Logger&) = delete;
    Logger& operator=(const Logger&) = delete;
};

// Macro definitions for easy logging
#define LOG_DEBUG(source, ...) Logger::getInstance().log(LogLevel::LOG_DEBUG, source, __VA_ARGS__)
#define LOG_INFO(source, ...) Logger::getInstance().log(LogLevel::LOG_INFO, source, __VA_ARGS__)
#define LOG_WARNING(source, ...) Logger::getInstance().log(LogLevel::LOG_WARNING, source, __VA_ARGS__)
#define LOG_ERROR(source, ...) Logger::getInstance().log(LogLevel::LOG_ERROR, source, __VA_ARGS__)
#define LOG_CRITICAL(source, ...) Logger::getInstance().log(LogLevel::LOG_CRITICAL, source, __VA_ARGS__)

// Specific source macros
#define LOG_UART2(...) Logger::getInstance().logUART2(LogLevel::LOG_INFO, __VA_ARGS__)
#define LOG_LORA_RX(...) Logger::getInstance().logLoRaRX(LogLevel::LOG_INFO, __VA_ARGS__)
#define LOG_LORA_TX(...) Logger::getInstance().logLoRaTX(LogLevel::LOG_INFO, __VA_ARGS__)
#define LOG_SYSTEM(...) Logger::getInstance().logSystem(LogLevel::LOG_INFO, __VA_ARGS__)
#define LOG_COMMAND(...) Logger::getInstance().logCommand(LogLevel::LOG_INFO, __VA_ARGS__)
#define LOG_CONFIG(...) Logger::getInstance().logConfig(LogLevel::LOG_INFO, __VA_ARGS__)

// Hex data logging macros
#define LOG_UART2_HEX(prefix, data, length) Logger::getInstance().logUART2Hex(prefix, data, length)
#define LOG_LORA_RX_HEX(prefix, data, length) Logger::getInstance().logLoRaRXHex(prefix, data, length)
#define LOG_LORA_TX_HEX(prefix, data, length) Logger::getInstance().logLoRaTXHex(prefix, data, length)

#endif /* INC_LOGGER_HPP_ */