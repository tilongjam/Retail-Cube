$(document).ready(function () {
	$("#selectIbgPvo1-breakdown").select2({
		dropdownParent: $("#ibgPvo1Breakdown-modal"),
	});

	$(document).scrollTop(0);

	// IBG PV01
	$("#selectIbgPvo1-breakdown").on("select2:select", function () {
		$("#ibgPvo1Breakdown-table").empty();
		var ibgpvo1_metric = $("#selectIbgPvo1-breakdown").val();
		if (ibgpvo1_metric == "IRS") {
			var string = `
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th></th>
                        <th>Loaction</th>
                        <th>Number of Deals</th>
                        <th>Notional</th>
                        <th>MTM</th>
                        <th>PV01</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                    <td>1</td>
                    <td>NEW YORK</td>
                    <td>127</td>
                    <td>7,523</td>
                    <td>-219.83</td>
                    <td>-11,24,601</td>
                    </tr>
                    <tr>
                    <td>2</td>
                    <td>LONDON</td>
                    <td>13</td>
                    <td>2,355</td>
                    <td>27.91</td>
                    <td>-3,12,182</td>
                    </tr>
                    <tr>
                    <td>3</td>
                    <td>WBB BAHRAIN</td>
                    <td>11</td>
                    <td>1,743</td>
                    <td>-7.99</td>
                    <td>-56,191.99</td>
                    </tr>
                    <tr>
                    <td>4</td>
                    <td>HONGKONG</td>
                    <td>16</td>
                    <td>1,643</td>
                    <td>-0.63</td>
                    <td>-2,301</td>
                    </tr>
                    <tr>
                    <td>5</td>
                    <td>DUBAI</td>
                    <td>0</td>
                    <td>0</td>
                    <td>0</td>
                    <td>0</td>
                    </tr>
                    <tr>
                    <td>6</td>
                    <td>NASSAU</td>
                    <td>0</td>
                    <td>0</td>
                    <td>0</td>
                    <td>0</td>
                    </tr>
                    <tr>
                    <td>7</td>
                    <td>CHICAGO</td>
                    <td>15</td>
                    <td>618</td>
                    <td>-34.73</td>
                    <td>-1,46,202</td>
                    </tr>
                    <tr>
                    <td>8</td>
                    <td>TOKYO</td>
                    <td>0</td>
                    <td>0</td>
                    <td>0</td>
                    <td>0</td>
                    </tr>
                    <tr>
                    <td>8</td>
                    <td>SINGAPORE</td>
                    <td>1</td>
                    <td>100</td>
                    <td>-0.06</td>
                    <td>-822</td>
                    </tr>
                    <tr>
                    <td>9</td>
                    <td>FRANKFURT</td>
                    <td>0</td>
                    <td>0</td>
                    <td>0</td>
                    <td>0</td>
                    </tr>
                    <tr>
                    <td>10</td>
                    <td>MALE</td>
                    <td>1</td>
                    <td>250</td>
                    <td>37.87</td>
                    <td>1,61,621</td>
                    </tr>
                    <tr>
                    <td></td>
                    <td>Total</td>
                    <td>184</td>
                    <td>14,232</td>
                    <td>-197.46</td>
                    <td>-14,80,679</td>
                    </tr>
                </tbody>
            </table>
            `;
		} else if (ibgpvo1_metric == "CCS") {
			var string = `
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th></th>
                        <th>Currency</th>
                        <th>Currency Control</th>
                        <th>Income</th>
                        <th>Expense</th>
                        <th>Not Accounted</th>
                        <th>Post EOD</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>1</td>
                        <td>LONDON</td>
                        <td>1</td>
                        <td>CCS</td>
                        <td>64</td>
                        <td>-1.45</td>
                        <td>-11,083.90</td>
                    </tr>
                    <tr>
                        <td>2</td>
                        <td>HONGKONG</td>
                        <td>2</td>
                        <td>CCS</td>
                        <td>69</td>
                        <td>0.07</td>
                        <td>25.4</td>
                    </tr>
                    <tr>
                        <td>3</td>
                        <td>CHINA</td>
                        <td>0</td>
                        <td>CCS</td>
                        <td>0</td>
                        <td>0</td>
                        <td>0</td>
                    </tr>
                    <tr>
                        <td>4</td>
                        <td>BAHRAIN</td>
                        <td>0</td>
                        <td>CCS</td>
                        <td>0</td>
                        <td>0</td>
                        <td>0</td>
                    </tr>
                    <tr>
                        <td></td>
                        <td>Total</td>
                        <td>3</td>
                        <td></td>
                        <td>133</td>
                        <td>-1.38</td>
                        <td>-11,058.50</td>
                    </tr>
                </tbody>
            </table>
            `;
		}
		$("#ibgPvo1Breakdown-table").append(string);
	});

	// Daylight Breakdown
	$("#viewBreakdown-daylight").on("click", function () {
		var string = `
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Branch Name</th>
                        <th>Limit</th>
                        <th>Daylight O/S</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                    <td>SBI-AUS</td>
                    <td>20</td>
                    <td>1.565</td>
                    <td>NO BREACH</td>
                    </tr>
                    <tr>
                    <td>SBI-BAN</td>
                    <td>7</td>
                    <td>0.951</td>
                    <td>NO BREACH</td>
                    </tr>
                    <tr>
                    <td>SBI-BEL</td>
                    <td>2</td>
                    <td>-0.155</td>
                    <td>NO BREACH</td>
                    </tr>
                    <tr>
                    <td>SBI-BH-FCB</td>
                    <td>5.5</td>
                    <td>3.957</td>
                    <td>NO BREACH</td>
                    </tr>
                    <tr>
                    <td>SBI-BHN</td>
                    <td>23</td>
                    <td>-3.44</td>
                    <td>NO BREACH</td>
                    </tr>
                    <tr>
                    <td>SBI-CHINA</td>
                    <td>4</td>
                    <td>-0.472</td>
                    <td>NO BREACH</td>
                    </tr>
                    <tr>
                    <td>SBI-GER</td>
                    <td>5</td>
                    <td>2.443</td>
                    <td>NO BREACH</td>
                    </tr>
                    <tr>
                    <td>SBI-HK-BR</td>
                    <td>26</td>
                    <td>0.324</td>
                    <td>NO BREACH</td>
                    </tr>
                    <tr>
                    <td>SBI-ISL</td>
                    <td>2</td>
                    <td>-0.244</td>
                    <td>NO BREACH</td>
                    </tr>
                    <tr>
                    <td>SBI-LON-BR</td>
                    <td>25</td>
                    <td>3.419</td>
                    <td>NO BREACH</td>
                    </tr>
                    <tr>
                    <td>SBI-MAL</td>
                    <td>25</td>
                    <td>-12.371</td>
                    <td>NO BREACH</td>
                    </tr>
                    <tr>
                    <td>SBI-OMN</td>
                    <td>3</td>
                    <td>-0.587</td>
                    <td>NO BREACH</td>
                    </tr>
                    <tr>
                    <td>SBI-OSK</td>
                    <td>0.5</td>
                    <td>0.02</td>
                    <td>NO BREACH</td>
                    </tr>
                    <tr>
                    <td>SBI-SA</td>
                    <td>7</td>
                    <td>0.282</td>
                    <td>NO BREACH</td>
                    </tr>
                    <tr>
                    <td>SBI-SEOUL</td>
                    <td>1</td>
                    <td>0.584</td>
                    <td>NO BREACH</td>
                    </tr>
                    <tr>
                    <td>SBI-SGP</td>
                    <td>6</td>
                    <td>0.721</td>
                    <td>NO BREACH</td>
                    </tr>
                    <tr>
                    <td>SBI-SL-DBU</td>
                    <td>3</td>
                    <td>1.248</td>
                    <td>NO BREACH</td>
                    </tr>
                    <tr>
                    <td>SBI-TKY</td>
                    <td>5</td>
                    <td>-0.346</td>
                    <td>NO BREACH</td>
                    </tr>
                    <tr>
                    <td>SBI-UAE</td>
                    <td>3</td>
                    <td>0.183</td>
                    <td>NO BREACH</td>
                    </tr>
                    <tr>
                    <td>SBI-US-CHG</td>
                    <td>1</td>
                    <td>0.037</td>
                    <td>NO BREACH</td>
                    </tr>
                    <tr>
                    <td>SBI-US-LA</td>
                    <td>2</td>
                    <td>0.182</td>
                    <td>NO BREACH</td>
                    </tr>
                    <tr>
                    <td>SBI-US-NY-BR</td>
                    <td>23</td>
                    <td>2.799</td>
                    <td>NO BREACH</td>
                    </tr>
                    <tr>
                    <td>SBI-YANGON</td>
                    <td>1</td>
                    <td>-0.32</td>
                    <td>NO BREACH</td>
                    </tr>
                    <tr>
                    <td>Total (IBG
                    Limit)</td>
                    <td>200</td>
                    <td>36.65</td>
                    <td>NO BREACH</td>
                    </tr>
                </tbody>
            </table>
        `;

		$("#daylightBreakdown-table").append(string);
	});

	// Charts
	// IBG PV01
	if ($("#ibgpvo1Fx-chart").length) {
		var ibgpvo1FxData = {
			labels: ["NY", "HK", "CHI", "LON", "BAH"],
			datasets: [
				{
					label: "",
					data: [-1164624, -2246, -148668, -354033, -56155.5],
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

		var ibgpvo1FxOptions = {
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
		var ibgpvo1FxChartCanvas = $("#ibgpvo1Fx-chart")
			.get(0)
			.getContext("2d");
		var ibgpvo1FxChart = new Chart(ibgpvo1FxChartCanvas, {
			type: "bar",
			data: ibgpvo1FxData,
			options: ibgpvo1FxOptions,
		});

		// Reset Chart
		$("#resetIbgpvo1Fx-chart").on("click", function () {
			ibgpvo1FxChart.data.labels = [
				"ICICI",
				"Federal",
				"CBI",
				"Kotak",
				"Indusland",
			];
			ibgpvo1FxChart.data.datasets[0].data = [
				293.82, 289.32, 70.5, 5.44, 5.34,
			];
			ibgpvo1FxChart.update();
		});
	}

	if ($("#ird-chart").length) {
		var irdData = {
			labels: ["IRS", "IRF"],
			datasets: [
				{
					label: "",
					data: [-7.81, 0],
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

		var irdOptions = {
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
			onClick: function (e) {
				var activePoints = irdChart.getElementsAtEvent(e);
				console.log(this.data.labels);
				var selectedIndex = activePoints[0]._index;
				var prod = this.data.labels[selectedIndex];
				if (prod == "IRS") {
					this.data.labels = ["OIS", "MIFOR"];
					this.data.datasets[0].data = [-99.52, 131.87];
					this.update();
				}
			},
		};
		var irdChartCanvas = $("#ird-chart").get(0).getContext("2d");
		var irdChart = new Chart(irdChartCanvas, {
			type: "bar",
			data: irdData,
			options: irdOptions,
		});

		$("#selectIrdChart").on("select2:select", function () {
			opt = $("#selectIrdChart").val();
			if (opt == "pnl") {
				var irdData = {
					labels: ["IRS", "IRF"],
					datasets: [
						{
							label: "",
							data: [-7.81, 0],
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
			} else {
				var irdData = {
					labels: ["IRS", "IRF"],
					datasets: [
						{
							label: "",
							data: [3450, 0],
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
			}
			irdChart.data = irdData;
			irdChart.update();
		});

		// Reset Chart
		$("#resetIrd-chart").on("click", function () {
			irdChart.data.labels = ["IRS", "IRF"];
			irdChart.data.datasets[0].data = [-7.81, 0];
			$("#selectIrdChart").val("pnl").trigger("change");
			irdChart.update();
		});
	}
});
