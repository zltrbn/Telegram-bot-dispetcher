from openai import OpenAI
#from datetime import datetime
import speech_recognition as sr

from aiogram import F
from aiogram.types import Voice
import soundfile
from typing import List
from pydantic import BaseModel
import json
import config
import pandas as pd
from scipy.spatial.distance import cosine
import numpy as np

from static_vars import static_vars

client = OpenAI(
    api_key=config.NEURO_TOKEN,
)

class EnquetAIResponse(BaseModel):
    Номер_объекта: str
    Адрес_объекта: str
    Проведенные_работы: str
    Необходимые_материалы: str


def get(text, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding

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

async def neuro_answer(request):
    try:
        response = client.chat.completions.create(model="gpt-3.5-turbo-0613",
        messages=[
       {"role": "user", "content": request}
    ],
    functions=[
        {
          "name": "get_answer_for_user_query",
          "description": "Заполни анкету, обычно она присылается в следующем виде: Номер объекта адрес объекта \
             произведенные работы обследование необходимые материалы смк102-502 одна штука, кс4 одна штука, кспв четыре на ноль точка пять три метра \
            Необходимые материалы укажи через запятую. \
            Если какой-то информации не хватает, укажи None",
          "parameters": EnquetAIResponse.schema()
        }
    ],
    function_call={"name": "get_answer_for_user_query"}
)
    
        answer = json.loads(response.choices[0].message.function_call.arguments)
        print(request)
    except:
        print("chat gpt is not avaible")
        return None

    if answer["Номер_объекта"] == "None" or answer["Адрес_объекта"] == "None":
        return f'Обязательно укажите в своем голосовом сообщении номер и адрес объекта'
    else:
        return answer


async def get_embedding(ar, f):
    df = pd.read_csv("datas.csv")

    df['embedding'] = df.Syn.apply(lambda x: get(x, model='text-embedding-ada-002'))
    df.to_csv("new_data.csv")

    with open(f"{f}", mode = "a") as file:
        for _, text in enumerate(ar):
            print(text)
            text_emb = get(text, model='text-embedding-ada-002')
            score = df.embedding.apply(lambda x: cosine(x, text_emb)).to_list()
            print(score)
            file.write("\n")
            print(f"{text}-{df['Id'][np.argmin(score)]}")
            file.write(f"{text}-{df['Id'][np.argmin(score)]}")
    