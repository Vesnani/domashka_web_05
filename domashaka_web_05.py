import asyncio
import aiohttp
from datetime import datetime, timedelta
import argparse

url = 'https://api.privatbank.ua/p24api/exchange_rates?json&date='


async def get_exchange_rate(session, url, date_str):
    async with session.get(url + date_str) as response:
        if response.status == 200:
            return date_str, await response.json()
        else:
            print(f"Failed to fetch data for {date_str}. Status code: {response.status}")
            return date_str, None


async def main(number_of_days, additional_currencies=None):
    try:
        number_of_days = int(number_of_days)
        if number_of_days > 10:
            print("Please enter no more than 10 days.")
            return

        current_date = datetime.now()
        date_range = [(current_date - timedelta(days=day)).strftime('%d.%m.%Y') for day in range(number_of_days)]

        async with aiohttp.ClientSession() as session:
            tasks = [get_exchange_rate(session, url, date_str) for date_str in date_range]
            results = await asyncio.gather(*tasks)

            exchange_rates_list = []
            for date_str, exchange_rate in results:
                if exchange_rate:
                    rates = {
                        currency['currency']: {'sale': currency['saleRateNB'], 'purchase': currency['purchaseRateNB']}
                        for currency in exchange_rate['exchangeRate']
                        if currency['currency'] in ['USD', 'EUR'] or (additional_currencies and currency['currency'] in additional_currencies)
                    }
                    exchange_rates_list.append({date_str: rates})

            print(exchange_rates_list)

    except ValueError:
        print("Invalid input. Please enter a valid number of days.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("number_of_days", help="Number of days to get exchange rates", type=int)
    parser.add_argument("-cur", nargs='+', help="Additional currencies", default=None)
    args = parser.parse_args()

    asyncio.run(main(args.number_of_days, args.cur))
