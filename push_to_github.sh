#!/bin/bash
# Script para subir el repositorio gateway-lora a GitHub
# Ejecutar DESPUÉS de crear el repositorio en GitHub.com

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Push de gateway-lora a GitHub                     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════╝${NC}"
echo ""

# Verificar que estamos en el directorio correcto
if [[ ! -d "/c/Users/artur/temp_gateway-lora" ]]; then
    echo -e "${RED}Error: El directorio temp_gateway-lora no existe${NC}"
    echo -e "Ejecuta primero: bash scripts/split_gateway_lora.sh"
    exit 1
fi

cd /c/Users/artur/temp_gateway-lora

echo -e "${YELLOW}Paso 1: Verificando estado del repositorio local...${NC}"
echo -e "Rama actual: ${GREEN}$(git branch --show-current)${NC}"
echo -e "Commits: ${GREEN}$(git log --oneline | wc -l)${NC}"
echo ""

echo -e "${YELLOW}Paso 2: Verificando remote...${NC}"
if git remote get-url origin &> /dev/null; then
    current_remote=$(git remote get-url origin)
    echo -e "Remote actual: ${YELLOW}$current_remote${NC}"
    
    if [[ "$current_remote" == *"gateway-lora"* ]]; then
        echo -e "${GREEN}✓ Remote ya está configurado correctamente${NC}"
    else
        echo -e "${YELLOW}⚠ Remote apunta a otro repositorio${NC}"
        read -p "¿Deseas reconfigurar el remote? (s/n): " reconfig
        if [[ "$reconfig" == "s" || "$reconfig" == "S" ]]; then
            git remote remove origin
            git remote add origin https://github.com/uqomm/gateway-lora.git
            echo -e "${GREEN}✓ Remote reconfigurado${NC}"
        fi
    fi
else
    echo -e "${YELLOW}No hay remote configurado${NC}"
    echo ""
    echo -e "${BLUE}Instrucciones:${NC}"
    echo -e "1. Ve a: ${YELLOW}https://github.com/new${NC}"
    echo -e "2. Crea un repositorio llamado: ${GREEN}gateway-lora${NC}"
    echo -e "3. NO inicialices con README, .gitignore o licencia"
    echo ""
    read -p "Presiona Enter cuando hayas creado el repositorio en GitHub..."
    
    git remote add origin https://github.com/uqomm/gateway-lora.git
    echo -e "${GREEN}✓ Remote agregado${NC}"
fi

echo ""
echo -e "${YELLOW}Paso 3: Verificando conectividad con GitHub...${NC}"
if git ls-remote origin &> /dev/null; then
    echo -e "${GREEN}✓ Conexión exitosa con GitHub${NC}"
else
    echo -e "${RED}✗ No se puede conectar con GitHub${NC}"
    echo -e "Verifica que:"
    echo -e "  - El repositorio existe en GitHub"
    echo -e "  - Tienes acceso al repositorio"
    echo -e "  - Tu conexión a internet funciona"
    exit 1
fi

echo ""
echo -e "${YELLOW}Paso 4: Preparando para push...${NC}"
echo -e "Se subirán ${GREEN}$(git log --oneline | wc -l)${NC} commits"
echo -e "Rama: ${GREEN}main${NC}"
echo -e "Remote: ${GREEN}https://github.com/uqomm/gateway-lora.git${NC}"
echo ""

read -p "¿Deseas continuar con el push? (s/n): " confirm
if [[ "$confirm" != "s" && "$confirm" != "S" ]]; then
    echo -e "${YELLOW}Push cancelado${NC}"
    exit 0
fi

echo ""
echo -e "${YELLOW}Paso 5: Subiendo código a GitHub...${NC}"
if git push -u origin main; then
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✓ Push exitoso!                                   ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}Repositorio disponible en:${NC}"
    echo -e "   ${BLUE}https://github.com/uqomm/gateway-lora${NC}"
    echo ""
    echo -e "${YELLOW}Próximos pasos:${NC}"
    echo -e "1. Verifica el repositorio en GitHub"
    echo -e "2. Si todo está correcto, ejecuta:"
    echo -e "   ${GREEN}cd /c/Users/artur/fw-gateway${NC}"
    echo -e "   ${GREEN}bash scripts/cleanup_original_repo.sh${NC}"
else
    echo ""
    echo -e "${RED}╔════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ✗ Error en el push                                ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}Posibles causas:${NC}"
    echo -e "  - El repositorio ya tiene contenido"
    echo -e "  - Problemas de autenticación"
    echo -e "  - Problemas de red"
    echo ""
    echo -e "${YELLOW}Soluciones:${NC}"
    echo -e "  - Verifica que el repositorio está vacío"
    echo -e "  - Usa: ${GREEN}git push -u origin main --force${NC} (si estás seguro)"
    echo -e "  - Verifica tus credenciales de Git"
    exit 1
fi
