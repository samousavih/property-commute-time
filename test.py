import asyncio
from lxml import html
import requests
import googlemaps
import json
from datetime import datetime
from pyppeteer import launch
from urllib.parse import urlencode, quote_plus


async def main():
    browser = await launch()
    gm_page = await browser.newPage()

    for pageNumber in range(1, 10):
        rea_page = requests.get(
            'https://www.realestate.com.au/buy/in-hawthorn,+vic+3122/list-'+str(pageNumber)+'?activeSort=price-asc')
        tree = html.fromstring(rea_page.content)
        addresses = tree.xpath(
            '//*[@id="page-wrapper"]/span/div/div[2]/div[1]/div[2]/div/*/article/div[4]/div[1]/div[2]/div/h2/a/span')

        for address in addresses:
            print('address: ', address.text)

            scaped_address = quote_plus(address.text)
            try:
                await gm_page.goto('https://www.google.com/maps/dir/'+scaped_address + '/231+Punt+Rd,+Richmond+VIC+3121')
                element = await gm_page.querySelector(
                    '#section-directions-trip-2 > div.section-directions-trip-description > div:nth-child(2) > div.section-directions-trip-numbers > div')
                if element != None:
                    comm_time = await gm_page.evaluate('(element) => element.textContent', element)
                    print('commute time: ', comm_time)
            except Exception as inst:
                print(inst)
                await browser.close()
                browser = await launch()
                gm_page = await browser.newPage()

    await browser.close()
asyncio.get_event_loop().run_until_complete(main())
