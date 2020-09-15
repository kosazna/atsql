from requests_html import HTMLSession

session = HTMLSession()
r = session.get(
    "https://www.tripadvisor.com/Hotel_Review-g189415-d250618-Reviews-or5-Casa_Delfino_Hotel_Spa-Chania_Town_Chania_Prefecture_Crete.html")

r.html.render()

r.ree
print(r.html.html)