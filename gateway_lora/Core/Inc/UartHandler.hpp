/*
 * UartHandler.hpp
 *
 *  Created on: Jun 18, 2024
 *      Author: artur
 */

#ifndef INC_UARTHANDLER_HPP_
#define INC_UARTHANDLER_HPP_

#include "main.h"
// Eliminar #include "CommandMessage.hpp" y reemplazar con una declaración adelantada
class CommandMessage; // Declaración adelantada

class UartHandler {
public:
	UartHandler(); // Constructor por defecto añadido
	UartHandler(UART_HandleTypeDef* _huart1 );
	virtual ~UartHandler();

	uint8_t transmitMessage(uint8_t* data_sen, uint16_t data_len);
	bool get_and_send_command(CommandMessage command);
	uint8_t read(uint8_t* data_received);
	uint8_t read_timeout(uint8_t* data_received, uint16_t timeout_ms);
	uint8_t read_timeout_new(uint8_t* data_received);
	void enable_receive_interrupt(uint8_t _bytes_it);
	uint8_t read_byte(uint8_t *data_received);
	
	// New improved frame-based reception method
	uint8_t process_received_byte(uint8_t received_byte, uint8_t *data_received);

protected:
	UART_HandleTypeDef* huart;
	uint8_t buffer[255] = {0};
	uint8_t rx_index;

};

#endif /* INC_UARTHANDLER_HPP_ */
