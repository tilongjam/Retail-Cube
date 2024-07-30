import { create_graph } from "./charting.js";

$(document).ready(function () {
	console.log("HI");
	$("#selectNoop-breakdown").select2({
		dropdownParent: $("#noopBreakdown-modal"),
	});

	$("#selectCounterparty-breakdown").select2({
		dropdownParent: $("#counterpartyBreakdown-modal"),
	});

	var varLevel = $("#selectVar-ci").val();
	$(".ci-varLevel").html(varLevel);

	var btLevel = $("#selectBt-ci").val();
	$(".ci-BtLevel").html(btLevel);

	$("#selectVar-ci").on("select2:select", function () {
		var varLevel = $("#selectVar-ci").val();
		$(".ci-varLevel").html(varLevel);
	});

	$("#selectBt-ci").on("select2:select", function () {
		var btLevel = $("#selectBt-ci").val();
		$(".ci-BtLevel").html(btLevel);
	});

	$(document).scrollTop(0);

	// Noop Breakdown
	$("#selectNoop-breakdown").on("select2:select", function () {
		$("#noopBreakdown-table").empty();
		var noop_metric = $("#selectNoop-breakdown").val();
		if (noop_metric == "Net Forward") {
			var string = `
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th></th>
                        <th>Currency</th>
                        <th>Off Balance Sheet Exposure</th>
                        <th>Placement Borrowing</th>
                        <th>Overdue Bills</th>
                        <th>Overdue Forwards</th>
                        <th>LC/BG</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>1</td>
                        <td>USD</td>
                        <td>-2,817.06</td>
                        <td>16,340.52</td>
                        <td>27.74</td>
                        <td>0.00</td>
                        <td>-5.45</td>
                    </tr>
                    <tr>
                        <td>
                            2
                        </td>
                        <td>EUR</td>
                        <td>-65.35</td>
                        <td>0.00</td>
                        <td>0.98</td>
                        <td>0.00</td>
                        <td>0.98</td>
                    </tr>
                    <tr>
                        <td>
                            3
                        </td>
                        <td>GBP</td>
                        <td>416.53</td>
                        <td>0.00</td>
                        <td>0.85</td>
                        <td>0.00</td>
                        <td>0.85</td>
                    </tr>
                </tbody>
            </table>
            `;
		} else if (noop_metric == "Net Spot") {
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
                        <td>USD</td>
                        <td>18,651.47</td>
                        <td>889.13</td>
                        <td>-4.43</td>
                        <td>-3.30</td>
                        <td>0.00</td>
                    </tr>
                    <tr>
                        <td>
                            2
                        </td>
                        <td>EUR</td>
                        <td>47.85</td>
                        <td>5.70</td>
                        <td>0.00</td>
                        <td>-0.75</td>
                        <td>0.00</td>
                    </tr>
                    <tr>
                        <td>
                            3
                        </td>
                        <td>GBP</td>
                        <td>-414.48</td>
                        <td>1.40</td>
                        <td>-0.39</td>
                        <td>-0.23</td>
                        <td>0.00</td>
                    </tr>
                </tbody>
            </table>
            `;
		}
		$("#noopBreakdown-table").append(string);
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

	// Counterparty Breakdown
	$("#selectCounterparty-breakdown").on("select2:select", function () {
		$("#counterpartyBreakdown-table").empty();
		var counterparty_metric = $("#selectCounterparty-breakdown").val();
		if (counterparty_metric == "Forward FX") {
			var string = `
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Counterparty</th>
                        <th>Allocated</th>
                        <th>Used</th>
                        <th>Available</th>
                        <th>% Utilised</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                    <td>ICICI BANK-FOREX</td>
                    <td>1,00,00,00,000.00</td>
                    <td>78,16,03,473.67</td>
                    <td>21,83,96,526.33</td>
                    <td>78.16%</td>
                    </tr>
                    <tr>
                    <td>FEDERAL BANK LTD-FOREX</td>
                    <td>75,00,00,000.00</td>
                    <td>24,88,37,758.91</td>
                    <td>50,11,62,241.09</td>
                    <td>33.18%</td>
                    </tr>
                    <tr>
                    <td>CENTRAL BANK OF INDIA - FX</td>
                    <td>2,00,00,00,000.00</td>
                    <td>53,24,41,591.73</td>
                    <td>1,46,75,58,408.27</td>
                    <td>26.62%</td>
                    </tr>
                    <tr>
                    <td>KOTAK MAHINDRA BANK LTD</td>
                    <td>1,00,00,00,000.00</td>
                    <td>0.00</td>
                    <td>1,00,00,00,000.00</td>
                    <td>0%</td>
                    </tr>
                    <tr>
                    <td>INDUS IND BANK-MUM</td>
                    <td>5,00,00,00,000.00</td>
                    <td>50,58,03,154.31</td>
                    <td>4,49,41,96,845.69</td>
                    <td>10.12%</td>
                    </tr>
                    <tr>
                    <td>INDIAN BANK-FOREX</td>
                    <td>4,50,00,00,000.00</td>
                    <td>13,03,35,713.17</td>
                    <td>4,36,96,64,286.83</td>
                    <td>2.90%</td>
                    </tr>
                    <tr>
                    <td>H D F C BANK -FOREX</td>
                    <td>1,45,00,00,000.00</td>
                    <td>87,83,75,274.03</td>
                    <td>57,16,24,725.97</td>
                    <td>60.58%</td>
                    </tr>
                    <tr>
                    <td>Axis Bank</td>
                    <td>25,00,00,000.00</td>
                    <td>85,61,45,056.55</td>
                    <td>-60,61,45,056.55</td>
                    <td>342.46%</td>
                    </tr>
                    <tr>
                    <td>UNION BANK OF INDIA</td>
                    <td>3,00,00,00,000.00</td>
                    <td>15,43,51,795.78</td>
                    <td>2,84,56,48,204.22</td>
                    <td>5.15%</td>
                    </tr>
                    <tr>
                    <td>I D B I BANK</td>
                    <td>0.00</td>
                    <td>13,83,930.00</td>
                    <td>-13,83,930.00</td>
                    <td>%</td>
                    </tr>
                    <tr>
                    <td>CITY UNION BANK FX</td>
                    <td>50,00,00,000.00</td>
                    <td>4,52,54,707.00</td>
                    <td>45,47,45,293.00</td>
                    <td>9.05%</td>
                    </tr>
                    <tr>
                    <td>BANK OF BARODA</td>
                    <td>1,60,00,00,000.00</td>
                    <td>18,99,62,500.00</td>
                    <td>1,41,00,37,500.00</td>
                    <td>11.87%</td>
                    </tr>
                    <tr>
                    <td>CANARA BANK</td>
                    <td>3,00,00,00,000.00</td>
                    <td>18,99,62,500.00</td>
                    <td>2,81,00,37,500.00</td>
                    <td>6.33%</td>
                    </tr>
                    <tr>
                    <td>INDIAN OVERSEAS BANK-FOREX</td>
                    <td>1,00,00,00,000.00</td>
                    <td>0.00</td>
                    <td>1,00,00,00,000.00</td>
                    <td>0%</td>
                    </tr>
                    <tr>
                    <td>SMALL INDUS DVP BNK OF IND-FOREX</td>
                    <td>25,00,00,000.00</td>
                    <td>4,05,91,162.00</td>
                    <td>20,94,08,838.00</td>
                    <td>16.24%</td>
                    </tr>
                    <tr>
                    <td>BANDHANBANK-KOL</td>
                    <td>1,70,00,00,000.00</td>
                    <td>0.00</td>
                    <td>1,70,00,00,000.00</td>
                    <td>0%</td>
                    </tr>
                    <tr>
                    <td>BANK OF INDIA</td>
                    <td>1,50,00,00,000.00</td>
                    <td>0.00</td>
                    <td>1,50,00,00,000.00</td>
                    <td>0%</td>
                    </tr>
                    <tr>
                    <td>DBIL-MUM</td>
                    <td>50,00,00,000.00</td>
                    <td>0.00</td>
                    <td>50,00,00,000.00</td>
                    <td>0%</td>
                    </tr>
                    <tr>
                    <td>Exim Bank</td>
                    <td>1,20,00,00,000.00</td>
                    <td>0.00</td>
                    <td>1,20,00,00,000.00</td>
                    <td>0%</td>
                    </tr>
                    <tr>
                    <td>THE RATNAKAR BANK LTD</td>
                    <td>5,00,00,000.00</td>
                    <td>0.00</td>
                    <td>5,00,00,000.00</td>
                    <td>0%</td>
                    </tr>
                </tbody>
            </table>
            `;
		} else if (counterparty_metric == "Ready FX") {
			var string = `
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Counterparty</th>
                        <th>Allocated</th>
                        <th>Used</th>
                        <th>Available</th>
                        <th>% Utilised</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                    <td>ICICI BANK-FOREX</td>
                    <td>5,00,00,00,000.00 </td>
                    <td>16,84,74,51,074.35 </td>
                    <td>-11,84,74,51,074.35 </td>
                    <td>336.95%</td>
                    </tr>
                    <tr>
                    <td>FEDERAL BANK LTD-FOREX</td>
                    <td>50,00,00,000.00 </td>
                    <td>3,36,77,10,919.92 </td>
                    <td>-2,86,77,10,919.92 </td>
                    <td>673.54%</td>
                    </tr>
                    <tr>
                    <td>CENTRAL BANK OF INDIA - FX</td>
                    <td>4,00,00,00,000.00 </td>
                    <td>3,69,78,24,947.10 </td>
                    <td>30,21,75,052.90 </td>
                    <td>92.45%</td>
                    </tr>
                    <tr>
                    <td>KOTAK MAHINDRA BANK LTD</td>
                    <td>2,50,00,00,000.00 </td>
                    <td>1,90,45,28,797.31 </td>
                    <td>59,54,71,202.69 </td>
                    <td>76.18%</td>
                    </tr>
                    <tr>
                    <td>INDUS IND BANK-MUM</td>
                    <td>2,50,00,00,000.00 </td>
                    <td>3,49,54,36,031.61 </td>
                    <td>-99,54,36,031.61 </td>
                    <td>139.82%</td>
                    </tr>
                    <tr>
                    <td>INDIAN BANK-FOREX</td>
                    <td>3,00,00,00,000.00 </td>
                    <td>2,31,37,47,085.53 </td>
                    <td>68,62,52,914.47 </td>
                    <td>77.12%</td>
                    </tr>
                    <tr>
                    <td>H D F C BANK -FOREX</td>
                    <td>6,00,00,00,000.00 </td>
                    <td>1,44,38,05,742.76 </td>
                    <td>4,55,61,94,257.24 </td>
                    <td>24.06%</td>
                    </tr>
                    <tr>
                    <td>Axis Bank</td>
                    <td>2,75,00,00,000.00 </td>
                    <td>7,59,85,000.00 </td>
                    <td>2,67,40,15,000.00 </td>
                    <td>2.76%</td>
                    </tr>
                    <tr>
                    <td>UNION BANK OF INDIA</td>
                    <td>7,00,00,00,000.00 </td>
                    <td>2,46,17,15,294.57 </td>
                    <td>4,53,82,84,705.43 </td>
                    <td>35.17%</td>
                    </tr>
                    <tr>
                    <td>UCO BANK</td>
                    <td>1,00,00,00,000.00 </td>
                    <td>22,83,73,424.93 </td>
                    <td>77,16,26,575.07 </td>
                    <td>22.84%</td>
                    </tr>
                    <tr>
                    <td>I D B I BANK</td>
                    <td>1,50,00,00,000.00 </td>
                    <td>22,79,55,000.00 </td>
                    <td>1,27,20,45,000.00 </td>
                    <td>15.20%</td>
                    </tr>
                    <tr>
                    <td>CITY UNION BANK FX</td>
                    <td>25,00,00,000.00 </td>
                    <td>6,32,67,418.23 </td>
                    <td>18,67,32,581.77 </td>
                    <td>25.31%</td>
                    </tr>
                    <tr>
                    <td>BANK OF BARODA</td>
                    <td>5,00,00,00,000.00 </td>
                    <td>75,98,92,850.74 </td>
                    <td>4,24,01,07,149.26 </td>
                    <td>15.20%</td>
                    </tr>
                    <tr>
                    <td>CANARA BANK</td>
                    <td>6,50,00,00,000.00 </td>
                    <td>60,81,37,104.48 </td>
                    <td>5,89,18,62,895.52 </td>
                    <td>9.36%</td>
                    </tr>
                    <tr>
                    <td>INDIAN OVERSEAS BANK-FOREX</td>
                    <td>40,00,00,000.00 </td>
                    <td>7,59,85,000.00 </td>
                    <td>32,40,15,000.00 </td>
                    <td>19%</td>
                    </tr>
                    <tr>
                    <td>SMALL INDUS DVP BNK OF IND-FOREX</td>
                    <td>2,00,00,00,000.00 </td>
                    <td>0.00 </td>
                    <td>2,00,00,00,000.00 </td>
                    <td>0%</td>
                    </tr>
                    <tr>
                    <td>BANDHANBANK-KOL</td>
                    <td>20,00,00,000.00 </td>
                    <td>0.00 </td>
                    <td>20,00,00,000.00 </td>
                    <td>0%</td>
                    </tr>
                    <tr>
                    <td>BANK OF INDIA</td>
                    <td>11,00,00,00,000.00 </td>
                    <td>0.00 </td>
                    <td>11,00,00,00,000.00 </td>
                    <td>0%</td>
                    </tr>
                    <tr>
                    <td>BANK OF MAHARASHTRA</td>
                    <td>50,00,00,000.00 </td>
                    <td>0.00 </td>
                    <td>50,00,00,000.00 </td>
                    <td>0%</td>
                    </tr>
                    <tr>
                    <td>DBIL-MUM</td>
                    <td>3,45,00,00,000.00 </td>
                    <td>0.00 </td>
                    <td>3,45,00,00,000.00 </td>
                    <td>0%</td>
                    </tr>
                    <tr>
                    <td>DEVELOPMENT CREDIT BANK LTD FX</td>
                    <td>25,00,00,000.00 </td>
                    <td>0.00 </td>
                    <td>25,00,00,000.00 </td>
                    <td>0%</td>
                    </tr>
                    <tr>
                    <td>Exim Bank</td>
                    <td>1,50,00,00,000.00 </td>
                    <td>0.00 </td>
                    <td>1,50,00,00,000.00 </td>
                    <td>0%</td>
                    </tr>
                    <tr>
                    <td>IDFC-MUM</td>
                    <td>25,00,00,000.00 </td>
                    <td>0.00 </td>
                    <td>25,00,00,000.00 </td>
                    <td>0%</td>
                    </tr>
                    <tr>
                    <td>KARNATAKA BANK LTD-FOREX</td>
                    <td>50,00,00,000.00 </td>
                    <td>0.00 </td>
                    <td>50,00,00,000.00 </td>
                    <td>0%</td>
                    </tr>
                    <tr>
                    <td>NABARD-MUM</td>
                    <td>5,50,00,00,000.00 </td>
                    <td>0.00 </td>
                    <td>5,50,00,00,000.00 </td>
                    <td>0%</td>
                    </tr>
                    <tr>
                    <td>NHBK-MUM</td>
                    <td>2,00,00,00,000.00 </td>
                    <td>0.00 </td>
                    <td>2,00,00,00,000.00 </td>
                    <td>0%</td>
                    </tr>
                    <tr>
                    <td>PUNJAB &amp; SIND BANK-FOREX</td>
                    <td>25,00,00,000.00 </td>
                    <td>0.00 </td>
                    <td>25,00,00,000.00 </td>
                    <td>0%</td>
                    </tr>
                    <tr>
                    <td>SOUTH INDIAN BANK LTD-FOREX</td>
                    <td>50,00,00,000.00 </td>
                    <td>0.00 </td>
                    <td>50,00,00,000.00 </td>
                    <td>0%</td>
                    </tr>
                    <tr>
                    <td>TAMILNADU MERCANTILE FOREX</td>
                    <td>40,00,00,000.00 </td>
                    <td>0.00 </td>
                    <td>40,00,00,000.00 </td>
                    <td>0%</td>
                    </tr>
                    <tr>
                    <td>THE RATNAKAR BANK LTD</td>
                    <td>1,00,00,00,000.00 </td>
                    <td>0.00 </td>
                    <td>1,00,00,00,000.00 </td>
                    <td>0%</td>
                    </tr>
                </tbody>
            </table>
            `;
		}
		$("#counterpartyBreakdown-table").append(string);
	});
	var lab = ["NOOP", "AGL", "VaR"];
	var dat = [
		{
			label: "Utilised",
			data: [3036.35, 6217.81, 815.09],
			backgroundColor: "#264674",
			hoverBackgroundColor: "rgba(255, 107, 107, 1)",
		},
		{
			label: "Available",
			data: [5963.35, 1782.19, 900],
			backgroundColor: "#378F5B",
			hoverBackgroundColor: "#264674",
		},
	];

	if ($("#noopFx-chart").length) {
		var nooFxData = {
			labels: ["USD", "EUR", "GBP", "AUD", "CAD"],
			datasets: [
				{
					label: "",
					data: [5855.53, 0.0, 35.43, 85.68, 134.42],
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

		// Clicking on any canvas and getting id.
		// $(document).on("click", "canvas", function () {
		// 	console.log("Clicked");
		// 	var id = $(this).attr("id");
		// 	console.log(id);
		// });

		var noopFxOptions = {
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
			onClick: function (e) {
				var activePoints = noopFxChart.getElementsAtEvent(e);
				console.log(this.data.labels);
				var selectedIndex = activePoints[0]._index;
				var currency = this.data.labels[selectedIndex];
				if (currency == "USD") {
					this.data.labels = ["Net Spot", "Net Forward"];
					this.data.datasets[0].data = [19137.4, -13281.56];
					this.update();
				}
			},
		};
		var noopFxChartCanvas = $("#noopFx-chart").get(0).getContext("2d");
		var noopFxChart = new Chart(noopFxChartCanvas, {
			type: "bar",
			data: nooFxData,
			options: noopFxOptions,
		});

		$("#resetNoopFx-chart").on("click", function () {
			noopFxChart.data.labels = ["USD", "EUR", "GBP", "AUD", "CAD"];
			noopFxChart.data.datasets[0].data = [
				5855.53, 0.0, 35.43, 85.68, 134.42,
			];
			noopFxChart.update();
		});
	}

	if ($("#counterpartyFx-chart").length) {
		var counterpartyFxData = {
			labels: ["ICICI", "Federal", "CBI", "Kotak", "Indusland"],
			datasets: [
				{
					label: "",
					data: [127.15, 120.55, 70.5, 5.44, 5.34],
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

		var counterpartyFxOptions = {
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
			onClick: function (e) {
				var activePoints = counterpartyFxChart.getElementsAtEvent(e);
				console.log(this.data.labels);
				var selectedIndex = activePoints[0]._index;
				var bank = this.data.labels[selectedIndex];
				if (bank == "ICICI") {
					this.data.labels = ["Forward FX", "Ready FX"];
					this.data.datasets[0].data = [78.16, 336.95];
					this.update();
				}
			},
		};
		var counterpartyFxChartCanvas = $("#counterpartyFx-chart")
			.get(0)
			.getContext("2d");
		var counterpartyFxChart = new Chart(counterpartyFxChartCanvas, {
			type: "bar",
			data: counterpartyFxData,
			options: counterpartyFxOptions,
		});

		$("#resetCounterpartyFx-chart").on("click", function () {
			counterpartyFxChart.data.labels = [
				"ICICI",
				"Federal",
				"CBI",
				"Kotak",
				"Indusland",
			];
			counterpartyFxChart.data.datasets[0].data = [
				293.82, 289.32, 70.5, 5.44, 5.34,
			];
			counterpartyFxChart.update();
		});
	}
});
