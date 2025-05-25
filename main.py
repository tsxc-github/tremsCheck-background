import json

import requests
import uvicorn
from openai import OpenAI
from fastapi import FastAPI
from typing import List, Union
from lxml import html
import trafilatura

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app=FastAPI()

@app.get("/api/get_website_content")
def GetContent(URL:str):
    """
    寻找页面主要内容
    - URL:要获取的网页的URL
    返回一个内容的string
    """
    result=requests.get(URL,headers={"user_agent":R'"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"'})
    result.encoding="utf-8"
    result=result.text
    tree=html.fromstring(result)
    content=trafilatura.extract(tree)

    return content

def RequestDeepseek(system_prompt,user_prompt,temperature=0):
    # 请替换为你的 API 密钥
    api_key = "sk-79e5d27cc085498ea8d417e240836ef0"

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
    )

    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}]

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        response_format={
            'type': 'json_object'
        },
        temperature=temperature
    )

    #输出
    print(response.choices[0].message.content)

    return response.choices[0].message.content




@app.get("/")
def root():
    return {"message": "Hello World"}

@app.post("/api/questions/")
def questions(message_request:str,message_content:str,session_id:int):
    """
    根据条文问ai问题
    - message_request: 问题
    - message_content: 条文内容
    - session_id: 会话id
    """
    system_prompt = open("prompt.md","r",encoding="utf-8").read().replace("{question}",message_request)
    user_prompt = message_content
    content=RequestDeepseek(system_prompt,user_prompt)

    return JSONResponse(content=content)

@app.post("/api/get_question")
def GetQuestion(message_content:str,number:int,session_id:int):
    """
    根据条文生成一个让用户概括的问题
    - message_content：条文
    - number: 需要的条文数量
    - session_id：会话id
    """
    system_prompt = open("prompt-ask.md", "r", encoding="utf-8").read().replace("{number}",str(number))
    user_prompt = message_content
    content=RequestDeepseek(system_prompt,user_prompt)

    return JSONResponse(content=content)

@app.post("/api/judge_answer")
def JudgeAnswer(question:str,answer:str,session_id:int):
    """
    判断question条文和用户的answer是否匹配
    - question: 条文内容
    - answer: 用户回答

    示例输出:
    ```json
    {
        "response": {
            "match": true
        }
    }
    ```
    """
    system_prompt = open("prompt-ask-test.md", "r", encoding="utf-8").read()
    user_prompt = {"question":question,"answer":answer}
    content=RequestDeepseek(system_prompt,str(user_prompt))
    return JSONResponse(content=content)

@app.post("/api/get_mcq")
def mcq(question:str,session_id:int):
    """
    给出一道选择题
    - question: 条文内容

    示例输出:

    ```json
{
    "response": {
        "A": {
          "content": "此产品要负任何法律责任",
          "right": false
        },
        "B": {
            "content": "此产品的法律责任是无穷多的",
            "right": false
        },
        "C": {
            "content": "此产品不负法律责任",
            "right": true
        },
        "D": {
            "content": "阿巴阿巴",
            "right": false
        }
    }
}
    ```
    """

    system_prompt = open("prompt-choose.md", "r", encoding="utf-8").read()
    user_prompt = question
    content=RequestDeepseek(system_prompt,str(user_prompt),1)
    return JSONResponse(content=content)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':
    uvicorn.run(app="main:app",reload=True,host="0.0.0.0")
    # print(GetContent("https://cdn.deepseek.com/policies/zh-CN/deepseek-terms-of-use.html"))
    pass
    # system_prompt = open("prompt.md","r",encoding="utf-8").read().replace("{question}","隐私相关")
    # print(questions("隐私相关",open("import.md","r",encoding="utf-8").read(),1))