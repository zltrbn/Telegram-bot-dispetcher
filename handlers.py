from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
import json
#from utils import save_voice_as_wav, voice_to_text, neuro_answer
import utils
router = Router()

JSON = {}

@router.message(Command("start"))
async def start_handler(msg: Message):
    await msg.answer("Укажите в вашем голосовом сообщении:\n\
- Номер объекта\n\
- Адрес объекта\n\
- Проведенные работы\n\
- Необходимые материалы")

@router.message(F.content_type == "voice")
async def process_voice_message(message: Message):

    global JSON

    voice_path = await utils.save_voice_as_wav(message.voice, message.chat.id)
    texto = await utils.voice_to_text(voice_path)
    if texto is None:
        await message.answer(text="Не удалось распознать речь, попробуйте еще раз")
        return 0 
    #json_path = voice_path.replace('voice_files', 'json_files').replace('wav', 'json')
    ans = await utils.neuro_answer(texto) 
    if ans is None:
        await message.answer(text="Не удается определить записанное сообщение. Пожалуйста, повторите")
        return 0 
    if ans == "Обязательно укажите в своем голосовом сообщении номер и адрес объекта" :
        await message.answer(text=ans)
        return 0 

    JSON = ans

    answer = ""
    request = ""
    for key, value in ans.items():
        request = str(key) + ": " + str(value) + "\n"
        answer += request

    kb = [[KeyboardButton(text='Все в порядке')], [KeyboardButton(text='Изменить введенные параметры')]]
    keyboar = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)

    await message.reply(text=f"{answer}\nТехник: id{message.chat.id}", reply_markup=keyboar)

@router.message(F.text == 'Все в порядке')
async def good_ans(Message):
    
    print(JSON)

    with open(f"json_files/id{Message.chat.id}.json", mode = "w") as file:
        file.write(json.dumps(JSON))

    await Message.reply("Спасибо, хорошего дня!")

@router.message(F.text == 'Изменить введенные параметры')
async def bad_ans(Message):
    await Message.answer("Пожалуйста, введите название поля и исправленные данные в следующем формате:\nПоле\nНовые данные")

@router.message(F.text)
async def change_ans(Message):
    try:
        name = Message.text.split("\n")
    except:
        await Message.answer("Пожалуйста, следуйте инструкции внимательнее")
        return 0

    if name[0] not in JSON.keys():
        await Message.answer("пожалуйста, следуйте инструкциям внимательнее")
        return 0

    for key in JSON.keys():
        if key == name[0]:
            JSON[key] = name[1]

    answer = ""
    request = ""
    for key, value in JSON.items():
        request = str(key) + ": " + str(value) + "\n"
        answer += request

    kb = [[KeyboardButton(text='Все в порядке')], [KeyboardButton(text='Изменить введенные параметры')]]
    keyboar = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)

    await Message.reply(text=f"{answer}\nТехник: id{Message.chat.id}", reply_markup=keyboar)



    

