Set ws = CreateObject("WScript.Shell")
ws.CurrentDirectory = "C:\projects\personal\scibot.telegram"
ws.Run """C:\Users\Alexander Bone\AppData\Local\Programs\Python\Python313\pythonw.exe"" telegram_bot.py", 0, False
