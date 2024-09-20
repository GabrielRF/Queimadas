from atproto import Client, client_utils
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from folium.plugins import MarkerCluster
import folium
import os
import requests
import sqlite3
import telebot
import time

URL = os.getenv('URL') 
FONTE = os.getenv('FONTE')

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHATS = os.getenv('TELEGRAM_CHATS').split(',')

BLUESKY_USER = os.getenv('BLUESKY_USER')
BLUESKY_TOKEN = os.getenv('BLUESKY_TOKEN')

HORAS = int(os.getenv('HORAS', 6))
ESTADO = os.getenv('ESTADO')
MAPA_CENTRO = os.getenv('MAPA_CENTRO').split(',')
MAPA_ZOOM=int(os.getenv('MAPA_ZOOM', 10))
MAPA_LARGURA=int(os.getenv('MAPA_LARGURA'))
MAPA_ALTURA=int(os.getenv('MAPA_ALTURA'))

LIMITE_NORTE=float(os.getenv('LIMITE_NORTE'))
LIMITE_SUL=float(os.getenv('LIMITE_SUL'))
LIMITE_LESTE=float(os.getenv('LIMITE_LESTE'))
LIMITE_OESTE=float(os.getenv('LIMITE_OESTE'))

def html_to_png(html):
    options = Options()
    options.add_argument('--headless')
    options.add_argument(f"--width={MAPA_LARGURA}")
    options.add_argument(f"--height={MAPA_ALTURA}")
    driver = webdriver.Firefox(options=options);
    driver.get(f'file://{html}')
    time.sleep(2)
    driver.save_screenshot(f'{html}.png')
    driver.quit()
    return f'{html}.png'

def create_map(coordinates, satelites):
    brasil = folium.Map(location=MAPA_CENTRO, zoom_start=MAPA_ZOOM)
    for coordinate in coordinates:
        lat = coordinate[0]
        lon = coordinate[1]
        satelite = coordinate[2]
        folium.CircleMarker(
            location=[lat,lon],
            fill_color=get_sat_color(satelites.index(satelite))[0],
            color=get_sat_color(satelites.index(satelite))[0],
            stroke=True,
            radius=10,
            fill_opacity=0.7
        ).add_to(brasil)
    brasil.save('/tmp/mapa.html')
    return html_to_png('/tmp/mapa.html')

def add_to_history(filename):
    conn = sqlite3.connect('filenames.db')
    cursor = conn.cursor()
    aux = f'INSERT INTO history (filename) VALUES ("{filename}")'
    cursor.execute(aux)
    conn.commit()
    conn.close()

def check_history(filename):
    conn = sqlite3.connect('filenames.db')
    cursor = conn.cursor()
    aux = f'SELECT * from history WHERE filename="{filename}"'
    cursor.execute(aux)
    data = cursor.fetchone()
    conn.close()
    return data

def send_message(message_text, map_file):
    for chat in TELEGRAM_CHATS:
        bot = telebot.TeleBot(TELEGRAM_TOKEN)
        telebot.util.antiflood(
            bot.send_photo,
            chat,
            open(map_file, 'rb'),
            message_text,
            parse_mode='HTML',
            show_caption_above_media=False
        )

def send_bluesky(text, map_file):
    client = Client(base_url='https://bsky.social')
    client.login(BLUESKY_USER, BLUESKY_TOKEN)
    text_builder = client_utils.TextBuilder()
    text_builder.link(
        f'{text}',
        FONTE
    )
    with open(map_file, 'rb') as f:
        image_data = f.read()
    client.send_image(
        text=text_builder,
        image=image_data,
        image_alt=text,
    )

def get_csv_files():
    response = requests.get(URL)
    return BeautifulSoup(response.content, 'html.parser')

def get_sat_color(sat):
    cases = {
        0: ['red',     '🔴'],
        1: ['orange',  '🟠'],
        2: ['#EED202', '🟡'],
        3: ['green',   '🟢'],
        4: ['blue',    '🔵'],
        5: ['purple',  '🟣'],
        6: ['#42280E', '🟤']
    }
    sat = sat%len(cases)
    return cases.get(sat)

def get_location(lat, lon):
    geolocator = Nominatim(user_agent="Queimadas")
    try:
        location = geolocator.reverse(f'{lat},{lon}')
    except:
        return None, None
    name = location.raw['display_name'].split(',')[0]
    state = location.raw['address']['state']
    return name, state

if __name__ == "__main__":
    print('Gerando lista dos arquivos csv...')
    html = get_csv_files()
    satelites = []
    send = False
    coordinates = []
    points = []
    message_text = (
        f'🔥 <b>Queimadas no DF!</b>\n'
    )
    bluesky_text = (
        f'🔥 Queimadas no DF!'
    )
    print('Lendo os arquivos...')
    for csv in html.findAll('a', href=True)[-(10*HORAS):]:
        filename = csv['href']
        if '.csv' not in filename:
            continue

        download = requests.get(f'{URL}{filename}')
        content = download.content.decode('utf-8')
        for line in content.split('\n'):
            try:
                lat, lon, satelite, data = line.strip().split(',')
            except:
                continue
            try:
                lat = float(lat)
                lon = float(lon)
            except:
                continue
            if LIMITE_NORTE > lat > LIMITE_SUL:
                if LIMITE_LESTE > lon > LIMITE_OESTE:
                    name, state = get_location(lat, lon)
                    if state != ESTADO:
                        continue
                    if not check_history(filename):
                        send = True
                    print(f'Foco: {lat:.6f} {lon:.6f} {name}')
                    satelite = satelite.split('-')[0]
                    satelite = satelite.split('_')[0]
                    try:
                        if satelite not in satelites:
                            satelites.append(satelite)
                    except:
                        continue
                    coordinates.append([lat,lon,satelite])
        add_to_history(filename)
    print('Histórico salvo.')
    satelites_list = ''
    for satelite in satelites:
        satelites_list = (
            f'{satelites_list} '+
            f'{get_sat_color(satelites.index(satelite))[1]}{satelite}'
        )
    message_text = (
        f'{message_text}\n'+
        f'<b>Quantidade</b>: {len(coordinates)} registros de focos\n'+
        f'<b>Satélites</b>: <code>{satelites_list}</code>\n'+
        f'<i>Dados acumulados das últimas {HORAS} horas</i>\n'+
        f'<a href="{FONTE}">[INPE]</a>'
    )
    bluesky_text = (
        f'{bluesky_text}\n'+
        f'Quantidade: {len(coordinates)} registros de focos\n'+
        f'Satélites: {satelites_list}\n'+
        f'Dados acumulados das últimas {HORAS} horas\n'+
        f'Fonte: INPE'
    )

    if send:
        print('Gerando mapa...')
        map_file = create_map(coordinates, satelites)
        print('Enviando para o Telegram')
        send_message(message_text, map_file)
        #print('Enviando para o Bluesky')
        #send_bluesky(bluesky_text, map_file)
        send = False
    else:
        print('Nenhuma informação enviada.')
