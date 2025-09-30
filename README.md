# Servidor MCP para Notion y GitHub

Este servidor MCP proporciona herramientas para interactuar con Notion y GitHub.

## Configuración

### Variables de entorno requeridas:

```bash
# Notion API Configuration
NOTION_TOKEN=your_notion_integration_token_here

# GitHub API Configuration (opcional, usa token para acceso privado)
GITHUB_TOKEN=your_github_personal_access_token_here
```

### Obtener tokens:

1. **Notion Token**:
   - Ve a [Notion Developers](https://developers.notion.com/)
   - Crea una nueva integración
   - Copia el token interno

2. **GitHub Token** (opcional):
   - Ve a GitHub Settings > Developer settings > Personal access tokens
   - Crea un nuevo token con permisos de `repo`

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

Ejecuta el servidor:

```bash
python server.py
```

## Herramientas disponibles

### Notion
- `create_page`: Crea una nueva página de documentación
- `search_a_page_in_notion`: Busca páginas existentes por título o contenido
- `get_notion_page_content`: Obtiene todo el contenido de una página existente (separado en bloques individuales con IDs para edición)
- `append_text_block`: Agrega texto plano a una página
- `append_title_block`: Agrega un título a una página
- `append_code_block`: Agrega bloque de código formateado
- `update_block`: Modifica contenido de un bloque existente

### GitHub
- `get_github_file_content`: Obtiene contenido de archivo desde URL de GitHub

## Ejemplos de uso

### Crear una página en Notion:
```python
create_page(title="Mi Documentación")
```

### Buscar páginas existentes:
```python
search_a_page_in_notion("proyecto", limit=5)
```

### Obtener contenido de una página (con bloques individuales):
```python
get_notion_page_content("page_id")
# Devuelve contenido completo + lista de bloques con IDs individuales
# Ejemplo de respuesta incluye instrucciones para editar cada bloque
```

### Agregar texto a una página:
```python
append_text_block(page_id="page_id", text="Este es texto adicional")
```

### Agregar un título:
```python
append_title_block(page_id="page_id", title="Sección Nueva", level=2)
```

### Agregar código:
```python
append_code_block(page_id="page_id", code="print('Hola mundo')", language="python")
```

### Obtener contenido de GitHub:
```python
get_github_file_content(repository='backoffice-leads-dashboard', file_path="manage.py", branch="main")
```

## Uso avanzado: Edición de bloques individuales

La herramienta `get_notion_page_content` devuelve información estructurada que facilita la edición precisa de contenido:

### Ejemplo de respuesta estructurada:
```
📄 **Página: Mi Documento** (ID: abc123...)

🔗 **Contenido completo:**
# Mi Documento

Este es un párrafo de ejemplo.

## Sección 1
Más contenido aquí.

📋 **Bloques individuales para edición:**

**Bloque 1** (ID: def456...)
- Tipo: paragraph
- Usar update_block(block_id="def456...", new_content="...", block_type="paragraph")

**Bloque 2** (ID: ghi789...)
- Tipo: heading_2
- Usar update_block(block_id="ghi789...", new_content="...", block_type="heading_2")
```

### Editar un bloque específico:
```python
# Editar el título de la página
update_block(block_id="titulo_block_id", new_content="Nuevo Título", block_type="heading_1")

# Editar un párrafo específico
update_block(block_id="parrafo_block_id", new_content="Texto modificado", block_type="paragraph")

# Editar un bloque de código
update_block(block_id="codigo_block_id", new_content="nuevo_codigo()", block_type="code")
```
