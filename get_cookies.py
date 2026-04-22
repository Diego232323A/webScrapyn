from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False) 
    context = browser.new_context()
    page = context.new_page()
    
    page.goto("https://www.instagram.com/")
    
    print("Por favor, inicia sesión manualmente en la ventana del navegador...")
    # El script esperará hasta que cierres el navegador manualmente tras loguearte
    page.wait_for_timeout(60000) 
    
    # Guardar el estado (cookies + local storage)
    context.storage_state(path="auth.json")
    browser.close()