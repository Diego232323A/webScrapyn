from playwright.sync_api import sync_playwright
import re

def scrape_instagram_profile(target_user):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state="auth.json")
        page = context.new_page()

        try:
            print(f"Accediendo al perfil de: {target_user}...")
            page.goto(f"https://www.instagram.com/{target_user}/", wait_until="networkidle")
            page.wait_for_selector("header", timeout=10000)
            
            # 1. Extraemos todo el texto del encabezado
            header_text = page.locator("header").inner_text()
            lines = [l.strip() for l in header_text.split('\n') if l.strip()]

            # 2. Extraer números con Regex (esto no falla)
            posts = re.search(r'(\d+)\s+publicaciones', header_text)
            followers = re.search(r'(\d+)\s+seguidores', header_text)
            following = re.search(r'(\d+)\s+seguidos', header_text)

            # 3. Lógica para el Nombre y la Bio
            # El nombre es casi siempre la línea después del username
            username_idx = -1
            for i, line in enumerate(lines):
                if target_user in line.lower():
                    username_idx = i
                    break
            
            nombre_real = lines[username_idx + 1] if username_idx != -1 else "No encontrado"

            # 4. Capturar la Bio
            # Buscamos qué hay entre las estadísticas y los botones
            # Vamos a filtrar líneas que ya conocemos
            palabras_clave = ["publicaciones", "seguidores", "seguidos", "siguiendo","destacada", "mensaje", "enviar mensaje", target_user]
            
            bio_parts = []
            for line in lines:
                # Si la línea no es el nombre real y no tiene palabras clave, es la BIO
                if line != nombre_real and not any(key in line.lower() for key in palabras_clave):
                    # Ignorar también el texto de "seguido por..." si prefieres
                    if "sigue esta cuenta" not in line.lower():
                        bio_parts.append(line)

            bio_final = " ".join(bio_parts) if bio_parts else "Perfil sin biografía"

            print("\n" + "🚀 EXTRACCIÓN EXITOSA ".center(40, "="))
            print(f"USUARIO:      {target_user}")
            print(f"NOMBRE REAL:  {nombre_real}")
            print(f"POSTS:        {posts.group(1) if posts else '0'}")
            print(f"FOLLOWERS:    {followers.group(1) if followers else '0'}")
            print(f"FOLLOWING:    {following.group(1) if following else '0'}")
            print(f"BIO:          {bio_final}")

            import csv
            import os

            # ... (dentro de la función, después de los print)
            file_exists = os.path.isfile('perfiles_instagram.csv')

            with open('perfiles_instagram.csv', mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # Si el archivo es nuevo, escribimos el encabezado
                if not file_exists:
                    writer.writerow(['Usuario', 'Nombre Real', 'Posts', 'Followers', 'Following', 'Bio'])
                
                writer.writerow([target_user, nombre_real, posts.group(1), followers.group(1), following.group(1), bio_final])

            print(f"✅ Datos de {target_user} guardados en perfiles_instagram.csv")
            
            # Extra: Si quieres saber quién lo sigue (lo que salía antes)
            social_proof = [l for l in lines if "sigue esta cuenta" in l.lower()]
            if social_proof:
                print(f"SOCIAL PROOF: {social_proof[0]}")
            
            print("="*40 + "\n")

        except Exception as e:
            print(f"Error: {e}")

        finally:
            browser.close()
        

scrape_instagram_profile("madeleinecalero")