import asyncio
from vk_api_tera import TeraVkClient
from moonraker_api_tera import TeraMoonrakerClient
import time
import os

MOONRAKER_CFG = "moonraker_vk.cfg"
DEBUG = 1


DataMetrics = ""
JPG_Snapshot_Stream = bytes(b"")


async def VK_BOT_TERA():
    global MOONRAKER_CFG
    global DataMetrics
    global JPG_Snapshot_Stream
    
    
    VkBot = TeraVkClient()
    VkBot.SetName_Cfg(MOONRAKER_CFG)
    
    Message_Update_id = await VkBot.initClient()
    
    if "ERROR" in Message_Update_id:
        print(Message_Update_id)
        return
        

    while True:
        if len(JPG_Snapshot_Stream) != 0:
            AttachFrame = await VkBot.sendPhoto(JPG_Snapshot_Stream)
            await VkBot.editMessage(DataMetrics, Message_Update_id, AttachFrame)
            
        else:
            await VkBot.editMessage(DataMetrics, Message_Update_id, b"")
        
        print("[+] VK ДАННЫЕ ОБНОВЛЕНЫ")
        print(f"[P] Длина изображения: {len(JPG_Snapshot_Stream)}")
        await asyncio.sleep(5.5)


async def MoonrakerBot_Tera():
    global MOONRAKER_CFG
    global DataMetrics
    global JPG_Snapshot_Stream
    
    MoonrakerWork = TeraMoonrakerClient(DEBUG)
    MoonrakerWork.SetName_Cfg(MOONRAKER_CFG)
    PROGRESS_PRC = int(MoonrakerWork._GetPARAM_CFG("PROGRESS_PRC"))

    
    if await MoonrakerWork.connect_moonraker() is not None:
        
        while True:
            await MoonrakerWork.update()
            
            Progress_Moonraker = MoonrakerWork.GetProgress()
            Progress_Bar = "[" + ("█" * int((Progress_Moonraker / 100) * PROGRESS_PRC)) + ("░" * int(PROGRESS_PRC - (Progress_Moonraker / 100) * PROGRESS_PRC)) + "]"
            
            DataMetrics = f"Температура стола: {MoonrakerWork.GetTemp_HeaterBed()}\nТемпература сопла: {MoonrakerWork.GetTemp_Extruder()}\r\nПрогресс: {Progress_Moonraker}%\r\n{Progress_Bar}"
            JPG_Snapshot_Stream = MoonrakerWork.GetFrame_Camera()
            
                
            await asyncio.sleep(3)
    



async def Work_ClientBot():
    VkTera = asyncio.create_task(VK_BOT_TERA())
    MoonrakerTera = asyncio.create_task(MoonrakerBot_Tera())
    
    await asyncio.gather(VkTera, MoonrakerTera)
    
asyncio.run(Work_ClientBot())


