# -*- coding: utf-8 -*-
import json
from random import choice

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from config import dataAnswer

TOKEN = "42f17c341b52931934b11a35dac42a19bf69bec695f286567b43265cca7715816390c2a131de493ec2635"
dictColor = [VkKeyboardColor.SECONDARY, VkKeyboardColor.PRIMARY,
             VkKeyboardColor.POSITIVE, VkKeyboardColor.NEGATIVE]


def main():
    vk_session = vk_api.VkApi(token=TOKEN)
    vk = vk_session.get_api()

    longpoll = VkBotLongPoll(vk_session, 212547104)

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.message.text.lower() == "привет":
                vk.messages.send(peer_id=event.message.from_id, message="Привет вездекодерам!",
                                 random_id=0, keyboard=create_keyboard(["Ответить на вопросы"], True, "answer_0"))

            if event.message.payload:
                buttonType = json.loads(event.message.payload).get("type")[-1]
                data = dataAnswer[int(buttonType)]

                vk.messages.send(peer_id=event.message.from_id, message=data.get("answer"),
                                 random_id=0, keyboard=create_keyboard(data.get("questions"), inline=False,
                                                                       typeButton="answer" + str(int(buttonType) + 1)))


def create_keyboard(data=None, inline=False, typeButton="answer"):
    keyboard = VkKeyboard(one_time=False, inline=inline)

    if data is None:
        return keyboard.get_empty_keyboard()

    for i in data:
        if i == "newLine":
            keyboard.add_line()
            continue

        keyboard.add_button(i, color=choice(dictColor), payload={"type": typeButton})

    return keyboard.get_keyboard()


if __name__ == '__main__':
    main()
