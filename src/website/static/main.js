


var d1 = [[0, 0]];

$(document).ready(function () {
    $.plot($("#placeholder"), [d1]);
    $("input[name=paramgroup]:radio").change(function () {
        $(".dynamic-vals").remove();
        var paramValue = $("#param-value");
        if ($(this).val() == "mean" || $(this).val() == "std" || $(this).val() == "blarg"){
            paramValue.append("<div class='dynamic-vals'>Lower Bound:<br /><input type='number' id='lower' /><br /></div>");
            paramValue.append("<div class='dynamic-vals'>Upper Bound:<br /><input type='number' id='upper' /></div>");
        }
        else if ($(this).val() == "level") {
            paramValue.append("<div class='dyn" +
                "amic-vals'>Categories:<br /><input type='string' id='categories' /></div>");
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
                element += "<td><button type='button' onclick='visualizeID(\"" + timeseriesEntry.id;
                element += "\")' id='viz" + timeseriesEntry.id + "'>Visualize</button></td>";
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
            console.log("### fReader Data ###");
            console.log(result);

            //visualize(undefined, d3.select("#selected-timeseries"), result);
            $.ajax({url:"/simquery", type:"POST", data:JSON.stringify(result), contentType:"application/json"})
            .done(function(msg){
                //for(var i = 0; i < msg.similar_ids.length && i < 5; ++i){
                    //visualize(msg.similar_ids[i], d3.select("#similar-timeseries-"+(i+1)));
                //}
                visualizeFlot2(result, msg)
            });
        };

        fReader.readAsText(files.item(0));
    });
});

//With ID Get Data and Call Visualization Function
function visualizeID(id){
    $.get("/simquery?id="+id, function(data){
        visualizeFlot(data);
    });
}

//Given ID : Plot Data
function visualizeFlot(data){
    console.log("### Flot Orig Data ###");
    console.log(data);
    flotData = [];

    for(var i = 0; i < data.similar_ids.length; ++i){
        a = data.similar_ts[i].time_points;
        b =data.similar_ts[i].data_points;
        var c = a.map(function (e, i) {
            return [e, b[i]];
        });
        var currLabel;
        if (i==0) {
            currLabel = "Ref TS";
        } else {
            currLabel = "Sim "+i;
        }
        flotData[i] = {label: currLabel, data: c};

        //$.plot($("#placeholder"), [c]);

    }
    console.log("### Flot Final Data ###");
    console.log(flotData);
    $.plot($("#placeholder"), flotData);

}


//Uploaded TS: Plot data
function visualizeFlot2(orig, data){
    console.log("### Flot2 Compare TS ###");
    console.log(orig);
    console.log("### Flot2 Compare Sim TS ###");
    console.log(data);
    flotData = [];
    var currLabel = "Ref Ts"
    flotData[0] = {label: currLabel, data: orig};


    for(var i = 0; i < data.similar_ids.length; ++i){
        a = data.similar_ts[i].time_points;
        b =data.similar_ts[i].data_points;
        var c = a.map(function (e, i) {
            return [e, b[i]];
        });

        currLabel = "Sim "+(i+1);

        flotData[i] = {label: currLabel, data: c};

        //$.plot($("#placeholder"), [c]);

    }
    console.log("### Flot2 Final Data ###");
    console.log(flotData);
    $.plot($("#placeholder"), flotData);

}



//var d1 = [[0, .01], [.25, .80], [.5, .6], [.75, .3], [1, .69]];