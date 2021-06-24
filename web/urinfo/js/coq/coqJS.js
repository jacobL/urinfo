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
 

function changeGraph(graph){  
	//logit("changeGraph",graph);
	//saveLog();
	var ym_end = $("#ym_end").html();	
	var app = $("#app").html();
	
	// 	CoQ 系列 ====================================================
	if(graph == 'BU月圖'){
		window.location.replace("bu.htm");
	}else if(graph == 'Tableau'){
		window.location.replace("tableau.htm");
	//}else if(graph == 'OU月圖'){
	//	window.location.replace("ou.htm?ym_end="+ym_end);
	}else if(graph == '預計損失圖'){
		//window.location.replace("aerb.htm?app="+app+"&ym_end="+ym_end);
		window.location.replace("aerb.htm");
	}else if(graph == '年度趨勢圖(By類別)'){
		//window.location.replace("year.htm?app="+app+"&ym_end="+ym_end);
		window.location.replace("year.htm");
	}else if(graph == '3D年度趨勢圖'){
		window.location.replace("buyear.htm");
	}else if(graph == '3D年度CoQ Rate趨勢圖'){
		window.location.replace("buyearRate.htm");
	}else if(graph == '3D年度m2趨勢圖'){
		window.location.replace("buyearM2.htm");
	}else if(graph == 'BU月累計圖'){
		//window.location.replace("accumulation_new.htm?app="+app);
		window.location.replace("accumulation_new.htm");
		
	// 	m2CoPQ 系列 ====================================================
	                    
	}else if(graph == 'M2 CoPQ月累計圖'){
		window.location.replace("m2CoPQ_accumulation.htm");
	}else if(graph == '3D年度m2趨勢圖'){
		window.location.replace("buyearM2.htm");
	}else if(graph == 'CoPQ BU月圖'){
		window.location.replace("m2CoPQ.htm");
		
	// 	RMA m2CoPQ 系列 ====================================================	
	}else if(graph == 'CoPQ BU月累計圖'){
		window.location.replace("accumulation_ActAchievement.htm");
	}else if(graph == 'CoPQ BU評核'){
		window.location.replace("accumulation_xy.htm");		
	}else if(graph == 'CoPQ 補充說明'){ // 20210401 Joyce
		window.location.replace("editCoPQComment_ActAchievement.htm");	
	// 	採購情報守門員 系列 20201118 ====================================================	
	}else if(graph == '事件對接'){
		window.location.replace("event1.htm");
	}else if(graph == '事件篩選'){
		window.location.replace("event0.htm");
	}
}

function GetFilename(url){
   if (url)
   {
      var m = url.toString().match(/.*\/(.+?)\./);
      if (m && m.length > 1)
      {
         return m[1];
      }
   }
   return "";
}