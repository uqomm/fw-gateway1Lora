#!/bin/bash
# Script para limpiar gateway_lora del repositorio original fw-gateway
# EJECUTAR SOLO DESPUÉS DE VERIFICAR QUE EL NUEVO REPOSITORIO ESTÁ OK

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}=== Limpieza de gateway_lora del repositorio fw-gateway ===${NC}"
echo -e "${RED}ADVERTENCIA: Esta operación eliminará el directorio projects/gateway_lora${NC}"
echo -e "${RED}Asegúrate de que el nuevo repositorio gateway-lora está funcionando correctamente.${NC}"
echo ""
read -p "¿Estás seguro de que deseas continuar? (escribir 'si' para confirmar): " confirm

if [[ "$confirm" != "si" ]]; then
    echo -e "${YELLOW}Operación cancelada.${NC}"
    exit 0
fi

# Verificar que estamos en fw-gateway
CURRENT_DIR=$(pwd)
if [[ ! "$CURRENT_DIR" == *"fw-gateway"* ]]; then
    echo -e "${RED}Error: Debes ejecutar este script desde el directorio fw-gateway${NC}"
    exit 1
fi

# Verificar que no hay cambios sin commitear
if [[ -n $(git status -s) ]]; then
    echo -e "${RED}Hay cambios sin commitear. Por favor, haz commit o stash de tus cambios primero.${NC}"
    git status -s
    exit 1
fi

echo -e "${YELLOW}Eliminando directorio projects/gateway_lora...${NC}"
git rm -rf projects/gateway_lora

echo -e "${YELLOW}Actualizando README del proyecto...${NC}"
# Actualizar README.md de projects si existe
if [ -f "projects/README.md" ]; then
    sed -i '/gateway_lora/d' projects/README.md
fi

# Actualizar tareas de VS Code para eliminar referencias a gateway_lora
echo -e "${YELLOW}Limpiando configuración de tareas...${NC}"
if [ -f ".vscode/tasks.json" ]; then
    # Hacer backup
    cp .vscode/tasks.json .vscode/tasks.json.backup
    echo -e "${GREEN}Backup de tasks.json creado${NC}"
fi

# Actualizar documentación
echo -e "${YELLOW}Actualizando documentación...${NC}"
cat >> README.md << 'EOF'

## Proyecto Separado

El proyecto `gateway_lora` (STM32F103) ha sido movido a su propio repositorio:
- [gateway-lora](https://github.com/uqomm/gateway-lora)

Este repositorio ahora contiene únicamente el proyecto `gateway-2lora` (STM32G474).
EOF

# Crear commit
echo -e "${YELLOW}Creando commit de limpieza...${NC}"
git add .
git commit -m "chore: remove gateway_lora project (moved to separate repository)

The gateway_lora project has been moved to its own repository:
https://github.com/uqomm/gateway-lora

This repository now focuses exclusively on the gateway-2lora project (STM32G474).
"

echo -e "${GREEN}=== Limpieza completada ===${NC}"
echo -e "${YELLOW}Cambios realizados:${NC}"
echo -e "- Eliminado: projects/gateway_lora"
echo -e "- Actualizado: README.md"
echo -e "- Backup creado: .vscode/tasks.json.backup (si existía)"
echo ""
echo -e "${YELLOW}Para aplicar los cambios al repositorio remoto:${NC}"
echo -e "   ${GREEN}git push origin feature/phase-1-persistent-modes${NC}"
echo ""
echo -e "${YELLOW}Recuerda actualizar manualmente:${NC}"
echo -e "1. .vscode/tasks.json - eliminar tareas relacionadas con gateway_lora"
echo -e "2. Cualquier script que referencie gateway_lora"
echo -e "3. Documentación adicional"
