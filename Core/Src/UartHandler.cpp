#include <UartHandler.hpp>
#include <CommandMessage.hpp> // Incluir el encabezado completo para la implementación
#include <cstring>

UartHandler::UartHandler() : huart(nullptr), rx_index(0) {
	// Constructor por defecto
	// Inicializar miembros si es necesario, huart a nullptr
	// memset(buffer, 0, sizeof(buffer)); // buffer ya se inicializa a 0 por ser global o estar en la clase
}

UartHandler::UartHandler(UART_HandleTypeDef *_huart) : huart(_huart), rx_index(0) {
	// Constructor existente
	// memset(buffer, 0, sizeof(buffer)); // buffer ya se inicializa a 0
}

UartHandler::~UartHandler() {

}

uint8_t UartHandler::transmitMessage(uint8_t *data_sen, uint16_t data_len) {
	if (HAL_UART_Transmit(huart, data_sen, data_len, 100) == HAL_OK) {
		return (uint8_t)HAL_OK;
	}
	return (uint8_t)HAL_ERROR;
}

bool UartHandler::get_and_send_command(CommandMessage command) {
	uint8_t *data = command.get_composed_message().data();
	uint8_t size = command.get_composed_message().size();
	if (HAL_UART_Transmit(huart, data, size, 1000)) {
		return HAL_OK;
	}
}

uint8_t UartHandler::read(uint8_t *data_received) {
	read_timeout(data_received, 2000);
}

uint8_t UartHandler::read_timeout(uint8_t *data_received, uint16_t timeout_ms) {
	int i = 0;
	uint8_t size = sizeof(buffer);
	HAL_StatusTypeDef resp;
	resp = HAL_UART_Receive(huart, buffer, size, timeout_ms);

	for (i = 0; buffer[0] == 0x7e && buffer[i] != 0x7f; i++) {
		if (i == 255) {
			i = 0;
			break;
		}
	}

	if (i > 0) {
		i++;
		memcpy(data_received, buffer, i);
		memset(buffer,0,sizeof(buffer));
		return i;
	} else{
		memset(buffer,0,sizeof(buffer));
		return 0;
	}
}


void UartHandler::enable_receive_interrupt(uint8_t _bytes_it){
	HAL_UART_Receive_IT(huart, buffer , _bytes_it);
}


uint8_t UartHandler::read_timeout_new(uint8_t *data_received) {
	int i = 0;
	uint8_t size = sizeof(buffer);
	HAL_StatusTypeDef resp;

	for (i = 0; buffer[0] == 0x7e && buffer[i] != 0x7f; i++) {
		if (i == 255) {
			i = 0;
			break;
		}
	}

	if (i > 0) {
		i++;
		memcpy(data_received, buffer, i);
		memset(buffer, 0, sizeof(buffer));
		return i;
	} else {
		memset(buffer, 0, sizeof(buffer));
		return 0;
	}
}

uint8_t UartHandler::read_byte(uint8_t *data_received) {
	// DEPRECATED: This method has been replaced by process_received_byte()
	// The original implementation had critical bugs:
	// 1. Incorrect DR register access
	// 2. Unstable interrupt chain
	// 3. Missing frame validation
	
	// Use process_received_byte() instead for proper frame-based reception
	return 0;
}

uint8_t UartHandler::process_received_byte(uint8_t received_byte, uint8_t *data_received) {
	uint8_t length_data = 0;
	
	// Add received byte to buffer
	if (rx_index < sizeof(buffer)) {
		buffer[rx_index] = received_byte;
		
		// Check for frame start
		if (rx_index == 0 && received_byte != 0x7E) {
			// Not a valid frame start, ignore this byte
			return 0;
		}
		
		rx_index++;
		
		// Check for frame end
		if (received_byte == 0x7F && rx_index > 1) {
			// Complete frame received (starts with 0x7E, ends with 0x7F)
			if (buffer[0] == 0x7E) {
				memcpy(data_received, buffer, rx_index);
				length_data = rx_index;
			}
			// Reset for next frame
			rx_index = 0;
			memset(buffer, 0, sizeof(buffer));
		}
	} else {
		// Buffer overflow - reset and start over
		rx_index = 0;
		memset(buffer, 0, sizeof(buffer));
	}
	
	return length_data;
}


