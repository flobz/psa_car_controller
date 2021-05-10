class Avg{
    constructor(){
        this.total = 0;
        this.count = 0;
    }
    add_value(value){
      if (typeof value === 'number') {
        this.count++;
        this.total = ((this.total*(this.count-1))/this.count) + (value/this.count);
      }
    }

    average(){
        return this.total;
    }
    static get_average_key(array, key){
          var avg = new Avg()
          array.forEach(function(obj){ avg.add_value(obj[key])})
          return avg.average();
    }
}
var logger = function()
{
    var oldConsoleLog = null;
    var pub = {};

    pub.enableLogger =  function enableLogger()
                        {
                            if(oldConsoleLog == null)
                                return;

                            window['console']['log'] = oldConsoleLog;
                        };

    pub.disableLogger = function disableLogger()
                        {
                            oldConsoleLog = console.log;
                            window['console']['log'] = function() {};
                        };

    return pub;
}();
function add_date_str(data, date_key){
    var date_option = [undefined, {"hour":"numeric", "minute":"numeric"}]
    for([dataset_name, dataset] of Object.entries(data)){
        dataset.forEach(function (row) {
            date_key[dataset_name].forEach(function (key) {
                var date= new Date(row[key]);
                row[key] = date
                row[key + "_str"] = date.toLocaleDateString(...date_option);
            })
        })
    }
}

function filter_dataset(data,range){
   function date_from_iso_str(st){
      return new Date(st).getTime()/1000
   }
   function is_in_range(st){
        ts_date = date_from_iso_str(st);
        return ts_date >= range[0] && ts_date <= range[1]
   }
   var res = {"trips": data["trips"].filter(line => is_in_range(line["start_at"])),
                                "chargings": data["chargings"].filter(line => is_in_range(line["start_at"]))};
   console.log("filtered_dataset", res);
   return res;
}


function filter_short_trip(data){
    var long_trips = {"trips": data["trips"].filter(line => line["distance"]>10),
                  "chargings": data["chargings"]};
    console.log("long trips:" , long_trips)
    return long_trips;
}

function update_figures(data, old_figure, x,y) {
            var trips = data["trips"]
            var figures = [];
            var i=0
             y.forEach(function (y_label){
                var x_label=x[i]
                var figure = Object.assign({}, old_figure[i]);
                i++;
               // console.log(old_figure[i]);
                // var unique_y_label = y[i].filter((v, i, a) => a.indexOf(v) === i);
                //var data_nonnull = trips
                // unique_y_label.forEach(function(label) {
                //     data_nonnull = data_nonnull.filter(line => line[label]);
                // });
                if ("mapbox" in figure["layout"]){
                    figure["data"][0]["lat"] = []
                    figure["data"][0]["lon"] = []
                    figure["data"][0]["hovertext"] = []
                    var trip = null;
                    for (trip of trips) {
                        x_pos = trip["positions"][x_label]
                        figure["data"][0]["lat"].push(...x_pos, null);
                        figure["data"][0]["lon"].push(...trip["positions"][y_label[0]]);
                        figure["data"][0]["hovertext"].push(...Array(x_pos.length).fill(trip[y_label[1]]), null);
                    }
                    if(trip){
                        var last_pos = trip["positions"][y_label[0]].length;
                        figure.layout.mapbox.center.lat = trip["positions"][x_label][last_pos - 1];
                        figure.layout.mapbox.center.lon = trip["positions"][y_label[0]][last_pos - 1];
                        figure.data[1].lat = [figure.layout.mapbox.center.lat]
                        figure.data[1].lon = [figure.layout.mapbox.center.lon]
                    }
                }
                else {
                    x_values = trips.map(a => a[x_label])
                    // for each y label
                    for (j = 0; j < y_label.length; j++) {
                        figure["data"][j]["y"] = trips.map(a => a[y_label[j]]);
                        figure["data"][j]["x"] = x_values
                    }
                }
                console.log(x_label, figure);
                figures.push(figure);
            });
            return figures;
}

function update_table(data, tables){
    console.log("tables", tables);
    figures = [];
    tables.forEach(function (table){
        figures.push(data[table.src]);
    })
    return figures;
}


function update_cards_value(data){
    var res = {}
    var avg_co2=new Avg(), avg_kw = new Avg(),avg_time = new Avg(), avg_price = new Avg();
    data["chargings"].forEach(function(charge){
      diff = ((new Date(charge["stop_at"])) - (new Date(charge["start_at"])))/3600000;
      avg_kw.add_value(charge["kw"]);
      avg_co2.add_value(charge["co2"]);
      avg_price.add_value(charge["price"]);
      if(diff > 0){
        avg_time.add_value(diff);
      }
    })
    if(data["chargings"].length>0){
        avg_kw = avg_kw.average();
        avg_co2 = avg_co2.average()
        avg_price_kw = avg_price.average()/avg_kw;
        res["avg_emission_kw"] = avg_co2;
        res["avg_chg_speed"] = avg_kw/avg_time.average();
    }
    if(data["trips"].length>0){
        var total_distance = data["trips"][data["trips"].length-1]["mileage"]-data["trips"][0]["mileage"]
        res["avg_consum_kw"] = Avg.get_average_key(data["trips"], "consumption_km");
        res["elec_consum_kw"] = total_distance*res["avg_consum_kw"]/100;
    }
    if(data["trips"].length>0 && data["chargings"].length>0){
        res["avg_emission_km"] = res["avg_emission_kw"]*res["avg_consum_kw"]/100;
        res["elec_consum_price"] = avg_price_kw*res["elec_consum_kw"]
        res["avg_consum_price"] = avg_price_kw*res["avg_consum_kw"]
    }
    for (const [key, value] of Object.entries(res)) {
          document.getElementById(key).innerHTML=value.toPrecision(3);
    }
}

function sort_dataset(ctx, data, tables){
    var table_id = ctx.prop_id.split(".")[0];
    if(ctx.value.length > 0){
        var  asc = ctx.value[0].direction==='asc';
        var column_id = ctx.value[0].column_id;
        var table = tables.filter(table => table.table_id === table_id)[0];
        var sorted = null;
        if (column_id.endsWith("_str")){
          column_id = column_id.slice(0, -4);
          sorted = data[table.src].sort(function(a,b){
                return a[column_id] - b[column_id];
              });
        }
        else if(typeof data[table.src][0][column_id] == 'number'){
            sorted = data[table.src].sort(function(a,b){
                return a[column_id] - b[column_id];
              });
        }
        else {
            sorted = data[table.src].sort((a, b) => a[column_id].localeCompare(b[column_id]));
        }
        if(asc===false){
            sorted = sorted.reverse();
        }
        data[table.src]=sorted;
    }
}



function filter_and_sort(data,range, figures, p, log) {
                if(log>10){
                     logger.disableLogger();
                }
                console.log("figures:", figures);
                console.log("data:", data)
                var ctx = dash_clientside.callback_context.triggered;
                console.log("ctx", ctx);
                var out_figures = [];
                if(ctx.length > 0 && ctx[0].prop_id.endsWith("sort_by")){
                    var data_filtered = filter_dataset(data, range);
                    sort_dataset(ctx[0], data_filtered, p.table_src);
                    out_figures.push(...update_table(data_filtered, p.table_src));
                    out_figures.push(...figures.graph);
                    out_figures.push(...figures.maps);
                }
                else{
                    add_date_str(data,p.date_columns);
                    var data_filtered = filter_dataset(data, range);
                    out_figures.push(...update_table(data_filtered, p.table_src));
                    console.log(data_filtered["trips"].length);
                    long_trips = filter_short_trip(data_filtered);
                    console.log("trips", data_filtered["trips"].length);
                    console.log("long_trips", long_trips["trips"].length);
                    out_figures.push(...update_figures(long_trips, figures["graph"], p.graph_x_label, p.graph_y_label));
                    out_figures.push(...update_figures(data_filtered, figures["maps"], p.map_x_label, p.map_y_label));
                    update_cards_value(long_trips);
                }
                return out_figures;
}