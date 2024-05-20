from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from utils import save_voice_as_wav, voice_to_text, neuro_answer
router = Router()

@router.message(Command("start"))
async def start_handler(msg: Message):
    await msg.answer("Укажите в вашем голосовом сообщении:\n\
- Номер объекта\n\
- Адрес объекта\n\
- Проведенные работы\n\
- Необходимые материалы")

@router.message(F.content_type == "voice")
async def process_voice_message(message: Message):
    voice_path = await save_voice_as_wav(message.voice, message.chat.id)
    texto = await voice_to_text(voice_path)
    if texto is None:
        await message.answer(text="Не удалось распознать речь, попробуйте еще раз")
        return 0 
    json_path = voice_path.replace('voice_files', 'json_files').replace('wav', 'json')
    ans = await neuro_answer(texto, json_path) 
    if ans is None:
        await message.answer(text="Не удается определить записанное сообщение. Пожалуйста, повторите")
        return 0 

    kb = [[KeyboardButton(text='Все в порядке')], [KeyboardButton(text='Изменить введенные параметры')]]
    keyboar = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)

    await message.reply(text=f"{ans}\nТехник: id{message.chat.id}", reply_markup=keyboar)

@router.message(F.text == 'Все в порядке')
async def good_ans(Message):
    await Message.reply("Спасибо, хорошего дня!")

@router.message(F.text == 'Изменить введенные параметры')
async def bad_ans(Message):
    await Message.answer("Пожалуйста, перезапишите голосовое сообщение")