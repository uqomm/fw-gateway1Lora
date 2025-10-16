# Gateway LoRa - STM32F103

Firmware para gateway LoRa basado en STM32F103C8T6.

## Descripción

Este proyecto es parte del ecosistema de gateways LoRa. Contiene el firmware para el gateway basado en STM32F103.

## Hardware

- **MCU**: STM32F103C8T6
- **Módulo LoRa**: SX1278

## Compilación

```bash
# Desde el directorio raíz
cd gateway_lora/Debug
make
```

## Flasheo

```bash
# Usando OpenOCD
openocd -f interface/stlink.cfg -f target/stm32f1x.cfg -c "program gateway_lora/Debug/gateway_lora.elf verify reset exit"
```

## Estructura del Proyecto

```
gateway_lora/
├── Core/           # Código principal de la aplicación
├── Drivers/        # Drivers HAL de STM32
├── Debug/          # Configuración de compilación
├── gateway_lora.ioc    # Configuración de STM32CubeMX
└── STM32F103C8TX_FLASH.ld  # Linker script
```

## Documentación

Para más información, consulta la documentación del proyecto principal [fw-gateway](https://github.com/uqomm/fw-gateway).

## Licencia

[Especificar licencia]
