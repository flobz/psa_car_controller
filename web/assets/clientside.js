function filter_dataset(data, range, old_figure, x,y) {
            function is_in_range(st){
                ts_date = new Date(st).getTime()/1000
                return ts_date >= range[0] && ts_date <= range[1]
            }
            var data_filtered = data.filter(line => is_in_range(line["start_at"]));
            var figures = [];
            var i=0
             y.forEach(function (y_label){
                var x_label=x[i]
                var figure = Object.assign({}, old_figure[i]);
                i++;
                // var unique_y_label = y[i].filter((v, i, a) => a.indexOf(v) === i);
                //var data_nonnull = data_filtered
                // unique_y_label.forEach(function(label) {
                //     data_nonnull = data_nonnull.filter(line => line[label]);
                // });
                if ("mapbox" in figure["layout"]){
                    figure["data"][0]["lat"] = []
                    figure["data"][0]["lon"] = []
                    figure["data"][0]["hovertext"] = []
                    var trip = null;
                    for (trip of data_filtered) {
                        x_pos = trip["positions"][x_label]
                        figure["data"][0]["lat"].push(...x_pos, null);
                        figure["data"][0]["lon"].push(...trip["positions"][y_label[0]]);
                        figure["data"][0]["hovertext"].push(...Array(x_pos.length).fill(trip[y_label[1]]), null);
                    }
                    var last_pos = trip["positions"][y_label[0]].length;
                    figure.layout.mapbox.center.lat = trip["positions"][x_label][last_pos - 1];
                    figure.layout.mapbox.center.lon = trip["positions"][y_label[0]][last_pos - 1];
                    figure.data[1].lat = [figure.layout.mapbox.center.lat]
                    figure.data[1].lon = [figure.layout.mapbox.center.lon]
                }
                else {
                    x_values = data_filtered.map(a => a[x_label])
                    // for each y label
                    for (j = 0; j < y_label.length; j++) {
                        figure["data"][j]["y"] = data_filtered.map(a => a[y_label[j]]);
                        figure["data"][j]["x"] = x_values
                    }
                }
                // console.log(figure);
                figures.push(figure);
            });
            return figures;
}
