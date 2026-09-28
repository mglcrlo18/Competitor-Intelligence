"""
financials.py
Retrieves financial data for public competitors via Yahoo Finance (yfinance)
and generates free regulatory registry lookups for private entities.
"""
from typing import Dict, Any, Optional
import yfinance as yf


def fetch_public_company_financials(ticker: str) -> Optional[Dict[str, Any]]:
    """
    Fetches real-time financial standing for public companies for free via yfinance.
    """
    try:
        stock = yf.Ticker(ticker.upper())
        info = stock.info
        
        # Financial health metrics
        summary = {
            "name": info.get("shortName") or info.get("longName") or ticker,
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "market_cap": info.get("marketCap"),
            "currency": info.get("currency", "USD"),
            "total_revenue": info.get("totalRevenue"),
            "revenue_growth": info.get("revenueGrowth"),
            "gross_margins": info.get("grossMargins"),
            "operating_margins": info.get("operatingMargins"),
            "ebitda": info.get("ebitda"),
            "free_cashflow": info.get("freeCashflow"),
            "total_cash": info.get("totalCash"),
            "total_debt": info.get("totalDebt"),
            "current_ratio": info.get("currentRatio"),
            "pe_ratio": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
        }
        return summary
    except Exception as e:
        print(f"Error fetching financials for ticker {ticker}: {e}")
        return None


def get_private_company_registry_links(company_name: str) -> Dict[str, str]:
    """
    Generates zero-cost links to statutory corporate filing portals for private company investigation.
    """
    return {
        "SEC EDGAR Company Search (US)": f"https://www.sec.gov/edgar/searchedgar/companysearch?companyName={company_name}",
        "UK Companies House (Free Accounts & Ownership)": f"https://find-and-update.company-information.service.gov.uk/search?q={company_name}",
        "OpenCorporates Global Registry": f"https://opencorporates.com/companies?q={company_name}",
        "Crunchbase Public Profile": f"https://www.crunchbase.com/textsearch?q={company_name}"
    }


if __name__ == "__main__":
    data = fetch_public_company_financials("MSFT")
    if data:
        print("Market Cap:", data["market_cap"])
        print("Total Revenue:", data["total_revenue"])
