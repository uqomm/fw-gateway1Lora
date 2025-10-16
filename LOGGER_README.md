# Logger System for LoRa Gateway

Sistema de logging simple pero útil para el Gateway LoRa STM32, que permite monitorear comunicaciones UART2 y LoRa enviando logs por UART3 via RS485.

## Características del Logger

### 🔍 **Monitoreo Completo**
- **UART2**: Datos recibidos y enviados por el puerto principal de comunicación
- **LoRa RX**: Paquetes recibidos por radio con validación de tramas
- **LoRa TX**: Paquetes transmitidos por radio
- **Comandos**: Procesamiento de comandos de configuración
- **Sistema**: Eventos del sistema, errores, heartbeat

### 📡 **Salida RS485**
- **Puerto**: UART3 (PB10: TX, PB11: RX) 
- **Control**: Pin DE (Data Enable) en PB8 para RS485
- **Baudrate**: 115200 (configurable)
- **Protocolo**: Half-duplex con control automático de dirección

### 📊 **Formato de Logs**
```
[timestamp] LEVEL:SOURCE mensaje
[00012345] INF:SYS LoRa Gateway Logger Started
[00012456] DBG:U2  RX: 7E 05 01 11 00 00 AF 3F 7F
[00012478] INF:CMD Processing command 0x11
[00012501] INF:LRX Received: 7E 10 0A 17 00 05 01 02 03 04 05 XX XX 7F
```

## Integración en el Proyecto

### 1. Archivos Agregados

```
Core/
├── Inc/
│   └── Logger.hpp          # Declaraciones del logger
└── Src/
    └── Logger.cpp          # Implementación del logger
```

### 2. Modificaciones en main.cpp

```cpp
// Include agregado
#include "Logger.hpp"

// En main(), después de inicializar UART3:
Logger& logger = Logger::getInstance();
logger.init();

// Logs agregados en puntos clave:
LOG_UART2_HEX("RX", uartReceiveBuffer, uartReceivedBytes);
LOG_LORA_RX_HEX("Received", loraReceiveBuffer, loraReceivedBytes);
LOG_COMMAND("Processing command 0x%02X", commandId);
```

## Configuración Hardware

### Conexiones RS485

| Pin STM32 | Función | Descripción |
|-----------|---------|-------------|
| PB10 | UART3_TX | Transmisión RS485 |
| PB11 | UART3_RX | Recepción RS485 |
| PB8 | RS485_DE | Data Enable (control dirección) |

### Circuito RS485 Típico

```
STM32F103          MAX485/SN65176
---------          ---------------
PB10 (TX) -------- DI (Driver Input)
PB11 (RX) -------- RO (Receiver Output)  
PB8 (DE)  -------- DE (Driver Enable)
PB8 (DE)  -------- /RE (Receiver Enable) - invertido
3.3V     -------- VCC
GND      -------- GND
                   A ---- RS485_A (línea diferencial +)
                   B ---- RS485_B (línea diferencial -)
```

## Uso del Logger

### Métodos Principales

```cpp
// Logger singleton
Logger& logger = Logger::getInstance();

// Inicialización (llamar una sola vez)
logger.init();

// Logging general
LOG_INFO(LogSource::SYSTEM, "Sistema iniciado");
LOG_ERROR(LogSource::UART2, "Error en UART2");

// Logging específico por fuente
LOG_UART2("Comando recibido: 0x%02X", cmd);
LOG_LORA_RX("Paquete válido, RSSI: %d", rssi);
LOG_LORA_TX("Transmitiendo %d bytes", length);
LOG_SYSTEM("Memoria libre: %d bytes", freeMemory);
LOG_COMMAND("Set frequency: %lu Hz", frequency);
LOG_CONFIG("Bandwidth changed to: %d", bandwidth);

// Logging de datos hexadecimales
LOG_UART2_HEX("Frame", data, length);
LOG_LORA_RX_HEX("Packet", packet, packetSize);
LOG_LORA_TX_HEX("Sending", txBuffer, txSize);

// Heartbeat periódico (automático cada 30s)
logger.logHeartbeat();
```

### Niveles de Log

| Nivel | Código | Uso |
|-------|--------|-----|
| DEBUG | DBG | Datos raw, debugging detallado |
| INFO | INF | Eventos normales del sistema |
| WARNING | WRN | Situaciones anómalas no críticas |
| ERROR | ERR | Errores recuperables |
| CRITICAL | CRT | Errores críticos del sistema |

### Fuentes de Log

| Fuente | Código | Descripción |
|--------|--------|-------------|
| SYSTEM | SYS | Eventos del sistema |
| UART2 | U2 | Comunicación UART2 |
| LORA_RX | LRX | Recepción LoRa |
| LORA_TX | LTX | Transmisión LoRa |
| COMMAND | CMD | Procesamiento comandos |
| CONFIG | CFG | Cambios configuración |

## Monitor de Logs

### Script Python logger_monitor.py

```bash
# Instalar dependencia
pip install pyserial

# Ejecutar monitor
python logger_monitor.py COM5 115200

# Listar puertos disponibles
python logger_monitor.py -l
```

### Características del Monitor

- **Conexión RS485**: Se conecta al puerto RS485 del gateway
- **Formato coloreado**: Diferentes colores para niveles y fuentes
- **Timestamps**: Conversión a formato HH:MM:SS.sss
- **Estadísticas**: Contador de mensajes y duración
- **Manejo de errores**: Recuperación ante datos corruptos

### Ejemplo de Salida del Monitor

```
================================================================================
LoRa Gateway Logger Monitor - Press Ctrl+C to stop
================================================================================
Port: COM5 | Baudrate: 115200
Started: 2025-10-16 15:30:25
================================================================================

[00:00:12.345] INF:SYS === LoRa Gateway Logger Started ===
[00:00:12.356] INF:SYS Firmware: 2.0.0
[00:00:12.367] INF:SYS Build: Oct 16 2025 15:30:12
[00:00:12.378] INF:SYS Operation Mode: TX_RX
[00:00:15.432] DBG:U2  RX: 7E 05 01 11 00 00 AF 3F 7F
[00:00:15.445] INF:CMD Processing command 0x11
[00:00:15.456] DBG:U2  TX: 7E 05 01 11 00 04 12 34 56 78 XX XX 7F
[00:00:18.567] INF:LRX Received: 7E 10 0A 17 00 05 01 02 03 04 05 XX XX 7F
[00:00:18.578] INF:LRX Frame validation: VALID
[00:00:42.123] INF:SYS Heartbeat - Uptime: 00:00:42, Messages: 156
```

## Configuración Avanzada

### Personalizar Buffer Size

```cpp
// En Logger.hpp
#define LOGGER_BUFFER_SIZE 256          // Tamaño buffer mensaje
#define LOGGER_MAX_MESSAGE_SIZE 200     // Tamaño máximo mensaje
#define LOGGER_UART_TIMEOUT 100         // Timeout UART (ms)
```

### Personalizar Heartbeat

```cpp
// En main.cpp, cambiar intervalo heartbeat
if (HAL_GetTick() - loggerHeartbeatLastTick > 30000) {  // 30 segundos
    loggerHeartbeatLastTick = HAL_GetTick();
    Logger::getInstance().logHeartbeat();
}
```

### Deshabilitar Logger

```cpp
// Comentar la inicialización en main.cpp
// Logger& logger = Logger::getInstance();
// logger.init();

// Los macros LOG_* no harán nada si no se inicializa
```

## Solución de Problemas

### 1. No se reciben logs

**Verificar:**
- Conexión RS485 correcta (A, B, GND)
- Baudrate correcto (115200)
- Pin DE configurado como salida
- UART3 inicializado correctamente

### 2. Datos corruptos

**Posibles causas:**
- Impedancia de línea RS485 incorrecta
- Cables demasiado largos sin terminación
- Interferencia electromagnética
- Baudrate incorrecto

### 3. Mensajes cortados

**Soluciones:**
- Aumentar `LOGGER_BUFFER_SIZE`
- Reducir tamaño de mensajes hex
- Verificar timeout UART

### 4. Logger no inicializa

**Verificar:**
- UART3 inicializado antes del logger
- Pin RS485_DE definido correctamente
- Memoria suficiente para instancia singleton

## Ejemplos de Integración

### Logging en Funciones Existentes

```cpp
// En función de recepción LoRa
void handleLoraReception() {
    // ... código existente ...
    
    if (loraReceivedBytes > 0) {
        LOG_LORA_RX_HEX("Received", loraReceiveBuffer, loraReceivedBytes);
        
        STATUS frameStatus = validateFrame(loraReceiveBuffer, loraReceivedBytes);
        LOG_LORA_RX("Frame validation: %s", getStatusString(frameStatus));
        
        if (frameStatus == STATUS::VALID_FRAME) {
            LOG_LORA_RX("Valid frame processed successfully");
        }
    }
}
```

### Logging en Comandos

```cpp
// En función de procesamiento de comandos
void processCommand(uint8_t cmd, uint8_t* data, uint16_t length) {
    LOG_COMMAND("Processing command 0x%02X with %d bytes", cmd, length);
    
    switch (cmd) {
        case SET_FREQUENCY:
            uint32_t freq = *(uint32_t*)data;
            LOG_CONFIG("Setting frequency to %lu Hz", freq);
            setFrequency(freq);
            LOG_CONFIG("Frequency set successfully");
            break;
    }
}
```

**¡El sistema de logger está listo para depurar y monitorear el Gateway LoRa!**