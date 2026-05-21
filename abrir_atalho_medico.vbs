Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

appDir = fso.GetParentFolderName(WScript.ScriptFullName)
pythonw = "C:\Users\zauli\anaconda3\pythonw.exe"
mainPy = fso.BuildPath(appDir, "main.py")

If Not fso.FileExists(pythonw) Then
  MsgBox "Python sem terminal nao foi encontrado em:" & vbCrLf & pythonw, vbExclamation, "Atalho Medico"
  WScript.Quit 1
End If

shell.CurrentDirectory = appDir
shell.Run """" & pythonw & """ """ & mainPy & """", 0, False
