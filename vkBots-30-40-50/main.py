# -*- coding: utf-8 -*-
import json
import os
import random

import requests
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

TOKEN = "42f17c341b52931934b11a35dac42a19bf69bec695f286567b43265cca7715816390c2a131de493ec2635"

vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()

jsonFile = open("data.json", "r")
data = json.loads(jsonFile.read())
jsonFile.close()


def main():
    global user_id
    longpoll = VkBotLongPoll(vk_session, 212547104)

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            user_id = str(event.message.from_id)

            if user_id not in data:
                data.update({user_id: {"photo-viewed": [], "like": 0, "dislike": 0}})

            if event.message.text.lower() == "мем":
                photo_id = random.choice(os.listdir("memes"))

                if photo_id not in data:
                    data.update({photo_id: {"like-photo": 0}})

                while photo_id in data.get(user_id).get("photo-viewed"):
                    photo_id = random.choice(os.listdir("memes"))

                vk.messages.send(peer_id=user_id, message="Вы можете оценить картинку, нажав одну из кнопок ниже👇🏻",
                                 keyboard=create_keyboard(photo_id), attachment=photo_upload(user_id, photo_id),
                                 random_id=0)

            if event.message.text.lower() == "статистика":
                vk.messages.send(peer_id=user_id, message=calc_statistic(), keyboard=create_keyboard(menu=True),
                                 attachment=best_photos(), random_id=0, )

            if event.message.payload:
                buttonType = json.loads(event.message.payload).get("type")[-1]
                photo_id = json.loads(event.message.payload).get("type")[:-1]

                data.get(user_id).get("photo-viewed").append(photo_id)

                vk.messages.send(peer_id=user_id, message="Вы оценили пост",
                                 keyboard=create_keyboard(photo_id, True), random_id=0)

                if buttonType == "+":
                    rate_post(photo_id, like=1)
                    continue

                rate_post(photo_id, dislike=1)

            if event.message.attachments:
                if event.message.attachments[0].get("type") == "photo":
                    download_photo(event.message.attachments[0].get("photo").get("sizes")[-1].get("url"))
                    vk.messages.send(peer_id=user_id, message="Фото загружено!",
                                     keyboard=create_keyboard(menu=True), random_id=0)


def calc_statistic():
    all_like = data.get('like')
    all_dislike = data.get('dislike')
    user_like = data.get(user_id).get('like')
    user_dislike = data.get(user_id).get('dislike')

    return f"Общая статистика:\n\n" \
           f"Лайки: {all_like}\n" \
           f"Дизлайки: {all_dislike}\n\n" \
           f"Ваша статистика:\n\n" \
           f"Лайки: {user_like}\n" \
           f"Дизлайки: {user_dislike}\n\n" \
           f"Вы можете загрузить картинку, отправив ее боту\n" \
           f"Топ 9 лучших картинок:"


def photo_upload(peer_id, photo_id):
    uploadServerUrl = vk.photos.getMessagesUploadServer(peer_id=peer_id)
    postRequest = requests.post(url=uploadServerUrl.get("upload_url"),
                                files={'photo': open(f"memes/{photo_id}", "rb")}).json()

    result = vk.photos.saveMessagesPhoto(server=postRequest.get("server"),
                                         photo=postRequest.get("photo"), hash=postRequest.get("hash"))[0]

    return f"photo{result.get('owner_id')}_{result.get('id')}"


def create_keyboard(photo_id="", menu=False):
    keyboard = VkKeyboard(one_time=True, inline=False)

    if menu:
        keyboard.add_button("Статистика", color=VkKeyboardColor.SECONDARY)
        keyboard.add_button("Мем", color=VkKeyboardColor.SECONDARY)

        return keyboard.get_keyboard()

    keyboard.add_button("👍🏻", color=VkKeyboardColor.POSITIVE, payload={"type": f"{photo_id}+"})
    keyboard.add_button("👎🏻", color=VkKeyboardColor.NEGATIVE, payload={"type": f"{photo_id}-"})

    return keyboard.get_keyboard()


def rate_post(photo_id, like=0, dislike=0):
    data.update({user_id: {"photo-viewed": data.get(user_id).get("photo-viewed"),
                           "like": data.get(user_id).get("like") + like,
                           "dislike": data.get(user_id).get("dislike") + dislike}})

    data.update({photo_id: {"like-photo": data.get(photo_id).get("like-photo") + like}})

    data.update({"like": data.get("like") + like})
    data.update({"dislike": data.get("dislike") + dislike})

    jsonFileWrite = open("data.json", "w")
    jsonFileWrite.write(json.dumps(data, indent=2))


def download_photo(url):
    image = open(f"memes/{random.randint(0, 10000)}.jpg", "wb")
    image.write(requests.get(url).content)
    image.close()


def best_photos():
    photo_dict = {}
    result = []

    for i in data.items():
        if "." in i[0]:
            photo_dict.update({i[0]: i[1].get("like-photo")})

    photo_dict = list(photo_dict.items())

    for i in sorted(photo_dict, key=lambda x: x[1])[-9:][::-1]:
        result.append(photo_upload(user_id, i[0]))

    return result


if __name__ == '__main__':
    main()
