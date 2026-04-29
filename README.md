# Instagram Profile Scraper
Este proyecto es un script de automatización avanzado desarrollado en **Python** utilizando **Playwright**. Permite extraer información pública de perfiles de Instagram y capturar datos dinámicos como Likes y Comentarios mediante simulación de interacción humana.

---

## 🚀 Características principales

* **Extracción Dinámica:** Captura métricas de interacción (Likes/Comments) activando el overlay de las publicaciones.
* **Filtro Inteligente (Regex):** Aislamiento de datos numéricos para evitar ruido visual o de interfaz.
* **Gestión de Sesión:** Persistencia de estado mediante `auth.json` para evitar bloqueos por autenticación.
* **Limpieza de Bio:** Algoritmo de filtrado basado en listas negras para obtener descripciones puras.
* **Exportación Estructurada:** Generación de reportes en `perfiles_instagram.csv` (UTF-8).

---

## 🛠️ Requisitos previos

1. **Python 3.8+**
2. **Playwright:**
   ```
   pip install playwright
   playwright install chromium
   ```

---

## 📖 Modo de Uso

## Configuración de Autenticación
El script requiere una sesión activa para evitar el muro de login de Instagram:

1. Loguéate manualmente ejecutando el archivo `get_cookies.py`.
2. Este guardará automáticamente el estado, en un archivo `auth.json`.
    
## Scrapyn 
Modifica el usuario objetivo en el archivo `scrapyn.py` y ejecuta:
```
py scrapyn.py
```

---

## 🧠 Explicación Técnica Detallada
Para garantizar la precisión de los datos, el script utiliza las siguientes estrategias técnicas:

1. **Extracción de Estadísticas con Patrones (Regex)**
En lugar de depender de posiciones fijas que cambian con el idioma o el diseño, buscamos patrones numéricos anclados a palabras clave:
    ```
    posts_count = re.search(r'([\\d.,]+)\\s+publicaciones', header_text)
    ```

2. **El "Colador" de la Biografía**
La biografía suele mezclarse con elementos de la interfaz (botones de seguir, mensaje, etc.). Usamos una Blacklist para purificar el texto:
    ```
    blacklist = ["seguido por", "verificado", "seguir", "mensaje"]
    bio_final = " ".join([l for l in bio_lines if not any(b in l.lower() for b in blacklist)])
    ```

3. **Captura de Datos Dinámicos (Hover + Overlay)**
Los Likes y Comentarios no están en el HTML inicial. El script debe "simular" el comportamiento humano:

    - **Hover:** El robot sitúa el cursor sobre la imagen (foto.hover()).

    - **Latencia:** Se espera 1.2 segundos para que el DOM renderice el cuadro de estadísticas.

    - **Regex de Precisión:** Se extraen solo los caracteres numéricos del cuadro flotante, ignorando texto como "Me gusta" o "Seguir":
        ```
        numeros = re.findall(r'([\\d.,]+[KkMm]?)', overlay_text)
        ```

4. **Seguridad de Datos en CSV**
Para evitar que el archivo CSV se rompa debido a saltos de línea en las biografías de los usuarios, se aplica una limpieza de caracteres de escape (\\n) antes de la escritura, asegurando que cada perfil ocupe exactamente una fila.