import asyncio
from lxml import html
import requests
import googlemaps
import json
from datetime import datetime
from pyppeteer import launch
from urllib.parse import urlencode, quote_plus
import heapq
import time


def convert_to_minute(comm_time):
    try:
        time_value = time.strptime(comm_time, '%H h %M min')
    except ValueError:
        try:
            time_value = time.strptime(comm_time, '%H h')
        except ValueError:
            time_value = time.strptime(comm_time, '%M min')
    return time_value.tm_hour * 60 + time_value.tm_min


async def main():
    browser = await launch()
    gm_page = await browser.newPage()

    minHeap = []
    heapq.heapify(minHeap)

    for pageNumber in range(1, 10):
        rea_page = requests.get(
            'https://www.realestate.com.au/buy/property-house-townhouse-with-2-bedrooms-between-0-500000/list-'+str(pageNumber)+'?numParkingSpaces=1&numBaths=1&keywords=brand%2Bnew&source=refinement')
        tree = html.fromstring(rea_page.content)
        addresses = tree.xpath(
            '//*[@id="page-wrapper"]/span/div/div[2]/div[1]/div[2]/div/*/article/div[4]/div[1]/div[2]/div/h2/a/span')

        for address in addresses:
            print('address: ', address.text)

            scaped_address = quote_plus(address.text)
            try:
                gm_link = 'https://www.google.com/maps/dir/' + \
                    scaped_address + '/231+Punt+Rd,+Richmond+VIC+3121'
                print(gm_link)
                await gm_page.goto(gm_link)
                element = await gm_page.querySelector(
                    '#section-directions-trip-2 > div.section-directions-trip-description > div:nth-child(2) > div.section-directions-trip-numbers > div')
                if element != None:
                    comm_time = await gm_page.evaluate('(element) => element.textContent', element)
                    print('commute time: ', comm_time)

                    heapq.heappush(
                        minHeap, (convert_to_minute(comm_time), address.text))

            except Exception as inst:
                print(inst)
                await browser.close()
                browser = await launch()
                gm_page = await browser.newPage()
    print("Top 10 addresses:")
    for item in minHeap[:10]:
        print(item)
    await browser.close()
asyncio.get_event_loop().run_until_complete(main())
