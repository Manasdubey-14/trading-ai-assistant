from app.market.instrument import Instrument
from app.providers.instrument_provider import InstrumentProvider


class LocalInstrumentProvider(InstrumentProvider):

    def get_instruments(self) -> list[Instrument]:

        stocks = [
            ("ADANIENT.NS", "Adani Enterprises"),
            ("ADANIPORTS.NS", "Adani Ports and Special Economic Zone"),
            ("APOLLOHOSP.NS", "Apollo Hospitals Enterprise"),
            ("ASIANPAINT.NS", "Asian Paints"),
            ("AXISBANK.NS", "Axis Bank"),
            ("BAJAJ-AUTO.NS", "Bajaj Auto"),
            ("BAJAJFINSV.NS", "Bajaj Finserv"),
            ("BAJFINANCE.NS", "Bajaj Finance"),
            ("BEL.NS", "Bharat Electronics"),
            ("BHARTIARTL.NS", "Bharti Airtel"),
            ("CIPLA.NS", "Cipla"),
            ("COALINDIA.NS", "Coal India"),
            ("DRREDDY.NS", "Dr. Reddy's Laboratories"),
            ("EICHERMOT.NS", "Eicher Motors"),
            ("ETERNAL.NS", "Eternal"),
            ("GRASIM.NS", "Grasim Industries"),
            ("HCLTECH.NS", "HCL Technologies"),
            ("HDFCBANK.NS", "HDFC Bank"),
            ("HDFCLIFE.NS", "HDFC Life Insurance"),
            ("HINDALCO.NS", "Hindalco Industries"),
            ("HINDUNILVR.NS", "Hindustan Unilever"),
            ("ICICIBANK.NS", "ICICI Bank"),
            ("INDIGO.NS", "InterGlobe Aviation"),
            ("INFY.NS", "Infosys"),
            ("ITC.NS", "ITC"),
            ("JSWSTEEL.NS", "JSW Steel"),
            ("JIOFIN.NS", "Jio Financial Services"),
            ("KOTAKBANK.NS", "Kotak Mahindra Bank"),
            ("LT.NS", "Larsen & Toubro"),
            ("M&M.NS", "Mahindra & Mahindra"),
            ("MARUTI.NS", "Maruti Suzuki India"),
            ("MAXHEALTH.NS", "Max Healthcare Institute"),
            ("NESTLEIND.NS", "Nestle India"),
            ("NTPC.NS", "NTPC"),
            ("ONGC.NS", "Oil & Natural Gas Corporation"),
            ("POWERGRID.NS", "Power Grid Corporation of India"),
            ("RELIANCE.NS", "Reliance Industries"),
            ("SBILIFE.NS", "SBI Life Insurance"),
            ("SBIN.NS", "State Bank of India"),
            ("SHRIRAMFIN.NS", "Shriram Finance"),
            ("SUNPHARMA.NS", "Sun Pharmaceutical Industries"),
            ("TATACONSUM.NS", "Tata Consumer Products"),
            ("TATASTEEL.NS", "Tata Steel"),
            ("TCS.NS", "Tata Consultancy Services"),
            ("TECHM.NS", "Tech Mahindra"),
            ("TITAN.NS", "Titan Company"),
            ("TMPV.NS", "Tata Motors Passenger Vehicles"),
            ("TRENT.NS", "Trent"),
            ("ULTRACEMCO.NS", "UltraTech Cement"),
            ("WIPRO.NS", "Wipro"),
        ]

        return [
            Instrument(
                symbol=symbol,
                name=name,
                exchange="NSE",
                segment="NSE",
                instrument_type="EQ",
            )
            for symbol, name in stocks
        ]