/*
 * Sx1278Lora.cpp
 *
 *  Created on: Aug 27, 2024
 *      Author: ALAN
 */

#include <Lora.hpp>

// Constructor por defecto añadido
Lora::Lora() : Sx1278(Gpio(), Gpio(), nullptr), // Llama al constructor de Sx1278 con Gpio por defecto y spi nullptr
    eeprom(nullptr),
    len(0),
    dioConfig(0), // Valor por defecto, ajustar si es necesario
    flagsMode(0), // Valor por defecto, ajustar si es necesario
    hi2c(nullptr), // Si Lora usa I2C directamente, inicializar a nullptr
    spread_factor(SpreadFactor::SF_7), // Valor por defecto
    bandwidth(LoraBandWidth::BW_125KHZ), // Valor por defecto
    coding_rate(CodingRate::CR_4_5), // Valor por defecto
    downlink_frequency(DOWNLINK_FREQ), // Usar constante definida
    uplink_frequency(UPLINK_FREQ),      // Usar constante definida
    header_mode(LoraHeaderMode::EXPLICIT), // Valor por defecto
    sf_key(EP_SF_ADDR), // Asumiendo que estas claves son constantes o se inicializan así
    bw_key(EP_BW_ADDR),
    cr_key(EP_CR_ADDR),
    frq_key(EP_FRQ_ADDR),
    frq_dw_key(EP_FRQ_DW_ADDR),
    frq_up_key(EP_FRQ_UP_ADDR)
{
    // Cuerpo del constructor por defecto, si se necesita lógica adicional.
    // Por ejemplo, inicializar arrays si los hubiera.
}

Lora::Lora(Gpio _nss, Gpio _reset, SPI_HandleTypeDef *_spi, Memory* _eeprom) :
	Sx1278(_nss, _reset, _spi) {

	spi = _spi;
	eeprom = _eeprom;

	//EPROM KEYS - Corregir las direcciones que estaban intercambiadas
	sf_key = eeprom->createKey(EP_SF_ADDR, sizeof(uint8_t));
	bw_key = eeprom->createKey(EP_BW_ADDR, sizeof(uint8_t));
	cr_key = eeprom->createKey(EP_CR_ADDR, sizeof(uint8_t));
	frq_key = eeprom->createKey(EP_FRQ_ADDR, sizeof(uint32_t));
	frq_up_key = eeprom->createKey(EP_FRQ_UP_ADDR, sizeof(uint32_t)); // Corrección: era frq_dw_key
	frq_dw_key = eeprom->createKey(EP_FRQ_DW_ADDR, sizeof(uint32_t)); // Corrección: era frq_up_key

	set_default_configurations();
}

Lora::~Lora() {
}

int8_t Lora::receive(uint8_t *data_received, LinkMode mode) {
	uint8_t op_mode = (read_8bit_reg(LoraRegisters::RegOpMode));
    if ((op_mode & 0x07) != static_cast<uint8_t>(DeviceOperatingMode::RX_CONTINUOUS)) {

		set_low_frequency_mode(DeviceOperatingMode::SLEEP); //Change modem mode Must in Sleep mode
		HAL_Delay(1);

		set_link_frequency(mode);

		write_8bit_reg(LoraRegisters::RegFifoAddrPtr, DATA_BUFFER_BASE_ADDR);
		set_low_frequency_mode(DeviceOperatingMode::RX_CONTINUOUS);
	}
	if (!wait_irq(RX_DONE_MASK, 0)) {
		uint8_t rx_nb_bytes = read_8bit_reg(LoraRegisters::RegRxNbBytes); //Number for received bytes
		uint8_t fifo_ptr = 0;
		fifo_ptr = read_8bit_reg(LoraRegisters::RegFifoRxCurrentaddr);
		write_8bit_reg(LoraRegisters::RegFifoAddrPtr, fifo_ptr);
		if (read_reg_addr(LoraRegisters::RegFifo, rx_nb_bytes) == 0) {
			memcpy(data_received, fifo, rx_nb_bytes);
			return rx_nb_bytes;
		} else {
			data_received = NULL;
			return 0;
		}
	} else
		return 0;
}

void Lora::set_link_frequency(LinkMode mode) {
	if (mode == LinkMode::DOWNLINK) {
		set_carrier_frquency(downlink_frequency);
	} else if (mode == LinkMode::UPLINK) {
		set_carrier_frquency(uplink_frequency);
	}
}

uint8_t Lora::transmit(uint8_t *data, uint8_t data_len, LinkMode mode) {

	set_low_frequency_mode(DeviceOperatingMode::STANDBY);

	set_link_frequency(mode);

	write_tx_fifo_data(data, data_len);
	set_low_frequency_mode(DeviceOperatingMode::TX);
	if((wait_irq(TX_DONE_MASK, 1000)))
			return HAL_ERROR;
	return HAL_OK;
}


void Lora::check_already_store_data() {
    // Leer configuración de EEPROM
    this->read_settings();
    
    // Verificar si la configuración es válida 
    if (spread_factor < SpreadFactor::SF_6 || spread_factor > SpreadFactor::SF_12 ||
        bandwidth < LoraBandWidth::BW_7_8KHZ || bandwidth > LoraBandWidth::BW_500KHZ ||
        coding_rate < CodingRate::CR_4_5 || coding_rate > CodingRate::CR_4_8 ||
        uplink_frequency < UPLINK_FREQ_MIN || uplink_frequency > UPLINK_FREQ_MAX ||
        downlink_frequency < DOWNLINK_FREQ_MIN || downlink_frequency > DOWNLINK_FREQ_MAX) {
        
        // Si algún parámetro no es válido, establece valores por defecto
        spread_factor = SpreadFactor::SF_7;
        bandwidth = LoraBandWidth::BW_500KHZ;
        coding_rate = CodingRate::CR_4_6;
        uplink_frequency = UPLINK_FREQ;
        downlink_frequency = DOWNLINK_FREQ;
        
        // Guardar configuración por defecto
        this->save_settings();
    }
    
    // Aplicar configuración al hardware
    configure_modem_internal();
}

uint32_t Lora::get_rx_frequency(){
	return uplink_frequency;
}

uint32_t Lora::get_tx_frequency(){
	return downlink_frequency;
}

uint8_t Lora::get_spread_factor(){
	return (uint8_t)spread_factor;
}

uint8_t Lora::get_coding_rate(){
	return (uint8_t)coding_rate;
}

uint8_t Lora::get_bandwidth(){
	return (uint8_t)bandwidth;
}

void Lora::set_tx_freq(uint32_t freq) {
    // Validar el rango de frecuencia
    if (freq >= DOWNLINK_FREQ_MIN && freq <= DOWNLINK_FREQ_MAX) {
        downlink_frequency = freq;
    }
    // No llamamos a configure_modem_internal() aquí porque la configuración
    // del módem no cambia, sólo la frecuencia que se usará en la próxima transmisión
}

void Lora::set_rx_freq(uint32_t freq) {
    // Validar el rango de frecuencia
    if (freq >= UPLINK_FREQ_MIN && freq <= UPLINK_FREQ_MAX) {
        uplink_frequency = freq;
    }
    // No llamamos a configure_modem_internal() aquí porque la configuración
    // del módem no cambia, sólo la frecuencia que se usará en la próxima recepción
}

void Lora::set_bandwidth(uint8_t bw) {
    // Validar que el ancho de banda esté dentro del rango permitido
    if (bw <= static_cast<uint8_t>(LoraBandWidth::BW_500KHZ)) {
        bandwidth = static_cast<LoraBandWidth>(bw);
    }
    // No actualizamos el hardware aquí para seguir el patrón de los otros setters
    // El usuario debe llamar a configure_modem() para aplicar los cambios
}

void Lora::set_spread_factor(uint8_t spread) {
    // Validar que el factor de dispersión esté dentro del rango permitido
    if (spread >= static_cast<uint8_t>(SpreadFactor::SF_6) && 
        spread <= static_cast<uint8_t>(SpreadFactor::SF_12)) {
        spread_factor = static_cast<SpreadFactor>(spread);
    }
    // No actualizamos el hardware aquí para seguir el patrón de los otros setters
    // El usuario debe llamar a configure_modem() para aplicar los cambios
}

void Lora::set_coding_rate(uint8_t cr){
    // Validar que la tasa de codificación esté dentro del rango permitido
    if (cr >= static_cast<uint8_t>(CodingRate::CR_4_5) && 
        cr <= static_cast<uint8_t>(CodingRate::CR_4_8)) {
        coding_rate = static_cast<CodingRate>(cr);
    }
    // No actualizamos el hardware aquí para seguir el patrón de los otros setters
    // El usuario debe llamar a configure_modem() para aplicar los cambios
}


void Lora::set_default_parameters(){
	downlink_frequency = (0xffff);
	uplink_frequency = (0xffff);
	bandwidth = (LoraBandWidth)(0xff);
	spread_factor = (SpreadFactor)(0xff);
	coding_rate = (CodingRate)(0xff);
	this->set_lora_settings(bandwidth, coding_rate, spread_factor, downlink_frequency, uplink_frequency);
	save_settings();
}


void Lora::set_lora_settings(LoraBandWidth bw, CodingRate cr, SpreadFactor sf,
		uint32_t dl_freq, uint32_t up_freq) {
	// Validar y establecer parámetros
	if (sf < SpreadFactor::SF_6 || sf > SpreadFactor::SF_12)
		spread_factor = SpreadFactor::SF_7;
	else
		spread_factor = sf;

	if (bw < LoraBandWidth::BW_7_8KHZ || bw > LoraBandWidth::BW_500KHZ)
		bandwidth = LoraBandWidth::BW_500KHZ;
	else
		bandwidth = bw;

	if (cr < CodingRate::CR_4_5 || cr > CodingRate::CR_4_8)
		coding_rate = CodingRate::CR_4_6;
	else
		coding_rate = cr;

	if (up_freq < UPLINK_FREQ_MIN || up_freq > UPLINK_FREQ_MAX)
		uplink_frequency = UPLINK_FREQ;
	else
		uplink_frequency = up_freq;

	if (dl_freq < DOWNLINK_FREQ_MIN || dl_freq > DOWNLINK_FREQ_MAX)
		downlink_frequency = DOWNLINK_FREQ;
	else
		downlink_frequency = dl_freq;

	// Aplicar los cambios al hardware
	configure_modem_internal();
}

void Lora::configure_modem() {
	// Esta función ahora solo llama a la implementación común
	configure_modem_internal();
}

// Método privado que contiene la implementación común
void Lora::configure_modem_internal() {
	uint8_t symb_timeout_msb = 0;
	
	// Verificaciones adicionales de configure_modem original
	if (spread_factor < SpreadFactor::SF_6 || spread_factor > SpreadFactor::SF_12)
		spread_factor = SpreadFactor::SF_10;
	
	// Configurar modo de encabezado basado en factor de dispersión
	if (spread_factor == SpreadFactor::SF_6) {
		header_mode = LoraHeaderMode::IMPLICIT;
		symb_timeout_msb = 0x03;
		setDetectionParametersReg();
	} else {
		header_mode = LoraHeaderMode::EXPLICIT;
		symb_timeout_msb = 0x00;
	}

	// Configurar registros del módem
	uint8_t modem_cfg1 = 0;
	uint8_t modem_cfg2 = 0;

	modem_cfg1 = static_cast<uint8_t>(bandwidth) << 4;
	modem_cfg1 |= static_cast<uint8_t>(coding_rate) << 1;
	modem_cfg1 |= static_cast<uint8_t>(header_mode);

	modem_cfg2 = static_cast<uint8_t>(spread_factor) << 4;
	modem_cfg2 |= static_cast<uint8_t>(CrcSum::CRC_DISABLE) << 2;
	modem_cfg2 |= static_cast<uint8_t>(symb_timeout_msb);
	
	// Aplicar configuración al hardware
	set_low_frequency_mode(DeviceOperatingMode::SLEEP);
	setRegModemConfig(modem_cfg1, modem_cfg2);
}

void Lora::set_low_frequency_mode(DeviceOperatingMode mode) {
	uint8_t cmd = LORA_MODE_ACTIVATION | LOW_FREQUENCY_MODE
			| static_cast<uint8_t>(mode);
	write_8bit_reg(LoraRegisters::RegOpMode, cmd);
	operatingMode = mode;
}

void Lora::set_default_configurations() {
	set_low_frequency_mode(DeviceOperatingMode::SLEEP);
	uint8_t flagsMode = 0x00;
	HAL_Delay(15);
	write_8bit_reg(LoraRegisters::RegFifoAddrPtr, DATA_BUFFER_BASE_ADDR);
	write_8bit_reg(LoraRegisters::RegFifoRxCurrentaddr, DATA_BUFFER_BASE_ADDR);
	write_8bit_reg(LoraRegisters::RegFifoRxBaseAddr, DATA_BUFFER_BASE_ADDR);
	write_8bit_reg(LoraRegisters::RegFifoTxBaseAddr, DATA_BUFFER_BASE_ADDR);
	write_8bit_reg(LoraRegisters::RegSyncWord, LTEL_COMPATIBLE_SYNC_WORD);
	write_8bit_reg(LoraRegisters::RegPaConfig, SX1278_POWER_17DBM);
	write_8bit_reg(LoraRegisters::RegOcp, DEFAULT_OVERCURRENTPROTECT);
	write_8bit_reg(LoraRegisters::RegLna, DEFAULT_LNAGAIN);
	write_8bit_reg(LoraRegisters::RegSymbTimeoutLsb, RX_TIMEOUT_LSB);
	write_8bit_reg(LoraRegisters::RegPreambleMsb, PREAMBLE_LENGTH_MSB);
	write_8bit_reg(LoraRegisters::RegPreambleLsb,
			LTEL_COMPATIBLE_PREAMBLE_LENGTH_LSB);
	write_8bit_reg(LoraRegisters::RegIrqFlags, CLEAR_IRQ_MASK);
	write_8bit_reg(LoraRegisters::RegHopPeriod, LTEL_COMPATIBLE_HOPS_PERIOD);
	write_8bit_reg(LoraRegisters::RegModemConfig3, LTEL_COMPATIBLE_AGC_AUTO_ON);
	//write_8bit_reg(LoraRegisters::RegDioMapping1, dioConfig);
	write_8bit_reg(LoraRegisters::RegIrqFlagsMask, flagsMode);
}

void Lora::save_settings(){
	eeprom->setValue(sf_key,  static_cast<uint8_t>(spread_factor));
	eeprom->setValue(bw_key,  static_cast<uint8_t>(bandwidth));
	eeprom->setValue(cr_key,  static_cast<uint8_t>(coding_rate));
	// Ya no guardamos la variable 'frequency' que es redundante
	eeprom->setValue(frq_dw_key, static_cast<uint32_t>(downlink_frequency));
	eeprom->setValue(frq_up_key, static_cast<uint32_t>(uplink_frequency));
}

uint32_t Lora::read_settings(){
	spread_factor = static_cast<SpreadFactor> (eeprom->getValue<uint8_t>(sf_key));
	bandwidth = static_cast<LoraBandWidth>(eeprom->getValue<uint8_t>(bw_key));
	coding_rate = static_cast <CodingRate>(eeprom->getValue<uint8_t>(cr_key));
	// Ya no leemos la variable 'frequency' que es redundante
	downlink_frequency = eeprom->getValue<uint32_t>(frq_dw_key);
	uplink_frequency = eeprom->getValue<uint32_t>(frq_up_key);
	
	// Devolvemos la frecuencia de descarga como valor por defecto para mantener retrocompatibilidad
	return downlink_frequency;
}
