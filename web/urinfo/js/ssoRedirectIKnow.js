function parse_query_string(query) {
  var vars = query.split("&");
  var query_string = {};
  for (var i = 0; i < vars.length; i++) {
	var pair = vars[i].split("=");
	var key = decodeURIComponent(pair[0]);
	var value = decodeURIComponent(pair[1]);
	if (typeof query_string[key] === "undefined") {
	  query_string[key] = decodeURIComponent(value);
	} else if (typeof query_string[key] === "string") {
	  var arr = [query_string[key], decodeURIComponent(value)];
	  query_string[key] = arr;
	} else {
	  query_string[key].push(decodeURIComponent(value));
	}
  }
  return query_string;
}

var ssoUrl = "http://10.55.8.136:2400/api/SSO"; //ID 136
var currentPath = window.location.href;
var query = window.location.search.substring(1);
var qs = parse_query_string(query);
//SSO 取得User資料
var helloContent = '';

//userChineseName='梁均銘'
//PERNR=18017220
//GENDER=1

if (qs['userChineseName'] !== undefined){ // SSO已取得工號	
	userChineseName = qs['userChineseName'];
	PERNR = qs['PERNR']; //工號
	GENDER = qs['GENDER']; //性別
	CSTEXT = qs['CSTEXT']; //職稱	 	 
	tag = ''
	if(currentPath.split('#')[1] !== undefined) tag = '#'+currentPath.split('#')[1];
	window.history.replaceState({}, document.title, window.location.pathname+tag);
}else{ // SSO未取得工號
	//window.location.href = ssoUrl+"?redirectUrl="+currentPath;	
	rand = Math.random();
	window.location.href = ssoUrl+"?rand="+rand+"&redirectUrl="+currentPath;
	setTimeout(function(){console.log('SSO未取得工號');},30000);
}