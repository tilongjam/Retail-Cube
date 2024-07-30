if ($("#equityPortfolio-chart").length) {
	var equityPortfolioData = {
		labels: ["AFS", "HFT"],
		datasets: [
			{
				label: "",
				data: [9688.84, 8.1],
				backgroundColor: [
					"#00d25b",
					"#2B3467",
					"#82CD47",
					"#ffffff",
					"#009EFF",
				],
				hoverBackgroundColor: "#B33F40",
			},
		],
	};

	var equityPortfolioOptions = {
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
			display: true,
		},
		tooltips: {
			enabled: true,
		},
		onClick: function (e) {
			var activePoints = equityPortfolioChart.getElementsAtEvent(e);
			var selectedIndex = activePoints[0]._index;
			var portfolio = this.data.labels[selectedIndex];
			if (portfolio == "AFS") {
				this.data.labels = [
					"MU-INEQ-AFS-ACT",
					"MU-INEQ-AFS-B",
					"MU-INEQ-AFS-COR",
				];
				this.data.datasets[0].data = [532.87, 9037.48, 118.49];
				this.update();
			} else if (portfolio == "HFT") {
				this.data.labels = ["MU-EQ-HFT-T04", "MU-EQ-HFT-T06"];
				this.data.datasets[0].data = [5.82, 2.28];
				this.update();
			}
		},
	};
	var equityPortfolioChartCanvas = $("#equityPortfolio-chart")
		.get(0)
		.getContext("2d");
	var equityPortfolioChart = new Chart(equityPortfolioChartCanvas, {
		type: "pie",
		data: equityPortfolioData,
		options: equityPortfolioOptions,
	});

	$("#resetEquityPortfolio-chart").on("click", function () {
		equityPortfolioChart.data.labels = ["AFS", "HFT"];
		equityPortfolioChart.data.datasets[0].data = [9688.84, 8.1];
		equityPortfolioChart.update();
	});
}

if ($("#equitySector-chart").length) {
	var equitySectorData = {
		labels: [
			"BANK AND FINANCE",
			"FMCG",
			"IT & ALLIED",
			"AUTOMOBILES",
			"CEMENT & CEMENT PRODUCTS",
		],
		datasets: [
			{
				label: "",
				data: [1722.64, 1603.87, 1402.9, 906.63, 829.07],
				// backgroundColor: [
				// 	"#00D25B",
				// 	"#02CA5C",
				// 	"#04C25C",
				// 	"#06BA5D",
				// 	"#09B25D",
				// 	"#0BAB5E",
				// 	"#0DA35F",
				// 	"#0F9B5F",
				// 	"#119360",
				// 	"#138B60",
				// 	"#168361",
				// 	"#187B62",
				// 	"#1A7362",
				// 	"#1C6B63",
				// 	"#1E6363",
				// 	"#205C64",
				// 	"#225465",
				// 	"#254C65",
				// 	"#274466",
				// 	"#293C66",
				// 	"#2B3467",
				// ],
				backgroundColor: [
					"#00d25b",
					"#2B3467",
					"#82CD47",
					"#ffffff",
					"#009EFF",
				],
				hoverBackgroundColor: "#B33F40",
				borderColor: "#ffffff",
				borderWidth: 1,
			},
		],
	};

	var equitySectorOptions = {
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
			display: true,
		},
		tooltips: {
			enabled: true,
		},
		// onClick: function (e) {
		// 	var activePoints = equityPortfolioChart.getElementsAtEvent(e);
		// 	var selectedIndex = activePoints[0]._index;
		// 	var portfolio = this.data.labels[selectedIndex];
		// 	if (portfolio == "AFS") {
		// 		this.data.labels = [
		// 			"MU-INEQ-AFS-ACT",
		// 			"MU-INEQ-AFS-B",
		// 			"MU-INEQ-AFS-COR",
		// 		];
		// 		this.data.datasets[0].data = [532.87, 9037.48, 118.49];
		// 		this.update();
		// 	} else if (portfolio == "HFT") {
		// 		this.data.labels = ["MU-EQ-HFT-T04", "MU-EQ-HFT-T06"];
		// 		this.data.datasets[0].data = [5.82, 2.28];
		// 		this.update();
		// 	}
		// },
	};
	var equitySectorChartCanvas = $("#equitySector-chart")
		.get(0)
		.getContext("2d");
	var equitySectorChart = new Chart(equitySectorChartCanvas, {
		type: "pie",
		data: equitySectorData,
		options: equitySectorOptions,
	});

	// $("#resetEquityPortfolio-chart").on("click", function () {
	// 	equityPortfolioChart.data.labels = ["AFS", "HFT"];
	// 	equityPortfolioChart.data.datasets[0].data = [9688.84, 8.1];
	// 	equityPortfolioChart.update();
	// });
}

if ($("#mf-chart").length) {
	var mfData = {
		labels: ["Equity", "Debt", "Liquid", "ETF"],
		datasets: [
			{
				label: "",
				data: [511.06, 16679.32, 1513.61, 2601.61],
				backgroundColor: [
					"#00d25b",
					"#2B3467",
					"#82CD47",
					"#ffffff",
					"#009EFF",
				],
				hoverBackgroundColor: "#B33F40",
				borderColor: "#ffffff",
				borderWidth: 1,
			},
		],
	};

	var mfOptions = {
		responsive: false,
		maintainAspectRatio: true,
		segmentShowStroke: false,
		cutoutPercentage: 70,
		elements: {
			arc: {
				borderWidth: 0,
			},
		},
		legend: {
			display: true,
		},
		tooltips: {
			enabled: true,
		},
		// onClick: function (e) {
		// 	var activePoints = equityPortfolioChart.getElementsAtEvent(e);
		// 	var selectedIndex = activePoints[0]._index;
		// 	var portfolio = this.data.labels[selectedIndex];
		// 	if (portfolio == "AFS") {
		// 		this.data.labels = [
		// 			"MU-INEQ-AFS-ACT",
		// 			"MU-INEQ-AFS-B",
		// 			"MU-INEQ-AFS-COR",
		// 		];
		// 		this.data.datasets[0].data = [532.87, 9037.48, 118.49];
		// 		this.update();
		// 	} else if (portfolio == "HFT") {
		// 		this.data.labels = ["MU-EQ-HFT-T04", "MU-EQ-HFT-T06"];
		// 		this.data.datasets[0].data = [5.82, 2.28];
		// 		this.update();
		// 	}
		// },
	};
	var mfChartCanvas = $("#mf-chart").get(0).getContext("2d");
	var mfChart = new Chart(mfChartCanvas, {
		type: "pie",
		data: equitySectorData,
		options: equitySectorOptions,
	});

	// $("#resetEquityPortfolio-chart").on("click", function () {
	// 	equityPortfolioChart.data.labels = ["AFS", "HFT"];
	// 	equityPortfolioChart.data.datasets[0].data = [9688.84, 8.1];
	// 	equityPortfolioChart.update();
	// });
}
