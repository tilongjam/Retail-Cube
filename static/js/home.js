import { getCookie } from "./ajax_csrf.js";

$(document).ready(function () {
	var token = getCookie("csrftoken");
	$.ajax({
		url: "compute_reports",
		type: "POST",
		data: {
			csrfmiddlewaretoken: token,
			date: "",
		},
		success: function (data) {
			var all_reports = JSON.parse(data)["content"];
			// NOOP Domestic
			var noop_data = JSON.parse(all_reports["NOOP"]["data"]);
			var noop_table_string = all_reports["NOOP"]["table_string"];
			$("#noopReportValues").empty();
			$("#noopReportValues").append(noop_table_string);
			var noop_breakdown_string = all_reports["NOOP"]["breakdown_string"];
			$("#noopOverallBreakdownRow").empty();
			$("#noopOverallBreakdownRow").append(noop_breakdown_string);
			var overall_domestic_noop = all_reports["NOOP"]["overall_number"];
			// AGL Domestic
			if ($("#domestic-overallLimit").length) {
				var barData = {
					labels: ["NOOP", "AGL", "VaR"],
					datasets: [
						{
							label: "Utilised",
							data: [
								overall_domestic_noop.toFixed(2),
								6217.81,
								815.09,
							],
							backgroundColor: "#264674",
							hoverBackgroundColor: "rgba(255, 107, 107, 1)",
						},
						{
							label: "Available",
							data: [
								(30000 - overall_domestic_noop).toFixed(2),
								1782.19,
								900,
							],
							backgroundColor: "#378F5B",
							hoverBackgroundColor: "#264674",
						},
					],
				};
				var barOptions_stacked = {
					tooltips: {
						enabled: true,
					},
					hover: {
						animationDuration: 0,
					},
					indexAxis: "y",
					scales: {
						xAxes: [
							{
								ticks: {
									beginAtZero: true,
									fontFamily: "'Open Sans Bold', sans-serif",
									fontSize: 11,
								},
								scaleLabel: {
									display: false,
								},
								gridLines: {},
								stacked: true,
							},
						],
						yAxes: [
							{
								gridLines: {
									display: false,
									color: "#fff",
									zeroLineColor: "#fff",
									zeroLineWidth: 0,
								},
								ticks: {
									fontFamily: "'Open Sans Bold', sans-serif",
									fontSize: 11,
								},
								stacked: true,
							},
						],
					},
					legend: {
						display: true,
					},

					pointLabelFontFamily: "Quadon Extra Bold",
					scaleFontFamily: "Quadon Extra Bold",
				};

				var domesticOverallCanvas = $("#domestic-overallLimit")
					.get(0)
					.getContext("2d");
				var domesticOverallChart = new Chart(domesticOverallCanvas, {
					type: "bar",
					data: barData,
					options: barOptions_stacked,
					// plugins: transactionhistoryChartPlugins,
				});
			}
		},
	});
});
