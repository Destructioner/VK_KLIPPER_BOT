import asyncio
import aiohttp
import random




class TeraVkClient:
    def __init__(self):
        self.__HEADERS_BROWSER = {"origin": "https://vk.com", "pragma": "no-cache", "priority": "u=1, i", "referer": "https://vk.com/", "sec-ch-ua": '''"Not(A:Brand";v="8", "Chromium";v="144"?"YaBrowser";v="26.3", "Yowser";v="2.5"''', "sec-ch-ua-mobile": "?0", "sec-ch-ua-platform": '"Windows"', "sec-fetch-dest": "empty", "sec-fetch-mode": "cors", "sec-fetch-site": "same-site", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 YaBrowser/26.3.0.0 Safari/537.36"}
        self.__COOKIE_VK = ""
        self.__ID_VK = ""
        self.__ID_MESSAGE_LAST = -1
        self.__cfg_name = ""
        self.vk_request = aiohttp.ClientSession(connector = aiohttp.TCPConnector(ssl=False))
    
        
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
        
        Cfg_Handle.close()
        return "[] Ошибка: отсутствует параметр " + Param_name + " в конфиге!"

    



    def _EditPARAM_CFG(self, Param_name, ValueParam):
        GetTemp_Value = _GetPARAM_CFG(Param_name)
        DataCfg = ""
    
        with open(self.__cfg_name, "r") as CfgGet:
            DataCfg = CfgGet.read()
        
        if Param_name not in DataCfg:
            return "[] Ошибка: отсутствует параметр " + Param_name + " в конфиге!"
            
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
        try:
            JsonRaw = await self.vk_request.post("https://login.vk.com/?act=web_token", data = {"version": "1", "app_id": "6287487", "access_token": "null"}, headers = self.__HEADERS_BROWSER, cookies = self.__COOKIE_VK)
            JsonVK = await JsonRaw.json()

            if JsonVK.get("error_info") != None:
                return "[-] ОШИБКА ПОЛУЧЕНИЯ ТОКЕНА API: " + JsonVK["error_info"]

        
            return JsonVK["data"]["access_token"]
            
        except aiohttp.client_exceptions.ClientConnectorCertificateError:
            return "[*] SSL СЕРТИФИКАТ VK НЕДЕЙСТВИТЕЛЕН"

        
    async def initClient(self):
        TokenVK = await self._GetToken_VK()
        if TokenVK == "unauthorized":
            sys.exit(-1)
        
        API_VK_INIT = await self.vk_request.post("https://api.vk.com/method/messages.send?v=5.274", data = {"peer_id": self.__ID_VK, "random_id": str(random.getrandbits(64)), "message": "___INIT___", "entrypoint": "popular_suggestions", "group_id": 0, "from": "reforged", "access_token": TokenVK}, headers = self.__HEADERS_BROWSER)

        if API_VK_INIT.status == 200:
            ResponseJson = await API_VK_INIT.json()

            if "error" in ResponseJson:
                return "ERROR API VK: " + ResponseJson["error"]["error_msg"]
        

            return str(ResponseJson["response"]["cmid"])
        
        else:
            return f"[] Ошибка запроса в VK REST API: {API_VK_INIT.status}"

    async def editMessage(self, MessageText, cmid, PhotoAttach = ""):
        TokenVK = await self._GetToken_VK()

        if PhotoAttach == "":
            API_VK_RESP = await self.vk_request.post("https://api.vk.com/method/messages.edit?v=5.274", data = {"cmid": cmid, "peer_id": self.__ID_VK, "message": MessageText, "group_id": "0", "keep_forward_messages": "0", "keep_snippets": "0", "access_token": TokenVK}, headers = self.__HEADERS_BROWSER)
        
            if API_VK_RESP.status != 200:
                f"[] Ошибка запроса в VK REST API: {API_VK_RESP.status}"
        
        else:
            API_VK_RESP = await self.vk_request.post("https://api.vk.com/method/messages.edit?v=5.274", data = {"cmid": cmid, "peer_id": self.__ID_VK, "message": MessageText, "attachment": PhotoAttach, "group_id": "0", "keep_forward_messages": "0", "keep_snippets": "0", "access_token": TokenVK}, headers = self.__HEADERS_BROWSER)
    
    async def getMessage(self):
        TokenVK = await self._GetToken_VK()
    
        API_VK_HISTORY_MESSAGE = await self.vk_request.post("https://api.vk.com/method/messages.getHistory?v=5.274", data = {"peer_id": self.__ID_VK, "start_message_id": "-1", "count": "1", "offset": "0", "extended": "0", "group_id": "0", "fwd_extended": "0", "fields": "id", "access_token": TokenVK}, headers = self.__HEADERS_BROWSER)
        
        if API_VK_HISTORY_MESSAGE.status == 200:
            JsonHist = await API_VK_HISTORY_MESSAGE.json()
        
            if len(JsonHist["response"]["items"]) == 0:
                return
    
            if (JsonHist["response"]["items"][0]["id"] == self.__ID_MESSAGE_LAST):
                return
                
        
            self.__ID_MESSAGE_LAST = JsonHist["response"]["items"][0]["id"]
            return JsonHist["response"]["items"][0]["text"]
            
        
        else:
            return f"[] Ошибка запроса в VK REST API: {API_VK_HISTORY_MESSAGE.status}"
            


    
    async def sendPhoto(self, PhotoBytes: bytes):

        TokenVK = await self._GetToken_VK()
        await asyncio.sleep(2)
        
        ALBUM_ID = ""
        UPLOAD_URL = ""

        
        UploadServer_URL = await self.vk_request.post("https://api.vk.com/method/photos.getMessagesUploadServer?v=5.275", data = {"peer_id": self.__ID_VK, "group_id": "0", "upload_v2": "1", "access_token": TokenVK}, headers = self.__HEADERS_BROWSER)
        
        JsonUploadServer_URL = await UploadServer_URL.json()
        if "upload_url" in JsonUploadServer_URL["response"]:
            UPLOAD_URL = JsonUploadServer_URL["response"]["upload_url"]
            ALBUM_ID = JsonUploadServer_URL["response"]["album_id"]
            await asyncio.sleep(4)
            

            FormPhoto_Data = aiohttp.FormData()
            FormPhoto_Data.add_field('file1', PhotoBytes, filename='temp.jpg', content_type='image/jpeg')
            
            
            UploadPhoto = await self.vk_request.post(UPLOAD_URL, data = FormPhoto_Data, headers = self.__HEADERS_BROWSER)
            JsonUpload = await UploadPhoto.text()
            
            
            if "error" in JsonUpload:
                while "error" in JsonUpload:
                    print(JsonUpload)
                    UploadPhoto = await self.vk_request.post(UPLOAD_URL, data = FormPhoto_Data, headers = self.__HEADERS_BROWSER)
                    JsonUpload = await UploadPhoto.text()
                    
                    await asyncio.sleep(10)
 
                    
            await asyncio.sleep(4)
            
            SavePHOTO = await self.vk_request.post("https://api.vk.com/method/photos.saveMessagesPhoto?v=5.275", data = {"upload_v2": "1", "photo": JsonUpload, "group_id": "0", "access_token": TokenVK})
            
            JsonSave = await SavePHOTO.json()
            return f"photo{str(JsonSave["response"][0]["owner_id"])}_{str(JsonSave["response"][0]["id"])}_{str(JsonSave["response"][0]["access_key"])}"
            
            
            
            
            
            
        
    
    def SetName_Cfg(self, name_cfg):
        self.__cfg_name = name_cfg
        
        self.__COOKIE_VK = self._parse_cookie_string(self._GetPARAM_CFG("COOKIE_VK"))
        self.__ID_VK = self._GetPARAM_CFG("ID_VK")
        