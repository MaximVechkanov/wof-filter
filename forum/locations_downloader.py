import urllib.request
from bs4 import *
from urllib.parse  import urljoin


def crawl(pages, depth=None) -> list[str]:
    indexed_url = [] # a list for the main and sub-HTML websites in the main website
    for i in range(depth):
        for page in pages:
            if page not in indexed_url:
                indexed_url.append(page)
                try:
                    c = urllib.request.urlopen(page)
                except:
                    print( "Could not open %s" % page)
                    continue
                soup = BeautifulSoup(c.read())
                links = soup('a') #finding all the sub_links
                for link in links:
                    if 'href' in dict(link.attrs):
                        url = urljoin(page, link['href'])
                        if url.find("'") != -1:
                                continue
                        url = url.split('#')[0] 
                        if url[0:4] == 'http':
                                indexed_url.append(url)
        pages = indexed_url
    return indexed_url

def main():
    pagelist=["https://wof.fish/forum/index.php/forum/43-vodoemy/", "https://wof.fish/forum/index.php/forum/43-vodoemy/page-2"]
    urls = crawl(pagelist, depth=1)
    # print( urls )

    counter = 0
    for url in urls:
        if '/topic' in url:
            counter = counter + 1
            print(url)
            response = urllib.request.urlopen(url)
            webContent = response.read().decode('UTF-8')
            soup = BeautifulSoup(webContent, 'html.parser')
            with open('forum/locations/' + str(counter) + '.txt', 'w') as file:
                 file.write(soup.get_text())

if __name__ == "__main__":
    main()
