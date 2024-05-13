#!/bin/python3

bites = {
    'post-1-0-09412400-1439478508' : 'Дождевой червь',
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
    "post-1-0-76968300-1440677782" : 'Опарыш',
    'post-1-0-17998000-1440831481' : 'Мякиш хлеба',
    'post-1-0-53637500-1440762668' : 'Муравей',
    'post-1-0-10187700-1440831531' : 'Мясо',
    'post-1-0-53771100-1440681006' : 'Капуста',
    'post-1-0-72683000-1440761688' : 'Зелень и водоросли',
    'post-1-0-22593500-1440760321' : 'Жук',
    'post-1-0-29029300-1440831309' : 'Мелкая рыбка',
    'post-1-0-01893700-1440680716' : 'Пиявка',
    'post-1-0-63392600-1440757432' : 'Кубик сыра',
    'post-1-0-46258100-1440831850' : 'Перловка',
    'post-1-0-59185900-1440761867' : 'Тесто',
    'post-1-0-03518600-1440758085' : 'Кукуруза',
    'post-1-0-31631100-1440831234' : 'Манка',
    'post-1-0-38020200-1440760197' : 'Филе рака',
    'post-1-0-24695000-1526479224' : 'Детрит',
    'post-1-0-67705200-1440754540' : 'Бабочка',
    'post-1-0-02947100-1440760557' : 'Зерно',
    'post-1-0-32837200-1440762062' : 'Стрекоза',
    'post-1-0-29909600-1440831709' : 'Мясо улитки',
    'post-1-0-28546300-1440756595' : 'Долька помидора',
    'post-1-0-59700000-1440760590' : 'Зеленый горошек',
    'post-1-0-77021600-1440754584' : 'Бойл',
    'post-1-0-88741700-1440762703' : 'Макуха',
    'post-1-0-55373300-1440680756' : 'Пескоройка',
    'post-1-0-88862500-1440680541' : 'Картофель',
    'post-1-0-58771000-1440830791' : 'Макароны',
    'post-1-0-85123200-1440831737' : 'Мышь',
    'post-1-0-93406200-1440831189' : 'Лягушка',
    'post-1-0-63071200-1440761799' : 'Вяленая рыба',
    'post-1-0-06013800-1440831353' : 'Морской гребешок',
    'post-1-0-68401700-1440680594' : 'Нереис',
    'post-1-0-23520700-1526479134' : 'Паук',
    'post-1-0-17238900-1440756723' : 'Кальмар',
    'post-1-0-88374400-1526479365' : 'Водяной ослик',
    'post-1-0-59452500-1446545849' : 'Цикада',
    # '' : '',
    # '' : '',
    # '' : '',
    # '' : '',
}

with open('bites_forum') as file:
    
    print("Num bites in parser: ", len(bites))
    
    raw = file.read()

    nole = raw.replace('\n', '')

    pics = nole.split('.png')

    del pics[-1]

    # print(pics)

    for p in pics:
        if p not in bites:
            print("New pic: " + p)
        print("    - " + bites[p])
