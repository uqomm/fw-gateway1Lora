#!/usr/bin/env python3
"""
FASE 1 Testing Tool - Gateway-2Lora Firmware
Herramienta para validar el sistema de persistencia EEPROM

Uso:
    python test_fase1.py COM3 --test all
    python test_fase1.py COM3 --test uart-mode
    python test_fase1.py COM3 --test radio-mode
"""

import serial
import time
import argparse
import sys
from typing import Tuple

# Configuración
BAUDRATE = 115200
TIMEOUT = 2

# Command IDs (según CommandMessage.hpp)
CMD_SET_UART_MODE = 0x60
CMD_QUERY_UART_MODE = 0x61
CMD_SET_RADIO_MODE = 0x52
CMD_QUERY_RADIO_MODE = 0x50
CMD_SET_SF = 0x41
CMD_QUERY_SF = 0x43
CMD_SET_BW = 0x42
CMD_QUERY_BW = 0x44

# Frame markers
FRAME_HEADER = bytes([0xAA, 0x55])

class Colors:
    """ANSI color codes para terminal"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def calculate_crc16(data: bytes) -> int:
    """Calcula CRC-16/MODBUS"""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc

def build_frame(cmd_id: int, data: bytes = b'') -> bytes:
    """Construye un frame de comando completo con CRC"""
    frame = FRAME_HEADER + bytes([cmd_id]) + data
    crc = calculate_crc16(frame)
    frame += bytes([crc & 0xFF, (crc >> 8) & 0xFF])
    return frame

def send_command(ser: serial.Serial, cmd_id: int, data: bytes = b'') -> Tuple[bool, bytes]:
    """Envía un comando y espera respuesta"""
    frame = build_frame(cmd_id, data)
    
    print(f"  {Colors.BLUE}→ Enviando:{Colors.RESET} {frame.hex().upper()}")
    
    # Limpiar buffer de entrada
    ser.reset_input_buffer()
    
    # Enviar comando
    ser.write(frame)
    ser.flush()
    
    # Esperar respuesta
    time.sleep(0.2)
    
    if ser.in_waiting > 0:
        response = ser.read(ser.in_waiting)
        print(f"  {Colors.BLUE}← Respuesta:{Colors.RESET} {response.hex().upper()}")
        return True, response
    else:
        print(f"  {Colors.YELLOW}⚠ Sin respuesta{Colors.RESET}")
        return False, b''

def test_uart_mode(ser: serial.Serial) -> bool:
    """Test 2: Modo UART Persistente"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}Test 2: Modo UART Persistente (0x70){Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")
    
    # 1. Cambiar a modo SINGLE
    print(f"{Colors.YELLOW}1. Configurando modo SINGLE UART (0x01)...{Colors.RESET}")
    success, response = send_command(ser, CMD_SET_UART_MODE, bytes([0x01]))
    
    if not success:
        print(f"{Colors.RED}✗ FALLO: No se recibió respuesta{Colors.RESET}")
        return False
    
    # Verificar respuesta
    if len(response) >= 4 and response[3] == 0x01:
        print(f"{Colors.GREEN}✓ Modo SINGLE configurado correctamente{Colors.RESET}")
    else:
        print(f"{Colors.RED}✗ FALLO: Respuesta incorrecta{Colors.RESET}")
        return False
    
    # 2. Consultar modo actual
    print(f"\n{Colors.YELLOW}2. Consultando modo actual...{Colors.RESET}")
    success, response = send_command(ser, CMD_QUERY_UART_MODE)
    
    if not success:
        print(f"{Colors.RED}✗ FALLO: No se recibió respuesta{Colors.RESET}")
        return False
    
    if len(response) >= 4 and response[3] == 0x01:
        print(f"{Colors.GREEN}✓ Modo actual: SINGLE (correcto){Colors.RESET}")
    else:
        print(f"{Colors.RED}✗ FALLO: Modo actual incorrecto{Colors.RESET}")
        return False
    
    # 3. Instrucciones para reinicio
    print(f"\n{Colors.YELLOW}3. {Colors.BOLD}ACCIÓN REQUERIDA:{Colors.RESET}")
    print(f"{Colors.YELLOW}   → Reinicia el dispositivo (presiona RESET){Colors.RESET}")
    print(f"{Colors.YELLOW}   → Presiona ENTER cuando esté listo...{Colors.RESET}")
    input()
    
    # 4. Verificar persistencia
    print(f"{Colors.YELLOW}4. Verificando persistencia después de reinicio...{Colors.RESET}")
    time.sleep(1)  # Esperar que el dispositivo arranque
    
    success, response = send_command(ser, CMD_QUERY_UART_MODE)
    
    if not success:
        print(f"{Colors.RED}✗ FALLO: No se recibió respuesta después del reinicio{Colors.RESET}")
        return False
    
    if len(response) >= 4 and response[3] == 0x01:
        print(f"{Colors.GREEN}✓✓✓ ÉXITO: El modo persistió después del reinicio!{Colors.RESET}")
        return True
    else:
        print(f"{Colors.RED}✗ FALLO: El modo no persistió (se perdió la configuración){Colors.RESET}")
        return False

def test_radio_mode(ser: serial.Serial) -> bool:
    """Test 3: Radio Mode Persistente"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}Test 3: Radio Mode Persistente (0x0F){Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")
    
    # 1. Cambiar a modo FSK
    print(f"{Colors.YELLOW}1. Configurando modo FSK (0x01)...{Colors.RESET}")
    success, response = send_command(ser, CMD_SET_RADIO_MODE, bytes([0x01]))
    
    if not success:
        print(f"{Colors.RED}✗ FALLO: No se recibió respuesta{Colors.RESET}")
        return False
    
    if len(response) >= 4 and response[3] == 0x01:
        print(f"{Colors.GREEN}✓ Modo FSK configurado correctamente{Colors.RESET}")
    else:
        print(f"{Colors.RED}✗ FALLO: Respuesta incorrecta{Colors.RESET}")
        return False
    
    # 2. Consultar modo actual
    print(f"\n{Colors.YELLOW}2. Consultando modo actual...{Colors.RESET}")
    success, response = send_command(ser, CMD_QUERY_RADIO_MODE)
    
    if not success:
        print(f"{Colors.RED}✗ FALLO: No se recibió respuesta{Colors.RESET}")
        return False
    
    if len(response) >= 4 and response[3] == 0x01:
        print(f"{Colors.GREEN}✓ Modo actual: FSK (correcto){Colors.RESET}")
    else:
        print(f"{Colors.RED}✗ FALLO: Modo actual incorrecto{Colors.RESET}")
        return False
    
    # 3. Instrucciones para reinicio
    print(f"\n{Colors.YELLOW}3. {Colors.BOLD}ACCIÓN REQUERIDA:{Colors.RESET}")
    print(f"{Colors.YELLOW}   → Reinicia el dispositivo (presiona RESET){Colors.RESET}")
    print(f"{Colors.YELLOW}   → Presiona ENTER cuando esté listo...{Colors.RESET}")
    input()
    
    # 4. Verificar persistencia
    print(f"{Colors.YELLOW}4. Verificando persistencia después de reinicio...{Colors.RESET}")
    time.sleep(1)
    
    success, response = send_command(ser, CMD_QUERY_RADIO_MODE)
    
    if not success:
        print(f"{Colors.RED}✗ FALLO: No se recibió respuesta después del reinicio{Colors.RESET}")
        return False
    
    if len(response) >= 4 and response[3] == 0x01:
        print(f"{Colors.GREEN}✓✓✓ ÉXITO: El modo Radio persistió después del reinicio!{Colors.RESET}")
        return True
    else:
        print(f"{Colors.RED}✗ FALLO: El modo Radio no persistió{Colors.RESET}")
        return False

def test_memory_map(ser: serial.Serial) -> bool:
    """Test 4: Mapa de Memoria Sin Conflictos"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}Test 4: Mapa de Memoria Sin Conflictos{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")
    
    configs = [
        ("Spreading Factor", CMD_SET_SF, CMD_QUERY_SF, 10, 0x0A),
        ("Bandwidth", CMD_SET_BW, CMD_QUERY_BW, 7, 0x07),
        ("UART Mode", CMD_SET_UART_MODE, CMD_QUERY_UART_MODE, 1, 0x01),
        ("Radio Mode", CMD_SET_RADIO_MODE, CMD_QUERY_RADIO_MODE, 0, 0x00),
    ]
    
    # Configurar todos los parámetros
    print(f"{Colors.YELLOW}1. Configurando todos los parámetros...{Colors.RESET}\n")
    for name, set_cmd, _, value, _ in configs:
        print(f"  → Configurando {name} = {value}")
        success, _ = send_command(ser, set_cmd, bytes([value]))
        if not success:
            print(f"{Colors.RED}✗ FALLO configurando {name}{Colors.RESET}")
            return False
        time.sleep(0.1)
    
    print(f"\n{Colors.GREEN}✓ Todos los parámetros configurados{Colors.RESET}")
    
    # Reiniciar
    print(f"\n{Colors.YELLOW}2. {Colors.BOLD}ACCIÓN REQUERIDA:{Colors.RESET}")
    print(f"{Colors.YELLOW}   → Reinicia el dispositivo{Colors.RESET}")
    print(f"{Colors.YELLOW}   → Presiona ENTER...{Colors.RESET}")
    input()
    
    time.sleep(1)
    
    # Verificar todos los parámetros
    print(f"\n{Colors.YELLOW}3. Verificando persistencia de TODOS los parámetros...{Colors.RESET}\n")
    all_ok = True
    
    for name, _, query_cmd, expected, expected_hex in configs:
        print(f"  → Verificando {name}...")
        success, response = send_command(ser, query_cmd)
        
        if not success or len(response) < 4:
            print(f"    {Colors.RED}✗ FALLO: Sin respuesta{Colors.RESET}")
            all_ok = False
            continue
        
        actual = response[3]
        if actual == expected_hex:
            print(f"    {Colors.GREEN}✓ {name} = {actual:02X} (correcto){Colors.RESET}")
        else:
            print(f"    {Colors.RED}✗ {name} = {actual:02X} (esperado: {expected_hex:02X}){Colors.RESET}")
            all_ok = False
        
        time.sleep(0.1)
    
    if all_ok:
        print(f"\n{Colors.GREEN}✓✓✓ ÉXITO: Todos los parámetros persistieron sin conflictos!{Colors.RESET}")
        return True
    else:
        print(f"\n{Colors.RED}✗ FALLO: Algunos parámetros no persistieron{Colors.RESET}")
        return False

def main():
    parser = argparse.ArgumentParser(description='FASE 1 Testing Tool')
    parser.add_argument('port', help='Puerto serial (ej: COM3, /dev/ttyUSB0)')
    parser.add_argument('--test', choices=['all', 'uart-mode', 'radio-mode', 'memory-map'], 
                       default='all', help='Test a ejecutar')
    parser.add_argument('--baudrate', type=int, default=BAUDRATE, help='Baudrate')
    
    args = parser.parse_args()
    
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}FASE 1 Testing Tool - Gateway-2Lora{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"Puerto: {args.port}")
    print(f"Baudrate: {args.baudrate}")
    print(f"Test: {args.test}")
    
    try:
        # Abrir puerto serial
        print(f"\n{Colors.YELLOW}Abriendo puerto serial...{Colors.RESET}")
        ser = serial.Serial(args.port, args.baudrate, timeout=TIMEOUT)
        time.sleep(0.5)
        print(f"{Colors.GREEN}✓ Puerto serial abierto{Colors.RESET}")
        
        results = {}
        
        # Ejecutar tests
        if args.test in ['all', 'uart-mode']:
            results['uart-mode'] = test_uart_mode(ser)
        
        if args.test in ['all', 'radio-mode']:
            results['radio-mode'] = test_radio_mode(ser)
        
        if args.test in ['all', 'memory-map']:
            results['memory-map'] = test_memory_map(ser)
        
        # Resumen
        print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}RESUMEN DE RESULTADOS{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")
        
        for test_name, passed in results.items():
            status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if passed else f"{Colors.RED}✗ FAIL{Colors.RESET}"
            print(f"{test_name:20s}: {status}")
        
        all_passed = all(results.values())
        
        if all_passed:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 TODOS LOS TESTS PASARON - FASE 1 COMPLETA! 🎉{Colors.RESET}")
            return 0
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ ALGUNOS TESTS FALLARON - REVISAR{Colors.RESET}")
            return 1
        
    except serial.SerialException as e:
        print(f"\n{Colors.RED}✗ Error de puerto serial: {e}{Colors.RESET}")
        return 1
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Interrumpido por usuario{Colors.RESET}")
        return 1
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print(f"\n{Colors.YELLOW}Puerto serial cerrado{Colors.RESET}")

if __name__ == '__main__':
    sys.exit(main())
