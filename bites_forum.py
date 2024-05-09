#!/bin/python3

bites = {
    'post-1-0-11110600-1440831591' : 'Мясо краба',
    'post-1-0-66027600-1440762771' : "Мясо мидии",
    'post-1-0-55813400-1440831680' : "Мясо рапана",
    'post-1-0-46316200-1440758711' : 'Мясо рыбы',
    'post-1-0-85012000-1440756630' : "Икринка",
    "post-1-0-31961200-1440760469" : "Живец",
    "post-1-0-49768600-1440831650" : "Мясо моллюска",
    'post-1-0-75358300-1440680678' : "Поденка",
    'post-1-0-77247700-1527047139' : 'Личинка ручейника',
    'post-1-0-01716700-1440680816' : 'Мотыль',
    'post-1-0-04805500-1440680910' : 'Личинка короеда',
    'post-1-0-35424300-1440681061' : 'Бокоплав',
    'post-1-0-74425100-1440831437' : 'Муха',
    'post-1-0-23744500-1440759070' : 'Кузнечик',
    'post-1-0-37540200-1440757047' : 'Креветка',
    'kusochek_sala' : 'Кусок сала',
    'post-1-0-09412400-1439478508' : 'Дождевой червь',
    "post-1-0-76968300-1440677782" : 'Опарыш',
    'post-1-0-17998000-1440831481' : 'Мякиш хлеба',
    'post-1-0-53637500-1440762668' : 'Муравей',
    'post-1-0-10187700-1440831531' : 'Мясо',
    'post-1-0-53771100-1440681006' : 'Капуста',
    'post-1-0-72683000-1440761688' : 'Зелень и водоросли',
    'post-1-0-22593500-1440760321' : 'Жук',
    'post-1-0-29029300-1440831309' : 'Мелкая рыбка',
    # '' : '',
    # '' : '',
    # '' : '',
    # '' : '',
    # '' : '',
    # '' : '',
    # '' : '',
}

with open('bites_forum') as file:
    raw = file.read()

    nole = raw.replace('\n', '')

    pics = nole.split('.png')

    del pics[-1]

    # print(pics)

    for p in pics:
        if p not in bites:
            print("New pic: " + p)
        print("    - " + bites[p])