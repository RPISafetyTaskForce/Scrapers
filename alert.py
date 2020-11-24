import requests

from bs4 import BeautifulSoup
import html2text
from discord_webhook import DiscordEmbed, DiscordWebhook
import traceback


try:
    import webhook_urls

    webhooks = webhook_urls.webhooks
except:
    print("No discord webhooks supplied - data will just be stored locally")
    traceback.print_exc()
    webhooks = None


SITE = "https://alert.rpi.edu/"
IMG = "https://i.imgur.com/WdSyxXi.jpgs"

def check_for_rpi_alerts():
    global SITE
    data = requests.get(SITE)
    soup = BeautifulSoup(data.text, features="lxml")
    incident_type = "incident"
    for incident in soup.findAll("div", {"class": incident_type}):
        return html2text.html2text(str(incident))

def main():
    global webhooks
    global IMG
    data = check_for_rpi_alerts()
    webhook2 = DiscordWebhook(
        url=webhooks, username="RPI Public Safety", avatar_url=IMG,
    )
    embed = DiscordEmbed(color=15158332)
    embed.add_embed_field(name="Alert Description", value=data)
    embed.set_author(name="Public Safety", url="https://alert.rpi.edu/")
    embed.set_thumbnail(url="https://i.imgur.com/WdSyxXi.jpg")
    webhook2.add_embed(embed)
    webhook2.execute()

if __name__ == "__main__":
    main()