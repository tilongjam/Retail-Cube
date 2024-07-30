export function date_range_form(from_id, to_id) {
	var dateFormat = "dd/mm/yy",
		from = $(from_id)
			.datepicker({
				dateFormat: dateFormat,
				defaultDate: "+1w",
				changeMonth: true,
				changeYear: true,
				numberOfMonths: 1,
			})
			.on("change", function () {
				to.datepicker("option", "minDate", getDate(this));
			}),
		to = $(to_id)
			.datepicker({
				dateFormat: dateFormat,
				defaultDate: "+1w",
				changeYear: true,
				changeMonth: true,
				numberOfMonths: 1,
			})
			.on("change", function () {
				from.datepicker("option", "maxDate", getDate(this));
			});

	function getDate(element) {
		var date;
		try {
			date = $.datepicker.parseDate(dateFormat, element.value);
		} catch (error) {
			date = null;
		}

		return date;
	}
}

export function single_date_form(date_id) {
	$(date_id).datepicker({
		dateFormat: "dd/mm/yy",
		changeMonth: true,
		changeYear: true,
		defaultDate: "+1w",
		numberOfMonths: 1,
	});
}

export function dayCount(from_id, to_id, element) {
	var dateFormat = "dd/mm/yy",
		from = $(from_id)
			.datepicker({
				dateFormat: dateFormat,
				defaultDate: "+1w",
				changeMonth: true,
				changeYear: true,
				numberOfMonths: 1,
			})
			.on("change", function () {
				to.datepicker("option", "minDate", getDate(this));
				days();
			}),
		to = $(to_id)
			.datepicker({
				dateFormat: dateFormat,
				defaultDate: "+1w",
				changeYear: true,
				changeMonth: true,
				numberOfMonths: 1,
			})
			.on("change", function () {
				from.datepicker("option", "maxDate", getDate(this));
				days();
			});

	function getDate(element) {
		var date;
		try {
			date = $.datepicker.parseDate(dateFormat, element.value);
		} catch (error) {
			date = null;
		}

		return date;
	}
	function days() {
		var a = $(from_id).datepicker("getDate");
		var b = $(to_id).datepicker("getDate");

		if (a && b) {
			a = a.getTime();
			b = b.getTime();
			console.log(a, b);
			var startDate = new Date(a),
				betweenDates = [];
			while (startDate <= b) {
				betweenDates.push(new Date(startDate));
				startDate.setDate(startDate.getDate() + 1);
			}
			diffDays = betweenDates.length;
			var dayCount = document.getElementById(element);
			dayCount.textContent = diffDays;
			return betweenDates;
		}
	}
}

// function daysCount(from_id, to_id, element) {
//     var a = $(from_id).datepicker('getDate');
//     var b = $(to_id).datepicker('getDate');
//     console.log(a, b)
//     if (a && b) {
//         a = a.getTime();
//         b = b.getTime();
//         var startDate = new Date(a),
//             betweenDates = [];
//         while (startDate <= b) {
//             betweenDates.push(new Date(startDate));
//             startDate.setDate(startDate.getDate() + 1);
//         }
//         diffDays = betweenDates.length;
//         var dayCount = document.getElementById(element);
//         dayCount.textContent = diffDays;
//     }
// }
