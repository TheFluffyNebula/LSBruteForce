from pynput.keyboard import Key, Controller, Listener
import time
champs=['Aatrox','Ahri','Akali','Akshan','Alistar','Amumu','Anivia','Annie','Aphelios','Ashe','Aurelion Sol','Azir','Bard',"Bel'Veth",
'Blitzcrank','Brand','Braum','Caitlyn','Camille','Cassiopeia',"Cho'Gath",'Corki','Darius','Diana','Draven','Dr. Mundo','Ekko','Elise',
'Evelynn','Ezreal','Fiddlesticks','Fiora','Fizz','Galio','Gangplank','Garen','Gnar','Gragas','Graves','Gwen','Hecarim','Heimerdinger',
'Illaoi','Irelia','Ivern','Janna','Jarvan IV','Jax','Jayce','Jhin','Jinx',"Kai'Sa",'Kalista','Karma','Karthus','Kassadin','Katarina',
'Kayle','Kayn','Kennen',"Kha'Zix",'Kindred','Kled',"Kog'Maw",'LeBlanc','Lee Sin','Leona','Lillia','Lissandra','Lucian','Lulu','Lux',
'Malphite','Malzahar','Maokai','Master Yi','Miss Fortune','Wukong','Mordekaiser','Morgana','Nami','Nasus','Nautilus','Neeko',
'Nidalee','Nilah','Nocturne','Nunu & Willump','Olaf','Orianna','Ornn','Pantheon','Poppy','Pyke','Qiyana','Quinn','Rakan','Rammus',
"Rek'Sai",'Rell','Renata Glasc','Renekton','Rengar','Riven','Rumble','Ryze','Samira','Sejuani','Senna','Seraphine','Sett','Shaco',
'Shen','Shyvana','Singed','Sion','Sivir','Skarner','Sona','Soraka','Swain','Sylas','Syndra','Tahm Kench','Taliyah','Talon','Taric',
'Teemo','Thresh','Tristana','Trundle','Tryndamere','Twisted Fate','Twitch','Udyr','Urgot','Varus','Vayne','Veigar',"Vel'Koz",'Vex',
'Vi','Viego','Viktor','Vladimir','Volibear','Warwick','Xayah','Xerath','Xin Zhao','Yasuo','Yone','Yorick','Yuumi',
'Zac','Zed','Zeri','Ziggs','Zilean','Zoe','Zyra']
keyboard = Controller()
time.sleep(2)
def print_champ(champ):
    for char in champ:
        keyboard.press(char)
        keyboard.release(char)
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)
    #time.sleep(0.03)
def print_all():
    for x in champs:
        print_champ(x)

#def on_press(key):
    #pass
def on_release(key):
    if key == Key.esc:
        t1 = time.time()
        print_all()
        t2 = time.time()
        print(t2-t1)
        return False
with Listener(
        #on_press=on_press,
        on_release=on_release) as listener:
    listener.join()