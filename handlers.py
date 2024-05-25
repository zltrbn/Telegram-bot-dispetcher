from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
import json
#from utils import save_voice_as_wav, voice_to_text, neuro_answer
import utils
router = Router()

JSON = {}
Action = {}
Number = {}

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
    global Number

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

    JSON[message.chat.id] = ans
    
    if Number.get(message.chat.id) is None:
        Number[message.chat.id] = 0

    answer = ""
    request = ""
    for key, value in ans.items():
        request = str(key).replace('_', ' ') + ": " + str(value) + "\n"
        answer += request

    kb = [[KeyboardButton(text='Все в порядке')], [KeyboardButton(text='Изменить введенные параметры')]]
    keyboar = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)

    await message.reply(text=f"{answer}\nТехник: id{message.chat.id}", reply_markup=keyboar)

@router.message(F.text == 'Все в порядке')
async def good_ans(Message):
    
    global Number

    tech_data = JSON.get(Message.chat.id)
    if tech_data is None:
        await Message.answer("Запишите, пожалуйста, голосовое сообщение")
        return 0

    Number[Message.chat.id] += 1
    c = Number[Message.chat.id] 

    with open(f"json_files/{c}-id{Message.chat.id}.json", mode = "w") as file:
        file.write(json.dumps(tech_data))

    JSON.pop(Message.chat.id)

    await Message.reply("Спасибо, хорошего дня!")

@router.message(F.text.in_({'Изменить введенные параметры', 'Отменить'}))
async def bad_ans(Message):
    if Action.get(Message.chat.id) is not None:
        Action.pop(Message.chat.id)

    kb = [[KeyboardButton(text='Номер объекта')], [KeyboardButton(text='Адрес объекта')], [KeyboardButton(text='Проведенные работы')], [KeyboardButton(text='Необходимые материалы')]]
    keyboar = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)

    await Message.reply(text="Выберите поле для изменения", reply_markup=keyboar)

@router.message(F.text.in_({'Номер объекта', 'Адрес объекта', 'Проведенные работы', 'Необходимые материалы'}))
async def change(Message):

    global Action

    Action[Message.chat.id] = Message.text.replace(' ', '_')

    kb = [[KeyboardButton(text='Отменить')]]
    keyboar = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)

    await Message.reply(text="Введите новые данные", reply_markup=keyboar)
    
@router.message(F.text)
async def change_ans(Message):

    ac_data = Action.get(Message.chat.id)
    if ac_data is None:
        await Message.answer("Пожалуйста, следуйте инструкции внимательнее")
        return 0

    tech_data = JSON.get(Message.chat.id)
    if tech_data is None:
        await Message.answer("Запишите, пожалуйста, голосовое сообщение")
        return 0

    tech_data[ac_data] = Message.text

    Action.pop(Message.chat.id)

    answer = ""
    request = ""
    for key, value in tech_data.items():
        request = str(key).replace('_', ' ') + ": " + str(value) + "\n"
        answer += request

    kb = [[KeyboardButton(text='Все в порядке')], [KeyboardButton(text='Изменить введенные параметры')]]
    keyboar = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)

    await Message.reply(text=f"{answer}\nТехник: id{Message.chat.id}", reply_markup=keyboar)



    

