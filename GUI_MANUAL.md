# LoRa Gateway Configuration Tool - GUI Manual

Una aplicación GUI completa para configurar y monitorear parámetros del Gateway LoRa usando comunicación serial basada en el código del proyecto.

## Instalación Rápida

```bash
# Instalar dependencias
pip install pyserial crccheck

# Ejecutar la aplicación
python lora_gui_config.py
```

## Características Principales

### 🖥️ Interfaz Gráfica Intuitiva
- **4 pestañas organizadas**: Connection, Parameters, Advanced, Log
- **Controles fáciles de usar**: Botones, combos, entradas de texto
- **Feedback visual**: Estados de conexión, validación de parámetros

### 📡 Comunicación Serial Completa  
- **Auto-detección de puertos**: Lista automática de puertos disponibles
- **Protocolo completo**: Implementación del protocolo de tramas con CRC16
- **Manejo de errores**: Detección y reporte de errores de comunicación

### ⚙️ Configuración de Parámetros
- **Parámetros LoRa**: Frecuencia TX/RX, bandwidth, spreading factor, coding rate
- **Configuración del módulo**: Module ID, UART baudrate, potencia de salida
- **Validación automática**: Verificación de rangos y valores válidos

### 🔧 Herramientas Avanzadas
- **Comandos personalizados**: Envío de comandos manuales
- **Monitor de datos raw**: Visualización de tramas en hexadecimal
- **Configuración persistente**: Guardado/carga en formato JSON

## Uso de la Aplicación

### 1. Pestaña Connection

**Configurar Conexión Serial:**
- Seleccionar puerto COM del dispositivo
- Configurar baudrate (por defecto 115200)
- Establecer Module Function (5 para VLAD) y Module ID

**Controles:**
- `Refresh`: Actualizar lista de puertos
- `Connect/Disconnect`: Alternar conexión
- Estado visual: Verde=Conectado, Rojo=Desconectado

### 2. Pestaña Parameters

**Parámetros Disponibles:**

| Parámetro | Descripción | Rango/Opciones |
|-----------|-------------|----------------|
| Module ID | ID único del módulo | 1-255 |
| TX Frequency | Frecuencia transmisión | 860-930 MHz |
| RX Frequency | Frecuencia recepción | 860-930 MHz |
| UART Baudrate | Velocidad serial | 9600-921600 |
| Bandwidth | Ancho de banda LoRa | 0-9 (7.8kHz-500kHz) |
| Spread Factor | Factor dispersión | 6-12 |
| Coding Rate | Tasa codificación | 1-4 (4/5-4/8) |
| Output Power | Potencia salida RF | -20 a +20 dBm |
| LTEL Attenuation | Atenuación LTEL | 0-63 |

**Operaciones:**
- `Query`: Consultar valor actual
- `Set`: Establecer nuevo valor  
- `Query All Parameters`: Consultar todos los parámetros
- `Save Configuration`: Guardar en JSON
- `Load Configuration`: Cargar desde JSON

### 3. Pestaña Advanced

**Comandos Personalizados:**
- Module Function: Función del módulo (ej: 5)
- Module ID: ID destino (ej: 1) 
- Command: Código comando hex (ej: 0x11)
- Data: Datos hex opcionales (ej: 01FF)

**Monitor Raw Data:**
- Visualización de todas las tramas enviadas/recibidas
- Formato hexadecimal con timestamp
- Scroll automático

### 4. Pestaña Log

**Sistema de Logging:**
- Logs detallados de todas las operaciones
- Diferentes niveles: INFO, WARNING, ERROR, DEBUG
- Guardado automático con timestamp
- Controles: Clear Log, Save Log

## Protocolo de Comunicación

### Estructura de Trama

```
Byte:  0    1    2    3    4    5    6...n  n+1  n+2  n+3
     +----+----+----+----+----+----+------+----+----+----+
     |0x7E|Func| ID |Cmd |0x00|Len | Data |CRC |CRC |0x7F|
     +----+----+----+----+----+----+------+----+----+----+
```

**Campos:**
- **Start (0x7E)**: Marca inicio de trama
- **Function**: Función del módulo (0x05 = VLAD)
- **ID**: Identificador del módulo
- **Command**: Código de comando
- **Reserved (0x00)**: Byte reservado
- **Length**: Longitud de datos
- **Data**: Datos del comando (opcional)
- **CRC16**: Checksum CRC16 XMODEM (little endian)
- **End (0x7F)**: Marca fin de trama

### Comandos Implementados

#### Query Commands (0x10-0x2F)
```python
QUERY_MODULE_ID = 0x10      # Consultar ID módulo
QUERY_PARAMETER_LTEL = 0x11 # Consultar parámetro LTEL
QUERY_TX_FREQ = 0x20        # Consultar frecuencia TX
QUERY_RX_FREQ = 0x21        # Consultar frecuencia RX
QUERY_BANDWIDTH = 0x23      # Consultar bandwidth
QUERY_SPREAD_FACTOR = 0x24  # Consultar spreading factor
QUERY_CODING_RATE = 0x25    # Consultar coding rate
```

#### Set Commands (0x90+)
```python
SET_MODULE_ID = 0x90        # Establecer ID módulo
SET_TX_FREQ = 0xB0         # Establecer frecuencia TX
SET_RX_FREQ = 0xB1         # Establecer frecuencia RX
SET_BANDWIDTH = 0xB3       # Establecer bandwidth
SET_SPREAD_FACTOR = 0xB4   # Establecer spreading factor
SET_CODING_RATE = 0xB5     # Establecer coding rate
```

## Ejemplos Prácticos

### Ejemplo 1: Query Module ID
```
Comando enviado: 7E 05 01 10 00 00 F3 3C 7F
Respuesta:       7E 05 01 10 00 01 0A XX XX 7F
                                   ↑
                              Module ID = 10
```

### Ejemplo 2: Set TX Frequency a 868.1 MHz
```
Frecuencia: 868100000 Hz = 0x33C4B540 (little endian: 40 B5 C4 33)
Comando: 7E 05 01 B0 00 04 40 B5 C4 33 XX XX 7F
```

### Ejemplo 3: Set Bandwidth a 125 kHz
```
Bandwidth 125 kHz = valor 7
Comando: 7E 05 01 B3 00 01 07 XX XX 7F
```

## Valores de Configuración

### Bandwidth LoRa
| Valor | Ancho de Banda | Uso Típico |
|-------|----------------|------------|
| 0 | 7.8 kHz | Largo alcance |
| 1 | 10.4 kHz | Largo alcance |
| 2 | 15.6 kHz | Largo alcance |
| 3 | 20.8 kHz | Balanceado |
| 4 | 31.25 kHz | Balanceado |
| 5 | 41.7 kHz | Balanceado |
| 6 | 62.5 kHz | Throughput medio |
| 7 | 125 kHz | **Estándar** |
| 8 | 250 kHz | Alto throughput |
| 9 | 500 kHz | Máximo throughput |

### Spreading Factor
| Valor | SF | Alcance | Velocidad |
|-------|----|---------|---------  |
| 6 | SF6 | Corto | Máxima |
| 7 | SF7 | Medio | Alta |
| 8 | SF8 | Medio | Media |
| 9 | SF9 | Largo | Media |
| 10 | SF10 | Largo | Baja |
| 11 | SF11 | Muy largo | Muy baja |
| 12 | SF12 | Máximo | Mínima |

### Coding Rate
| Valor | Coding Rate | Robustez | Throughput |
|-------|-------------|----------|------------|
| 1 | 4/5 | Baja | **Máximo** |
| 2 | 4/6 | Media | Alto |
| 3 | 4/7 | Alta | Medio |
| 4 | 4/8 | **Máxima** | Mínimo |

## Solución de Problemas

### Problemas de Conexión

**❌ Error: "Failed to connect"**
- Verificar que el dispositivo esté conectado
- Revisar drivers del puerto COM
- Comprobar que no esté siendo usado por otra aplicación

**❌ Error: "No response"**
- Verificar baudrate (por defecto 115200)
- Comprobar Module Function y Module ID
- Revisar cables de conexión

### Problemas de Configuración

**❌ Error: "Invalid value"**
- Verificar que el valor esté dentro del rango permitido
- Para frecuencias usar valores en Hz (ej: 868100000)
- Para bandwidth usar valores 0-9

**❌ Error: "CRC Error"**
- Problema de comunicación serial
- Verificar integridad de la conexión
- Revisar configuración del puerto

### Debugging

**Usar la pestaña Log:**
- Nivel DEBUG muestra todas las tramas hex
- Nivel INFO muestra operaciones principales
- Nivel ERROR muestra solo problemas

**Usar la pestaña Advanced:**
- Monitor Raw Data muestra tráfico serial completo
- Enviar comandos personalizados para testing
- Verificar formato de tramas manualmente

## Tips de Uso

### 🎯 Configuración Recomendada para Europa
```
TX Frequency: 868100000 Hz (868.1 MHz)
RX Frequency: 868300000 Hz (868.3 MHz)  
Bandwidth: 7 (125 kHz)
Spread Factor: 7
Coding Rate: 1 (4/5)
```

### 🔧 Flujo de Trabajo Típico
1. Conectar dispositivo y abrir aplicación
2. Configurar conexión serial
3. Query All Parameters para ver estado actual
4. Modificar parámetros necesarios con Set
5. Guardar configuración para backup
6. Verificar con Query individual

### 📊 Monitoreo y Debug
- Usar pestaña Log para seguimiento detallado
- Raw Data para análisis de protocolo  
- Guardar logs para análisis posterior
- Usar comandos personalizados para testing

**¡La aplicación está lista para usar con tu Gateway LoRa STM32!**