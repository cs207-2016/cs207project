$(document).ready(function () {
    $("input[name=paramgroup]:radio").change(function () {
        $(".dynamic-vals").remove();
        var paramValue = $("#param-value");
        if ($(this).val() == "mean" || $(this).val() == "std" || $(this).val() == "blarg"){
            paramValue.append("<div class='dynamic-vals'>Lower Bound:<br /><input type='number' id='lower' /><br /></div>");
            paramValue.append("<div class='dynamic-vals'>Upper Bound:<br /><input type='number' id='upper' /></div>");
        }
        else if ($(this).val() == "level") {
            paramValue.append("<div class='dynamic-vals'>Categories:<br /><input type='string' id='categories' /></div>");
        }
        else {
            paramValue.append("<div class='dynamic-vals'>None</div>");
        }
    });

    $("#submit-form").on("submit", function(e){
        e.preventDefault();
        var url = "/timeseries";
        var paramSelection = $("input:radio[name='paramgroup']:checked");
        if (paramSelection.val() == "mean"){
            url += "?mean_in="
        }
        else if (paramSelection.val() == "std"){
            url += "?std_in="
        }
        else if (paramSelection.val() == "blarg"){
            url += "?blarg_in="
        }
        else if (paramSelection.val() == "level"){
            url += "?level_in="
        }

        if (paramSelection.val() == "mean" || paramSelection.val() == "std" || paramSelection.val() == "blarg"){
            url += $("#lower").val() + "-" + $("#upper").val();
        }
        else if (paramSelection.val() == "level") {
            url += $("#categories").val();
        }

        $.get(url, function(data){
            var table = $("#select-series");
            $("#select-series tr").remove();
            table.append("<tr><td>ID</td><td>Mean</td><td>Standard Dev</td><td>Level</td><td>Blarg</td></tr>")
            for(var i = 0; i < data.timeseries.length; ++i){
                var timeseriesEntry = data.timeseries[i];
                var element = "<tr>";
                element += "<td>" + timeseriesEntry.id + "</td>";
                element += "<td>" + timeseriesEntry.mean + "</td>";
                element += "<td>" + timeseriesEntry.std + "</td>";
                element += "<td>" + timeseriesEntry.level + "</td>";
                element += "<td>" + timeseriesEntry.blarg + "</td>";
                element += "<td><button type='button' onclick='visualizeID(" + timeseriesEntry.id;
                element += ")' id='viz" + timeseriesEntry.id + "'>Visualize</button></td>";
                element += "</tr>";
                table.append(element);
            }
        })
    });

    $("#generate-random").click(function(){
        var time_points = [];
        var data_points = [];
        for(var i = 0; i < 100; ++i){
            time_points.push(i / 10);
            data_points.push(Math.random() * 10);
        }
        var payload = JSON.stringify({"time_points": time_points, "data_points": data_points});
        $.ajax({url:"/timeseries", type:"POST", data:payload, contentType:"application/json"})
            .done(function(msg){
                visualizeID(msg.id);
            });
    });

    $("#upload-button").click(function(){
        var files = $("#file-select").prop("files");
        if (files.length <= 0){
            return false;
        }

        var fReader = new FileReader();
        fReader.onload = function(e){
            var result = JSON.parse(e.target.result);
            $.ajax({url:"/timeseries", type:"POST", data:JSON.stringify(result), contentType:"application/json"})
            .done(function(msg){
                visualizeID(msg.id);
            });
        };

        fReader.readAsText(files.item(0));
    });

    $("#similar-button").click(function(){
        var files = $("#file-select").prop("files");
        if (files.length <= 0){
            return false;
        }

        var fReader = new FileReader();
        fReader.onload = function(e){
            var result = JSON.parse(e.target.result);
            visualize(undefined, d3.select("#selected-timeseries"), result);
            $.ajax({url:"/simquery", type:"POST", data:JSON.stringify(result), contentType:"application/json"})
            .done(function(msg){
                for(var i = 0; i < msg.similar_ids.length && i < 5; ++i){
                    visualize(msg.similar_ids[i], d3.select("#similar-timeseries-"+(i+1)));
                }
            });
        };

        fReader.readAsText(files.item(0));
    });
});

function visualizeID(id){
    var svg = d3.select("#selected-timeseries");
    visualize(id, svg);
    $.get("/simquery?id="+id, function(data){
        for(var i = 0; i < data.similar_ids.length && i < 5; ++i){
            visualize(data.similar_ids[i], d3.select("#similar-timeseries-"+(i+1)));
        }
    });
}

function visualize(id, svg, preData){
    svg.selectAll("*").remove();

    var margin = {top: 30, right: 20, bottom:30, left:30};
    var width = svg.attr("width") - margin.left - margin.right;
    var height = svg.attr("height") - margin.top - margin.bottom;

    var x = d3.scale.linear().range([0, width]);
    var y = d3.scale.linear().range([height, 0]);

    var xAxis = d3.svg.axis().scale(x).orient("bottom").ticks(10);
    var yAxis = d3.svg.axis().scale(y).orient("left").ticks(5);

    var valueline = d3.svg.line()
        .x(function(d){ return x(d.time);})
        .y(function(d){ return y(d.value);});

    var g = svg.append("g").attr("transform","translate("+margin.left+","+margin.top+")");

    function updateWithJSON(data){
        var dataObjs = [];
        for(var i = 0; i < data.time_points.length; ++i){
            var newObj = {time:data.time_points[i], value:data.data_points[i]};
            dataObjs.push(newObj);
        }
        x.domain(d3.extent(dataObjs, function(d){ return d.time;}));
        y.domain([0, d3.max(dataObjs, function(d){ return d.value;})]);

        g.append("path").attr("class","line").attr("d", valueline(dataObjs));

        g.selectAll("dot").data(dataObjs)
            .enter().append("circle")
            .attr("r",3.5)
            .attr("cx", function(d){ return x(d.time); })
            .attr("cy", function(d){ return y(d.value); });

        g.append("g").attr("class","x axis")
            .attr("transform","translate(0,"+height+")")
            .call(xAxis);

        g.append("g").attr("class","y axis")
            .call(yAxis);
    }

    if (preData != undefined){
        updateWithJSON(preData);
    }
    else {
        d3.json("/timeseries/" + id, function (error, data) {
            updateWithJSON(data);
        });
    }
}
