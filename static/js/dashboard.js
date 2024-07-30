(function ($) {
	"use strict";
	$.fn.andSelf = function () {
		return this.addBack.apply(this, arguments);
	};
	$(function () {
		// if ($("#domestic-overallLimit").length) {
		// 	var barData = {
		// 		labels: ["NOOP", "AGL", "VaR"],
		// 		datasets: [
		// 			{
		// 				label: "Utilised",
		// 				data: [3036.35, 6217.81, 815.09],
		// 				backgroundColor: "#264674",
		// 				hoverBackgroundColor: "rgba(255, 107, 107, 1)",
		// 			},
		// 			{
		// 				label: "Available",
		// 				data: [5963.35, 1782.19, 900],
		// 				backgroundColor: "#378F5B",
		// 				hoverBackgroundColor: "#264674",
		// 			},
		// 		],
		// 	};
		// 	var barOptions_stacked = {
		// 		tooltips: {
		// 			enabled: true,
		// 		},
		// 		hover: {
		// 			animationDuration: 0,
		// 		},
		// 		indexAxis: "y",
		// 		scales: {
		// 			xAxes: [
		// 				{
		// 					ticks: {
		// 						beginAtZero: true,
		// 						fontFamily: "'Open Sans Bold', sans-serif",
		// 						fontSize: 11,
		// 					},
		// 					scaleLabel: {
		// 						display: false,
		// 					},
		// 					gridLines: {},
		// 					stacked: true,
		// 				},
		// 			],
		// 			yAxes: [
		// 				{
		// 					gridLines: {
		// 						display: false,
		// 						color: "#fff",
		// 						zeroLineColor: "#fff",
		// 						zeroLineWidth: 0,
		// 					},
		// 					ticks: {
		// 						fontFamily: "'Open Sans Bold', sans-serif",
		// 						fontSize: 11,
		// 					},
		// 					stacked: true,
		// 				},
		// 			],
		// 		},
		// 		legend: {
		// 			display: true,
		// 		},

		// 		pointLabelFontFamily: "Quadon Extra Bold",
		// 		scaleFontFamily: "Quadon Extra Bold",
		// 	};

		// 	var domesticOverallCanvas = $("#domestic-overallLimit")
		// 		.get(0)
		// 		.getContext("2d");
		// 	var domesticOverallChart = new Chart(domesticOverallCanvas, {
		// 		type: "bar",
		// 		data: barData,
		// 		options: barOptions_stacked,
		// 		// plugins: transactionhistoryChartPlugins,
		// 	});
		// }

		if ($("#ibg-overallLimit").length) {
			var ibgData = {
				labels: ["NOOP", "AGL", "VaR"],
				datasets: [
					{
						label: "Utilised",
						data: [199.98, 118, 60.42],
						backgroundColor: "#264674",
						hoverBackgroundColor: "rgba(255, 107, 107, 1)",
					},
					{
						label: "Available",
						data: [1100.02, 312, 100],
						backgroundColor: "#378F5B",
						hoverBackgroundColor: "#264674",
					},
				],
			};
			var ibgOptions_stacked = {
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

			var ibgOverallCanvas = $("#ibg-overallLimit")
				.get(0)
				.getContext("2d");
			var ibgOverallCanvasChart = new Chart(ibgOverallCanvas, {
				type: "bar",
				data: ibgData,
				options: ibgOptions_stacked,
				// plugins: transactionhistoryChartPlugins,
			});
		}
		if ($("#fxExposure").length) {
			var fxExposureData = {
				labels: ["USDINR", "EURINR", "GBPINR", "JPYINR", "SGDINR"],
				datasets: [
					{
						label: "",
						data: [2100192, 784022, 687435, 580315, 455578],
						backgroundColor: [
							"#00d25b",
							"#82CD47",
							"#ffffff",
							"#2B3467",
							"#009EFF",
						],
						hoverBackgroundColor: "#B33F40",
					},
				],
			};
			var fxExposureOptions = {
				responsive: true,
				maintainAspectRatio: true,
				segmentShowStroke: false,
				cutoutPercentage: 70,
				elements: {
					arc: {
						borderWidth: 0,
					},
				},
				legend: {
					display: false,
				},
				tooltips: {
					enabled: true,
				},
			};
			var fxExposureChartCanvas = $("#fxExposure")
				.get(0)
				.getContext("2d");
			var fxExposureChart = new Chart(fxExposureChartCanvas, {
				type: "bar",
				data: fxExposureData,
				options: fxExposureOptions,
			});
		}
		if ($("#counterpartyExposure").length) {
			var counterpartyExposureData = {
				labels: [
					"JPMC",
					"Axis Bank Ltd",
					"JSW",
					"Citi Bank India Ltd",
					"Deutsche Bank GmbH",
				],
				datasets: [
					{
						label: "",
						data: [4662302, 2624097, 2453556, 2331896, 1428093],
						backgroundColor: [
							"#00d25b",
							"#82CD47",
							"#ffffff",
							"#2B3467",
							"#009EFF",
						],
						hoverBackgroundColor: "#B33F40",
					},
				],
			};
			var counterpartyExposureOptions = {
				responsive: true,
				maintainAspectRatio: true,
				segmentShowStroke: false,
				cutoutPercentage: 70,
				elements: {
					arc: {
						borderWidth: 0,
					},
				},
				legend: {
					display: false,
				},
				tooltips: {
					enabled: true,
				},
			};
			var counterpartyExposureChartCanvas = $("#counterpartyExposure")
				.get(0)
				.getContext("2d");
			var counterpartyExposureChart = new Chart(
				counterpartyExposureChartCanvas,
				{
					type: "bar",
					data: counterpartyExposureData,
					options: counterpartyExposureOptions,
				}
			);
		}
		if ($("#transaction-history-arabic").length) {
			var areaData = {
				labels: ["Paypal", "Stripe", "Cash"],
				datasets: [
					{
						data: [55, 25, 20],
						backgroundColor: ["#111111", "#00d25b", "#ffab00"],
					},
				],
			};
			var areaOptions = {
				responsive: true,
				maintainAspectRatio: true,
				segmentShowStroke: false,
				cutoutPercentage: 70,
				elements: {
					arc: {
						borderWidth: 0,
					},
				},
				legend: {
					display: false,
				},
				tooltips: {
					enabled: true,
				},
			};
			var transactionhistoryChartPlugins = {
				beforeDraw: function (chart) {
					var width = chart.chart.width,
						height = chart.chart.height,
						ctx = chart.chart.ctx;

					ctx.restore();
					var fontSize = 1;
					ctx.font = fontSize + "rem sans-serif";
					ctx.textAlign = "left";
					ctx.textBaseline = "middle";
					ctx.fillStyle = "#ffffff";

					var text = "$1200",
						textX = Math.round(
							(width - ctx.measureText(text).width) / 2
						),
						textY = height / 2.4;

					ctx.fillText(text, textX, textY);

					ctx.restore();
					var fontSize = 0.75;
					ctx.font = fontSize + "rem sans-serif";
					ctx.textAlign = "left";
					ctx.textBaseline = "middle";
					ctx.fillStyle = "#6c7293";

					var texts = "مجموع",
						textsX = Math.round(
							(width - ctx.measureText(text).width) / 1.93
						),
						textsY = height / 1.7;

					ctx.fillText(texts, textsX, textsY);
					ctx.save();
				},
			};
			var transactionhistoryChartCanvas = $("#transaction-history-arabic")
				.get(0)
				.getContext("2d");
			var transactionhistoryChart = new Chart(
				transactionhistoryChartCanvas,
				{
					type: "doughnut",
					data: areaData,
					options: areaOptions,
					plugins: transactionhistoryChartPlugins,
				}
			);
		}
		if ($("#owl-carousel-basic").length) {
			$("#owl-carousel-basic").owlCarousel({
				loop: true,
				margin: 10,
				dots: false,
				nav: true,
				autoplay: true,
				autoplayTimeout: 4500,
				navText: [
					"<i class='mdi mdi-chevron-left'></i>",
					"<i class='mdi mdi-chevron-right'></i>",
				],
				responsive: {
					0: {
						items: 1,
					},
					600: {
						items: 1,
					},
					1000: {
						items: 1,
					},
				},
			});
		}
		var isrtl = $("body").hasClass("rtl");
		if ($("#owl-carousel-rtl").length) {
			$("#owl-carousel-rtl").owlCarousel({
				loop: true,
				margin: 10,
				dots: false,
				nav: true,
				rtl: isrtl,
				autoplay: true,
				autoplayTimeout: 4500,
				navText: [
					"<i class='mdi mdi-chevron-right'></i>",
					"<i class='mdi mdi-chevron-left'></i>",
				],
				responsive: {
					0: {
						items: 1,
					},
					600: {
						items: 1,
					},
					1000: {
						items: 1,
					},
				},
			});
		}
	});
})(jQuery);
