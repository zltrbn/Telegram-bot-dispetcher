import openai
#from datetime import datetime
import speech_recognition as sr

from aiogram import F
from aiogram.types import Voice
import soundfile
import config
import json

from static_vars import static_vars

@static_vars(counter=0)
async def save_voice_as_wav(voice: Voice, id):

    save_voice_as_wav.counter += 1
    c = save_voice_as_wav.counter
    #time = str(datetime.now()).replace(' ', '!').replace(':', '-')[:19]

    path_name = f"voice_files/{c}-id{id}.wav"
    voice_file_info = await voice.bot.get_file(voice.file_id)
    await voice.bot.download_file(voice_file_info.file_path, path_name)

    return path_name

async def voice_to_text(path_name):
    data, samplerate = soundfile.read(f'{path_name}')
    soundfile.write('new.wav', data, samplerate, subtype='PCM_16')
    r = sr.Recognizer()
    file = sr.AudioFile('new.wav')
    with file as source:
        audio = r.record(source)
    try:
        text = r.recognize_google(audio, language="ru-RU")
    except:
        print("speech error")
        return None
    
    return text

def beauty_json(s):
    fields = ["Номер объекта", "Адрес объекта", "Проведенные работы", "Необходимые материалы"]
    lines = s.split('\n')
    ans = "{\n"
    for line in lines:
        for i, field in enumerate(fields):
            if field in line:
                if line.count(':') != 1:
                    continue
                key, value = line.split(':')
                if not key or not value:
                    continue

                key = key.strip()
                if key and key[0] != '"':
                    key = '"' + key
                if key and key[-1] != '"':
                    key += '"'

                value = value.strip().strip(',')
                if value and value[0] != '"':
                    value = '"' + value
                if value and value[-1] != '"':
                    value += '"'

                ans += key + ':' + value
                if i != len(fields) - 1:
                    ans += ','
                ans += '\n'
    ans += "}\n"
    return ans    

def parse_json(s):
    return json.loads(str(s))

def save_json_to_file(data, path):
    with open(path, mode = "w") as file:
        file.write(json.dumps(data))

def load_from_file(path):
    with open(path) as file:
        return json.loads(file.read())

async def neuro_answer(request, PATH):
    
    openai.api_key = config.NEURO_TOKEN

    question = request + "\nЗаполни пожалуйста следующую информацию:\
        \nНомер объекта:\
        \nАдрес объекта:\
        \nПроведенные работы:\
        \nНеобходимые материалы(в формате кабель канал 10*10 или кроб 10*10):\
        \nОформи, пожалуйста, ответ обязательно в виде словаря в формате json, если какой-то информации не хватает, напиши что это не указано"
    print(request)
    try:
        response = openai.completions.create(model="gpt-3.5-turbo-instruct", prompt=question, max_tokens=2000)
    except:
        print("chat gpt is not avaible")
        return None
    
    ans = response.choices[0].text
    ans = beauty_json(ans)
    print(ans)

    try:
        data = parse_json(ans)
    except:
        print("parse json error")
        return None
    
    save_json_to_file(data, PATH)
    
    ans = ""
    request = ""
    for key, value in data.items():
        request = str(key) + ": " + str(value) + "\n"
        ans += request

    print(ans)
    return(ans)