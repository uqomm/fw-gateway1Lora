# UART Communication Change Summary

## Changes Made: UART1 → UART2

The main communication has been changed from UART1 to UART2 for command and data processing.

### 🔄 **Modified Files:**

#### main.cpp Changes:

1. **UART Callback Function:**
   ```cpp
   // OLD: if (huart == &huart1 && uartHandler != nullptr)
   // NEW: if (huart == &huart2 && uartHandler != nullptr)
   ```

2. **UartHandler Creation:**
   ```cpp
   // OLD: uartHandler = new UartHandler(&huart1);
   // NEW: uartHandler = new UartHandler(&huart2);
   ```

3. **UART Interrupt Initialization:**
   ```cpp
   // OLD: HAL_UART_Receive_IT(&huart1, uartReceiveBuffer, 1);
   // NEW: HAL_UART_Receive_IT(&huart2, uartReceiveBuffer, 1);
   ```

4. **UART Interrupt Restart:**
   ```cpp
   // OLD: HAL_UART_Receive_IT(&huart1, uartReceiveBuffer, 1);
   // NEW: HAL_UART_Receive_IT(&huart2, uartReceiveBuffer, 1);
   ```

### 📡 **UART Configuration:**

| UART | Instance | Purpose | Pins (typical) | Status |
|------|----------|---------|----------------|---------|
| UART1 | USART1 | Available for debug/other | PA9/PA10 (USB) | Available |
| UART2 | USART2 | **Main communication** | PA2/PA3 | **Active** |
| UART3 | USART3 | RS485 Logger | PB10/PB11 | Logger |

### ⚙️ **Current Settings:**

**UART2 (Main Communication):**
- **Baudrate**: 115200
- **Data bits**: 8
- **Stop bits**: 1  
- **Parity**: None
- **Flow control**: None
- **Mode**: TX + RX
- **Purpose**: Command processing and LoRa data relay

**UART3 (Logger):**
- **Baudrate**: 115200
- **Mode**: TX (RS485 with DE control)
- **DE Pin**: PB8
- **Purpose**: Logging output

### 🔧 **Hardware Connections:**

**For Main Communication (UART2):**
- Connect external device to PA2 (TX) and PA3 (RX)
- GND connection required
- 3.3V logic levels

**For Logger Monitoring (UART3):**
- RS485 transceiver on PB10/PB11
- DE control on PB8
- Differential A/B lines for RS485 network

### 📊 **Logged Events:**

The logger will now show:
```
[timestamp] INF:SYS Main communication: UART2 (USART2)
[timestamp] INF:SYS Logger output: UART3 (USART3) RS485
[timestamp] DBG:U2  RX: [hex data from UART2]
[timestamp] INF:CMD Processing command 0xXX
```

### 🔍 **Testing the Change:**

1. **Connect to UART2** (PA2/PA3) instead of UART1 (PA9/PA10)
2. **Use the GUI application** with the new port
3. **Monitor logs via UART3** RS485 connection
4. **Verify command processing** works correctly

### ⚠️ **Important Notes:**

- **UART1 is now free** for other purposes (debug, additional communication)
- **All existing commands** work the same, just on different pins
- **Logger continues** to work on UART3 RS485
- **No protocol changes** - only hardware pin assignment

### 🧪 **Verification Commands:**

Test with these commands on UART2:
```
Query Module ID: 7E 05 01 10 00 00 [CRC] 7F
Query TX Freq:   7E 05 01 20 00 00 [CRC] 7F
Set Operation:   7E 05 01 40 00 01 [mode] [CRC] 7F
```

**The change is complete and ready for testing!**