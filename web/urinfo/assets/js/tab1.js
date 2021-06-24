am4core.ready(function() {

// Themes begin
am4core.useTheme(am4themes_animated);
// Themes end

/**
 * Create container for charts
 */
var container = am4core.create("chartdiv1", am4core.Container);
container.width = am4core.percent(100);
container.height = am4core.percent(100);
container.layout = "horizontal";

/**
 * Population pyramid chart
 */

var pyramidChart = container.createChild(am4charts.XYChart);
//chart.logo.height = -150000; 
pyramidChart.cursor = new am4charts.XYCursor();
pyramidChart.cursor.behavior = "none";
//pyramidChart.arrangeTooltips = false;

pyramidChart.numberFormatter.numberFormat = "#,###.#a";
pyramidChart.numberFormatter.bigNumberPrefixes = [
  { "number": 1e+3, "suffix": "M" }
];

pyramidChart.dataSource.url = "https://s3-us-west-2.amazonaws.com/s.cdpn.io/t-160/un_population_age_groups.csv";
pyramidChart.dataSource.parser = new am4core.CSVParser();
pyramidChart.dataSource.parser.options.numberFields = ["col5", "col6", "col7"];
pyramidChart.dataSource.events.on("parseended", function(ev) {
  sourceData = ev.target.data;
  ev.target.data = getCurrentData();
});

function getCurrentData() {
  var currentData = [];
  am4core.array.each(sourceData, function(row, i) {
    if (row.col3 == currentYear) {
      currentData.push(row);
    }
  });
  currentData.sort(function(a, b) {
    var a1 = Number(a.col4.replace(/[^0-9]+.*$/, ""));
    var b1 = Number(b.col4.replace(/[^0-9]+.*$/, ""));
    if (a1 > b1) {
      return 1;
    }
    else if (a1 < b1) {
      return -1;
    }
    return 0;
  });
  return currentData;
}

function updateData() {
  var data = getCurrentData();
  if (data.length == 0) {
    return;
  }
  am4core.array.each(pyramidChart.data, function(row, i) {
    if (!data[i]) {
      pyramidChart.data[i].col5 = 0;
      pyramidChart.data[i].col6 = 0;
    }
    else {
      pyramidChart.data[i].col5 = data[i].col5;
      pyramidChart.data[i].col6 = data[i].col6;
    }
  });
  pyramidChart.invalidateRawData();
  
  // Set title
  pyramidChart.titles.getIndex(0).text = currentYear;
}

// An adapter which filters data for the current year
var currentYear = new Date().getFullYear().toString();
var sourceData = [];

var pyramidXAxisMale = pyramidChart.xAxes.push(new am4charts.ValueAxis());
pyramidXAxisMale.min = 0;
pyramidXAxisMale.max = 20000;
pyramidXAxisMale.strictMinMax = true;

var maleRange = pyramidXAxisMale.axisRanges.create();
maleRange.value = 0;
maleRange.endValue = 20000;
maleRange.label.text = "Males";
maleRange.label.inside = true;
maleRange.label.valign = "top";
maleRange.label.fontSize = 20;
maleRange.label.fill = pyramidChart.colors.getIndex(0);

var pyramidXAxisFemale = pyramidChart.xAxes.push(new am4charts.ValueAxis());
pyramidXAxisFemale.min = 0;
pyramidXAxisFemale.max = 20000;
pyramidXAxisFemale.renderer.inversed = true;
pyramidXAxisFemale.strictMinMax = true;

var maleRange = pyramidXAxisFemale.axisRanges.create();
maleRange.value = 0;
maleRange.endValue = 20000;
maleRange.label.text = "Females";
maleRange.label.inside = true;
maleRange.label.valign = "top";
maleRange.label.fontSize = 20;
maleRange.label.fill = pyramidChart.colors.getIndex(1);

pyramidChart.bottomAxesContainer.layout = "horizontal";

var pyramidYAxis = pyramidChart.yAxes.push(new am4charts.CategoryAxis());
pyramidYAxis.dataFields.category = "col4";
pyramidYAxis.renderer.minGridDistance = 10;
pyramidYAxis.renderer.grid.template.location = 0;
pyramidYAxis.renderer.inside = true;
pyramidYAxis.title.text = "Age groups";
pyramidYAxis.renderer.labels.template.adapter.add("textOutput", function(text, target) {
  if (text == "80-84") {
    text += "*";
  }
  return text;
});

var pyramidSeriesMale = pyramidChart.series.push(new am4charts.ColumnSeries());
pyramidSeriesMale.dataFields.categoryY = "col4";
pyramidSeriesMale.dataFields.valueX = "col5";
pyramidSeriesMale.tooltipText = "{valueX}";
pyramidSeriesMale.name = "Male";
pyramidSeriesMale.xAxis = pyramidXAxisMale;
pyramidSeriesMale.clustered = false;
pyramidSeriesMale.columns.template.strokeOpacity = 0;

var pyramidSeriesFemale = pyramidChart.series.push(new am4charts.ColumnSeries());
pyramidSeriesFemale.dataFields.categoryY = "col4";
pyramidSeriesFemale.dataFields.valueX = "col6";
pyramidSeriesFemale.tooltipText = "{valueX}";
pyramidSeriesFemale.name = "Female";
pyramidSeriesFemale.xAxis = pyramidXAxisFemale;
pyramidSeriesFemale.clustered = false;
pyramidSeriesFemale.columns.template.strokeOpacity = 0;

var pyramidTitle = pyramidChart.titles.create();
pyramidTitle.text = currentYear;
pyramidTitle.fontSize = 20;
pyramidTitle.marginBottom = 22;

var note = pyramidChart.tooltipContainer.createChild(am4core.Label);
note.text = "* Until 1990 U.S. did not collect detailed age stats for persons above 80. For years prior to 1990 this category represents all 80+ persons."
note.fontSize = 10;
note.valign = "bottom";
note.align = "center";

/**
 * Create population chart
 */
var popChart = container.createChild(am4charts.XYChart);
popChart.marginLeft = 15;
popChart.data = [{}];

var popSubtitle = popChart.titles.create();
popSubtitle.text = "(hover to see breakdown)";

var popTitle = popChart.titles.create();
popTitle.text = "U.S. population";
popTitle.fontSize = 20;

popChart.numberFormatter.numberFormat = "#,###.#a";
popChart.numberFormatter.bigNumberPrefixes = [
  { "number": 1e+3, "suffix": "M" }
];

popChart.dateFormatter.dateFormat = "yyyy";

var popXAxis = popChart.xAxes.push(new am4charts.DateAxis());
popXAxis.renderer.minGridDistance = 40;

var popYAxis = popChart.yAxes.push(new am4charts.ValueAxis());
popYAxis.renderer.opposite = true;

var popSeriesMale = popChart.series.push(new am4charts.LineSeries());
popSeriesMale.dataFields.dateX = "col3";
popSeriesMale.dataFields.valueY = "col4";
popSeriesMale.propertyFields.strokeDasharray = "dash";
popSeriesMale.propertyFields.fillOpacity = "opacity";
popSeriesMale.stacked = true;
popSeriesMale.strokeWidth = 2;
popSeriesMale.fillOpacity = 0.5;
popSeriesMale.name = "Male";

var popSeriesFemale = popChart.series.push(new am4charts.LineSeries());
popSeriesFemale.dataFields.dateX = "col3";
popSeriesFemale.dataFields.valueY = "col5";
popSeriesFemale.propertyFields.strokeDasharray = "dash";
popSeriesFemale.propertyFields.fillOpacity = "opacity";
popSeriesFemale.stacked = true;
popSeriesFemale.strokeWidth = 2;
popSeriesFemale.fillOpacity = 0.5;
popSeriesFemale.tooltipText = "[bold]U.S. population in {dateX}[/]\n[font-size: 20]Male: {col4}\nFemale: {col5}";
popSeriesFemale.name = "Female";

popChart.dataSource.url = "https://s3-us-west-2.amazonaws.com/s.cdpn.io/t-160/un_population.csv";
popChart.dataSource.parser = new am4core.CSVParser();
popChart.dataSource.parser.options.numberFields = ["col4", "col5", "col6"];
popChart.dataSource.adapter.add("parsedData", function(data) {
  am4core.array.each(data, function(item) {
    if (item.col3.getFullYear() == currentYear) {
      item.dash = "3,3";
      item.opacity = 0.3;
    }
  });
  return data;
});

popChart.cursor = new am4charts.XYCursor();
popChart.snapToSeries = popSeriesFemale;
popChart.cursor.events.on("cursorpositionchanged", function(ev) {
  currentYear = popXAxis.positionToDate(popXAxis.toAxisPosition(ev.target.xPosition)).getFullYear().toString();
  updateData();
});

popChart.cursor.events.on("hidden", function(ev) {
  var currentYear = new Date().getFullYear().toString();
  updateData();
});

}); // end am4core.ready()

am4core.ready(function() {

// Themes begin
am4core.useTheme(am4themes_animated);
// Themes end

var data = {
	"asahi":{"business":982,"economy":1021,"politics":1233,"tech":876,"health":231,"covid-19":123,"travel":32},
	"cnn":{"business":876,"economy":1344,"politics":1211,"tech":567,"health":121,"covid-19":56,"travel":67},
	"dailymail":{"business":1254,"economy":1098,"politics":987,"tech":342,"health":78,"covid-19":89,"travel":33},
	"mainichi":{"business":2111,"economy":1232,"politics":1222,"tech":456,"health":321,"covid-19":123,"travel":44},
	"nytimes":{"business":2133,"economy":2133,"politics":1211,"tech":454,"health":245,"covid-19":321,"travel":90},
	"thesun":{"business":4533,"economy":1233,"politics":543,"tech":1300,"health":432,"covid-19":123,"travel":113},
	"usatoday":{"business":4321,"economy":2311,"politics":2356,"tech":1211,"health":987,"covid-19":234,"travel":543},
	"wsj":{"business":3212,"economy":3421,"politics":2768,"tech":1399,"health":675,"covid-19":234,"travel":198},
	"yomiuri":{"business":1345,"economy":321,"politics":1098,"tech":234,"health":654,"covid-19":188,"travel":30}}

function processData(data) {
    var treeData = [];

    var smallBrands = { name: "Other", children: [] };

    for (var brand in data) {
        var brandData = { name: brand, children: [] }
        var brandTotal = 0;
        for (var model in data[brand]) {
            brandTotal += data[brand][model];
        }

        for (var model in data[brand]) {
            // do not add very small
            if (data[brand][model] > 100) {
                brandData.children.push({ name: model, count: data[brand][model] });
            }
        }

        // only bigger brands
        if (brandTotal > 2000) {
            treeData.push(brandData);
        }
    }

    return treeData;
}

// create chart
var chart = am4core.create("chartdiv", am4charts.TreeMap);
chart.logo.height = -150000; 
chart.padding(0,0,0,0);
chart.hiddenState.properties.opacity = 0; // this makes initial fade in effect

// only one level visible initially
chart.maxLevels = 2;
// define data fields
chart.dataFields.value = "count";
chart.dataFields.name = "name";
chart.dataFields.children = "children";
chart.homeText = "各網站資料分布";

// enable navigation
chart.navigationBar = new am4charts.NavigationBar();
chart.zoomable = false;

// level 0 series template
var level0SeriesTemplate = chart.seriesTemplates.create("0");
level0SeriesTemplate.strokeWidth = 2;

// by default only current level series bullets are visible, but as we need brand bullets to be visible all the time, we modify it's hidden state
level0SeriesTemplate.bulletsContainer.hiddenState.properties.opacity = 1;
level0SeriesTemplate.bulletsContainer.hiddenState.properties.visible = true;
// create hover state
var columnTemplate = level0SeriesTemplate.columns.template;
var hoverState = columnTemplate.states.create("hover");

// darken
hoverState.adapter.add("fill", function (fill, target) {
    if (fill instanceof am4core.Color) {
        return am4core.color(am4core.colors.brighten(fill.rgb, -0.2));
    }
    return fill;
})

// add logo
var image = columnTemplate.createChild(am4core.Image);
image.opacity = 0.15;
image.align = "center";
image.valign = "middle";
image.width = am4core.percent(80);
image.height = am4core.percent(80);

// add adapter for href to load correct image
image.adapter.add("href", function (href, target) {
    var dataItem = target.parent.dataItem;
    if (dataItem) {
        //return "https://www.amcharts.com/lib/images/logos/" + dataItem.treeMapDataItem.name.toLowerCase() + ".png";
		return "assets/img/logos/" + dataItem.treeMapDataItem.name.toLowerCase() +".png";
    }
});

// level1 series template
var level1SeriesTemplate = chart.seriesTemplates.create("1");
level1SeriesTemplate.columns.template.fillOpacity = 0;
level1SeriesTemplate.columns.template.strokeOpacity = 0.4;

var bullet1 = level1SeriesTemplate.bullets.push(new am4charts.LabelBullet());
bullet1.locationX = 0.5;
bullet1.locationY = 0.5;
bullet1.label.text = "{name}";
bullet1.label.fill = am4core.color("#ffffff");
bullet1.label.fontSize = 9;
bullet1.label.fillOpacity = 0.7;

chart.data = processData(data);

}); // end am4core.ready()
