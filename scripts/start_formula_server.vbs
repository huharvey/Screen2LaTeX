Set shell = CreateObject("WScript.Shell")

shell.CurrentDirectory = "E:\Tools\UniMERNet"

shell.Run _
    """D:\deeplearning\envs\unimernet\pythonw.exe"" ""E:\Tools\UniMERNet\formula_server.py""", _
    0, _
    False

Set shell = Nothing