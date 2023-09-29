from flask import Flask, render_template, request, send_file, jsonify
import pandas as pd
import wbdata
import json
import csv

app = Flask(__name__)

# Define the specific country code for Nigeria
NIGERIA_COUNTRY_CODE = "NGA"

# List of available data options for the user to choose from
DATA_OPTIONS = [
    {'id': 'FB.AST.NPER.ZS', 'name': 'Access to Banking (% of population)'},
    {'id': 'EG.ELC.ACCS.ZS', 'name': 'Access to Electricity (% of Population)'},
    {'id': 'SE.ADT.LITR.ZS', 'name': 'Adult literacy rate (% ages 15 and older)'},
    {'id': 'IS.AIR.GOOD.MT.K1', 'name': 'Air Transport, Goods Transported (1000 metric tons)'},
    {'id': 'IS.AIR.PSGR', 'name': 'Air Transport, Passengers Carried'},
    {'id': 'IS.AIR.DPRT', 'name': 'Airports'},
    {'id': 'FB.BNK.CAPA.ZS', 'name': 'Banking Sector Capitalization Ratio (%)'},
    {'id': 'EN.ATM.CO2E.PC', 'name': 'CO2 Emissions (metric tons per capita)'},
    {'id': 'EN.ATM.CO2E.SF.ZS', 'name': 'CO2 Emissions from Solid Fuel Consumption (% of total)'},
    {'id': 'IC.FRM.CORR.ZS', 'name': 'Control of Corruption (percentile rank)'},
    {'id': 'AG.PRD.CROP.XD', 'name': 'Crop Production Index'},
    {'id': 'SH.XPD.CHEX.GD.ZS', 'name': 'Current Health Expenditure (% of GDP)'},
    {'id': 'FS.AST.PRVT.GD.ZS', 'name': 'Domestic Credit to Private Sector (% of GDP)'},
    {'id': 'IC.REG.COST.PC.ZS', 'name': 'Ease of Doing Business Score (0=difficult to 100=easy)'},
    {'id': 'EG.IMP.CONS.ZS', 'name': 'Electricity Imports (% of Total Electricity Use)'},
    {'id': 'EG.ELC.LOSS.ZS', 'name': 'Electricity Losses (% of Output)'},
    {'id': 'EG.USE.PCAP.KG.OE', 'name': 'Electricity Use (Kilograms of Oil Equivalent per Capita)'},
    {'id': 'EG.FEC.RNEW.ZS', 'name': 'Electricity from Renewable Sources (% of Total)'},
    {'id': 'SL.AGR.EMPL.ZS', 'name': 'Employment in Agriculture (% of total employment)'},
    {'id': 'SL.EMP.TOTL.SP.ZS', 'name': 'Employment to Population Ratio'},
    {'id': 'SL.EMP.1524.SP.ZS', 'name': 'Employment to Population Ratio, Ages 15-24 (%)'},
    {'id': 'NE.EXP.GNFS.ZS', 'name': 'Exports of Goods and Services (% of GDP)'},
    {'id': 'NE.EXP.GNFS.KD.ZG', 'name': 'Exports of Goods and Services (Annual % Growth)'},
    {'id': 'NE.EXP.GNFS.KD', 'name': 'Exports of Goods and Services (Constant 2010 US$)'},
    {'id': 'NE.EXP.GNFS.CD', 'name': 'Exports of Goods and Services (Current US$)'},
    {'id': 'AG.PRD.FOOD.XD', 'name': 'Food Production Index'},
    {'id': 'BX.KLT.DINV.CD.WD', 'name': 'Foreign Direct Investment (in current US dollars)'},
    {'id': 'BX.KLT.DINV.WD.GD.ZS', 'name': 'Foreign direct investment, net inflows (% of GDP)'},
    {'id': 'NY.GDP.MKTP.CD', 'name': 'GDP (current US$)'},
    {'id': 'NY.GDP.MKTP.KD.ZG', 'name': 'GDP Growth (%)'},
    {'id': 'NY.GDP.PCAP.KD.ZG', 'name': 'GDP Per Capita Growth (%)'},
    {'id': 'NY.GDP.PCAP.CD', 'name': 'GDP per capita (current US$)'},
    {'id': 'IQ.CPA.GNDR.XQ', 'name': 'Gender Equality Index (1=best)'},
    {'id': 'SI.POV.GINI', 'name': 'Gini Index (Income Inequality)'},
    {'id': 'GC.XPN.TOTL.GD.ZS', 'name': 'Government Expenditure (% of GDP)'},
    {'id': 'SE.XPD.TOTL.GD.ZS', 'name': 'Government Expenditure on Education (% of GDP)'},
    {'id': 'NE.GDI.FTOT.ZS', 'name': 'Gross Fixed Capital Formation (% of GDP)'},
    {'id': 'NE.GDI.FTOT.CD', 'name': 'Gross Fixed Capital Formation (in current US dollars)'},
    {'id': 'NY.GNS.ICTR.ZS', 'name': 'Gross savings (% of GDP)'},
    {'id': 'SH.XPD.CHEX.PC.CD', 'name': 'Health Expenditure per Capita (current US$)'},
    {'id': 'UNDP.HDI.XD', 'name': 'Human Development Index (HDI)'},
    {'id': 'NE.IMP.GNFS.ZS', 'name': 'Imports of Goods and Services (% of GDP)'},
    {'id': 'NE.IMP.GNFS.KD', 'name': 'Imports of Goods and Services (in constant US dollars)'},
    {'id': 'NE.IMP.GNFS.CD', 'name': 'Imports of Goods and Services (in current US dollars)'},
    {'id': 'NE.IMP.GNFS.KD.ZG', 'name': 'Imports of Goods and Services Growth Rate (%)'},
    {'id': 'SI.DST.FRST.10', 'name': 'Income Share Held by Lowest 10%'},
    {'id': 'SI.DST.04TH.20', 'name': 'Income Share Held by Top 10%'},
    {'id': 'FP.CPI.TOTL.ZG', 'name': 'Inflation (% change in consumer prices)'},
    {'id': 'IT.NET.USER.ZS', 'name': 'Internet Users (% of population)'},
    {'id': 'SL.TLF.CACT.ZS', 'name': 'Labor Force Participation Rate'},
    {'id': 'SL.TLF.CACT.FM.ZS', 'name': 'Labor Force Participation Rate, Female (% of Female Population Ages 15+)'},
    {'id': 'SL.TLF.CACT.MA.ZS', 'name': 'Labor Force Participation Rate, Male (% of Male Population Ages 15+)'},
    {'id': 'FR.INR.LEND', 'name': 'Lending Interest Rate (%)'},
    {'id': 'AG.PRD.LVSK.XD', 'name': 'Livestock Production Index'},
    {'id': 'SE.SEC.CMPT.LO.ZS', 'name': 'Lower Secondary Completion Rate (% of relevant age group)'},
    {'id': 'CM.MKT.LCAP.GD.ZS', 'name': 'Market Capitalization of Listed Domestic Companies (% of GDP)'},
    {'id': 'SH.STA.MMRT', 'name': 'Maternal Mortality Ratio (per 100,000 live births)'},
    {'id': 'EN.ATM.METH.AG.ZS', 'name': 'Methane Emissions from Agriculture (% of total)'},
    {'id': 'IT.CEL.SETS.P2', 'name': 'Mobile Cellular Subscriptions (per 100 people)'},
    {'id': 'SH.DYN.MORT', 'name': 'Mortality Rate, Under-5 (per 1,000 live births)'},
    {'id': 'SI.POV.DDAY', 'name': 'Multidimensional Poverty Headcount Ratio'},
    {'id': 'SI.POV.NAHC', 'name': 'National Headcount Ratio of Multidimensional Poverty'},
    {'id': 'NE.RSB.GNFS.ZS', 'name': 'Net Trade (% of GDP)'},
    {'id': 'NE.RSB.GNFS.CD', 'name': 'Net Trade (in current US dollars)'},
    {'id': 'EN.ATM.NOXE.AG.ZS', 'name': 'Nitrous Oxide Emissions from Agriculture (% of total)'},
    {'id': 'SP.POP.GROW', 'name': 'Population Growth (%)'},
    {'id': 'EN.POP.DNST', 'name': 'Population density (people per sq. km)'},
    {'id': 'SP.POP.TOTL', 'name': 'Population, total'},
    {'id': 'SI.POV.LMIC', 'name': 'Poverty Headcount Ratio at $3.20 a day (2011 PPP) (% of population)'},
    {'id': 'SN.ITK.DEFC.ZS', 'name': 'Prevalence of Undernourishment (% of population)'},
    {'id': 'SE.PRM.CMPT.ZS', 'name': 'Primary Completion Rate (% of relevant age group)'},
    {'id': 'IC.CRD.PRVT.ZS', 'name': 'Private Credit by Depository Corporations (% of GDP)'},
    {'id': 'IQ.CPA.PROP.XQ', 'name': 'Property Rights Index (0=low to 100=high)'},
    {'id': 'SG.GEN.PARL.ZS', 'name': 'Proportion of Seats Held by Women in National Parliaments (%)'},
    {'id': 'IS.RRS.TOTL.KM', 'name': 'Railways (Total Route-Kilometers)'},
    {'id': 'NY.GDP.MKTP.KD', 'name': 'Real GDP (in current US dollars)'},
    {'id': 'SG.VAW.REAS.ZS', 'name': 'Reasons for Not Reporting Violence Incidence (%)'},
    {'id': 'SG.VAW.REFU.ZS', 'name': 'Refusal to Marry as a Percentage of Violence Incidence (%)'},
    {'id': 'EG.ELC.RNEW.ZS', 'name': 'Renewable Energy Share of Total Electricity Output (%)'},
    {'id': 'ER.H2O.FWTL.ZS', 'name': 'Renewable Internal Freshwater Resources (% of total freshwater withdrawal)'},
    {'id': 'EG.ELC.ACCS.RU.ZS', 'name': 'Rural Access to Electricity (% of Rural Population)'},
    {'id': 'SE.PRM.NENR', 'name': 'School Enrollment, Primary (% net)'},
    {'id': 'CM.MKT.LCAP.CD', 'name': 'Stock Market Capitalization (Current US dollars)'},
    {'id': 'IC.LGL.CRED.XQ', 'name': 'Strength of Legal Rights Index (0=weak to 12=strong)'},
    {'id': 'AG.SRF.TOTL.K2', 'name': 'Surface area (sq. km)'},
    {'id': 'NE.TRD.GNFS.ZS', 'name': 'Trade (% of GDP)'},
    {'id': 'SL.UEM.TOTL.ZS', 'name': 'Unemployment Rate'},
    {'id': 'SL.UEM.TOTL.FE.ZS', 'name': 'Unemployment Rate, Female (% of Female Labor Force)'},
    {'id': 'SL.UEM.TOTL.MA.ZS', 'name': 'Unemployment Rate, Male (% of Male Labor Force)'},
    {'id': 'EG.ELC.ACCS.UR.ZS', 'name': 'Urban Access to Electricity (% of Urban Population)'},
    {'id': 'SP.URB.TOTL.IN.ZS', 'name': 'Urban population (% of total)'},
    {'id': 'SL.EMP.VULN.ZS', 'name': 'Vulnerable Employment (% of total employment)'},
    {'id': 'SL.UEM.1524.FE.ZS', 'name': 'Youth Unemployment Rate, Ages 15-24, Female (% of Female Labor Force Ages 15-24)'},
    {'id': 'SL.UEM.1524.MA.ZS', 'name': 'Youth Unemployment Rate, Ages 15-24, Male (% of Male Labor Force Ages 15-24)'},
    {'id': 'SE.ADT.1524.LT.ZS', 'name': 'Youth literacy rate (% ages 15-24)'},
]


# Selected data variables
selected_data = []

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data_option_id = request.form.get('data_option')
        data_option = DATA_OPTIONS[int(data_option_id)]
        selected_data.append(data_option)  # Add the selected data option to the list
    return render_template('index.html', data_options=DATA_OPTIONS, selected_data=selected_data)


@app.route('/confirm_download', methods=['POST'])
def confirm_download():
    selected_options = request.form.get('selected_options')

    if not selected_options:
        return "No valid data options selected. Please go back and select data options."

    selected_options = json.loads(selected_options)

    # Check if there are any valid data options selected
    if not selected_options:
        return "No valid data options selected. Please go back and select data options."

    # Initialize a dictionary to store data for selected options
    selected_data_dict = {}

    for option_index in selected_options:
        option_index = int(option_index)
        if option_index >= 0 and option_index < len(DATA_OPTIONS):
            data_option = DATA_OPTIONS[option_index]
            indicator_id = data_option["id"]
            data = wbdata.get_data(indicator_id, country="NGA")

            if data:
                # Extract the relevant data
                data_list = {d['date']: d['value'] for d in data if d['value'] is not None}
                selected_data_dict[data_option["name"]] = data_list

    if not selected_data_dict:
        return "No valid data found for the selected options."

    # Get a sorted list of unique years across all data variables
    all_years = sorted({year for data in selected_data_dict.values() for year in data.keys()})

    # Create a list of dictionaries, each containing the year and values for selected data variables
    combined_data = [{"Year": year, **{variable: data.get(year, '') for variable, data in selected_data_dict.items()}} for year in all_years]

    # Generate a CSV file containing the combined data
    csv_filename = "selected_data.csv"
    with open(csv_filename, "w", newline="") as csvfile:
        fieldnames = ["Year"] + list(selected_data_dict.keys())
        csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_writer.writerows(combined_data)

    return send_file(
        csv_filename,
        as_attachment=True,
        download_name="selected_data.csv",
        mimetype="text/csv",
    )

@app.route('/documentation')
def documentation():
    return render_template('documentation.html', DATA_OPTIONS=DATA_OPTIONS)

if __name__ == "__main__":
    app.run(debug=True)