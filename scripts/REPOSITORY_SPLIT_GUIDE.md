# Guía de Separación de Repositorios

## Objetivo

Separar el proyecto `gateway_lora` (STM32F103) en un repositorio independiente, manteniendo el historial de Git, mientras se conserva `gateway-2lora` (STM32G474) en el repositorio actual `fw-gateway`.

## Repositorios Resultantes

### 1. fw-gateway (existente)
- **Proyecto**: gateway-2lora (STM32G474)
- **URL**: https://github.com/uqomm/fw-gateway

### 2. gateway-lora (nuevo)
- **Proyecto**: gateway_lora (STM32F103)
- **URL**: https://github.com/uqomm/gateway-lora (se creará)

## Prerrequisitos

### Opción A: Con GitHub CLI (Recomendado)

1. Instalar GitHub CLI desde: https://cli.github.com/
2. Autenticarse:
   ```bash
   gh auth login
   ```

### Opción B: Sin GitHub CLI (Manual)

Crearás el repositorio manualmente en GitHub durante el proceso.

### Opcional: git-filter-repo (Recomendado para mejor rendimiento)

```bash
# Con pip
pip install git-filter-repo

# O descargar desde: https://github.com/newren/git-filter-repo
```

## Proceso de Separación

### Paso 1: Preparación

1. **Asegúrate de que todos los cambios estén commiteados**:
   ```bash
   cd /c/Users/artur/fw-gateway
   git status
   ```

2. **Si hay cambios sin commitear**:
   ```bash
   git add .
   git commit -m "Save work before repository split"
   git push
   ```

### Paso 2: Ejecutar el Script de Separación

```bash
cd /c/Users/artur/fw-gateway
bash scripts/split_gateway_lora.sh
```

Este script:
1. ✅ Clona el repositorio a un directorio temporal
2. ✅ Filtra el historial para mantener solo `gateway_lora`
3. ✅ Reorganiza la estructura de archivos
4. ✅ Crea README y .gitignore apropiados
5. ✅ Crea el nuevo repositorio en GitHub (con `gh`) o te guía para hacerlo manualmente
6. ✅ Hace push del código al nuevo repositorio

### Paso 3: Verificación

1. **Visita el nuevo repositorio**:
   ```
   https://github.com/uqomm/gateway-lora
   ```

2. **Verifica que**:
   - [ ] El historial de commits está preservado
   - [ ] Todos los archivos están presentes
   - [ ] La estructura es correcta
   - [ ] El proyecto compila correctamente

3. **Clonar y probar**:
   ```bash
   cd /c/Users/artur
   git clone https://github.com/uqomm/gateway-lora.git
   cd gateway-lora
   # Probar compilación
   ```

### Paso 4: Limpiar Repositorio Original

⚠️ **IMPORTANTE**: Solo ejecuta este paso después de verificar que el nuevo repositorio funciona correctamente.

```bash
cd /c/Users/artur/fw-gateway
bash scripts/cleanup_original_repo.sh
```

Este script:
1. ✅ Elimina `projects/gateway_lora` del repositorio fw-gateway
2. ✅ Actualiza la documentación
3. ✅ Crea un commit con los cambios
4. ⚠️ **NO hace push automáticamente** (debes hacerlo manualmente)

### Paso 5: Push de Cambios

Después de revisar los cambios:

```bash
cd /c/Users/artur/fw-gateway
git log -1  # Verificar el commit
git push origin feature/phase-1-persistent-modes
```

### Paso 6: Actualización Manual

Actualiza manualmente los siguientes archivos:

1. **`.vscode/tasks.json`**: Eliminar tareas relacionadas con gateway_lora
2. **Scripts**: Actualizar cualquier script que referencie gateway_lora
3. **Documentación**: Actualizar referencias en la documentación

## Estructura Final

### fw-gateway (después de limpieza)
```
fw-gateway/
├── projects/
│   └── gateway-2lora/    # Solo STM32G474
├── scripts/
├── tools/
└── docs/
```

### gateway-lora (nuevo repositorio)
```
gateway-lora/
├── gateway_lora/
│   ├── Core/
│   ├── Drivers/
│   ├── Debug/
│   ├── gateway_lora.ioc
│   └── STM32F103C8TX_FLASH.ld
├── README.md
└── .gitignore
```

## Rollback (En caso de problemas)

Si algo sale mal:

1. **El repositorio original no se ha modificado** hasta que ejecutes `cleanup_original_repo.sh`
2. **Eliminar el nuevo repositorio** (si se creó):
   ```bash
   gh repo delete uqomm/gateway-lora --confirm
   ```
3. **Eliminar el directorio temporal**:
   ```bash
   rm -rf /c/Users/artur/temp_gateway-lora
   ```

## Comandos Útiles

### Ver historial del nuevo repositorio
```bash
cd /c/Users/artur/temp_gateway-lora
git log --oneline --all
```

### Ver tamaño del repositorio
```bash
cd /c/Users/artur/temp_gateway-lora
git count-objects -vH
```

### Verificar archivos incluidos
```bash
cd /c/Users/artur/temp_gateway-lora
git ls-files
```

## Notas Adicionales

- **Historial preservado**: Todos los commits relacionados con gateway_lora se mantienen
- **Sin pérdida de datos**: El repositorio original permanece intacto hasta que ejecutes el script de limpieza
- **Reversible**: Puedes revertir el proceso antes del paso de limpieza
- **Colaboradores**: Los colaboradores del repositorio original tendrán acceso al nuevo repositorio si les das permisos

## Soporte

Si encuentras problemas:
1. Verifica los logs del script
2. Revisa el estado de Git: `git status`
3. Consulta el historial: `git log`

## Referencias

- [git-filter-repo documentation](https://github.com/newren/git-filter-repo)
- [GitHub CLI documentation](https://cli.github.com/manual/)
- [Git filter-branch](https://git-scm.com/docs/git-filter-branch)
