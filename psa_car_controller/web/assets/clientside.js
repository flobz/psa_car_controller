class Avg {
  constructor () {
    this.total = 0
    this.count = 0
  }

  addValue (value) {
    if (typeof value === 'number') {
      this.count++
      this.total = ((this.total * (this.count - 1)) / this.count) + (value / this.count)
    }
  }

  average () {
    return this.total
  }

  static getAverageFromKey (array, key) {
    const avg = new Avg()
    array.forEach(function (obj) { avg.addValue(obj[key]) })
    return avg.average()
  }
}
const logger = (function () {
  let oldConsoleLog = null
  const pub = {}

  pub.enableLogger = function enableLogger () {
    if (oldConsoleLog == null) {
      return
    }

    window.console.log = oldConsoleLog
  }

  pub.disableLogger = function disableLogger () {
    oldConsoleLog = console.log
    window.console.log = function () {}
  }

  return pub
}())
function addLocaleDate (data, dateKey) {
  const dateOption = [undefined, { hour: 'numeric', minute: 'numeric' }]
  function dateToLocale (row, key) {
    const date = new Date(row[key])
    row[key] = date.getTime()
    row[key + '_str'] = date.toLocaleDateString(...dateOption)
  }
  let datasetName, dataset
  for ([datasetName, dataset] of Object.entries(data)) {
    dataset.forEach(function (row) {
      dateKey[datasetName].forEach(key => dateToLocale(row, key))
    })
  }
}

function filterDataset (data, range) {
  function dateFromISO (st) {
    return new Date(st).getTime() / 1000
  }
  function isInRange (st) {
    const tsDate = dateFromISO(st)
    return tsDate >= range[0] && tsDate <= range[1]
  }
  const res = {}
  res.trips = data.trips.filter(line => isInRange(line.start_at))
  res.chargings = data.chargings.filter(line => isInRange(line.start_at))
  console.log('filtered_dataset', res)
  return res
}

function filterShortTrip (data, minimumLength) {
  const longTrips = {
    trips: data.trips.filter(line => line.distance > minimumLength),
    chargings: data.chargings
  }
  console.log('long trips:', longTrips)
  return longTrips
}

function updateFigures (data, oldFigure, x, y) {
  const trips = data.trips
  const figures = []
  let i = 0
  y.forEach(function (yLabel) {
    const xLabel = x[i]
    const figure = Object.assign({}, oldFigure[i])
    i++
    const xValues = trips.map(a => a[xLabel])
    // for each y label
    for (let j = 0; j < yLabel.length; j++) {
      figure.data[j].y = trips.map(a => a[yLabel[j]])
      figure.data[j].x = xValues
    }
    console.log(xLabel, figure)
    figures.push(figure)
  })
  return figures
}

function updateMap (data, oldFigure, x, y, lastPos) {
  const trips = data.trips
  const figures = []
  let i = 0
  y.forEach(function (yLabel) {
    const xLabel = x[i]
    const figure = Object.assign({}, oldFigure[i])
    i++
    figure.data[0].lat = []
    figure.data[0].lon = []
    figure.data[0].hovertext = []
    let trip = null
    for (trip of trips) {
      const xPos = trip.positions[xLabel]
      figure.data[0].lat.push(...xPos, null)
      figure.data[0].lon.push(...trip.positions[yLabel[0]], null)
      figure.data[0].hovertext.push(...Array(xPos.length).fill(trip[yLabel[1]]), null)
    }
    if (trip) {
      figure.layout.mapbox.center.lat = lastPos.lat
      figure.layout.mapbox.center.lon = lastPos.lon
      figure.data[1].lat = [lastPos.lat]
      figure.data[1].lon = [lastPos.lon]
    }
    console.log(xLabel, figure)
    figures.push(figure)
  })
  return figures
}

function removeObjectFromTableRow (data) {
  const rows = []
  data.forEach(object => {
    const row = {}
    for (const key in object) {
      if (typeof object[key] !== 'object') {
        row[key] = object[key]
      }
    }
    rows.push(row)
  })
  return rows
}

function updateTables (data, tables) {
  console.log('tables', tables)
  const figures = []
  tables.forEach(function (table) {
    const tableData = removeObjectFromTableRow(data[table.src])
    figures.push(tableData)
  })
  return figures
}

function nbFormat (nb) {
  const nbStr = nb.toFixed(2)
  const nbInt = nbStr.split('.')[0]
  if (nbInt.length > 3) {
    return nbInt
  }
  return nbStr
}

function updateCardsValue (data) {
  const res = {}
  let avgPriceKw
  let avgC02 = new Avg(); let avgKw = new Avg(); const avgTime = new Avg()
  const avgPrice = new Avg()
  data.chargings.forEach(function (charge) {
    const diff = ((new Date(charge.stop_at)) - (new Date(charge.start_at))) / 3600000
    avgKw.addValue(charge.kw)
    avgC02.addValue(charge.co2)
    avgPrice.addValue(charge.price)
    if (diff > 0) {
      avgTime.addValue(diff)
    }
  })
  if (data.chargings.length > 0) {
    avgKw = avgKw.average()
    avgC02 = avgC02.average()
    avgPriceKw = avgPrice.average() / avgKw
    res.avg_emission_kw = avgC02
    res.avg_chg_speed = avgKw / avgTime.average()
  }
  if (data.trips.length > 0) {
    const totalDistance = Math.abs(data.trips[data.trips.length - 1].mileage - data.trips[0].mileage)
    res.avg_consum_kw = Avg.getAverageFromKey(data.trips, 'consumption_km')
    res.elec_consum_kw = totalDistance * res.avg_consum_kw / 100
  }
  if (data.trips.length > 0 && data.chargings.length > 0) {
    res.avg_emission_km = res.avg_emission_kw * res.avg_consum_kw / 100
    res.elec_consum_price = avgPriceKw * res.elec_consum_kw
    res.avg_consum_price = avgPriceKw * res.avg_consum_kw
  }
  for (const [key, value] of Object.entries(res)) {
    document.getElementById(key).innerHTML = nbFormat(value)
  }
}

function sortDataset (ctx, data, tables) {
  const tableId = ctx.prop_id.split('.')[0]
  const table = tables.filter(table => table.table_id === tableId)[0]
  if (ctx.value.length > 0 && data[table.src].length > 0) {
    const asc = ctx.value[0].direction === 'asc'
    let columnId = ctx.value[0].column_id
    let sorted
    if (columnId.endsWith('_str')) {
      columnId = columnId.slice(0, -4)
      sorted = data[table.src].sort(function (a, b) {
        return a[columnId] - b[columnId]
      })
    } else if (typeof data[table.src][0][columnId] === 'number') {
      sorted = data[table.src].sort(function (a, b) {
        return a[columnId] - b[columnId]
      })
    } else {
      sorted = data[table.src].sort((a, b) => a[columnId].localeCompare(b[columnId]))
    }
    if (asc === false) {
      sorted = sorted.reverse()
    }
    data[table.src] = sorted
  }
}

function sortMultipleTable (sortParams, data, tables) {
  for (const [propId, ctxValue] of Object.entries(sortParams)) {
    const ctx = {}
    ctx.prop_id = propId + '.sort_by'
    ctx.value = ctxValue
    console.log(ctx)
    sortDataset(ctx, data, tables)
  }
}

function getLastPosition (trips) {
  const lastPos = {}
  if (Array.isArray(trips) && trips.length > 0) {
    const lastTrip = trips.reduce(function (prev, current) {
      return (prev.start_at > current.start_at) ? prev : current
    })
    console.log('lastTrip:', lastTrip)
    lastPos.lat = lastTrip.positions.lat.at(-1)
    lastPos.lon = lastTrip.positions.long.at(-1)
  } else {
    lastPos.lat = 40
    lastPos.lon = 40
  }
  console.log('last position:', lastPos)
  return lastPos
}

function filterAndSort (data, range, figures, p, log, sort, config) { // eslint-disable-line no-unused-vars
  if (log > 10) {
    logger.disableLogger()
  }
  const ctx = dash_clientside.callback_context.triggered // eslint-disable-line  no-undef
  const outFigures = []; let dataFiltered
  console.log('figures:', figures)
  console.log('data:', data)
  console.log('ctx', ctx)
  console.log('sort', sort)
  if (ctx.length > 0 && ctx[0].prop_id.endsWith('sort_by')) {
    dataFiltered = filterDataset(data, range)
    sortDataset(ctx[0], dataFiltered, p.table_src)
    outFigures.push(...updateTables(dataFiltered, p.table_src))
    outFigures.push(...figures.graph)
    outFigures.push(...figures.maps)
  } else {
    addLocaleDate(data, p.date_columns)
    dataFiltered = filterDataset(data, range)
    sortMultipleTable(sort, dataFiltered, p.table_src)
    outFigures.push(...updateTables(dataFiltered, p.table_src))
    const longTrips = filterShortTrip(dataFiltered, config.minimumLength)
    console.log('trips', dataFiltered.trips)
    console.log('longTrips', longTrips.trips.length)
    outFigures.push(...updateFigures(longTrips, figures.graph, p.graph_x_label, p.graph_y_label))
    outFigures.push(...updateMap(dataFiltered, figures.maps, p.map_x_label, p.map_y_label, getLastPosition(dataFiltered.trips)))
    updateCardsValue(longTrips)
  }
  return outFigures
}
