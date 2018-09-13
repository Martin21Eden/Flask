import requests
from bs4 import BeautifulSoup
from TED import db, Post

url = 'https://content.guardianapis.com/technology'
page = 1
bd_data = [r.url for r in db.session.query(Post.url)]


post_data = {}

while True:
    difference_list=[]
    payload = {'api-key': 'caa32833-084d-4ce2-9637-825c5d4945a0', 'page': f'{page}'}
    posts_list = [i['webUrl'] for i in requests.get(url, params=payload).json()['response']['results']]
    for item in set(posts_list).difference(bd_data):
        difference_list.append(item)

    if len(difference_list) > 0:
        # print(difference_list[0])
        response = requests.get(difference_list[0]).text
        soup = BeautifulSoup(response, 'lxml')
        teg = soup.find('div', class_="content__main-column content__main-column--article js-content-main-column ")
        title = soup.find('h1', class_="content__headline ")
        # print(title.text)
        image = soup.find('img', class_="maxed responsive-img")['src']
        # print(image)
        content = []
        text = (p.text for p in soup.find('div', class_="content__article-body from-content-api js-article__body").find_all('p'))
        for p in text:
            content.append(p)
        post_data['title'] = title.text
        post_data['url'] = difference_list[0]
        post_data['content'] = ''.join(content)
        post_data['file_image'] = image
        post = Post(url=post_data['url'], title=post_data['title'], image_file=post_data['file_image'],
                    content=post_data['content'])
        db.session.add(post)
        db.session.commit()
        break
    page += 1

