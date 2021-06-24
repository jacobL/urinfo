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
//var ssoUrl = "http://10.55.8.137/SSO"; //ID 136

var currentPath = window.location.href;
var query = window.location.search.substring(1);
var qs = parse_query_string(query);
var userChineseName = '';
var PERNR = '';
//SSO 取得User資料
if (qs['userChineseName'] !== undefined){ 
	userChineseName = qs['userChineseName'];
	PERNR = qs['PERNR'];
	CSTEXT = qs['CSTEXT']; //職稱
	GENDER = qs['GENDER']; //性別
	R = qs['R']; //
	console.log(userChineseName+' '+PERNR)
	//var params = 'url='+location.protocol + '//' + location.host + location.pathname+'&PERNR='+PERNR+'&userChineseName='+userChineseName+'&CSTEXT='+CSTEXT//encodeURIComponent(CSTEXT);
	//alert(ssoUrl+' '+userChineseName)
	tag = ''
	if(currentPath.split('#')[1] !== undefined) tag = '#'+currentPath.split('#')[1];
	window.history.replaceState({}, document.title, window.location.pathname+tag);
	
	/*
	//SSO Log
	var http = new XMLHttpRequest();
	//var url = 'http://pc89600059495s:34088/sso_log';
	var url = 'http://10.55.8.137/SSO_log';
	
	http.open('POST', url, true);
	http.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');	 
	http.send(params); 
	*/
}else{
	rand = Math.random();
	window.location.href = ssoUrl+"?rand="+rand+"&redirectUrl="+currentPath;
	setTimeout(function(){console.log('SSO未取得工號');},30000);
}