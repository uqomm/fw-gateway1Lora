/*
 * UartHandler.hpp
 *
 *  Created on: Jun 18, 2024
 *      Author: artur
 */

#ifndef INC_COMMANDMESSAGE_HPP_
#define INC_COMMANDMESSAGE_HPP_

#include "main.h"
// Reemplazar inclusión directa con declaración adelantada
class UartHandler; // Declaración adelantada en lugar de #include "UartHandler.hpp"
#include <vector>
#include <cstdint>
#include <cstring> // Para std::memcpy si se usa directamente en el header, o para referencia

// Abstract class Function

namespace CommandConstants {
    static constexpr uint8_t RDSS_FRAME_SIZE = 14;
    static constexpr uint8_t SIGMA_FRAME_SIZE = 14;
    static constexpr uint8_t RDSS_START_MARK = 0x7e;
    static constexpr uint8_t RDSS_END_MARK = 0x7f;
    static constexpr uint8_t RDSS_BUFFER_SIZE = 50;
    static constexpr uint8_t LTEL_SET_LENGTH = 13;
    static constexpr uint8_t LTEL_QUERY_LENGTH = 9;
    static constexpr uint8_t MINIMUN_FRAME_LEN = 6;
    static constexpr uint8_t CRC_HIGH_BYTE_OFFSET = 2;
    static constexpr uint8_t CRC_LOW_BYTE_OFFSET = 3;
    static constexpr uint8_t FRAME_HEADER_SIZE = 4;

    // Bytes number
    static constexpr uint8_t CRC_BYTES = 2;

    static constexpr uint8_t QUERY_MASTER_STATUS_BYTES = 16;
}

enum class CommandType : uint8_t {
    NONE = 0x00, // No command

    // Query commands
    QUERY_MODULE_ID = 0x10,
    QUERY_STATUS = 0x11,
    SET_VLAD_ATTENUATION = 0x13,
    QUERY_MASTER_STATUS = 0x14,
    QUERY_UART1 = 0x15,

    QUERY_TX_FREQ = 0x20,               // Query transmit frequency
    QUERY_RX_FREQ = 0x21,               // Query receive frequency
    QUERY_UART_BAUDRATE = 0x22,         // Query UART baud rate
    QUERY_BANDWIDTH = 0x23,             // Query bandwidth
    QUERY_SPREAD_FACTOR = 0x24,         // Query spread factor
    QUERY_CODING_RATE = 0x25,           // Query coding rate
    QUERY_PARAMETER_PdBm = 0x26,        // Query parameter PdBm

    // Set commands (base value 0x90)
    SET_MODULE_ID = 0x90,               // Set module ID
    SET_TX_FREQ = 0xB0,                 // Set transmit frequency
    SET_RX_FREQ = 0xB1,                 // Set receive frequency
    SET_UART_BAUDRATE = 0xB2,           // Set UART baud rate
    SET_BANDWIDTH = 0xB3,               // Set bandwidth
    SET_SPREAD_FACTOR = 0xB4,           // Set spread factor
    SET_CODING_RATE = 0xB5,             // Set coding rate
    SET_OUT = 0xB6,                     // Set output control
    SET_AOUT_0_10V = 0xB7,              // Set analog output 0-10V
    SET_AOUT_4_20mA = 0xB8,             // Set analog output 4-20mA
    SET_AOUT_0_20mA = 0xB9,             // Set analog output 0-20mA
    SET_DOUT1 = 0xBA,                   // Set digital output 1

    SET_VLAD_MODE = 0xC0,               // Set VLAD mode
    SET_PARAMETER_FREQOUT = 0x31,       // Set parameter frequency output
    SET_PARAMETERS = 0xC2,              // Set multiple parameters
    SET_PARAMETER_FREQBASE = 0xC3,      // Set parameter frequency base

    // Mode control
    SET_OPERATION_MODE = 0x40,          // Set operation mode (RX/TX/TX_RX)
};


// ADC definitions
#define ADC_CHANNELS_NUM 2
#define ADC_EXTRA_DATA 1

enum class STATUS {
    MESSAGE_OK,
    WAITING,
    START_READING,
    CONFIG_FRAME,
    RETRANSMIT_FRAME,
    VALID_FRAME,
    NOT_VALID_FRAME,
    RDSS_DATA_OK,
    CRC_ERROR,
    // Añade otros estados según sea necesario
};

enum class INDEX {
    START,
    MODULE_TYPE,
    MODULE_ID,
    CMD,
    DATA_LENGHT1,
    DATA_LENGHT2,
    DATA_START
};

enum class MODULE_FUNCTION {
    SERVER,
    QUAD_BAND,
    PSU,
    TETRA,
    ULADR,
    VLADR,
    BDA,
    LOW_NOISE_AMPLIFIER,
    POWER_AMPLIFIER,
    UHF_TONE,
    SNIFFER = 0x10,
};


class CommandMessage {
public:
    // Constantes de la clase que antes eran #define
    static constexpr uint8_t LTEL_START_MARK = 0x7e;
    static constexpr uint8_t LTEL_END_MARK = 0x7f;
    static constexpr uint8_t MIN_FRAME_HEADER_SIZE = 9;

    static constexpr uint8_t QUERY_PARAMETER_LTEL = 0x11;
    static constexpr uint8_t QUERY_PARAMETER_SIGMA = 0x12;
    static constexpr uint8_t QUERY_PARAMETER_STR = 0x15;
    static constexpr uint8_t QUERY_PARAMETER_ADC = 0x16;

    static constexpr uint8_t SET_ATT_LTEL = 0x20;
    static constexpr uint8_t SET_POUT_MAX = 0x24;
    static constexpr uint8_t SET_POUT_MIN = 0x23;

    // Índices y desplazamientos de bytes (anteriormente en CommandMessage.cpp)
    static constexpr uint8_t MODULE_TYPE_BYTE = 0;
    static constexpr uint8_t MODULE_ID_BYTE = 1;
    static constexpr uint8_t MODULE_FUNCTION_BYTE = 2;
    static constexpr uint8_t COMMAND_ID_BYTE = 3;
    static constexpr uint8_t DATA_LENGTH_BYTE = 4;
    static constexpr uint8_t DATA_START_INDEX = 5;
    static constexpr uint8_t CRC_BYTE_1_BACKWARD = 1; // Desde el final del buffer
    static constexpr uint8_t CRC_BYTE_2_BACKWARD = 2; // Desde el final del buffer
    static constexpr uint8_t DATA_LENGTH_INDEX = 3; // Índice para la longitud de datos en ciertos contextos

    CommandMessage(uint8_t _module_function, uint8_t _module_id, uint8_t max_size);
    CommandMessage(uint8_t _module_function, uint8_t _module_id); // Constructor que delega
    CommandMessage(uint8_t max_size);
    CommandMessage();
    virtual ~CommandMessage();


    STATUS validate(uint8_t *buffer, uint8_t length);

    // Cambiado a static ya que no depende del estado de la instancia
    static uint16_t crc_get(uint8_t *buffer, uint8_t buff_len);


    size_t getDataSize() const;
    uint8_t getDataAsUint8() const;
    uint16_t getDataAsUint16() const;
    uint32_t getDataAsUint32() const;
    float getDataAsFloat() const;
    int freqDecode() const;


    void setMessage(uint8_t *arr, uint8_t size);
    // Getters y Setters
    uint8_t getModuleFunction() const {
        return module_function;
    }
    void setModuleFunction(uint8_t _module_function) {
        module_function = _module_function;
    }

    uint8_t getModuleId() const {
        return module_id;
    }
    void setModuleId(uint8_t _module_id) {
        module_id = _module_id;
    }

    uint8_t getCommandId() const {
        return command_id;
    }
    void setCommandId(uint8_t _command_id) {
        command_id = _command_id;
    }

    bool isListening() const {
        return listening;
    }

    bool isReady() const {
        return ready;
    }

    void setMaxSize(uint8_t max_size) {
        max_message_size = max_size;
    }

    uint8_t getMaxSize() const {
        return max_message_size;
    }

    std::vector<uint8_t> get_composed_message() const {
        return message;
    }

    uint8_t getLTELStartMark() const {
        return LTEL_START_MARK;
    }
    uint8_t getLTELEndMark() const {
        return LTEL_END_MARK;
    }
    uint8_t getMinFrameHeaderSize() const {
        return MIN_FRAME_HEADER_SIZE;
    }

    bool isQueryParameterLTEL() const {
        return (command_id == QUERY_PARAMETER_LTEL);
    }

    bool isQueryParameterSigma() const {
        return (command_id == QUERY_PARAMETER_SIGMA);
    }

    bool isQueryParameterStr() const {
        return (command_id == QUERY_PARAMETER_STR);
    }

    bool isQueryADC() const {
        return (command_id == QUERY_PARAMETER_ADC);
    }

    bool isSetAttLTEL() const {
        return (command_id == SET_ATT_LTEL);
    }

    bool isSetPoutMax() const {
        return (command_id == SET_POUT_MAX);
    }

    bool isSetPoutMin() const {
        return (command_id == SET_POUT_MIN);
    }

    void checkByte(uint8_t number);
    std::vector<uint8_t> getData();
    bool composeMessage(std::vector<uint8_t> *data);
    bool composeMessage();
    void reset(bool init);
    void reset();
    //METODO PARA DESGLOSAR FRAME QUE LLEGA DESDE RS485
    void saveFrame(uint8_t *buffer, uint8_t length);

    // Nuevo método para limpiar el mensaje actual
    void messageClear() {
        message.clear();
    }
    
    // Método simplificado para componer y enviar mensajes en un solo paso
    bool composeAndGetMessage(uint8_t* data, uint8_t size, std::vector<uint8_t>& output) {
        messageClear();
        setMessage(data, size);
        bool result = composeMessage();
        output = get_composed_message();
        
        // Guardar copia para depuración
        saveMessageTrace(output.data(), output.size());
        
        return result;
    }
    
    // Método para obtener información de debug sobre el último mensaje
    void getLastMessageTrace(uint8_t* buffer, uint8_t* size) {
        if (buffer && size && last_message_size > 0) {
            uint8_t copySize = (last_message_size <= MAX_DEBUG_SIZE) ? last_message_size : MAX_DEBUG_SIZE;
            memcpy(buffer, last_message_buffer, copySize);
            *size = copySize;
        } else if (size) {
            *size = 0;
        }
    }

    // Método simplificado para componer y enviar mensajes directamente
    bool composeAndSendMessage(UartHandler* uartComm, uint8_t* data, uint8_t size);

protected:
    void setVars();
    bool prepareTxData(const char *message);
    void handleRxData(uint8_t data);
    bool validateChecksum();
    bool checkCRC();
    uint16_t calculateCRC(uint8_t start, uint8_t end); // Esta llamará a la versión estática


    //METODO PARA DESGLOSAR FRAME QUE LLEGA DESDE RS485
    void storeData(size_t dataLength, const void* dataPtr);


    //METODOS SACADOS DE rdss_protocol
    STATUS checkFrameValidity(uint8_t *frame, uint8_t length);
    STATUS checkModule(uint8_t *frame, uint8_t length);
    STATUS checkCRCValidity(uint8_t *frame, uint8_t len);
    //uint16_t crc_get(uint8_t *buffer, uint8_t buff_len); // Ya es estático y público

    uint8_t max_message_size;
    uint8_t module_function;
    uint8_t module_id;
    uint8_t command_id;
    uint8_t num_byte_data;
    uint8_t data_frame;
    size_t data_size;


    uint8_t cmd;
    uint8_t *buff;
    uint8_t buffSize;
    uint16_t crc_calculated;
    uint16_t crc_received;
    uint8_t id_query;
    uint8_t id_received;
    uint8_t id;
    STATUS status;
    STATUS last_status;
    uint8_t query_buffer[30];
    uint32_t last_update_ticks;

    std::vector<uint8_t> message;
    bool listening;
    bool ready;

    // Buffer de debug para almacenar el último mensaje compuesto
    static const uint8_t MAX_DEBUG_SIZE = 64;
    uint8_t last_message_buffer[MAX_DEBUG_SIZE];
    uint8_t last_message_size;

    // Método para guardar una copia del mensaje para depuración
    void saveMessageTrace(const uint8_t* data, uint8_t size) {
        if (data && size > 0) {
            uint8_t copySize = (size <= MAX_DEBUG_SIZE) ? size : MAX_DEBUG_SIZE;
            memcpy(last_message_buffer, data, copySize);
            last_message_size = copySize;
        } else {
            last_message_size = 0;
        }
    }

    // Constantes para la interpretación de la estructura del mensaje
    // Índices dentro del vector 'message' cuando contiene una trama completa.
    // Asumen que message[0] es el START_MARKER.
    static constexpr uint8_t MESSAGE_INDEX_MODULE_FUNCTION = 1;
    static constexpr uint8_t MESSAGE_INDEX_MODULE_ID = 2;
    static constexpr uint8_t MESSAGE_INDEX_COMMAND = 3;
    // El índice 4 está reservado en este formato de mensaje
    static constexpr uint8_t MESSAGE_INDEX_DATA_LENGTH = 5;
    static constexpr uint8_t MESSAGE_INDEX_DATA_START = 6;

    // Constantes para la extracción de CRC del vector 'message' (desplazamientos desde el final)
    // Asume que el mensaje es [..., CRC_LOW, CRC_HIGH, END_MARKER]
    static constexpr uint8_t MESSAGE_OFFSET_CRC_LOW_FROM_END = 3;  // Accede al byte bajo del CRC (ej. message[message.size() - 3])
    static constexpr uint8_t MESSAGE_OFFSET_CRC_HIGH_FROM_END = 2; // Accede al byte alto del CRC (ej. message[message.size() - 2])
};

#endif /* INC_LORA_HPP_ */
