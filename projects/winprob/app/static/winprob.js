// TODO: Move all the styling to CSS

var margin = {
    top: 40,
    right: 10,
    bottom: 80,
    left: 40
};
var width = 720 - margin.left - margin.right,
height = 300 - margin.top - margin.bottom;


var svg_outer = d3.select("#plot").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom);

var svg = svg_outer.append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
    .attr("class", "winprob");


var formatAsPercentage = d3.format(".0%");
var max_timestamp = Math.round((winprob_line.length + 5)/ 10) * 10;
var xScale = d3.scale.linear()
    .domain([0, max_timestamp])
    .range([0, width]);

var yScale = d3.scale.linear()
    .domain([0, 1])
    .range([height, 0]);



var lines = svg.selectAll("line")
    .data(winprob_line)
    .enter()
    .append("line");

var lineAttributes = lines.attr("x1", function (d) {
    return xScale(d.timestamp - 1);
})
    .attr("x2", function (d) {
        return xScale(d.timestamp);
    })
    .attr("y1", function (d) {
        return yScale(d.winprob_before);
    })
    .attr("y2", function (d) {
        return yScale(d.winprob_now);
    })
    .style("stroke", "rgb(218,165,32)")
    .style("stroke-width", "4")

// Create invisible overlay
var rects = svg.selectAll("rect")
    .data(winprob_line)
    .enter().append("svg:rect")
    .attr("x", function(d) {return xScale(d.timestamp - 1)})
    .attr("y", yScale(1))
    .attr("width", xScale(1))
    .attr("height", height)
    .attr("opacity", 0)
    .attr("background", "red")


// Tooltip for diyplaying more informations
var tooltip = svg.append("div")
    .attr("class", "tooltip")
    .style("opacity", 0);

var eventbox = d3.select(".eventbox")

var rectsMouse = rects.on("mouseover", function(d) {
    d3.select(d3.event.target).classed("highlight", true);
    tooltip.transition()
        .style("opacity", .9);
    tooltip.html("Minute : " + d.timestamp + "<br/>"  + d.close)
        .style("left", (d3.event.pageX) + "px")
        .style("top", (d3.event.pageY - 28) + "px");
    eventbox.html("Minute: " + d.timestamp + "</br> Winchance change from </br>" + Math.round(d.winprob_before * 100) +  "% to " + Math.round(d.winprob_now * 100) + "%")
 })
     .on("mouseout", function(d) {
	 d3.select(d3.event.target).classed("highlight", false);
        tooltip.transition()
            .style("opacity", 0);
    });


//Create the Axis
var xAxis = d3.svg.axis().scale(xScale).orient("bottom").ticks(5);
var xAxisGroup = svg.append("g")
    .attr("class", "axis")
    .attr("transform", "translate(0," + height + ")")
    .call(xAxis);


var yPadding = 0;
var n_y_ticks = 3;
var yAxis = d3.svg.axis().scale(yScale).orient("left").ticks(n_y_ticks).tickFormat(formatAsPercentage);


var yAxisGroup = svg.append("g")
    .attr("class", "axis")
    .attr("transform", "translate(" + yPadding + ",0)")
    .attr("stroke-width", "1px")
    .call(yAxis);


svg.selectAll("line.horizontalGrid").data(yScale.ticks(2)).enter()
    .append("line")
    .attr({
        "class": "horizontalGrid",
        "x1": 0,
        "x2": width,
        "y1": function (d) {
            return yScale(d);
        },
        "y2": function (d) {
            return yScale(d);
        },
        "fill": "none",
        "shape-rendering": "crispEdges",
        "stroke": "black",
        "stroke-width": "1px",
        "stroke-dasharray": "2, 2"
    });

svg.selectAll("line.vertcialGrid").data(xScale.ticks(5)).enter()
    .append("line")
    .attr({
        "class": "verticalGrid",
        "y1": 0,
        "y2": height,
        "x1": function (d) {
            return xScale(d);
        },
        "x2": function (d) {
            return xScale(d);
        },
        "fill": "none",
        "shape-rendering": "crispEdges",
        "stroke": "black",
        "stroke-width": "1px",
        "stroke-dasharray": "2, 2"
    });

// Add plot title
svg.append("text")
    .attr("x", (width / 2))
    .attr("y",  0 - (margin.top / 2))
    .attr("text-anchor", "middle")
    .attr("fill", "#d3d3d3")
    .style("font-size", "16px")
    .text("Win chance during match")

svg.append("text")
    .attr("x", (width / 2))
    .attr("y", height + margin.bottom/2)
    .attr("text-anchor", "middle")
    .attr("fill", "lightgrey")
    .style("font-size", "16px")
    .text("Match minutes");
