# class="freeAdPadding"
import requests
import os
from lxml import etree
# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.message import EmailMessage


class ApartmentAD:
    def __init__(self, title, link):
        self.cell_phone_xpath = '//*[@id="info-phone"]'
        self.start_url = "https://www.vansky.com/info/"
        self.title = title.text
        self.link = self.start_url + link
    
    def load_data(self):
        return {"title": self.title,
                "link": self.link,
                "cell": self._get_phone_num()}

    def _get_phone_num(self):
        res = requests.get(self.link)
        res.encoding = "utf-8"
        if (res.status_code == 200):
            ad_page = etree.HTML(res.text)
            cellphone = ad_page.xpath(self.cell_phone_xpath)[0].text
            return cellphone

def parse_data(data_dict):
    content = "Title: {title}\n \
               Link: {link}\n \
               Cell Phone: {cell}\n\n".format(title=data_dict.get("title"),
                                          link=data_dict.get("link"),
                                          cell=data_dict.get("cell"))
    return content

def send_email(content):
    msg = EmailMessage()
    msg.set_content(content)

    # me == the sender's email address
    # you == the recipient's email address
    msg['Subject'] = "Vansky apartment news"
    msg['From'] = os.environ["email_from"]
    msg['To'] = os.environ["email_from"]
    # msg['To'] = ",".join(recipients)

    # Send the message via our own SMTP server.
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(os.environ["email_from"], os.environ["email_pwd"])
    server.send_message(msg)
    server.quit()

content = ""
url =  "https://www.vansky.com/info/ZFBG08.html?page={}"

page_num = 1
res = requests.get(url.format(page_num))
res.encoding = "utf-8"


if (res.status_code == 200):
    print("\n第{}页短评爬取成功！".format(page_num))
    x = etree.HTML(res.text)
    apt_ads = x.xpath('//tr[@class="freeAdPadding"]')
    for apt_ad in apt_ads:
        apt_ad_obj = ApartmentAD(apt_ad.xpath('.//a[@class=" adsTitleFont"]')[0],
                                 apt_ad.xpath('.//a[@class=" adsTitleFont"]/@href')[0])
        data_dict = apt_ad_obj.load_data()
        content += parse_data(data_dict)
    
    send_email(content)
        
else:
    print("\n第{}页爬取失败！".format(page_num))