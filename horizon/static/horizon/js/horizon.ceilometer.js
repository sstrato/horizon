horizon.ceilometer = {
  initVariables: function () {
    var self = this;
    self.margin = {
      top: 40,
      right: 100,
      bottom: 80,
      left: 200
    };
    self.width = 1100 - self.margin.left - self.margin.right;
    self.height = 480 - self.margin.top - self.margin.bottom;
    self.svg = undefined;
    self.x = d3.time.scale().range([0, self.width]);
    self.y = d3.scale.linear().range([self.height, 0]);
    self.xAxis = d3.svg.axis().scale(self.x).orient("bottom");
    self.yAxis = d3.svg.axis().scale(self.y).orient("left");
    self.line = d3.svg.line()
      .x(function (d) {
        return self.x(d.date);
      })
      .y(function (d) {
        return self.y(d.value);
      });

    self.$meter = $("#meter");
    self.$resource = $("#resource");
    self.$date_from = $("#date_from");
    self.$date_to = $("#date_to");
    self.$get_samples = $("#samples_url");
    self.$chart_container = $("#chart_container");
    self.parseDate = d3.time.format("%Y-%m-%dT%H:%M:%S").parse;
  },
  getResources: function (meters) {
    // Get ``meters`` variable from django template.
    var self = this;
    if (meters) {
      self.meters = meters;
    }
  },

  updateResourceOptions: function () {
    // Update resource select field on stats.html template.
    var self = this,
      meter_name = self.$meter.val(),
      i,
      option;
    self.$resource.empty();
    if (self.meters) {
      for (i = 0; i < self.meters.length; i = i + 1) {
        if (meter_name === self.meters[i].name) {
          option = '<option value="' + self.meters[i].resource_id + '">';
          option += self.meters[i].resource_id + '</option>';
          self.$resource.append(option);
        }
      }
    }
  },

  loadChartData: function () {
    var self = this,
      sample = self.$meter.val(),
      resource = self.$resource.val(),
      from = self.$date_from.val(),
      to = self.$date_to.val(),
      horizon_samples_url = self.$get_samples.attr("url");
    d3.select("svg").remove();

    self.svg = d3.select("#chart_container").append("svg")
      .attr("width", self.width + self.margin.left + self.margin.right)
      .attr("height", self.height + self.margin.top + self.margin.bottom)
      .append("g")
      .attr("transform", "translate(" + self.margin.left + "," + self.margin.top + ")");

    // get sample, resource, from and to

    if (sample && resource) {
      var date_ts = (new Date()).getTime();
      d3.csv(horizon_samples_url + "?ts=" + date_ts + "&sample=" + sample + "&resource=" + resource + "&from=" + from + "&to=" + to,
        function (error, data) {
          var chart_title = self.$meter.val() + " ";
          chart_title += gettext("for resource") + " " + self.$resource.val();
          chart_title += " (" + gettext("From") + " " + self.$date_to.val() + " " + gettext("to") + " ";
          chart_title += self.$date_to.val() + ")";

          // read selected option
          var option = self.$meter.find("option").filter(":selected");
          var meter_text = gettext("Value");
          var current_type = self.$meter.find(":selected").attr("data-type");
          if (option) {
            var unit = option[0].getAttribute("data-unit");
            meter_text = meter_text + " (" + unit + ")";
          }

          data.forEach(function (d) {
            d.date = self.parseDate(d.date);
            d.value = +d.value;
          });

          self.x.domain(d3.extent(data, function (d) {
            return d.date;
          }));
          self.y.domain(d3.extent(data, function (d) {
            return d.value;
          }));

          if (current_type === "cumulative") {
            self.svg.append("g")
              .attr("class", "x axis")
              .attr("transform", "translate(0," + self.height + ")")
              .call(self.xAxis);
          } else {
            // show in m/d/Y hh:mm:ss format
            self.svg.append("g")
              .attr("class", "x axis")
              .attr("transform", "translate(0," + self.height + ")")
              .call(self.xAxis.tickFormat(d3.time.format("%m-%d %H:%M:%S")))
              .selectAll("text")
              .style("text-anchor", "end")
              .attr("dx", "-.8em")
              .attr("dy", ".15em")
              .attr("transform", "rotate(-65)");
          }

          self.svg.append("g")
            .attr("class", "y axis")
            .call(self.yAxis)
            .append("text")
            .attr("transform", "rotate(-90)")
            .attr("y", 6)
            .attr("dy", ".71em")
            .style("text-anchor", "end")
            .text(meter_text);

          // draw line or bar depending on type
          if (current_type === "cumulative") {
            self.svg.append("path")
              .datum(data)
              .attr("class", "line")
              .style("stroke", "steelblue")
              .style("stroke-width", 1.5)
              .style("fill", "none")
              .attr("d", self.line);
          } else {
            self.svg.selectAll(".bar")
              .data(data)
              .enter().append("rect")
              .attr("class", "bar")
              .attr("width", 5)
              .style("fill", "steelblue")
              .attr("x", function (d) {
                return self.x(d.date);
              })
              .attr("y", function (d) {
                return self.y(d.value);
              })
              .attr("height", function (d) {
                return self.height - self.y(d.value);
              });
          }

          self.svg.append("text")
            .attr("x", (self.width / 2))
            .attr("y", -(self.margin.top / 2))
            .attr("text-anchor", "middle")
            .style("font-size", "14px")
            .style("text-decoration", "none")
            .text(chart_title);

          d3.selectAll("path.domain")
            .style("fill", "none")
            .style("stroke", "black")
            .style("stroke-width", 1);

          d3.selectAll(".axis path")
            .style("fill", "none")
            .style("stroke", "black")
            .style("shape-rendering", "crispEdges");

          d3.selectAll(".axis")
            .style("font-size", "10px");

          d3.selectAll(".axis line")
            .style("fill", "none")
            .style("stroke", "black")
            .style("shape-rendering", "crispEdges");
        });
    }
  },

  refreshPickers: function (date_interval) {
    var now;
    var targetDate;
    var self = this;
    now = new Date();
    self.$date_to.datepicker('setValue', now);
    targetDate = new Date();
    targetDate.setDate(now.getDate() - date_interval);
    self.$date_from.datepicker('setValue', targetDate);
  },

  init: function () {
    var self = this,
      to,
      from;
    self.initVariables();
    from = self.$date_from.datepicker()
      .on('changeDate', function (ev) {
        if (ev.date.valueOf() > to.date.valueOf()) {
          var newDate = new Date(ev.date);
          newDate.setDate(newDate.getDate() + 1);
          to.setValue(newDate);
        }
        from.hide();
        self.$date_to[0].focus();
      }).data('datepicker');
    to = self.$date_to.datepicker({
      onRender: function (date) { return date.valueOf() <= from.date.valueOf() ? 'disabled' : ''; }
    }).on('changeDate', function () {
      to.hide();
      self.loadChartData();
    }).data('datepicker');

    $(".action_display_chart").click(function () {
      self.loadChartData();
    });

    self.$meter.change(function () {
      self.updateResourceOptions();
      self.loadChartData();
    });
    self.$resource.change(function () {
      self.loadChartData();
    });

    $("#date_options").change(function () {
      var current = $(this).val();
      if (current) {
        self.refreshPickers(current);
        self.loadChartData();
      }
    });
    self.refreshPickers(1);
    self.loadChartData();
  }
};

horizon.addInitFunction(function () {
  horizon.ceilometer.init();
});