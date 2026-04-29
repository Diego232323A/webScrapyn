from playwright.sync_api import sync_playwright
import re, csv, os

def scrape_instagram_profile(target_user):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state="auth.json")
        page = context.new_page()

        try:
            print(f"🕵️ Investigando a: {target_user}...")
            page.goto(f"https://www.instagram.com/{target_user}/", wait_until="domcontentloaded", timeout=60000)
            
            # Esperar a que el perfil cargue
            page.wait_for_selector("header", timeout=15000)
            page.mouse.wheel(0, 400) # Un pequeño scroll para activar la carga
            page.wait_for_timeout(2000)

            # --- 1. EXTRACCIÓN DE BIO MEJORADA ---
            # Buscamos el contenedor específico de la biografía
            bio_container = page.locator("section main header section > div:nth-child(3)").first
            bio_text = bio_container.inner_text() if bio_container.count() > 0 else "Sin biografía"
            
            # Limpiamos la bio de palabras basura
            blacklist = ["seguido por", "verificado", "verificar", "seguir"]
            bio_final = " ".join([l for l in bio_text.split('\n') if not any(b in l.lower() for b in blacklist)])

            # --- 2. EXTRACCIÓN DE NÚMEROS (POSTS, FOLLOWERS) ---
            header_text = page.locator("header").inner_text()
            posts_count = re.search(r'([\d.,]+)\s+publicaciones', header_text)
            followers = re.search(r'([\d.,]+)\s+seguidores', header_text)
            following = re.search(r'([\d.,]+)\s+seguidos', header_text)

            # --- 3. EXTRACCIÓN DE POSTS (MÉTODO ROBUSTO) ---
            print("📸 Analizando fotos y estadísticas...")
            posts_info_list = []
            
            # Buscamos los contenedores de los posts
            fotos = page.locator("a[href*='/p/']").all()
            
            for i, foto in enumerate(fotos[:10]):
                try:
                    img_url = foto.locator("img").first.get_attribute("src")
                    
                    # Hover para activar el cuadro de likes
                    foto.hover()
                    page.wait_for_timeout(1000)
                    
                    # Capturamos todo el texto del cuadro de la foto
                    overlay_text = foto.inner_text()
                    
                    # Usamos REGEX para buscar solo los números en ese texto
                    # Esto evita que palabras como "Seguir" o "Mensaje" se metan
                    numeros_encontrados = re.findall(r'([\d.,]+[KkMm]?)', overlay_text)
                    
                    likes = numeros_encontrados[0] if len(numeros_encontrados) > 0 else "0"
                    comms = numeros_encontrados[1] if len(numeros_encontrados) > 1 else "0"
                    
                    posts_info_list.append(f"P{i+1}:({likes}L, {comms}C) URL: {img_url}")
                except:
                    continue

            info_posts_final = " | ".join(posts_info_list) if posts_info_list else "No se detectaron posts"

            # --- 4. GUARDADO EN CSV ---
            file_name = 'perfiles_instagram.csv'
            file_exists = os.path.isfile(file_name)
            
            with open(file_name, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                if not file_exists:
                    writer.writerow(['Usuario', 'Posts', 'Followers', 'Following', 'Bio', 'Detalle Posts'])
                
                writer.writerow([
                    target_user, 
                    posts_count.group(1) if posts_count else '0',
                    followers.group(1) if followers else '0',
                    following.group(1) if following else '0',
                    bio_final.replace('\n', ' '), 
                    info_posts_final
                ])

            print(f"✅ ¡Hecho! Datos limpios guardados para {target_user}")

        except Exception as e:
            print(f"❌ Error crítico: {e}")
        finally:
            browser.close()

scrape_instagram_profile("irene_araceli05")