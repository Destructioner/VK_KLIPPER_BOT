import asyncio
from vk_api_tera import TeraVkClient
from moonraker_api_tera import TeraMoonrakerClient
import time
import os


MOONRAKER_CFG = "moonraker_vk.cfg"
DEBUG = 1


DataMetrics = ""

async def VK_BOT_TERA():
    global MOONRAKER_CFG
    global DataMetrics
    
    
    VkBot = TeraVkClient()
    VkBot.SetName_Cfg(MOONRAKER_CFG)
    
    Message_Update_id = await VkBot.initClient()
    
    if "ERROR" in Message_Update_id:
        print(Message_Update_id)
        return
        

    while True:
        await VkBot.editMessage(DataMetrics, Message_Update_id)
        print("[+] VK ДАННЫЕ ОБНОВЛЕНЫ")
        await asyncio.sleep(4.5)


async def MoonrakerBot_Tera():
    global MOONRAKER_CFG
    global DataMetrics
       
    MoonrakerWork = TeraMoonrakerClient(DEBUG)
    MoonrakerWork.SetName_Cfg(MOONRAKER_CFG)
    PROGRESS_PRC = int(MoonrakerWork._GetPARAM_CFG("PROGRESS_PRC"))

    
    if await MoonrakerWork.connect_moonraker() is not None:
        
        while True:
            await MoonrakerWork.update_metrics()
            
            Progress_Moonraker = MoonrakerWork.GetProgress()
            Progress_Bar = "[" + ("█" * int((Progress_Moonraker / 100) * PROGRESS_PRC)) + ("░" * int(PROGRESS_PRC - (Progress_Moonraker / 100) * PROGRESS_PRC)) + "]"
            
            DataMetrics = f"Температура стола: {MoonrakerWork.GetTemp_HeaterBed()}\nТемпература сопла: {MoonrakerWork.GetTemp_Extruder()}\r\nПрогресс: {Progress_Moonraker}%\r\n{Progress_Bar}"
            await asyncio.sleep(3)
    



async def Work_ClientBot():
    VkTera = asyncio.create_task(VK_BOT_TERA())
    MoonrakerTera = asyncio.create_task(MoonrakerBot_Tera())
    
    await asyncio.gather(VkTera, MoonrakerTera)
    
asyncio.run(Work_ClientBot())


