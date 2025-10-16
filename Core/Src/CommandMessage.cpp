/*
 * Function.cpp
 *
 *  Created on: Jun
 *   19, 2024
 *      Author: artur
 */

#include <CommandMessage.hpp> // Include the header file
#include <UartHandler.hpp> // Incluir ahora el encabezado de UartHandler para la implementación

CommandMessage::CommandMessage(uint8_t _module_function, uint8_t _module_id,
		uint8_t max_size) :
		module_function(_module_function), module_id(_module_id), max_message_size(
				max_size) {
	reset(true);
}

CommandMessage::CommandMessage(uint8_t _module_function, uint8_t _module_id) :
		CommandMessage(_module_function, _module_id, 255) {
	// La inicialización principal se hace en el constructor delegado.
}

CommandMessage::CommandMessage(uint8_t max_size) :
		max_message_size(max_size) {
	reset();
}

CommandMessage::CommandMessage() :
		CommandMessage(255) {
}

CommandMessage::~CommandMessage() {
}

void CommandMessage::setVars() {
	if (!ready)
		return;

	command_id = message[MESSAGE_INDEX_COMMAND];
	module_id = message[MESSAGE_INDEX_MODULE_ID];
	module_function = message[MESSAGE_INDEX_MODULE_FUNCTION];
}

std::vector<uint8_t> CommandMessage::getData() {
	if (!ready)
		return std::vector<uint8_t>();

	uint8_t length = message[MESSAGE_INDEX_DATA_LENGTH];
	uint8_t end_index = MESSAGE_INDEX_DATA_START + length;
	// Asegurarse de que end_index no exceda el tamaño del mensaje
	if (end_index > message.size()) {
		// Manejar error: longitud de datos excede el tamaño del mensaje
		return std::vector<uint8_t>(); 
	}
	return std::vector<uint8_t>(message.begin() + MESSAGE_INDEX_DATA_START,
			message.begin() + end_index);
}

void CommandMessage::reset(bool init) {
	if (!init) {
		module_function = 0;
		module_id = 0;
	}

	command_id = 0;
	ready = false;
	listening = false;
	message.clear();
}

void CommandMessage::reset() {
	reset(false);
}

void CommandMessage::checkByte(uint8_t number) {
	if (listening) {
		message.push_back(number);
		if (number == getLTELEndMark()) {
			listening = false;
			ready = checkCRC();
			if (ready) {
				setVars();
			}
		}
		if (message.size() >= max_message_size) {
			reset();
		}
	} else {
		if (number == getLTELStartMark()) {
			message.clear();
			message.push_back(number);
			listening = true;
		}
	}
}

bool CommandMessage::checkCRC() {
	if (message.size() < MESSAGE_OFFSET_CRC_LOW_FROM_END) { // Mínimo tamaño para tener START, un byte de datos, CRC y END. Ajustar según sea necesario.
		return false; // No hay suficientes bytes para un CRC válido y marcadores.
	}

	uint16_t crc_val; // Renombrado de 'crc' para evitar confusión con el método crc_get
	uint8_t test_frame_crc[2]; // Renombrado de 'testframe'
	uint8_t received_crc_frame[2] = { message[message.size() - MESSAGE_OFFSET_CRC_LOW_FROM_END],
			message[message.size() - MESSAGE_OFFSET_CRC_HIGH_FROM_END] };

	// El CRC se calcula sobre los datos desde el byte después de START_MARK hasta antes del CRC mismo.
	// El '3' como segundo argumento de calculateCRC significa excluir los 3 últimos bytes (CRC_L, CRC_H, END_MARK)
	crc_val = calculateCRC(1, 3); 
	std::memcpy(test_frame_crc, &crc_val, 2); 
	// Comparar bytes del CRC. Cuidado con el endianness si es relevante.
	// Asumiendo que crc_val (un uint16_t) se copia a test_frame_crc en orden little-endian (byte bajo primero)
	// y que received_crc_frame también está en ese orden [LOW, HIGH]
	if (test_frame_crc[0] == received_crc_frame[0] && test_frame_crc[1] == received_crc_frame[1]) {
		return true;
	}
	return false;
}

// calculateCRC ahora llama a la función estática crc_get, 
// pasando los datos relevantes del miembro 'message'.
// El parámetro 'start' es el índice inicial en 'message' para calcular el CRC.
// El parámetro 'end' es el número de bytes a excluir del final de 'message' antes de calcular el CRC.
uint16_t CommandMessage::calculateCRC(uint8_t start_index, uint8_t bytes_to_exclude_from_end) {
    if (message.empty() || (start_index >= message.size()) || (start_index + bytes_to_exclude_from_end > message.size() )) {
        return 0; 
    }
    uint8_t effective_buff_len = message.size() - bytes_to_exclude_from_end - start_index;
    if (effective_buff_len <= 0) { // No data to calculate CRC on
        return 0;
    }
    return crc_get(message.data() + start_index, effective_buff_len);
}

// La función crc_get ahora es estática y contiene la lógica principal de CRC.
uint16_t CommandMessage::crc_get(uint8_t *buffer, uint8_t buff_len) {
	uint8_t byte_idx;
	uint8_t bit_idx;
	uint16_t generator = 0x1021; // 16-bit divisor
	uint16_t crc = 0;            // 16-bit CRC value

	for (byte_idx = 0; byte_idx < buff_len; byte_idx++) {
		crc ^= ((uint16_t) (buffer[byte_idx] << 8)); // Move byte into MSB of 16-bit CRC

		for (bit_idx = 0; bit_idx < 8; bit_idx++) {
			if ((crc & 0x8000) != 0) { // Test for MSB = bit 15
				crc = ((uint16_t) ((crc << 1) ^ generator));
			} else {
				crc <<= 1;
			}
		}
	}

	return crc;
}

bool CommandMessage::composeMessage(std::vector<uint8_t> *data) {
	uint8_t current_size;
	uint16_t calculated_crc;
	if (command_id == 0)
		return false;

	if (data == nullptr) {
		current_size = 0;
	} else {
		current_size = data->size();
	}
	message.clear();

	message.push_back(getLTELStartMark());

	message.push_back(module_function);
	message.push_back(module_id);
	message.push_back(command_id);
	message.push_back(0);

	message.push_back(current_size);
	if (current_size > 0) {
		message.insert(message.end(), data->begin(), data->end());
	}

    // Primero, construimos el mensaje sin el CRC y el END_MARK para calcular el CRC
    std::vector<uint8_t> temp_message_for_crc;
    temp_message_for_crc.push_back(module_function);
    temp_message_for_crc.push_back(module_id);
    temp_message_for_crc.push_back(command_id);
    temp_message_for_crc.push_back(0); // Reservado
    temp_message_for_crc.push_back(current_size);
    if (current_size > 0) {
        temp_message_for_crc.insert(temp_message_for_crc.end(), data->begin(), data->end());
    }

    calculated_crc = crc_get(temp_message_for_crc.data(), temp_message_for_crc.size());

    // Ahora construimos el mensaje final completo en el miembro 'message'
    // (ya se hizo push_back de START_MARK y los datos antes de temp_message_for_crc)
    // Solo necesitamos añadir el CRC y END_MARK a 'message'
	message.push_back(static_cast<uint8_t>(calculated_crc & 0xFF));
	message.push_back(static_cast<uint8_t>((calculated_crc >> 8) & 0xFF));

	message.push_back(getLTELEndMark());

	return true;
}

void CommandMessage::setMessage(uint8_t *arr, uint8_t size) {
	message.clear();
	for (int i = 0; i < size; i++)
		message.push_back(arr[i]);
}

bool CommandMessage::composeMessage() {
    uint16_t calculated_crc;
    
    if (command_id == 0)
        return false;
    
    // No limpiamos el mensaje aquí, para conservar los datos establecidos por set_message()
    // Solo aseguramos el formato correcto del mensaje
    
    // Si message está vacío o no tiene el formato correcto, lo inicializamos
    if (message.empty() || message[0] != getLTELStartMark()) {
        message.clear();
        message.push_back(getLTELStartMark());
        message.push_back(module_function);
        message.push_back(module_id);
        message.push_back(command_id);
        message.push_back(0); // Reservado
        message.push_back(0); // Tamaño de datos (por defecto 0)
    }
    
    // Calculamos CRC y añadimos bytes de cierre si no están ya
    size_t originalSize = message.size();
    if (originalSize < 8 || message[originalSize-1] != getLTELEndMark()) {
        // Si el mensaje no tiene los bytes de cierre, los añadimos
        // Necesitamos calcular el CRC sobre el contenido actual ANTES de añadir el CRC mismo.
        // Extraer los datos relevantes para el CRC:
        // desde después de LTEL_START_MARK (índice 1) hasta antes de donde iría el CRC.
        // La longitud para crc_get sería message.size() - 1 (excluyendo START_MARK)
        // si el CRC se calcula sobre todo lo que está después de START_MARK.
        // Esto necesita ser consistente con cómo se valida el CRC.
        
        // Suponiendo que el CRC se calcula sobre los bytes desde module_function hasta el final de los datos.
        // message[0] es START_MARK
        // message[1] es module_function
        // ... datos ...
        // Luego viene CRC y END_MARK
        // Si message actualmente contiene [START, MF, MID, CMD, 0, LEN, DATA...]
        // El CRC se calcula sobre [MF, MID, CMD, 0, LEN, DATA...]
        // que es message.data() + 1, con longitud message.size() - 1

        if (message.size() > 1) { // Debe haber al menos START_MARK y un byte más
            calculated_crc = crc_get(message.data() + 1, message.size() - 1);
        } else {
            // No hay suficientes datos para calcular CRC, podría ser un error o estado inválido
            calculated_crc = 0; // O manejar de otra forma
        }
        
        // Eliminamos los bytes de CRC y fin si existían (esta lógica puede necesitar ajuste)
        // Esta parte es delicada si el mensaje ya tenía un CRC y se está recomponiendo.
        // Por ahora, asumimos que si llegamos aquí, es para añadir un nuevo CRC.
        // Si la intención es recalcular, la lógica de pop_back debe ser precisa.
        // Por simplicidad, si ya hay un END_MARK, lo quitamos y los 2 bytes anteriores (supuesto CRC)
        if (message.back() == getLTELEndMark()) {
            message.pop_back(); // END_MARK
            if (!message.empty()) message.pop_back(); // CRC high
            if (!message.empty()) message.pop_back(); // CRC low
        }
        
        // Añadimos CRC y fin
        message.push_back(static_cast<uint8_t>(calculated_crc & 0xFF));
        message.push_back(static_cast<uint8_t>((calculated_crc >> 8) & 0xFF));
        message.push_back(getLTELEndMark());
    }
    
    return true;
}

STATUS CommandMessage::validate(uint8_t *buffer, uint8_t length) {
	STATUS frameStatus = checkFrameValidity(buffer, length);
	if (frameStatus != (STATUS::VALID_FRAME))
		return (frameStatus);
	STATUS crcStatus = checkCRCValidity(buffer, length);
	if (crcStatus != (STATUS::RDSS_DATA_OK))
		return (crcStatus);
	STATUS moduleStatus = checkModule(buffer, length);
	if (moduleStatus != (STATUS::CONFIG_FRAME)) {
		return (moduleStatus);
	} else {
		saveFrame(buffer, length);
		return (STATUS::CONFIG_FRAME);
	}
}
STATUS CommandMessage::checkFrameValidity(uint8_t *frame, uint8_t length) {
	if (length > (CommandConstants::MINIMUN_FRAME_LEN)) {
		if (frame[0] == CommandConstants::RDSS_START_MARK) {
			if (frame[length - 1] == CommandConstants::RDSS_END_MARK)
				return STATUS::VALID_FRAME;
			else
				return STATUS::START_READING;
		} else
			return STATUS::NOT_VALID_FRAME;
	} else

		return STATUS::WAITING;
}

/*
 * Método que determina el tipo de mensaje basado en su destino
 * 
 * Lógica:
 * - Si el mensaje está dirigido específicamente a este dispositivo 
 *   (coincide module_function Y module_id) → CONFIG_FRAME (procesar localmente)
 * - Si el mensaje está dirigido a otro dispositivo
 *   (no coincide module_function O no coincide module_id) → RETRANSMIT_FRAME (retransmitir)
 */
STATUS CommandMessage::checkModule(uint8_t *frame, uint8_t length) {
    uint8_t frameModuleType = frame[static_cast<int>(INDEX::MODULE_TYPE)];
    uint8_t frameModuleId = frame[static_cast<int>(INDEX::MODULE_ID)];
    
    // Mensaje dirigido a este dispositivo (configuración local)
    if (frameModuleType == module_function && frameModuleId == module_id) {
        return STATUS::CONFIG_FRAME;
    } 
    
    // Mensaje dirigido a otro dispositivo (retransmitir)
    return STATUS::RETRANSMIT_FRAME;
}

STATUS CommandMessage::checkCRCValidity(uint8_t *frame, uint8_t len) {
	uint16_t calculatedCrc;
	uint16_t savedCrc;
	savedCrc = ((uint16_t) frame[len - CommandConstants::CRC_HIGH_BYTE_OFFSET] << 8);
	savedCrc |= (uint16_t) frame[len - CommandConstants::CRC_LOW_BYTE_OFFSET];
	calculatedCrc = crc_get(&frame[1], len - CommandConstants::FRAME_HEADER_SIZE); // Usar la función estática
	return ((calculatedCrc == savedCrc) ?
			(STATUS::RDSS_DATA_OK) : (STATUS::CRC_ERROR));
}

void CommandMessage::saveFrame(uint8_t *buffer, uint8_t length) {

	command_id = buffer[static_cast<int>(INDEX::CMD)];
	module_id = buffer[static_cast<int>(INDEX::MODULE_ID)];
	module_function = buffer[static_cast<int>(INDEX::MODULE_TYPE)];

	num_byte_data = (buffer[static_cast<int>(INDEX::DATA_LENGHT1)]
			+ buffer[static_cast<int>(INDEX::DATA_LENGHT2)]);

	storeData(num_byte_data,
			reinterpret_cast<const uint8_t*>(buffer)
					+ static_cast<int>(INDEX::DATA_START));
}
/*
 template <typename T>
 T data_frame = frame[data];
 */

void CommandMessage::storeData(size_t dataLength, const void *dataPtr) {
	if (dataLength <= 0) {
		return; // Manejo de errores: No guardar datos inválidos
	}

	data_size = dataLength;
	message.resize(dataLength); // Redimensiona el vector para el nuevo tamaño

	// Copia la data al vector interno
	std::copy(static_cast<const uint8_t*>(dataPtr),
			static_cast<const uint8_t*>(dataPtr) + dataLength, message.begin());
}

// Devuelve el tamaño de la data almacenada
size_t CommandMessage::getDataSize() const {
	return data_size;
}

// Devuelve el valor almacenado como uint8_t, si el tamaño es 1
uint8_t CommandMessage::getDataAsUint8() const {
	if (data_size != 1) {
		// Manejo de errores: El tamaño no es 1
		return 0;
	}
	return message[0];
}

// Devuelve el valor almacenado como uint16_t, si el tamaño es 2
uint16_t CommandMessage::getDataAsUint16() const {
	if (data_size != 2) {
		// Manejo de errores: El tamaño no es 4
		return 0;
	}
	union {
		uint16_t value;
		uint8_t bytes[2];
	} converter;

	std::copy(message.begin(), message.begin() + 2, converter.bytes);

	return converter.value;
}

// Devuelve el valor almacenado como uint32_t, si el tamaño es 4
uint32_t CommandMessage::getDataAsUint32() const {
	if (data_size != 4) {
		// Manejo de errores: El tamaño no es 4
		return 0;
	}
	union {
		uint32_t value;
		uint8_t bytes[4];
	} converter;

	std::copy(message.begin(), message.begin() + 4, converter.bytes);

	return converter.value;
}

// Devuelve el valor almacenado como float, si el tamaño es 4
float CommandMessage::getDataAsFloat() const {
	if (data_size != 4) {
		// Manejo de errores: El tamaño no es 4
		return 0;
	}
	union {
		float value;
		uint8_t bytes[4];
	} converter;

	std::copy(message.begin(), message.begin() + 4, converter.bytes);

	return converter.value;
}


int CommandMessage::freqDecode() const{
    if (message.size() < 4) {
        return 0; // O lanza una excepción
    }

    union {
        uint32_t i;
        float f;
    } freq;

    // Copia segura de los 4 bytes usando memcpy (metodo más eficiente si siempre hay 4 bytes)
    memcpy(&freq.i, message.data(), 4);

    // Manejo del Endianness (solo necesario si es crítico la portabilidad)
    // Si necesitas manejarlo, aquí deberías incluir el código para el intercambio de bytes


    return static_cast<int>(freq.f * 1000000.0f);

}

// Método simplificado para componer y enviar mensajes directamente
bool CommandMessage::composeAndSendMessage(UartHandler* uartComm, uint8_t* data, uint8_t size) {
    if (!uartComm) return false;
    
    // Calculate total frame size: START + MODULE_FUNC + MODULE_ID + CMD + RESERVED + SIZE + DATA + CRC_L + CRC_H + END
    const uint8_t HEADER_SIZE = 6;  // START, MODULE_FUNC, MODULE_ID, CMD, RESERVED, SIZE
    const uint8_t FOOTER_SIZE = 3;  // CRC_L, CRC_H, END
    uint8_t frame_size = HEADER_SIZE + size + FOOTER_SIZE;
    
    // Use stack buffer for small frames, avoid dynamic allocation
    uint8_t frame_buffer[255];  // Maximum UART frame size
    
    if (frame_size > sizeof(frame_buffer)) {
        return false;  // Frame too large
    }
    
    uint8_t* frame = frame_buffer;
    uint8_t index = 0;
    
    // Build frame header
    frame[index++] = getLTELStartMark();
    frame[index++] = module_function;
    frame[index++] = module_id;
    frame[index++] = command_id;
    frame[index++] = 0;  // Reserved
    frame[index++] = size;  // Data size
    
    // Add data payload
    if (size > 0 && data != nullptr) {
        memcpy(&frame[index], data, size);
        index += size;
    }
    
    // Calculate CRC over the payload (from module_function to end of data)
    uint16_t calculated_crc = crc_get(&frame[1], index - 1);
    
    // Add CRC and end marker
    frame[index++] = static_cast<uint8_t>(calculated_crc & 0xFF);
    frame[index++] = static_cast<uint8_t>((calculated_crc >> 8) & 0xFF);
    frame[index++] = getLTELEndMark();
    
    // Send frame directly
    return (uartComm->transmitMessage(frame, index) == HAL_OK);
}




