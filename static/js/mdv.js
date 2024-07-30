import { getCookie } from "./ajax_csrf.js";
import { date_range_form, single_date_form } from "./datePicker.js";

$(document).ready(function () {
	var token = getCookie("csrftoken");
	single_date_form(".datepicker-single");

	// Volatilities
	var date = $.now();
	console.log(date);
	if (date == "") {
		date = $("#dateSelect-volAsonDate").val();
	}
	var volAsonDateData = {
		date: date,
	};

	$.ajax({
		url: "mdv_funcs",
		type: "POST",
		data: {
			func: "plotVolSurfaceAsonDate",
			// csrfmiddlewaretoken: token,
			data: JSON.stringify(volAsonDateData),
		},
		success: function (context) {
			var context = JSON.parse(context);
			console.log(context);
			var content = context["content"];
			console.log(content);
			if (context["func"] == "plotVolSurfaceAsonDate") {
				console.log("works");
				$("#plot-volSurfaceAsonDate").append(content["plot"]);
				console.log(content["plot"]);
			}
		},
	});

	// Interest Rate
	$("#dateSelect-viewCurveMdv").on("change", function () {
		var curve_date = $("#dateSelect-viewCurveMdv").val();
		curve_date = "30-06-2022";
		// $.ajax({
		// 	url: "/mdv_funcs",
		// 	type: "POST",
		// 	data: {
		// 		csrfmiddlewaretoken: token,
		// 		data: JSON.stringify({
		// 			date: curve_date,
		// 		}),
		// 	},
		// 	success: function (data) {
		// 		var content = JSON.parse(data);
		// 		$("#plot-volSurfaceAsonDate").append(content["plot"]);
		// 		console.log(content["plot"]);
		// 	},
		// });
	});
});
