import os
import requests
from notion_client import Client
from fastmcp import FastMCP, Context
import dotenv
from middleware import UserAuthMiddleware
dotenv.load_dotenv()
# Configuración del servidor MCP
mcp = FastMCP("Notion-GitHub MCP Server")
mcp.add_middleware(UserAuthMiddleware())

@mcp.tool()
def create_page(title: str, notion_database_id: str, context: Context = None) -> str:
    """
    Crea una nueva página de documentación en la base de conocimiento de Notion.

    Args:
        title: Título de la nueva página
        notion_database_id: ID de la base de datos donde se creará la página

    Returns:
        ID de la página creada
    """
    notion = context.get_state("notion")
    try:
        # Crear la página con título y contenido opcional

        page = notion.pages.create(
            parent={"database_id": notion_database_id},
            properties={
                "title": {
                    "title": [
                        {
                            "type": "text",
                            "text": {"content": title}
                        }
                    ]
                }
            },
        )

        return f"Página creada exitosamente con ID: {page['id']}"

    except Exception as e:
        return f"Error al crear la página: {str(e)}"

@mcp.tool()
def append_text_block(page_id: str, text: str, after_block_id: str = None, context: Context = None) -> str:
    """
    Agrega un bloque de texto plano a una página existente de Notion.

    Args:
        page_id: ID de la página donde agregar el texto
        text: Contenido de texto a agregar
        after_block_id: ID del bloque después del cual se agregará el nuevo bloque. Si no se proporciona, se agrega al final de la página.
    Returns:
        Mensaje de confirmación
    """
    notion = context.get_state("notion")
    try:
        # Crear bloque de texto
        block = {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": text}
                    }
                ]
            }
        }
        body = {
            "block_id": page_id,
            "children": [block]
        }
        if after_block_id:
            body["after"] = after_block_id

        notion.blocks.children.append(**body)

        return "Bloque de texto agregado exitosamente"

    except Exception as e:
        return f"Error al agregar bloque de texto: {str(e)}"

@mcp.tool()
def append_title_block(page_id: str, title: str, level: int = 1, context: Context = None) -> str:
    """
    Agrega un título a una página de Notion.

    Args:
        page_id: ID de la página donde agregar el título
        title: Texto del título
        level: Nivel del título (1, 2, o 3)

    Returns:
        Mensaje de confirmación
    """
    try:
        notion = context.get_state("notion")
        # Crear bloque de título según el nivel
        block = {
            "object": "block",
            "type": "heading_1" if level == 1 else "heading_2" if level == 2 else "heading_3",
            "heading_1" if level == 1 else "heading_2" if level == 2 else "heading_3": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": title}
                    }
                ]
            }
        }

        notion.blocks.children.append(
            block_id=page_id,
            children=[block]
        )

        return f"Título de nivel {level} agregado exitosamente"

    except Exception as e:
        return f"Error al agregar título: {str(e)}"

@mcp.tool()
def append_code_block(page_id: str, code: str, language: str, context: Context = None) -> str:
    """
    Agrega un bloque de código formateado a una página de Notion.

    Args:
        page_id: ID de la página donde agregar el código
        code: Código a agregar
        language: Lenguaje de programación para el resaltado de sintaxis. Posibles valores: python, javascript, typescript, html, css, json, bash, sql, markdown.

    Returns:
        Mensaje de confirmación
    """
    try:
        notion = context.get_state("notion")
        # Crear bloque de código
        block = {
            "object": "block",
            "type": "code",
            "code": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": code}
                    }
                ],
                "language": language
            }
        }

        notion.blocks.children.append(
            block_id=page_id,
            children=[block]
        )

        return f"Bloque de código ({language}) agregado exitosamente"

    except Exception as e:
        return f"Error al agregar bloque de código: {str(e)}"

@mcp.tool()
def search_a_page_in_notion(search_query: str, limit: int = 10, context: Context = None) -> str:
    """
    Busca páginas existentes en Notion por título o contenido.

    Args:
        search_query: Término de búsqueda para encontrar páginas
        limit: Número máximo de resultados a devolver (por defecto 10)

    Returns:
        Lista de páginas encontradas con su ID, título y URL
    """
    notion = context.get_state("notion")
    try:
        # Buscar páginas usando la API de Notion
        search_results = notion.search(
            query=search_query,
            filter={"property": "object", "value": "page"},
            page_size=limit
        )

        # Procesar resultados
        pages = search_results.get("results", [])

        if not pages:
            return f"No se encontraron páginas que contengan '{search_query}'"

        # Formatear resultados
        results = []
        for page in pages:
            page_id = page.get("id", "N/A")
            properties = page.get("properties", {})
            title_prop = properties.get("Title", {})

            # Extraer título
            title = "Sin título"
            if title_prop.get("title"):
                print(title_prop.get("Title"))
                title_parts = [part.get("plain_text", "") for part in title_prop["title"]]
                title = "".join(title_parts).strip()

            # Crear URL de la página (formato estándar de Notion)
            page_url = f"https://notion.so/{page_id.replace('-', '')}"

            results.append(f"- **{title}** (ID: {page_id})\n  URL: {page_url}")

        result_text = f"**Resultados de búsqueda para '{search_query}'** ({len(pages)} encontrados):\n\n" + "\n".join(results)

        return result_text

    except Exception as e:
        return f"Error al buscar páginas: {str(e)}"

@mcp.tool()
def list_pages_in_notion(start_cursor: str = None, limit: int = 20, context: Context = None) -> str:
    """
    Lista todas las páginas existentes en Notion.

    Args:
        start_cursor: posición de inicio para la paginación. Si no se proporciona, se devuelve la primera página. Se debe extraer del resultado de la función anterior.
        limit: Número máximo de resultados a devolver (por defecto 20)

    Returns:
        Lista de páginas encontradas con su ID, título y URL
    """
    notion = context.get_state("notion")
    try:
        # Buscar páginas usando la API de Notion
        search_object = {
            "query": "",
            "filter": {
                "property": "object",
                "value": "page"
            },
            "page_size": limit
        }
        if start_cursor:
            search_object["start_cursor"] = start_cursor
        search_results = notion.search(**search_object)

        # Procesar resultados
        pages = search_results.get("results", [])

        if not pages:
            return f"No se encontraron páginas"

        # Formatear resultados
        results = []
        for page in pages:
            page_id = page.get("id", "N/A")
            properties = page.get("properties", {})
            title_prop = properties.get("Title", {})

            # Extraer título
            title = "Sin título"
            if title_prop.get("title"):
                print(title_prop.get("Title"))
                title_parts = [part.get("plain_text", "") for part in title_prop["title"]]
                title = "".join(title_parts).strip()

            # Crear URL de la página (formato estándar de Notion)
            page_url = f"https://notion.so/{page_id.replace('-', '')}"

            results.append(f"- **{title}** (ID: {page_id})\n  URL: {page_url}")

        result_text = f"**Resultados de búsqueda** ({len(pages)} encontrados):\n\n" + "\n".join(results)

        return result_text

    except Exception as e:
        return f"Error al buscar páginas: {str(e)}"

@mcp.tool()
def get_notion_page_content(page_id: str, context: Context = None) -> str:
    """
    Obtiene todo el contenido de una página existente de Notion, separado en bloques individuales.

    Args:
        page_id: ID de la página de Notion

    Returns:
        Contenido completo formateado con información de bloques individuales para edición
    """
    try:
        notion = context.get_state("notion")
        # Obtener información básica de la página
        page = notion.pages.retrieve(page_id)

        # Obtener propiedades de la página
        properties = page.get("properties", {})
        title_prop = properties.get("Title", {})

        # Extraer título
        title = "Sin título"
        if title_prop.get("title"):
            title_parts = [part.get("plain_text", "") for part in title_prop["title"]]
            title = "".join(title_parts).strip()

        # Obtener bloques de contenido de la página
        blocks = notion.blocks.children.list(page_id)
        block_objects = blocks.get("results", [])

        if not block_objects:
            return f"La página '{title}' está vacía o no tiene contenido accesible."

        # Procesar bloques individuales
        formatted_blocks = []
        blocks_info = []

        for i, block in enumerate(block_objects, 1):
            block_id = block.get("id")
            block_type = block.get("type")

            # Información del bloque para edición posterior
            block_info = {
                "id": block_id,
                "type": block_type,
                "position": i
            }

            # Contenido formateado del bloque
            block_content = ""
            raw_content = ""

            if block_type == "paragraph":
                # Procesar texto enriquecido
                rich_text = block.get("paragraph", {}).get("rich_text", [])
                for text_segment in rich_text:
                    if text_segment.get("type") == "text":
                        content = text_segment.get("text", {}).get("content", "")
                        raw_content += content

                        # Aplicar formato básico según anotaciones
                        annotations = text_segment.get("annotations", {})
                        if annotations.get("bold"):
                            content = f"**{content}**"
                        if annotations.get("italic"):
                            content = f"*{content}*"
                        if annotations.get("code"):
                            content = f"`{content}`"
                        block_content += content

                block_info["block_type"] = "paragraph"
                block_info["raw_content"] = raw_content

            elif block_type.startswith("heading_"):
                # Procesar encabezados (heading_1, heading_2, heading_3)
                level = int(block_type.split("_")[1])
                rich_text = block.get(block_type, {}).get("rich_text", [])
                for text_segment in rich_text:
                    if text_segment.get("type") == "text":
                        content = text_segment.get("text", {}).get("content", "")
                        raw_content += content
                        block_content = f"{'#' * level} {content}"

                block_info["block_type"] = block_type
                block_info["level"] = level
                block_info["raw_content"] = raw_content

            elif block_type == "code":
                # Procesar bloques de código
                code_text = block.get("code", {}).get("rich_text", [])
                code_content = ""
                for text_segment in code_text:
                    if text_segment.get("type") == "text":
                        code_content += text_segment.get("text", {}).get("content", "")

                language = block.get("code", {}).get("language", "text")
                block_content = f"```{language}\n{code_content}\n```"
                raw_content = code_content

                block_info["block_type"] = "code"
                block_info["language"] = language
                block_info["raw_content"] = raw_content

            elif block_type == "bulleted_list_item":
                # Procesar listas con viñetas
                rich_text = block.get("bulleted_list_item", {}).get("rich_text", [])
                content = ""
                for text_segment in rich_text:
                    if text_segment.get("type") == "text":
                        content += text_segment.get("text", {}).get("content", "")
                block_content = f"- {content}"
                raw_content = content

                block_info["block_type"] = "bulleted_list_item"
                block_info["raw_content"] = raw_content

            elif block_type == "numbered_list_item":
                # Procesar listas numeradas (simplificado)
                rich_text = block.get("numbered_list_item", {}).get("rich_text", [])
                content = ""
                for text_segment in rich_text:
                    if text_segment.get("type") == "text":
                        content += text_segment.get("text", {}).get("content", "")
                block_content = f"1. {content}"
                raw_content = content

                block_info["block_type"] = "numbered_list_item"
                block_info["raw_content"] = raw_content

            # Solo agregar bloques con contenido
            if block_content.strip():
                formatted_blocks.append(block_content)
                blocks_info.append(block_info)

        # Crear contenido completo formateado
        full_content = f"# {title}\n\n" + "\n".join(formatted_blocks)

        # Crear respuesta estructurada
        response = {
            "title": title,
            "page_id": page_id,
            "full_content": full_content,
            "blocks": blocks_info,
            "total_blocks": len(blocks_info)
        }

        # Formatear respuesta para que sea fácil de leer y usar
        formatted_response = f"""**Página: {title}** (ID: {page_id})

**Contenido completo:**
{full_content}

**Bloques individuales para edición:**
"""

        for block in blocks_info:
            block_id = block["id"]
            block_type = block["type"]
            position = block["position"]

            formatted_response += f"""
**Bloque {position}** (ID: {block_id})
- Tipo: {block_type}
- Usar update_block(block_id="{block_id}", new_content="...", block_type="{block_type}")
"""

        return formatted_response

    except Exception as e:
        return f"Error al obtener contenido de la página: {str(e)}"

@mcp.tool()
def update_block(block_id: str, new_content: str, block_type: str = "paragraph", context: Context = None) -> str:
    """
    Modifica el contenido de un bloque de Notion ya existente.

    Args:
        block_id: ID del bloque a modificar
        new_content: Nuevo contenido para el bloque
        block_type: Tipo de bloque (paragraph, heading_1, heading_2, heading_3, code)

    Returns:
        Mensaje de confirmación
    """
    try:
        notion = context.get_state("notion")
        # Preparar el contenido según el tipo de bloque
        if block_type == "code":
            content = {
                "code": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": new_content}
                        }
                    ]
                }
            }
        elif block_type.startswith("heading_"):
            heading_key = block_type
            content = {
                heading_key: {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": new_content}
                        }
                    ]
                }
            }
        else:  # paragraph
            content = {
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": new_content}
                        }
                    ]
                }
            }

        # Actualizar el bloque
        notion.blocks.update(
            block_id=block_id,
            **content
        )

        return "Bloque actualizado exitosamente"

    except Exception as e:
        return f"Error al actualizar bloque: {str(e)}"

@mcp.tool()
def get_github_file_content(repository_name: str, file_path: str, branch: str = "main", context: Context = None) -> str:
    """
    Recibe la URL de un archivo en un repositorio de GitHub y devuelve su contenido en formato de texto.

    Args:
        repository_name: Nombre del repositorio de GitHub (ej: owner/repo)
        file_path: Ruta del archivo en el repositorio (ej: file.py)
        branch: Rama del repositorio (ej: main)
    Returns:
        Contenido del archivo como texto
    """
    try:
        github_token = context.get_state("github_token")
        # Convertir URL de GitHub a URL raw
        raw_url = f"https://raw.githubusercontent.com/{repository_name}/refs/heads/{branch}/{file_path}"

        # Headers para autenticación si hay token
        headers = {}
        if github_token:
            headers["Authorization"] = f"token {github_token}"

        # Obtener contenido del archivo
        response = requests.get(raw_url, headers=headers)
        if response.status_code == 404 and branch == "main":
            response = requests.get(raw_url.replace("main", "master"), headers=headers)

        response.raise_for_status()

        return response.text

    except requests.exceptions.RequestException as e:
        return f"Error al obtener contenido del archivo: {str(e)}"
    except Exception as e:
        return f"Error inesperado: {str(e)}"

@mcp.tool()
def append_text_link_block(page_id: str, text: str, link: str, after_block_id: str = None, context: Context = None) -> str:
    """
    Agrega un bloque de texto plano a una página existente de Notion.

    Args:
        page_id: ID de la página donde agregar el texto
        text: Contenido de texto a agregar
        link: URL del enlace a agregar
        after_block_id: ID del bloque después del cual se agregará el nuevo bloque. Si no se proporciona, se agrega al final de la página.
    Returns:
        Mensaje de confirmación
    """
    notion = context.get_state("notion")
    try:
        # Crear bloque de texto
        block = {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": text,
                            "link": {
                                "url": link
                            }
                        }
                    }
                ]
            }
        }

        body = {
            "block_id": page_id,
            "children": [block]
        }
        if after_block_id:
            body["after"] = after_block_id

        notion.blocks.children.append(**body)

        return "Bloque de texto agregado exitosamente"

    except Exception as e:
        return f"Error al agregar bloque de texto: {str(e)}"

@mcp.tool()
def delete_block(block_id: str, context: Context = None) -> str:
    """
    Elimina un bloque de Notion ya existente.

    Args:
        block_id: ID del bloque a eliminar
    Returns:
        Mensaje de confirmación
    """
    try:
        notion = context.get_state("notion")
        # Eliminar el bloque
        notion.blocks.delete(block_id=block_id)

        return "Bloque eliminado exitosamente"

    except Exception as e:
        return f"Error al eliminar bloque: {str(e)}"

if __name__ == "__main__":
    mcp.run()