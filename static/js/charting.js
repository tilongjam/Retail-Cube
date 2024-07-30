export function create_graph(dataset, labels, type, canvas_id) {
	var data = {
		labels: labels,
		datasets: dataset,
	};

	var options = {
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
		scales: {
			xAxes: [
				{
					ticks: {
						beginAtZero: true,
						fontFamily: "'Open Sans Bold', sans-serif",
						fontSize: 12,
						fontColor: "#fff",
					},
					scaleLabel: {
						display: false,
					},
					gridLines: {
						display: false,
						color: "#fff",
						zeroLineColor: "#fff",
						zeroLineWidth: 10,
						ticks: { beginAtZero: true },
					},
				},
			],
			yAxes: [
				{
					gridLines: {
						display: true,
						color: "#fff",
						zeroLineColor: "#fff",
						zeroLineWidth: 1,
						ticks: { beginAtZero: true },
					},
					ticks: {
						beginAtZero: true,
						// maxTicksLimit: 2,
						// color: "#fff",
						fontFamily: "'Open Sans Bold', sans-serif",
						fontSize: 12,
						fontColor: "#fff",
					},
				},
			],
		},
	};
	var id = "#".concat(canvas_id);
	console.log(id);
	var canvas = $(id).get(0).getContext("2d");
	var chart = new Chart(canvas, { type: type, data: data, options: options });
}
