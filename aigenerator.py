import openai
import config
from bs4 import BeautifulSoup
import requests
import urllib.request
import random


openai.api_key = config.OPENAI_API_KEY


def generateBlogTopics(prompt1):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt="Generate 3 blog topics ideas for ""{}"": \n \n".format(prompt1),
        temperature=0.7,
        max_tokens=100,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    return response['choices'][0]['text'].strip()


def generateBlogSections(prompt1):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt="Expand the blog title in to high level blog sections: {} \n\n".format(prompt1),
        # prompt="Expand the blog title in to high level blog sections: {} \n\n- Introduction: ".format(prompt1),
        temperature=0.6,
        max_tokens=200,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    return response['choices'][0]['text']


def blogSectionExpander(prompt1, prompt2):
    art = []

    for i in prompt1:
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt="Blog topic: " + prompt2 + "\nWrite blog section: " + i + "\nExpand the blog section, write detailed blog section in a professional, witty and clever tone:\nIntroduction:",
            temperature=0.7,
            max_tokens=2000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        text = response['choices'][0]['text'].strip()
        text = text.strip().replace('\n\n', '<br /><br />').strip()
        # text = text.replace('\n', '<br />')

        counter = random.randint(1,1000)
        all = "<h3>" + str(i).strip('-') + "</h3>\n" + str(text).strip('-') + "\n"

        #Only for content testing
        #with open(f"{i[0:15]}{counter}.txt", "w") as file:
        #    file.write(all)

        art.append(all)
        vtitle = prompt2
        article = [vtitle, art]
    return article


def featured_image(i):
    URL = "https://www.freepik.com/search?format=search&query=" + i  # Replace this with the website's URL
    getURL = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(getURL.text, 'html.parser')

    image_tags = soup.find_all(class_='showcase__item')

    links = []
    for a in image_tags:
        links.append(a['data-image'])

    randomlink = random.choice(links)
    img_name = randomlink.split('/')[-1]
    img_name = img_name.split('?')[0]

    urllib.request.urlretrieve(randomlink, "static/images/" + img_name)
    return img_name
