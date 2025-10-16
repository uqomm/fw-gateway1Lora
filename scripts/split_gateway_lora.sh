#!/bin/bash
# Script para separar gateway_lora en un repositorio independiente
# Mantiene el historial de Git completo

set -e  # Salir si hay algún error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Separación de gateway_lora en repositorio independiente ===${NC}"

# Variables
ORIGINAL_REPO="fw-gateway"
NEW_REPO="gateway-lora"
GITHUB_USER="uqomm"
TEMP_DIR="/c/Users/artur/temp_${NEW_REPO}"

# Paso 1: Verificar que estamos en el directorio correcto
echo -e "${YELLOW}Paso 1: Verificando directorio actual...${NC}"
CURRENT_DIR=$(pwd)
if [[ ! "$CURRENT_DIR" == *"$ORIGINAL_REPO"* ]]; then
    echo -e "${RED}Error: Debes ejecutar este script desde el directorio fw-gateway${NC}"
    exit 1
fi

# Paso 2: Verificar que no hay cambios sin commitear
echo -e "${YELLOW}Paso 2: Verificando estado de Git...${NC}"
if [[ -n $(git status -s) ]]; then
    echo -e "${RED}Hay cambios sin commitear. Por favor, haz commit o stash de tus cambios primero.${NC}"
    git status -s
    exit 1
fi

# Paso 3: Crear directorio temporal y clonar
echo -e "${YELLOW}Paso 3: Clonando repositorio a directorio temporal...${NC}"
if [ -d "$TEMP_DIR" ]; then
    echo -e "${YELLOW}Eliminando directorio temporal existente...${NC}"
    rm -rf "$TEMP_DIR"
fi

git clone "https://github.com/${GITHUB_USER}/${ORIGINAL_REPO}.git" "$TEMP_DIR"
cd "$TEMP_DIR"

# Paso 4: Filtrar el historial para mantener solo gateway_lora
echo -e "${YELLOW}Paso 4: Filtrando historial para mantener solo gateway_lora...${NC}"
echo -e "${YELLOW}Esto puede tomar unos minutos...${NC}"

# Verificar si git-filter-repo está disponible
if command -v git-filter-repo &> /dev/null; then
    echo -e "${GREEN}Usando git-filter-repo (método recomendado)...${NC}"
    git filter-repo --path projects/gateway_lora --path-rename projects/gateway_lora/:
else
    echo -e "${YELLOW}git-filter-repo no encontrado, usando git filter-branch...${NC}"
    git filter-branch --prune-empty --subdirectory-filter projects/gateway_lora HEAD
fi

# Paso 5: Crear estructura de carpetas adecuada
echo -e "${YELLOW}Paso 5: Reorganizando estructura de archivos...${NC}"
mkdir -p gateway_lora
# Si los archivos ya están en la raíz después del filtrado, moverlos a gateway_lora
if [ -f "gateway_lora.ioc" ]; then
    mv * gateway_lora/ 2>/dev/null || true
fi

# Crear README para el nuevo repositorio
cat > README.md << 'EOF'
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
EOF

# Crear .gitignore si no existe
if [ ! -f ".gitignore" ]; then
    cat > .gitignore << 'EOF'
# Build artifacts
Debug/
Release/
*.o
*.d
*.elf
*.bin
*.hex
*.map
*.lst

# IDE
.settings/
.vscode/
*.launch

# System
.DS_Store
Thumbs.db
EOF
fi

# Commit de cambios si los hay
if [[ -n $(git status -s) ]]; then
    git add .
    git commit -m "Reorganize repository structure after split"
fi

# Paso 6: Crear el repositorio en GitHub (requiere gh CLI o se hace manualmente)
echo -e "${YELLOW}Paso 6: Creando repositorio en GitHub...${NC}"

# Verificar si gh está instalado
if command -v gh &> /dev/null; then
    echo -e "${GREEN}GitHub CLI encontrado, creando repositorio...${NC}"
    gh repo create "${GITHUB_USER}/${NEW_REPO}" --public --source=. --remote=origin --push
else
    echo -e "${YELLOW}GitHub CLI no encontrado.${NC}"
    echo -e "${YELLOW}Por favor, sigue estos pasos manualmente:${NC}"
    echo -e "1. Ve a https://github.com/new"
    echo -e "2. Crea un repositorio llamado: ${NEW_REPO}"
    echo -e "3. NO inicialices con README, .gitignore o licencia"
    echo -e "4. Después, ejecuta estos comandos:"
    echo -e "   ${GREEN}cd $TEMP_DIR${NC}"
    echo -e "   ${GREEN}git remote add origin https://github.com/${GITHUB_USER}/${NEW_REPO}.git${NC}"
    echo -e "   ${GREEN}git branch -M main${NC}"
    echo -e "   ${GREEN}git push -u origin main${NC}"
    echo ""
    read -p "Presiona Enter cuando hayas creado el repositorio en GitHub..."
    
    # Configurar remote y push
    git remote add origin "https://github.com/${GITHUB_USER}/${NEW_REPO}.git"
    git branch -M main
    git push -u origin main
fi

echo -e "${GREEN}=== ¡Separación completada! ===${NC}"
echo -e "${GREEN}Nuevo repositorio creado en: https://github.com/${GITHUB_USER}/${NEW_REPO}${NC}"
echo -e "${YELLOW}El repositorio temporal está en: $TEMP_DIR${NC}"
echo ""
echo -e "${YELLOW}Próximos pasos:${NC}"
echo -e "1. Verifica el nuevo repositorio en GitHub"
echo -e "2. Si todo está correcto, ejecuta el script de limpieza:"
echo -e "   ${GREEN}bash scripts/cleanup_original_repo.sh${NC}"
echo -e "3. Esto eliminará gateway_lora del repositorio fw-gateway original"
