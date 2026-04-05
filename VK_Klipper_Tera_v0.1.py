import requests
import json
import asyncio
import websockets
import time
import random



COOKIE_VK = ""
ID_VK = ""

IP_ADDR_SERVER = ""
LOGIN_MOONRAKER = ""
PASSWORD_MOONRAKER = ""

PROGRESS_PRC = 26




##################################################### VK БОТ, ИСПОЛЬЗУЕТСЯ СТРАНИЦА ВАНИ


def parse_cookie_string(cookie):
    CookieVK_Result = {}

    for Iter in cookie.split(';'):
        Iter = Iter.strip()
        if '=' in Iter:
            key, value = Iter.split('=', 1)
            CookieVK_Result[key.strip()] = value.strip()
            
    return CookieVK_Result

HEADERS_BROWSER = {"origin": "https://vk.com", "pragma": "no-cache", "priority": "u=1, i", "referer": "https://vk.com/", "sec-ch-ua": '''"Not(A:Brand";v="8", "Chromium";v="144"?"YaBrowser";v="26.3", "Yowser";v="2.5"''', "sec-ch-ua-mobile": "?0", "sec-ch-ua-platform": '"Windows"', "sec-fetch-dest": "empty", "sec-fetch-mode": "cors", "sec-fetch-site": "same-site", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 YaBrowser/26.3.0.0 Safari/537.36"}


COOKIE = parse_cookie_string(COOKIE_VK)

def GetToken_VK():
    JsonVK = json.loads(requests.post("https://login.vk.com/?act=web_token", data = {"version": "1", "app_id": "6287487", "access_token": "vk1.a.BtvLVu0gcI9eLmH4Masxbf3PeQ0ahFoIBr3yRtM1OTHEHRfZNNikW9uAM5kqKSI8PAIWL0ucneXKAILdRFDMn_KB1aDuH1TzkJEfjRnA_Q5tXk_3Pi0nzdLTvIMz32NKDSGCYVKvD60sPv3r73wySjevm_hRHmSu-CsQsR6HbYCBn7blkV7D8-tFttXcKMr976b_pLyOoSVXPQz2grbeRw"}, headers = HEADERS_BROWSER, cookies = COOKIE, ).text)
    
    return JsonVK["data"]["access_token"]

def VkBot_Init():
    TokenVK = GetToken_VK()
    
    API_VK_INIT = requests.post("https://api.vk.com/method/messages.send?v=5.274&client_id=6287487", data = {"peer_id": ID_VK, "random_id": str(random.randint(-124443543, 3255334523)), "message": "___INIT___", "entrypoint": "popular_suggestions", "group_id": 0, "from": "reforged", "access_token": TokenVK}, headers = HEADERS_BROWSER).text
    
    ResponseJson = json.loads(API_VK_INIT)
    
    if "error" in ResponseJson:
        print("[-] ERROR API VK: ", ResponseJson["error"]["error_msg"])
        return "error_msg"
        
    return str(ResponseJson["response"]["cmid"])


def VkBot_Sender(MessageText, cmid_message):
    TokenVK = GetToken_VK()

    API_VK_RESP = requests.post("https://api.vk.com/method/messages.edit?v=5.274&client_id=6287487", data = {"cmid": cmid_message, "peer_id": ID_VK, "message": MessageText, "group_id": "0", "keep_forward_messages": "0", "keep_snippets": "0", "access_token": GetToken_VK()}, headers = HEADERS_BROWSER).text
    
    print("[+] VK_API: отправлено\r\n\r\n")

ID_MESSAGE_LAST = -1


async def VkBot_Commands(DescWB_Socket):
    global ID_VK
    global ID_MESSAGE_LAST

    
    
    TokenVK = GetToken_VK()
    
    API_VK_HISTORY_MESSAGE = requests.post("https://api.vk.com/method/messages.getHistory?v=5.274&client_id=6287487", data = {"peer_id": ID_VK, "start_message_id": "-1", "count": "1", "offset": "0", "extended": "0", "group_id": "0", "fwd_extended": "0", "fields": "id", "access_token": TokenVK}, headers = HEADERS_BROWSER).text
    JsonHist = json.loads(API_VK_HISTORY_MESSAGE)
    
    if len(JsonHist["response"]["items"]) == 0:
        return
    
    if (JsonHist["response"]["items"][0]["id"] == ID_MESSAGE_LAST):
        return
        
    ID_MESSAGE_LAST = JsonHist["response"]["items"][0]["id"]
    print("[=] DEBUG_API_VK_COMMANDS\r\nID MESSAGE: ", ID_MESSAGE_LAST, "\r\nTEXT: ", JsonHist["response"]["items"][0]["text"], "\r\n\r\n")
    
    if JsonHist["response"]["items"][0]["text"] == "/STOP_PRINT":
        await DescWB_Socket.send(r'{"jsonrpc":"2.0","method":"printer.emergency_stop","id": 4564}'.encode())
        
        print("\r\n\r\n")
        print(await DescWB_Socket.recv())
        print("\r\n\r\n[-] ПРИНТЕР ВЫКЛЮЧАЕТСЯ [-]\r\n\r\n")
        
#################################################



#################################################
def GetAuthBearer_Token():
    Auth_Data = requests.post(f"http://{IP_ADDR_SERVER}/access/login", data = {"username": LOGIN_MOONRAKER,"password": PASSWORD_MOONRAKER,"source":"moonraker"}).text
    AuthJson = json.loads(Auth_Data)
    
    return AuthJson["result"]["token"]

def Get_WebSocket_Token():
    TokenWeb_SOCKET = requests.get(f"http://{IP_ADDR_SERVER}/access/oneshot_token", headers = {"Authorization": f"Bearer {GetAuthBearer_Token()}"}).text
    JsonConv = json.loads(TokenWeb_SOCKET)
    
    return JsonConv["result"]

# Функции для облегчения получения токена авторизации и токена websocket для получения данных в потоковом режиме
#################################################

Extruder_Temperature = [""]
Heater_Bed_Temperature = [""]
Progress = [""]
ProgressInt = 0

def parse_data(JsonPrinter_WebSocket): # для автоматизации парсинга
    global Extruder_Temperature
    global Heater_Bed_Temperature
    global Progress
    global ProgressInt
    
    if "method" in JsonPrinter_WebSocket:
        if JsonPrinter_WebSocket["method"] == "notify_status_update":
            if "params" in JsonPrinter_WebSocket:
            
                for TempT in JsonPrinter_WebSocket["params"][0]:
                    if TempT == "heater_bed":
                        print(f'DEBUG: {str(JsonPrinter_WebSocket["params"][0][TempT])}')
                    
                        if ("temperature" in str(JsonPrinter_WebSocket["params"][0][TempT])):
                            if (str(JsonPrinter_WebSocket["params"][0][TempT]) == Heater_Bed_Temperature[0]):
                                continue
                        
                            Heater_Bed_Temperature[0] = str(JsonPrinter_WebSocket["params"][0][TempT]["temperature"])

                
                    if TempT == "extruder":
                        print(f"DEBUG: {str(JsonPrinter_WebSocket["params"][0][TempT])}")
                        if ("temperature" in str(JsonPrinter_WebSocket["params"][0][TempT])):
                            if (str(JsonPrinter_WebSocket["params"][0][TempT]) == Extruder_Temperature[0]):
                                continue
                        
                            Extruder_Temperature[0] = str(JsonPrinter_WebSocket["params"][0][TempT]["temperature"])
                            
                    if TempT == "virtual_sdcard":
                        print(f"DEBUG: {str(JsonPrinter_WebSocket["params"][0][TempT])}")
                        if ("progress" in str(JsonPrinter_WebSocket["params"][0][TempT])):
                            if (str(JsonPrinter_WebSocket["params"][0][TempT]["progress"] * 100) == Progress[0]):
                                continue
                            
                            Progress[0] = str(JsonPrinter_WebSocket["params"][0][TempT]["progress"] * 100)
                            
                            ProgressInt = int(JsonPrinter_WebSocket["params"][0][TempT]["progress"] * 100)

    
    
    


async def Info_TeraPrinter():
    ID_MESSAGE_BOT = VkBot_Init()
    
    if (ID_MESSAGE_BOT == "error_msg"):
        return
    
    StartTime_VK = time.time()
    EndTime_ExecuteVK = StartTime_VK + 10 # для периодической отправки в вк
    
    StartTime_VKRead = time.time()
    EndTime_VKReadExecute = StartTime_VKRead + random.randint(12, 14)
    
    TokenWeb_Socket = Get_WebSocket_Token()
    print(f"[+] СОЕДИНЕНИЕ С СЕРВЕРОМ... \r\nТокен: {TokenWeb_Socket}\r\n\r\n")
    
    async for WebSocket_Tera in websockets.connect(f"ws://{IP_ADDR_SERVER}/websocket?token={TokenWeb_Socket}"):
        print("[] СОЕДИНЕНИЕ УСТАНОВЛЕНО\r\n\r\n\r\n")
        await WebSocket_Tera.send(r"""{"id":10020,"method":"printer.objects.subscribe","jsonrpc":"2.0","params":{"objects":{"gcode":null,"webhooks":null,"configfile":null,"mcu":null,"pause_resume":null,"filament_switch_sensor filament_detection":null,"output_pin caselight":null,"output_pin _Zummer":null,"gcode_macro beep":null,"gcode_macro endprintbeep":null,"gcode_macro startprintbeep":null,"heaters":null,"heater_bed":null,"stepper_enable":null,"controller_fan mcu":null,"fan":null,"heater_fan nozzle_fan":null,"temperature_host Raspbery_Pi":null,"temperature_sensor Raspbery_Pi":null,"temperature_sensor mcu_temp":null,"firmware_retraction":null,"gcode_move":null,"exclude_object":null,"bed_screws":null,"print_stats":null,"virtual_sdcard":null,"display_status":null,"gcode_macro PAUSE":null,"gcode_macro RESUME":null,"gcode_macro CANCEL_PRINT":null,"gcode_macro PID_E":null,"gcode_macro PID_B":null,"gcode_macro Parking":null,"gcode_macro SWAP_FILAMENT":null,"query_endstops":null,"motion_report":null,"toolhead":null,"extruder":null,"idle_timeout":null,"system_stats":null,"manual_probe":null}}}""".encode())
        while True:
            try:
                WebSocket_Data = await WebSocket_Tera.recv()
                WB_json = json.loads(WebSocket_Data)
                
                Data_Printer = parse_data(WB_json)

                print(f"[*] Температура стола: {Heater_Bed_Temperature[0]}\r\n[*] Температура сопла: {Extruder_Temperature[0]}\r\n[*] Прогресс: {Progress[0]}%\r\n")
                
                
                ProgressBar = "[" + ("█" * int((ProgressInt / 100) * PROGRESS_PRC)) + ("░" * int(26 - (ProgressInt / 100) * PROGRESS_PRC)) + "]"

                if time.time() >= EndTime_ExecuteVK:
                    VkBot_Sender(f"Температура стола: {Heater_Bed_Temperature[0]}\r\nТемпература сопла: {Extruder_Temperature[0]}\r\nПрогресс: {Progress[0]}%\r\n{ProgressBar}", ID_MESSAGE_BOT)

                    StartTime_VK = time.time()
                    EndTime_ExecuteVK = StartTime_VK + 10
                    
                if time.time() >= EndTime_VKReadExecute:
                    await VkBot_Commands(WebSocket_Tera)
                    
                    StartTime_VKRead = time.time()
                    EndTime_VKReadExecute = StartTime_VKRead + random.randint(12, 14)
                    
                
                
            except websockets.ConnectionClosed:
                TokenWeb_Socket = Get_WebSocket_Token()
                WebSocket_Tera = websockets.connect(f"ws://{IP_ADDR_SERVER}/websocket?token={TokenWeb_Socket}")
                continue

############################################################## Асинхронная часть для получения показателей с сервера принтера Tera
########################################################################################
########################################################################################


asyncio.run(Info_TeraPrinter())

####################################################################
####################################################################
