# Universal STM32 Flasher - Herramienta de Programación

## 📦 ¿Qué es esto?

Una herramienta **UNIVERSAL** para programar **CUALQUIER** placa STM32 a través de ST-Link.

**Características:**
- ✅ Interfaz gráfica (GUI) - fácil de usar
- ✅ Soporta archivos: **BIN**, **HEX**, **ELF**
- ✅ Funciona con TODOS los STM32 (F0, F1, F4, G4, H7, etc.)
- ✅ Un solo archivo EXE - no requiere Python
- ✅ Detección automática de herramientas

---

## 🚀 Uso Rápido (3 Pasos)

### Paso 1: Instalar ST-Link Drivers
Descargar e instalar drivers ST-Link:
- **Descarga**: https://www.st.com/en/development-tools/stsw-link009.html
- **Tamaño**: ~5 MB
- **Instalación**: Siguiente → Siguiente → Instalar

### Paso 2: Instalar STM32CubeProgrammer
Descargar STM32CubeProgrammer (herramienta oficial de ST):
- **Descarga**: https://www.st.com/stm32cubeprog
- **Tamaño**: ~400 MB
- **Instalación**: Ubicación recomendada: `C:\Program Files\STMicroelectronics\`

### Paso 3: Usar el Flasher
1. Conectar ST-Link a la placa STM32
2. Ejecutar `STM32_Universal_Flasher.exe`
3. Seleccionar archivo de firmware (BIN/HEX/ELF)
4. Hacer clic en "FLASH DEVICE"

---

## 🖥️ Interfaz Gráfica

```
┌────────────────────────────────────────────┐
│   Universal STM32 Flasher                  │
├────────────────────────────────────────────┤
│                                            │
│  Firmware File:                            │
│  ┌──────────────────────┐  ┌──────────┐  │
│  │ C:\firmware.bin      │  │ Browse...│  │
│  └──────────────────────┘  └──────────┘  │
│                                            │
│  Flash Address (solo para BIN):            │
│  ┌────────────┐                           │
│  │ 0x08000000 │  (HEX/ELF usan dirección  │
│  └────────────┘   embebida)               │
│                                            │
│  Opciones:                                 │
│  ☑ Borrado total antes de programar       │
│  ☑ Verificar después de programar         │
│  ☑ Resetear dispositivo después           │
│                                            │
│  ┌────────────────────────────────────┐   │
│  │      FLASH DEVICE                  │   │
│  └────────────────────────────────────┘   │
│                                            │
│  Output Log:                               │
│  ┌────────────────────────────────────┐   │
│  │ Searching for programmer...        │   │
│  │ ✓ Found: STM32_Programmer_CLI.exe  │   │
│  │ Programming flash memory...        │   │
│  │ SUCCESS! Device programmed         │   │
│  └────────────────────────────────────┘   │
│                                            │
│  Estado: Ready                             │
└────────────────────────────────────────────┘
```

---

## 📝 Tipos de Archivos Soportados

| Tipo | Extensión | Dirección | Uso Típico |
|------|-----------|-----------|------------|
| **Binary** | `.bin` | Manual (ej: 0x08000000) | Compiladores, exportación directa |
| **Intel HEX** | `.hex` | Automática (embebida) | Keil, IAR, STM32CubeIDE |
| **ELF** | `.elf` | Automática (embebida) | GCC, salida de compilación |

### ¿Qué archivo usar?

- **¿Tienes `.hex` o `.elf`?** → Úsalos directamente (más fácil)
- **¿Solo tienes `.bin`?** → Necesitas saber la dirección flash:
  - STM32F0/F1/F4/G4/L4: `0x08000000` (mayoría)
  - Algunos bootloaders: `0x08004000` o `0x08008000`

---

## 🔌 Conexión ST-Link

### Pines Mínimos Requeridos:
```
ST-Link V2/V3 → Placa STM32
───────────────────────────
  SWDIO  →  SWDIO (PA13)
  SWCLK  →  SWCLK (PA14)
  GND    →  GND
  3.3V   →  VDD (opcional, si placa no tiene alimentación)
```

### Verificar Conexión:
1. Conectar ST-Link USB a PC
2. LED en ST-Link debe encender (rojo/verde)
3. Abrir `STM32_Universal_Flasher.exe`
4. Debe detectar automáticamente el programador

---

## 💻 Uso por Línea de Comandos

Para automatización o scripts:

```cmd
REM Ejemplo 1: Archivo BIN
STM32_Universal_Flasher.exe firmware.bin 0x08000000

REM Ejemplo 2: Archivo HEX (dirección automática)
STM32_Universal_Flasher.exe firmware.hex

REM Ejemplo 3: Archivo ELF (dirección automática)
STM32_Universal_Flasher.exe firmware.elf
```

---

## 🎯 Casos de Uso Comunes

### 1. Programar STM32F103 (Blue Pill)
```
- Archivo: firmware.bin
- Dirección: 0x08000000
- Borrado total: SÍ
- Verificar: SÍ
```

### 2. Programar STM32G474 (tu gateway)
```
- Archivo: gateway-2lora.bin
- Dirección: 0x08000000
- Borrado total: SÍ
```

### 3. Programar con bootloader personalizado
```
- Archivo: app.bin
- Dirección: 0x08008000  ← Bootloader en 0x08000000
- Borrado total: NO (preservar bootloader)
```

### 4. Programar desde Keil/IAR
```
- Archivo: proyecto.hex  ← Exportado de IDE
- Dirección: (automática)
- Borrado total: SÍ
```

---

## 🐛 Solución de Problemas

### "STM32CubeProgrammer not found"
**Solución:**
1. Descargar: https://www.st.com/stm32cubeprog
2. Instalar en: `C:\Program Files\STMicroelectronics\`
3. Reiniciar el flasher

### "No ST-Link detected"
**Verificar:**
- ✅ ST-Link conectado a USB
- ✅ Drivers instalados (STSW-LINK009)
- ✅ Cables SWDIO/SWCLK conectados
- ✅ Placa STM32 alimentada (3.3V)

**Probar:**
```
1. Desconectar ST-Link del USB
2. Cerrar todas las herramientas ST
3. Reconectar ST-Link
4. Ejecutar flasher nuevamente
```

### "Error: dual-bank mode"
**Solución (solo una vez):**
```cmd
# Deshabilitar modo dual-bank
STM32_Programmer_CLI.exe -c port=SWD -ob DBANK=0
```

### "Verification failed"
**Causas:**
- Protección de lectura (RDP) activada
- Conexión inestable
- Archivo corrupto

**Solución:**
1. Desactivar protección:
   ```cmd
   STM32_Programmer_CLI.exe -c port=SWD -ob RDP=0xAA
   ```
2. Probar con cables más cortos
3. Verificar archivo de firmware

---

## 📋 Checklist Antes de Programar

- [ ] ST-Link drivers instalados
- [ ] STM32CubeProgrammer instalado
- [ ] ST-Link conectado a USB (LED encendido)
- [ ] Cables SWDIO/SWCLK conectados
- [ ] Placa STM32 alimentada
- [ ] Archivo de firmware preparado (.bin/.hex/.elf)
- [ ] Conoces la dirección flash (para .bin)

---

## 🔒 Configuración de Protección

### Desactivar Protección de Lectura (RDP)
```
Option Bytes → RDP → Level 0 (0xAA)
```

### Desactivar Protección de Escritura
```
Option Bytes → WRP → Disabled
```

### Modo Single-Bank (recomendado)
```
Option Bytes → DBANK → 0 (Single Bank)
```

---

## 📦 Distribución al Equipo

### Opción 1: Solo EXE + Instrucciones
```
Carpeta_Para_Compartir/
├── STM32_Universal_Flasher.exe  ← Este archivo
├── LEEME.txt                    ← Este documento
└── ejemplo_firmware.bin         ← Ejemplo (opcional)
```

**Nota:** Cada PC debe tener STM32CubeProgrammer instalado.

### Opción 2: Package Completo (Portable)
```
STM32_Flasher_Portable/
├── STM32_Universal_Flasher.exe
├── LEEME.txt
├── tools/                       ← Copiar de instalación
│   ├── STM32_Programmer_CLI.exe
│   ├── *.dll
│   └── api/
└── drivers/
    └── STSW-LINK009.exe         ← Instalador drivers
```

**Ventaja:** Funciona sin instalar nada (excepto drivers).

---

## 🎓 Ejemplos de Uso

### Ejemplo 1: Estudiante con Blue Pill
```
1. Compilar en Arduino IDE/PlatformIO → obtener firmware.bin
2. Conectar ST-Link a Blue Pill
3. Abrir STM32_Universal_Flasher.exe
4. Seleccionar firmware.bin
5. Dirección: 0x08000000
6. FLASH DEVICE
```

### Ejemplo 2: Producción - Programar 100 placas
```batch
REM Script automático
@echo off
for %%f in (firmwares\*.bin) do (
    echo Programando %%f...
    STM32_Universal_Flasher.exe %%f 0x08000000
    if errorlevel 1 (
        echo ERROR en %%f
        pause
    ) else (
        echo OK - Siguiente placa...
        timeout /t 5
    )
)
```

### Ejemplo 3: Update OTA via archivo HEX
```
1. Recibir firmware.hex por email
2. Conectar placa al ST-Link
3. Arrastrar firmware.hex al flasher
4. Click "FLASH DEVICE"
5. Listo - no necesitas saber dirección
```

---

## 🌍 Dispositivos STM32 Soportados

**Todas las familias STM32:**
- ✅ STM32F0 (Cortex-M0)
- ✅ STM32F1 (Blue Pill, etc.)
- ✅ STM32F4 (Black Pill, Discovery)
- ✅ STM32G0/G4 (tu gateway)
- ✅ STM32H7 (alto rendimiento)
- ✅ STM32L0/L4 (bajo consumo)
- ✅ STM32WB (Bluetooth)
- ✅ Y más...

---

## 📞 Soporte

### Problemas comunes:
1. **No detecta programador** → Instalar STM32CubeProgrammer
2. **Error de conexión** → Verificar cables y alimentación
3. **Verificación falla** → Desactivar protecciones

### Recursos:
- STMicroelectronics: https://www.st.com
- STM32CubeProgrammer: https://www.st.com/stm32cubeprog
- ST-Link Drivers: https://www.st.com/en/development-tools/stsw-link009.html

---

## 📄 Licencia

Herramienta gratuita para uso interno del equipo de ingeniería.

**Nota:** STM32CubeProgrammer es propiedad de STMicroelectronics.

---

**Creado**: Octubre 2025  
**Versión**: 1.0  
**Para**: Equipo de Ingeniería
