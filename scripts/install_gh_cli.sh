#!/bin/bash
# Script para instalar GitHub CLI en Windows (Git Bash)

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== Instalador de GitHub CLI para Windows ===${NC}"

# Verificar si ya está instalado
if command -v gh &> /dev/null; then
    echo -e "${GREEN}GitHub CLI ya está instalado!${NC}"
    gh --version
    exit 0
fi

echo -e "${YELLOW}GitHub CLI no encontrado. Opciones de instalación:${NC}"
echo ""
echo "1. Con winget (recomendado para Windows 10/11)"
echo "2. Con scoop"
echo "3. Descargar instalador manual"
echo "4. Cancelar"
echo ""
read -p "Selecciona una opción (1-4): " option

case $option in
    1)
        echo -e "${YELLOW}Instalando con winget...${NC}"
        cmd.exe /c "winget install --id GitHub.cli"
        ;;
    2)
        echo -e "${YELLOW}Instalando con scoop...${NC}"
        if ! command -v scoop &> /dev/null; then
            echo -e "${RED}Scoop no está instalado. Instálalo primero: https://scoop.sh${NC}"
            exit 1
        fi
        scoop install gh
        ;;
    3)
        echo -e "${YELLOW}Abriendo página de descarga...${NC}"
        echo -e "Descarga el instalador desde: https://cli.github.com/"
        cmd.exe /c "start https://cli.github.com/"
        echo ""
        echo -e "${YELLOW}Después de instalar, cierra y vuelve a abrir Git Bash${NC}"
        exit 0
        ;;
    4)
        echo -e "${YELLOW}Instalación cancelada.${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}Opción inválida${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}Instalación completada!${NC}"
echo -e "${YELLOW}Ahora debes autenticarte con GitHub:${NC}"
echo -e "   ${GREEN}gh auth login${NC}"
echo ""
echo -e "${YELLOW}Selecciona las opciones:${NC}"
echo "- GitHub.com"
echo "- HTTPS"
echo "- Login with a web browser (recomendado)"
echo ""
read -p "¿Deseas autenticarte ahora? (s/n): " auth_now

if [[ "$auth_now" == "s" || "$auth_now" == "S" ]]; then
    gh auth login
    echo ""
    echo -e "${GREEN}¡Listo! Ahora puedes ejecutar el script de separación:${NC}"
    echo -e "   ${GREEN}bash scripts/split_gateway_lora.sh${NC}"
else
    echo -e "${YELLOW}Recuerda autenticarte antes de ejecutar el script:${NC}"
    echo -e "   ${GREEN}gh auth login${NC}"
fi
