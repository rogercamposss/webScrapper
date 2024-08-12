import re
from playwright.sync_api import sync_playwright
import pandas as pd
from bs4 import BeautifulSoup as bs
import time
from random import randint

def scrape_followers(user, password, user_to_search):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=['--incognito'])
        page = browser.new_page()

        # Acessar página de login do Instagram
        page.goto('https://www.instagram.com/accounts/login/')
        page.fill('input[name="username"]', user)
        page.fill('input[name="password"]', password)
        page.click('button[type="submit"]')

        # Esperar e lidar com a tela de "Salvar informações de login"
        page.wait_for_timeout(3000)
        try:
            # Tentar diferentes seletores para o botão "Não agora"
            #page.click('button:has-text("Agora não")')
            #page.get_by_role("button", name="Agora não").click()
            page.wait_for_load_state('networkidle')
            page.get_by_role("button", name=re.compile("Agora não", re.IGNORECASE)).click()


            # Ou usando XPath
            #page.click('//*[@id="mount_0_0_GZ"]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/section/main/div/div/div/div/div[text()="Agora não"]')
        except:
            print("Botão 'Agora não' não encontrado ou não clicável.")
        time.sleep(20)        
        try:
            # Tentar diferentes seletores para o botão "Não agora"
            page.wait_for_load_state('networkidle')
            page.get_by_role("button", name=re.compile("Agora não", re.IGNORECASE)).click()

        except:
            print("Botão 'Agora não' não encontrado ou não clicável.")
        time.sleep(20)

        # Navegar para a página do usuário
        page.goto(f'https://www.instagram.com/{user_to_search}/')
        page.wait_for_load_state('networkidle')

        # Abrir a lista de seguidores
        try:
            page.wait_for_load_state('networkidle')
            page.click(f'a[href="/{user_to_search}/followers/"]')
            page.wait_for_load_state('networkidle')
        except:
            print("Link de seguidores não encontrado.")
        time.sleep(20)
        # Capturar seguidores
        # Seletor XPATH atualizado para o modal e lista de seguidores
        followers_selector = '//div[@role="dialog"]//div[contains(@class, "x1qjc9v5")]//div[contains(@class, "x1plvlek")]'
        # Aguardar até que o modal esteja visível
        page.wait_for_selector(f'xpath={followers_selector}', state='visible')
        followers_list = page.query_selector(f'xpath={followers_selector}')

        if followers_list is None:
            print("Lista de seguidores não encontrada.")
            return

        last_scroll_height = 0
        call = 0
        counter = 0
        data = []

        while True:                                
            page.wait_for_load_state('networkidle')                                                                                                                                                                              
            page.evaluate('element => element.scrollBy(0, element.scrollHeight)', followers_list)
            time.sleep(randint(30, 35))
            scroll_height = page.evaluate('element => element.scrollHeight', followers_list)
            
            if scroll_height != last_scroll_height:
                call += 1
                text = followers_list.inner_html()
                soup = bs(text, 'html.parser')
                
                for img in soup.find_all('img'):
                    data.append('@' + img['alt'][:-18])

                last_scroll_height = scroll_height
                print('API Call: ' + str(call))
            else:
                counter += 1
                print('API Request Failed: ' + str(counter))
                if counter >= 5:
                    break

        # Salvar dados em um arquivo CSV
        df = pd.DataFrame(data, columns=['Follower'])
        df.to_csv(user_to_search + ".csv", sep=',', index=False, header=False)
        
        if len(data) > 0:
            print(len(data), data[-1])
        else:
            print("A lista está vazia.")

        browser.close()

# Exemplo de uso
user = 'scrappingdev'
password = 'Roger.Dev'
user_to_search = 'rogercamposss'
scrape_followers(user, password, user_to_search)
