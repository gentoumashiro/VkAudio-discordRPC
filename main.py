import os
import time
from random import choice

import requests
import vk_api
from bs4 import BeautifulSoup
from pypresence import Presence


UserAgents = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
)

image = ['6f042f6867a06a513653ca0131f9f61e']


with open('tokens.txt', 'r', encoding='utf-8') as file:
    vktoken, vk_user_id, discord_app_id = [i.strip().split('=')[1] for i in file.readlines()]

session = vk_api.VkApi(token=vktoken)
vk = session.get_api()
rpc = Presence(discord_app_id)


def get_vk_user_status() -> bool | tuple:
    status = vk.users.get(user_id=vk_user_id, fields='status')
    try:
        status = status[0]['status_audio']
    except IndexError and KeyError:
        return False

    current_audio = status['artist'], status['title']
    return current_audio


def get_audio_image(image_name: str) -> str:
    """
    Функция через которую получаем ссылку на картинку текущего аудио
    и заменяем единственный элемент в списке Image На найденную картинку,
    Если же функция не сможет найти изображение, то используем прдыдущую картинку
    """
    global image

    try:
        headers = {
            'user-agent': choice(UserAgents)
        }

        req = requests.get(f'https://www.google.com/search?q={image_name.replace(" ", "%")}&tbm=isch', headers=headers)
        soup = BeautifulSoup(req.text, 'xml')
        images = soup.find_all("img")
        image[0] = images[1].get('src')
        return image[0]
    except Exception as exx:
        print(f"Ошибка: {exx}")
        return image[0]


def stream_music_to_discord(timestamp: int = int(time.time()), count: int = 3):
    if not (status := get_vk_user_status()):
        if not count:
            print(f"\bАудио так и не было найдено, попробуем повторно подключиться через 2.5 минут")
            time.sleep(150)
            count = 3
        for i in range(5, 0, -1):
            print(f"\bАудио не производится, презапуск через {i} секунд")
            time.sleep(1)

        stream_music_to_discord(count=count - 1)

    artist = f"{status[0]}   "
    track = f"{status[-1]}   "
    img = get_audio_image(f"{track} {artist}")

    print(f"Current Track: {artist.strip()} - {track.strip()}")

    rpc.update(
        start=timestamp,
        large_image=img,
        small_image=img,
        state=artist,
        details=track,
    )

    time.sleep(30)
    os.system('cls')
    stream_music_to_discord(count=3)


def main():
    try:
        print('Conecting to discord...')
        rpc.connect()
        timestamp_start = int(time.time())
        stream_music_to_discord(timestamp_start)
    except Exception as ex:
        print(F"Ошибка: {ex} !!!")
        print(F"Попробуйте запустить дискорд или запустить exe от имени администратора!!\nПерезапуск через 10 секунд!!")
        time.sleep(10)
        main()


if __name__ == '__main__':
    main()
