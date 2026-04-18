import asyncio
import aiohttp
import random
import sys




class TeraVkClient:
    def __init__(self):
        self.__HEADERS_BROWSER = {"origin": "https://vk.com", "pragma": "no-cache", "priority": "u=1, i", "referer": "https://vk.com/", "sec-ch-ua": '''"Not(A:Brand";v="8", "Chromium";v="144"?"YaBrowser";v="26.3", "Yowser";v="2.5"''', "sec-ch-ua-mobile": "?0", "sec-ch-ua-platform": '"Windows"', "sec-fetch-dest": "empty", "sec-fetch-mode": "cors", "sec-fetch-site": "same-site", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 YaBrowser/26.3.0.0 Safari/537.36"}
        self.__COOKIE_VK = ""
        self.__ID_VK = ""
        self.__ID_MESSAGE_LAST = -1
        self.__ID_MESSAGE_UPDATE = -1
        self.__cfg_name = ""
        self.vk_request = aiohttp.ClientSession()
    
    def _GetPARAM_CFG(self, Param_name):
        Cfg_Handle = open(self.__cfg_name, "r")
    
        LineCfg = Cfg_Handle.readline()
        
        while LineCfg != "":
            if Param_name in LineCfg:
                Offset = LineCfg.find("=") + 1

                while LineCfg[Offset] == " ":
                    Offset += 1
            
                Cfg_Handle.close()
                return LineCfg[Offset:].strip()
        
            LineCfg = Cfg_Handle.readline()
            
        print("[] Ошибка: отсутствует параметр ", Param_name, " в конфиге!")
        Cfg_Handle.close()
        sys.exit(1)

    



    def _EditPARAM_CFG(self, Param_name, ValueParam):
        GetTemp_Value = _GetPARAM_CFG(Param_name)
        DataCfg = ""
    
        with open(self.__cfg_name, "r") as CfgGet:
            DataCfg = CfgGet.read()
        
        if Param_name not in DataCfg:
            print("[] Ошибка: отсутствует параметр ", Param_name, " в конфиге!")
            sys.exit(1)
            
        with open(self.__cfg_name, "w") as CfgEdit:
            CfgEdit.write(DataCfg.replace(Param_name + " = " + GetTemp_Value, Param_name + " = " + ValueParam))
    
    
    def _parse_cookie_string(self, cookie):
        CookieVK_Result = {}

        for Iter in cookie.split(';'):
            Iter = Iter.strip()
            if '=' in Iter:
                key, value = Iter.split('=', 1)
                CookieVK_Result[key.strip()] = value.strip()
            
        return CookieVK_Result
        
    async def _GetToken_VK(self):
        JsonRaw = await self.vk_request.post("https://login.vk.com/?act=web_token", data = {"version": "1", "app_id": "6287487", "access_token": "null"}, headers = self.__HEADERS_BROWSER, cookies = self.__COOKIE_VK)
        JsonVK = await JsonRaw.json()
    
        if "error_info" in JsonVK:
            print("[-] ОШИБКА ПОЛУЧЕНИЯ ТОКЕНА API: ", JsonVK["error_info"])
            sys.exit(1)
        
        return JsonVK["data"]["access_token"]
        
    async def initClient(self):
        TokenVK = await self._GetToken_VK()

        
        API_VK_INIT = await self.vk_request.post("https://api.vk.com/method/messages.send?v=5.274&client_id=6287487", data = {"peer_id": self.__ID_VK, "random_id": str(random.getrandbits(64)), "message": "___INIT___", "entrypoint": "popular_suggestions", "group_id": 0, "from": "reforged", "access_token": TokenVK}, headers = self.__HEADERS_BROWSER)

        if API_VK_INIT.status == 200:
            ResponseJson = await API_VK_INIT.json()

            if "error" in ResponseJson:
                return "ERROR API VK: " + ResponseJson["error"]["error_msg"]
        

            return str(ResponseJson["response"]["cmid"])
        
        else:
            print(f"[] Ошибка запроса в VK REST API: {API_VK_INIT.status}")
            sys.exit(1)
        
    async def editMessage(self, MessageText, cmid):
        TokenVK = await self._GetToken_VK()

        API_VK_RESP = await self.vk_request.post("https://api.vk.com/method/messages.edit?v=5.274&client_id=6287487", data = {"cmid": cmid, "peer_id": self.__ID_VK, "message": MessageText, "group_id": "0", "keep_forward_messages": "0", "keep_snippets": "0", "access_token": TokenVK}, headers = self.__HEADERS_BROWSER)
        
        if API_VK_RESP.status != 200:
            print(f"[] Ошибка запроса в VK REST API: {API_VK_RESP.status}")
            sys.exit(1)
        
    async def getMessage(self):
        TokenVK = await self._GetToken_VK()
    
        API_VK_HISTORY_MESSAGE = await self.vk_request.post("https://api.vk.com/method/messages.getHistory?v=5.274&client_id=6287487", data = {"peer_id": self.__ID_VK, "start_message_id": "-1", "count": "1", "offset": "0", "extended": "0", "group_id": "0", "fwd_extended": "0", "fields": "id", "access_token": TokenVK}, headers = self.__HEADERS_BROWSER)
        
        if API_VK_HISTORY_MESSAGE.status == 200:
            JsonHist = await API_VK_HISTORY_MESSAGE.json()
        
            if len(JsonHist["response"]["items"]) == 0:
                return
    
            if (JsonHist["response"]["items"][0]["id"] == self.__ID_MESSAGE_LAST):
                return
                
        
            self.__ID_MESSAGE_LAST = JsonHist["response"]["items"][0]["id"]
            
        
        else:
            print(f"[] Ошибка запроса в VK REST API: {API_VK_HISTORY_MESSAGE.status}")
            sys.exit(1)
    
    def SetName_Cfg(self, name_cfg):
        self.__cfg_name = name_cfg
        
        self.__COOKIE_VK = self._parse_cookie_string(self._GetPARAM_CFG("COOKIE_VK"))
        self.__ID_VK = self._GetPARAM_CFG("ID_VK")
        