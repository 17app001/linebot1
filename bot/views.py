from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse,HttpResponseBadRequest,HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

from linebot import LineBotApi, WebhookHandler,WebhookParser
from linebot.exceptions import InvalidSignatureError,LineBotApiError
from linebot.models import MessageEvent,TextSendMessage,TextMessage,ImageSendMessage

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parse=WebhookParser(settings.LINE_CHANNEL_SECRET)


@csrf_exempt    
def callback(request):
    if request.method=='POST':
        signature=request.META['HTTP_X_LINE_SIGNATURE']
        body=request.body.decode('utf-8')
        try:
            events=parse.parse(body,signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
        for event in events:
            if isinstance(event,MessageEvent):
                if isinstance(event.message,TextMessage):
                    mtext=event.message.text
                    if mtext=='1':
                        message="你好啊!!"
                    elif mtext=='2':
                        message="還沒吃飽"
                    elif '天氣' in mtext:
                        message="天氣真好"
                    elif '捷運' in mtext:
                        send_image(event,'https://th.bing.com/th/id/OIP.iij4Kfjpft1W9pe7-nJpJAHaHa?pid=ImgDet&rs=1')
                        continue
                    elif '電影' in mtext:
                        message=get_movie()
                    else:
                        messages=[TextSendMessage(message) for message in ['我不懂你在說什麼','你在說什麼?','我聽不懂你說的']]                        
                        line_bot_api.reply_message(event.reply_token,messages)
                        continue

                    line_bot_api.reply_message(
                        event.reply_token,                       
                        TextSendMessage(text=message)
                    )
        return HttpResponse()
    else:
        return HttpResponseBadRequest()



def send_image(event,url):
    message=ImageSendMessage(
        original_content_url=url,
        preview_image_url=url,
    )

    line_bot_api.reply_message( event.reply_token,message)    
  


def get_movie():
    import requests
    from bs4 import BeautifulSoup

    import json
    url='https://movies.yahoo.com.tw/chart.html'
    soup=BeautifulSoup(requests.get(url).text,'html.parser')
    movies=soup.find_all('div',class_='release_info_text')
    datas=''
    for i,tr in enumerate(soup.find_all('div','tr')[2:]):
        data=[]
        for j,td in enumerate(tr.find_all('div','td')):        
            print(td.text.strip(),end='\t')
            data.append(td.text.strip())
        datas+=' '.join(data)+'\n'    
        print()
        
    return datas