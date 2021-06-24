

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

var authorLevel = 1;
var ssoUrl = "http://10.55.8.136:2400/api/SSO"; //ID 136
//var ssoUrl = "http://10.55.8.137/SSO"; //ID 136
var currentPath = window.location.href;
var query = window.location.search.substring(1);
var qs = parse_query_string(query);
//SSO 取得User資料
/* 20200722
//RQM
10016034	JOYCE.CHENG	鄭淑燕
18025683	SHAN33.LEE	李蔚杉
20001546	ANNIE.TUNG	童于真
10019039	SIMON.CHUNG	鍾鳴遠
10007902	JUNHONG.CHEN	陳俊宏
10002451	JH.LIAO	廖健宏

//ID
12022032	KT.TSAO	蔡光庭
18017220	JACOB.LIANG	梁均銘
14039729    盧秉佑 
08000866    許家豪 
10009521    張幼銘 
*/
if (qs['userChineseName'] !== undefined){ 
	userChineseName = qs['userChineseName'];
	PERNR = qs['PERNR'];
	CSTEXT = qs['CSTEXT']; //職稱
	console.log(userChineseName+' '+PERNR);
	if (['10016034','18025683','20001546','10019039','10007902','10002451','12022032','18017220','14039729','08000866','10009521'].indexOf(PERNR) >= 0) {
		authorLevel = 0;
	}	
	window.history.replaceState({}, document.title, window.location.pathname); 
	var params = 'url='+location.protocol + '//' + location.host + location.pathname+'&PERNR='+PERNR+'&userChineseName='+userChineseName+'&CSTEXT='+CSTEXT//encodeURIComponent(CSTEXT);
		 
	//SSO Log
	var http = new XMLHttpRequest();
	//var url = 'http://pc89600059495s:34088/sso_log';
	var url = 'http://10.55.8.137/SSO_log';
	http.open('POST', url, true);
	http.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');	 
	http.send(params); 
}else{
	window.location.href = ssoUrl+"?redirectUrl="+currentPath;
	setTimeout(function(){console.log('SSO未取得工號');},30000);
}