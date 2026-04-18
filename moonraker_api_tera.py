import aiohttp
import json
import asyncio
import sys


class TeraMoonrakerClient:
    def __init__(self, DEBUG_MODE = 1):
        self.__Extruder_Temperature = ""
        self.__Heater_Bed_Temperature = ""
        self.__Progress = 0
        self.__DEBUG_MODE = DEBUG_MODE
        self.__cfg_name = ""
        self.__WB_API_MOONRAKER = None
        self.__MoonrakerSess = aiohttp.ClientSession()
        self.__MoonrakerWebSocket = aiohttp.ClientSession()
        
        self.__IP_SERVER_MOONRAKER = ""
        self.__LOGIN_MOONRAKER = ""
        self.__PASSWORD_MOONRAKER = ""
    
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
        GetTemp_Value = self._GetPARAM_CFG(Param_name)
        DataCfg = ""
    
        with open(self.__cfg_name, "r") as CfgGet:
            DataCfg = CfgGet.read()
            
        if Param_name not in DataCfg:
            print("[] Ошибка: отсутствует параметр ", Param_name, " в конфиге!")
            sys.exit(1)
            
        with open(self.__cfg_name, "w") as CfgEdit:
            CfgEdit.write(DataCfg.replace(Param_name + " = " + GetTemp_Value, Param_name + " = " + ValueParam))
    
    
    async def _GetAuthBearer_Token(self):
        Auth_Data = await self.__MoonrakerSess.post(f"http://{self.__IP_SERVER_MOONRAKER}/access/login", data = {"username": self.__LOGIN_MOONRAKER, "password": self.__PASSWORD_MOONRAKER,"source":"moonraker"})
        
        if Auth_Data.status == 200:
            AuthJson = await Auth_Data.json()
    
            return AuthJson["result"]["token"]
            
        else:
            print(f"[] Ошибка запроса в Moonraker API: {Auth_Data.status}")
            sys.exit(1)

    async def _Get_WebSocket_Token(self):
        TokenWeb_SOCKET = await self.__MoonrakerSess.get(f"http://{self.__IP_SERVER_MOONRAKER}/access/oneshot_token", headers = {"Authorization": f"Bearer {await self._GetAuthBearer_Token()}"})
        
        if TokenWeb_SOCKET.status == 200:
            JsonConv = await TokenWeb_SOCKET.json()
    
            return JsonConv["result"]
            
        else:
            print(f"[] Ошибка запроса в Moonraker API: {TokenWeb_SOCKET.status}")
            sys.exit(1)
        
        
    def _parse_data(self, JsonPrinter_WebSocket): # для автоматизации парсинга

        if "method" in JsonPrinter_WebSocket:
            if JsonPrinter_WebSocket["method"] == "notify_status_update":
                if "params" in JsonPrinter_WebSocket:
            
                    for TempT in JsonPrinter_WebSocket["params"][0]:
                        if TempT == "heater_bed":
                            if self.__DEBUG_MODE == 1: print(f'DEBUG: {str(JsonPrinter_WebSocket["params"][0][TempT])}')
                    
                            if ("temperature" in str(JsonPrinter_WebSocket["params"][0][TempT])):
                                if (str(JsonPrinter_WebSocket["params"][0][TempT]["temperature"]) == self.__Heater_Bed_Temperature):
                                    continue
                        
                                self.__Heater_Bed_Temperature = str(JsonPrinter_WebSocket["params"][0][TempT]["temperature"])

                
                        if TempT == "extruder":
                            if self.__DEBUG_MODE == 1: print(f"DEBUG: {str(JsonPrinter_WebSocket["params"][0][TempT])}")
                            
                            if ("temperature" in str(JsonPrinter_WebSocket["params"][0][TempT])):
                                if (str(JsonPrinter_WebSocket["params"][0][TempT]["temperature"]) == self.__Extruder_Temperature):
                                    continue
                        
                                self.__Extruder_Temperature = str(JsonPrinter_WebSocket["params"][0][TempT]["temperature"])
                            
                        if TempT == "virtual_sdcard":
                            if self.__DEBUG_MODE == 1: print(f"DEBUG: {str(JsonPrinter_WebSocket["params"][0][TempT])}")
                            
                            if ("progress" in str(JsonPrinter_WebSocket["params"][0][TempT])):
                                if (str(JsonPrinter_WebSocket["params"][0][TempT]["progress"] * 100) == self.__Progress):
                                    continue
                            
                                self.__Progress = JsonPrinter_WebSocket["params"][0][TempT]["progress"] * 100
                            

    
    async def connect_moonraker(self):
        TokenWeb_Socket = await self._Get_WebSocket_Token()
        
        try:
            self.__WB_API_MOONRAKER = await self.__MoonrakerWebSocket.ws_connect(f"ws://{self.__IP_SERVER_MOONRAKER}/websocket?token={TokenWeb_Socket}")
            await self.__WB_API_MOONRAKER.send_str(r'{"id":10020,"method":"printer.objects.subscribe","jsonrpc":"2.0","params":{"objects":{"gcode":null,"webhooks":null,"configfile":null,"mcu":null,"pause_resume":null,"filament_switch_sensor filament_detection":null,"output_pin caselight":null,"output_pin _Zummer":null,"gcode_macro beep":null,"gcode_macro endprintbeep":null,"gcode_macro startprintbeep":null,"heaters":null,"heater_bed":null,"stepper_enable":null,"controller_fan mcu":null,"fan":null,"heater_fan nozzle_fan":null,"temperature_host Raspbery_Pi":null,"temperature_sensor Raspbery_Pi":null,"temperature_sensor mcu_temp":null,"firmware_retraction":null,"gcode_move":null,"exclude_object":null,"bed_screws":null,"print_stats":null,"virtual_sdcard":null,"display_status":null,"gcode_macro PAUSE":null,"gcode_macro RESUME":null,"gcode_macro CANCEL_PRINT":null,"gcode_macro PID_E":null,"gcode_macro PID_B":null,"gcode_macro Parking":null,"gcode_macro SWAP_FILAMENT":null,"query_endstops":null,"motion_report":null,"toolhead":null,"extruder":null,"idle_timeout":null,"system_stats":null,"manual_probe":null}}}')
        
            return self.__WB_API_MOONRAKER
                
        except aiohttp.ClientConnectionError:
            return "ClientConnectionError"
            
        except asyncio.TimeoutError:
            return "TimeOutError"
            
        except aiohttp.ClientConnectorError:
            return "ClientConnectorError"
        
        except:
            return None
        
    async def update_metrics(self):
        if self.__WB_API_MOONRAKER is not None:

            try:
                WebSocket_DataJson = await self.__WB_API_MOONRAKER.receive_json()

                Data_Printer = self._parse_data(WebSocket_DataJson)

                if self.__DEBUG_MODE == 1: print(f"DEBUG Температура стола: {self.__Heater_Bed_Temperature}\r\n[*] Температура сопла: {self.__Extruder_Temperature}\r\n[*] Прогресс: {self.__Progress}%\r\n")

            except aiohttp.ClientConnectionClosedError:
                self.__WB_API_MOONRAKER = await self.__MoonrakerWebSocket.ws_connect(f"ws://{self.__IP_SERVER_MOONRAKER}/websocket?token={await self._Get_WebSocket_Token()}")
                
    def GetTemp_Extruder(self):
        return self.__Extruder_Temperature
        
    def GetTemp_HeaterBed(self):
        return self.__Heater_Bed_Temperature
        
    def GetProgress(self):
        return self.__Progress
        
    def SetName_Cfg(self, name_cfg):
        self.__cfg_name = name_cfg
        
        self.__IP_SERVER_MOONRAKER = self._GetPARAM_CFG("IP_ADDR_SERVER")
        self.__LOGIN_MOONRAKER = self._GetPARAM_CFG("LOGIN_MOONRAKER")
        self.__PASSWORD_MOONRAKER = self._GetPARAM_CFG("PASSWORD_MOONRAKER")
        
        