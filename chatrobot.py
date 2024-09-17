import os
from openai import OpenAI
import requests
import pygame
import time

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key=api_key,
    base_url="https://api.chatanywhere.tech/v1"
)


def generate_text(text: str, demand: str):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": demand},
            {
                "role": "user",
                "content": text
            }
        ]
    )
    print('回答：' + completion.choices[0].message.content)
    return completion.choices[0].message.content

def text2speech(text: str):
    base_path = r'E:\DL\Transformers\Projects\audio2text\ChatTTS-UI-0.84\ChatTTS-UI-0.84\static\wavs'
    origin_files = os.listdir(base_path)
    try:
        requests.post('http://127.0.0.1:9966/tts', data={
            "text": text,
            "prompt": "[laugh_0]",
            "voice": "6132",
            "temperature": 0.00001,
            "top_p": 0.7,
            "top_k": 20,
            "refine_max_new_token": "384",
            "infer_max_new_token": "2048",
            "skip_refine": 0,
            "is_split": 1,  # 数字转文字？
            "custom_voice": 6132
        })
    except requests.exceptions.RequestException as e:
        print(f"请求 TTS 服务器时出错: {e}")
    else:
        new_files = os.listdir(base_path)
        for file in new_files:
            if file not in origin_files:
                path = file
                break
        path = os.path.join(base_path, path)
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        pygame.mixer.music.set_volume(1.0)
        while pygame.mixer.music.get_busy():
            time.sleep(1)
        pygame.mixer.music.stop()

class ChatSession:
    def __init__(self, system_prompt: str):
        self.messages = [{"role": "system", "content": system_prompt}]

    def add_user_message(self, text: str):
        self.messages.append({"role": "user", "content": text})

    def get_response(self):
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=self.messages
        )
        response = completion.choices[0].message.content
        self.messages.append({"role": "assistant", "content": response})
        return response

def main():
    pygame.init()  # 初始化所有 Pygame 模块
    system_prompt = input('请输入你对于聊天机器人的要求:')
    chat_session = ChatSession(system_prompt)
    while True:
        user_input = input('请输入文本(输入q退出)：')
        if user_input == "q":
            print('程序退出！')
            break
        chat_session.add_user_message(user_input)
        response = chat_session.get_response()
        print(response)
        text2speech(response)
    pygame.quit()

if __name__ == "__main__":
    main()