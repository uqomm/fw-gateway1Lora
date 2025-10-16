#!/bin/bash
# Script de verificación pre-split
# Verifica que todo está listo para la separación del repositorio

# No usar set -e para permitir que continúe con errores

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Verificación Pre-Split del Repositorio           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════╝${NC}"
echo ""

# Contadores
checks_passed=0
checks_failed=0
warnings=0

# Función para check exitoso
check_ok() {
    echo -e "${GREEN}✓${NC} $1"
    ((checks_passed++))
}

# Función para check fallido
check_fail() {
    echo -e "${RED}✗${NC} $1"
    ((checks_failed++))
}

# Función para advertencia
check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((warnings++))
}

# 1. Verificar directorio actual
echo -e "${BLUE}[1/10]${NC} Verificando directorio actual..."
if [[ "$PWD" == *"fw-gateway"* ]]; then
    check_ok "En el directorio fw-gateway"
else
    check_fail "No estás en el directorio fw-gateway"
fi

# 2. Verificar que gateway_lora existe
echo -e "${BLUE}[2/10]${NC} Verificando proyecto gateway_lora..."
if [ -d "projects/gateway_lora" ]; then
    check_ok "Proyecto gateway_lora encontrado"
    file_count=$(find projects/gateway_lora -type f | wc -l)
    echo -e "      ${YELLOW}→${NC} Archivos encontrados: $file_count"
else
    check_fail "Proyecto gateway_lora NO encontrado"
fi

# 3. Verificar estado de Git
echo -e "${BLUE}[3/10]${NC} Verificando estado de Git..."
if [[ -z $(git status -s) ]]; then
    check_ok "No hay cambios sin commitear"
else
    check_warn "Hay cambios sin commitear:"
    git status -s | head -5
    echo -e "      ${YELLOW}→${NC} Debes hacer commit antes de continuar"
fi

# 4. Verificar rama actual
echo -e "${BLUE}[4/10]${NC} Verificando rama actual..."
current_branch=$(git branch --show-current)
echo -e "      ${YELLOW}→${NC} Rama actual: ${GREEN}$current_branch${NC}"

# 5. Verificar remote
echo -e "${BLUE}[5/10]${NC} Verificando remote de GitHub..."
remote_url=$(git remote get-url origin 2>/dev/null || echo "")
if [[ "$remote_url" == *"github.com"* ]]; then
    check_ok "Remote configurado: $remote_url"
else
    check_warn "Remote no apunta a GitHub"
fi

# 6. Verificar historial de gateway_lora
echo -e "${BLUE}[6/10]${NC} Verificando historial de gateway_lora..."
commit_count=$(git log --oneline --all -- projects/gateway_lora | wc -l)
if [ $commit_count -gt 0 ]; then
    check_ok "Historial encontrado: $commit_count commits"
else
    check_warn "No se encontró historial de gateway_lora"
fi

# 7. Verificar GitHub CLI
echo -e "${BLUE}[7/10]${NC} Verificando GitHub CLI..."
if command -v gh &> /dev/null; then
    gh_version=$(gh --version | head -1)
    check_ok "GitHub CLI instalado: $gh_version"
    
    # Verificar autenticación
    if gh auth status &> /dev/null; then
        check_ok "GitHub CLI autenticado"
    else
        check_warn "GitHub CLI NO está autenticado. Ejecuta: gh auth login"
    fi
else
    check_warn "GitHub CLI NO instalado. Ejecuta: bash scripts/install_gh_cli.sh"
    echo -e "      ${YELLOW}→${NC} Puedes continuar sin gh (creación manual del repo)"
fi

# 8. Verificar git-filter-repo (opcional)
echo -e "${BLUE}[8/10]${NC} Verificando git-filter-repo (opcional)..."
if command -v git-filter-repo &> /dev/null; then
    check_ok "git-filter-repo instalado (rendimiento óptimo)"
else
    check_warn "git-filter-repo no instalado (se usará filter-branch)"
    echo -e "      ${YELLOW}→${NC} Para mejor rendimiento: pip install git-filter-repo"
fi

# 9. Verificar espacio en disco
echo -e "${BLUE}[9/10]${NC} Verificando espacio en disco..."
available_space=$(df -h . | awk 'NR==2 {print $4}')
echo -e "      ${YELLOW}→${NC} Espacio disponible: $available_space"
check_ok "Suficiente espacio en disco"

# 10. Verificar scripts
echo -e "${BLUE}[10/10]${NC} Verificando scripts de separación..."
if [ -f "scripts/split_gateway_lora.sh" ] && [ -x "scripts/split_gateway_lora.sh" ]; then
    check_ok "Script split_gateway_lora.sh encontrado y ejecutable"
else
    check_fail "Script split_gateway_lora.sh no encontrado o no ejecutable"
fi

if [ -f "scripts/cleanup_original_repo.sh" ] && [ -x "scripts/cleanup_original_repo.sh" ]; then
    check_ok "Script cleanup_original_repo.sh encontrado y ejecutable"
else
    check_fail "Script cleanup_original_repo.sh no encontrado o no ejecutable"
fi

# Resumen
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Resumen de Verificación                           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✓ Checks exitosos:${NC} $checks_passed"
echo -e "${RED}✗ Checks fallidos:${NC} $checks_failed"
echo -e "${YELLOW}⚠ Advertencias:${NC} $warnings"
echo ""

# Recomendaciones
if [ $checks_failed -gt 0 ]; then
    echo -e "${RED}❌ NO PUEDES CONTINUAR${NC}"
    echo -e "Hay $checks_failed problemas críticos que debes resolver primero."
    echo ""
    exit 1
elif [ $warnings -gt 0 ]; then
    echo -e "${YELLOW}⚠ PUEDES CONTINUAR CON PRECAUCIÓN${NC}"
    echo -e "Hay $warnings advertencias. Revísalas antes de continuar."
    echo ""
    echo -e "${YELLOW}Recomendaciones:${NC}"
    if [[ -n $(git status -s) ]]; then
        echo -e "1. Hacer commit de cambios: ${GREEN}git add . && git commit -m 'Save work'${NC}"
    fi
    if ! command -v gh &> /dev/null; then
        echo -e "2. Instalar GitHub CLI: ${GREEN}bash scripts/install_gh_cli.sh${NC}"
    fi
    echo ""
else
    echo -e "${GREEN}✅ TODO LISTO PARA LA SEPARACIÓN${NC}"
    echo ""
    echo -e "${GREEN}Puedes proceder con:${NC}"
    echo -e "   ${BLUE}bash scripts/split_gateway_lora.sh${NC}"
    echo ""
    echo -e "${YELLOW}Pasos recomendados:${NC}"
    echo -e "1. Lee la guía completa: ${BLUE}scripts/REPOSITORY_SPLIT_GUIDE.md${NC}"
    echo -e "2. Ejecuta el split: ${GREEN}bash scripts/split_gateway_lora.sh${NC}"
    echo -e "3. Verifica el nuevo repositorio en GitHub"
    echo -e "4. Limpia el repositorio original: ${GREEN}bash scripts/cleanup_original_repo.sh${NC}"
    echo ""
fi

# Información adicional
echo -e "${BLUE}📚 Documentación:${NC}"
echo -e "   • Guía completa: scripts/REPOSITORY_SPLIT_GUIDE.md"
echo -e "   • Documentación de scripts: scripts/README.md"
echo ""
echo -e "${BLUE}🆘 Ayuda:${NC}"
echo -e "   • GitHub CLI: https://cli.github.com/"
echo -e "   • git-filter-repo: https://github.com/newren/git-filter-repo"
echo ""
