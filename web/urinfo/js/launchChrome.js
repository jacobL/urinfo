if (document.all) launchChrome();

function launchChrome() {
                     
  var ws = null;
  var username = "";
  var isLaunchChrome = false;
  
  try {
    ws = new ActiveXObject("WScript.Shell");
    var wshNetwork = new ActiveXObject("WScript.Network");
    username = wshNetwork.UserName;
  }
  catch(e) {
    
    alert(
      " 請將 " + location.protocol + "//" + location.hostname + 
      " 加入IE的信任網站清單。\\r\\n (" + e.description + ")"
    );
    
    window.open("", "_self", "");
    window.close();
    
    return;
  }
                     
  var chromePathList = [
    "C:/Program Files/Google/Chrome/Application/chrome.exe",
    "C:/Documents and Settings/All Users/Application Data/WinNexus/WPD/GoogleChrome/GoogleChromePortable.exe",
    "C:/ProgramData/WinNexus/WPD/GoogleChrome/GoogleChromePortable.exe",
    "C:/Users/" + username + "/AppData/Local/Google/Chrome/Application/chrome.exe",
    "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
  ];

  for (var i in chromePathList) {
    try {
      ws.Exec(chromePathList[i] + " " + location.href);
      isLaunchChrome = true;
      break;
    }
    catch (e) {
    }
  }
  
  if (isLaunchChrome) {
    window.open("", "_self", "");
    window.close();
  }
  else if (confirm("Cannot launch Chrome for you. Would you install Chrome now?")) {
    window.location.href = "http://servicemap.cminl.oa/Backend/winnexus.htm";
  }
}