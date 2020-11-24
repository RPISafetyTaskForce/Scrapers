import requests
import datetime
import json

from discord_webhook import DiscordEmbed, DiscordWebhook

import traceback


try:
    import webhook_urls

    webhooks = webhook_urls.webhooks
except:
    print("No discord webhooks supplied - data will just be stored locally")
    traceback.print_exc()
    webhooks = None

START_DATE = str(datetime.datetime.now() - datetime.timedelta(weeks=2)).split(" ")[0]
SITE = f"https://portal.arms.com/Home/DetailsRequest?_search=false&nd=1603496151216&rows=50&page=1&sidx=Date&sord=asc&AgencyId=92&CrimeTypesIds=1&CrimeTypesIds=20&CrimeTypesIds=26&CrimeTypesIds=2&CrimeTypesIds=21&CrimeTypesIds=27&CrimeTypesIds=5&CrimeTypesIds=22&CrimeTypesIds=28&CrimeTypesIds=6&CrimeTypesIds=10&CrimeTypesIds=7&CrimeTypesIds=13&CrimeTypesIds=11&CrimeTypesIds=9&CrimeTypesIds=3&CrimeTypesIds=12&CrimeTypesIds=8&CrimeTypesIds=4&CrimeTypesIds=17&CrimeTypesIds=24&CrimeTypesIds=23&CrimeTypesIds=18&CrimeTypesIds=25&CrimeTypesIds=14&CrimeTypesIds=19&CrimeTypesIds=15&fakeId=0.664140281677307&beginDate={START_DATE}&__ko_mapping__=%5Bobject+Object%5D"
THUMBNAIL_IMG = "https://images-na.ssl-images-amazon.com/images/I/71D1O6EA8sL.png"


def generate_embed(offense, loc, time, details, offenseDetails):
    global THUMBNAIL_IMG
    embed = DiscordEmbed(color=15158332)
    embed.add_embed_field(name="Type", value=offense, inline=False)
    embed.add_embed_field(name="Location", value=loc, inline=False)
    embed.add_embed_field(name="Time", value=time, inline=False)
    embed.add_embed_field(
        name="Offense Info", value=f"{details}\n{offenseDetails}", inline=False
    )
    embed.set_thumbnail(url=THUMBNAIL_IMG)
    return embed

img = "https://i.imgur.com/WdSyxXi.jpgs"


def check_for_rpi_alerts(old_alert_ids):
    global SITE
    global webhooks
    global img
    data = json.loads(requests.get(SITE).text)
    spotted_alert_ids = []

    webhook2 = DiscordWebhook(
        url=webhooks,
        username="RPI Crime Watch",
        avatar_url=img,
        content="Crime detected!",
    )
    embeds = []
    for entry in data["rows"]:
        id = entry["id"]
        spotted_alert_ids.append(id)
        if id in old_alert_ids:
            continue
        entry = entry["cell"]
        date = entry["Date"]
        offense = entry["Offense"]
        location = entry["Location"]
        details = entry["Details"]
        offenseDetails = entry["OffensesDetail"]
        embeds.append(generate_embed(offense, location, date, details, offenseDetails))

        print(
            f"Found new offense: {offense} @ {location} on {date}. \nInfo: {details}\n{offenseDetails}"
        )

    for embed in embeds:
        webhook2.add_embed(embed)
        webhook2.execute()
        webhook2.embeds = []

    return spotted_alert_ids


def load_old_alert():
    try:
        with open(".crimecache", "r") as f:
            return [x.strip() for x in f.readlines()]
    except:
        return []


def write_alerts(data):
    with open(".crimecache", "w") as f:
        for x in data:
            f.write(f"{x}\n")


def main():
    data = check_for_rpi_alerts(load_old_alert())
    write_alerts(data)


if __name__ == "__main__":
    main()
