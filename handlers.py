from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
import json
#from utils import save_voice_as_wav, voice_to_text, neuro_answer
import utils
router = Router()

JSON = {}
data_message = {}
Action = {}
Number1 = {}
Number2 = {}

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
    global Number1
    global Number2
    global data_message

    voice_path = await utils.save_voice_as_wav(message.voice, message.chat.id)
    texto = await utils.voice_to_text(voice_path)
    if texto is None:
        await message.answer(text="Не удалось распознать речь, попробуйте еще раз")
        return 0

    if data_message.get(message.chat.id) is None:
        data_message[message.chat.id] = texto
    else:
        data_message[message.chat.id] += " " + texto

    ans = await utils.neuro_answer(data_message[message.chat.id]) 
    if ans is None:
        await message.answer(text="Не удается определить записанное сообщение. Пожалуйста, повторите")
        return 0 
    if ans == "Обязательно укажите в своем голосовом сообщении номер и адрес объекта" :
        await message.answer(text=ans)
        return 0 

    JSON[message.chat.id] = ans
    
    if Number1.get(message.chat.id) is None:
        Number1[message.chat.id] = 0

    if Number2.get(message.chat.id) is None:
        Number2[message.chat.id] = 0

    answer = ""
    request = ""
    for key, value in ans.items():
        request = str(key).replace('_', ' ') + ": " + str(value) + "\n"
        answer += request

    kb = [[KeyboardButton(text='Все в порядке')], [KeyboardButton(text='Изменить введенные параметры')], [KeyboardButton(text='Продолжить вводить голосовые сообщения')]]
    keyboar = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)

    await message.reply(text=f"{answer}\nТехник: id{message.chat.id}", reply_markup=keyboar)

@router.message(F.text == 'Все в порядке')
async def good_ans(Message):
    
    global Number1

    tech_data = JSON.get(Message.chat.id)
    if tech_data is None:
        await Message.answer("Запишите, пожалуйста, голосовое сообщение")
        return 0

    Number1[Message.chat.id] += 1
    c = Number1[Message.chat.id] 

    name = f"json_files/{c}-id{Message.chat.id}.json"

    with open(f"{name}", mode = "w") as file:
        file.write(json.dumps(tech_data))

    l = JSON[Message.chat.id]['Необходимые_материалы'].split(',')

    try:
        await utils.get_embedding(l, name)
    except:
        await Message.answer(text="Не удается определить записанное сообщение. Пожалуйста, повторите")
        print("chat gpt isn't avaible")
        return 0 

    JSON.pop(Message.chat.id)
    data_message.pop(Message.chat.id)
    Number2.pop(Message.chat.id)

    await Message.reply("Спасибо, не забудьте отправить фото акта")

@router.message(F.text == 'Продолжить вводить голосовые сообщения')
async def gc(Message):
    await Message.reply(text="Уточните недостающую информацию в голосовом сообщении")

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

@router.message(F.content_type == "photo")
async def photo(message):

    global Number2

    if Number2.get(message.chat.id) is None:
        Number2[message.chat.id] = 0

    Number2[message.chat.id] += 1
    c = Number2[message.chat.id] 

    photo = message.photo[-1]
    path_name = f"photo_files/{c}-id{message.chat.id}.jpeg"
    voice_file_info = await photo.bot.get_file(photo.file_id)
    await photo.bot.download_file(voice_file_info.file_path, path_name)

    await message.answer("Спасибо, фото сохранено")

