import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# Cargar la API key desde .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("No se ha encontrado OPENAI_API_KEY en el archivo .env")

client = OpenAI(api_key=api_key)

# Carpeta donde guardaremos los mitos como páginas Markdown
BASE_DIR = Path(__file__).parent
MITOS_DIR = BASE_DIR / "src" / "pages" / "mitologia"
MITOS_DIR.mkdir(parents=True, exist_ok=True)


def generar_mito():
    """
    Llama al modelo y devuelve un dict con 'title' y 'body' (markdown).
    Este es el 'Mitopoeta' básico.
    """
    system_prompt = (
        "Eres el Mitopoeta de un mundo ficticio completamente original. "
        "Tu tarea es escribir mitos fundacionales y relatos sagrados en castellano peninsular, "
        "con tono solemne pero legible, evitando referencias directas a nuestro mundo real "
        "(ni países, ni religiones, ni nombres reales). "
        "Este será uno de los primeros mitos del mundo, así que debe funcionar de manera aislada, "
        "sin depender de conocimientos previos del lector.\n\n"
        "No inventes todavía demasiados nombres propios: uno o dos como mucho, bien sonoros. "
        "Usa entre 600 y 900 palabras.\n\n"
        "Tu salida NO debe ser markdown completo, sino un JSON con esta estructura exacta:\n"
        '{ "title": "TÍTULO DEL MITO", "body": "CUERPO DEL TEXTO EN VARIOS PÁRRAFOS" }\n'
        "El campo 'body' debe ser texto plano con saltos de línea dobles entre párrafos."
    )

    user_prompt = "Genera un mito autónomo para el archivo de la Mitología Autónoma."

    response = client.responses.create(
        model="gpt-4.1-mini",  # Ajusta si quieres otro modelo
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    # La nueva API no devuelve directamente JSON, así que extraemos el texto generado
    raw_text = response.output[0].content[0].text.strip()

    import json
    # Forzamos parsing seguro:
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        raise RuntimeError(
            f"El modelo no devolvió JSON válido.\nRespuesta recibida:\n{raw_text}"
        )

    title = data.get("title", "Mito sin título").strip()
    body = data.get("body", "").strip()
    return title, body



def slugify(text: str) -> str:
    """
    Convierte un título en algo apto para nombre de archivo.
    """
    import re

    text = text.lower()
    text = re.sub(r"[^a-z0-9áéíóúüñ]+", "-", text)
    text = re.sub(r"-+", "-", text)
    text = text.strip("-")
    if not text:
        text = "mito"
    return text


def guardar_mito_como_markdown(title: str, body: str) -> Path:
    """
    Crea un archivo .md en src/pages/mitologia con frontmatter + contenido.
    """
    fecha = datetime.utcnow().strftime("%Y-%m-%d")
    slug = slugify(title)
    filename = f"{fecha}-{slug}.md"
    filepath = MITOS_DIR / filename

    frontmatter = f"---\ntitle: \"{title}\"\ndate: \"{fecha}\"\n---\n\n"
    contenido = frontmatter + body + "\n"

    filepath.write_text(contenido, encoding="utf-8")
    return filepath


def main():
    print("Generando mito...")
    title, body = generar_mito()
    ruta = guardar_mito_como_markdown(title, body)
    print(f"Mito guardado en: {ruta}")
    print("Ahora puedes ejecutar `npm run dev` y visitar la ruta correspondiente en /mitologia/.")


if __name__ == "__main__":
    main()
