# Zpracování dat z hlasování na czech craft-craft.eu

import json, urllib.request, csv
from ttkwidgets.autocomplete import AutocompleteEntry
from ttkwidgets import Calendar
from tkinter import *
from time import strftime
from datetime import timedelta
from os import path
from operator import itemgetter
import matplotlib.pyplot as plt
import numpy

# třída pro ověření, načtení a vyčištění dat pro jeden měsíc
class Votes_data_source:
    def new_file(self, yy, mm):
        
        # definice cesty a souboru dat
        mnth = '{:02d}'.format(mm)
        link = "https://czech-craft.eu/api/server/cube-craft/votes/" + str(yy) + "/" + str(mnth) + "/"
        file_name = "votes_" + str(yy) + "_" + str(mnth) + ".csv"

        # Ověření, zda data již máme
        if not (path.isfile(file_name)):
            # načtení dat z url
            with urllib.request.urlopen(link) as url:
                data = json.loads(url.read().decode())
            data_clear = data["data"]
            data_clear_list = []
            for row_dict in data_clear:
                data_clear_list.append([row_dict["username"], row_dict["datetime"], row_dict["delivered"]])

            # uložení do souboru
            with open( file_name, mode = 'w', newline = '', encoding = "utf-8") as file:    
                write = csv.writer(file, delimiter=';', quotechar = '"', quoting = csv.QUOTE_ALL)
                write.writerows(data_clear_list)

# Smyčka pro pro volání třídy a doplnění parametrů pro jednotlivé měsíce
# definice objektů
data_call = Votes_data_source()
act_time_yyyy = int ( strftime ( "%Y" ))
act_time_mm = int ( strftime ( "%m" ))
# todle je tady asi zbytečný
mnth = '{:02d}'.format(act_time_mm)
link = "https://czech-craft.eu/api/server/cube-craft/votes/" + str(act_time_yyyy) + "/" + str(mnth) + "/"
file_name = "votes_" + str(act_time_yyyy) + "_" + str(mnth) + "_temp.csv"

# smyčka pro získání zdrojů po měsících
for y in range (2020, act_time_yyyy + 1):
    for m in range (1, 13):
        if not (( y == 2020 and m < 6) or ( y == act_time_yyyy and m >= act_time_mm)):
            data_call.new_file( y, m)

# vytvoření temp struktury s daty z aktuálního měsíce
with urllib.request.urlopen(link) as url:
    data = json.loads(url.read().decode())
data_clear = data["data"]
data_clear_list = []
for row_dict in data_clear:
    data_clear_list.append([row_dict["username"], row_dict["datetime"], row_dict["delivered"]])

# uložení do souboru
with open( file_name, mode = 'w', newline = '', encoding = "utf-8") as file:    
    write = csv.writer(file, delimiter=';', quotechar = '"', quoting = csv.QUOTE_ALL)
    write.writerows(data_clear_list)

# funkce pro vytvoření seznamu votes
def plus_month( yy, mm ):
    mnth = '{:02d}'.format(mm)
    file_name = "votes_" + str(yy) + "_" + str(mnth) + ".csv"
    with open( file_name, encoding='utf-8' ) as csvfile:
        reader = csv.reader(csvfile, quotechar='"', delimiter=';')
        for row in reader:
            data_base.append(row)

# smyčka pro získání zdrojů po měsících
data_base = []
for y in range (2020, act_time_yyyy + 1):
    for m in range (1, 13):
        if not (( y == 2020 and m < 6) or ( y == act_time_yyyy and m >= act_time_mm)):
            plus_month( y, m)

# připojení dat z temp souboru z aktuálního měsíce
with open( file_name, encoding='utf-8' ) as csvfile:
    reader = csv.reader(csvfile, quotechar='"', delimiter=';')
    for row in reader:
        data_base.append(row)

#Třídění databáze votes podle data
data_base.sort(key=itemgetter(1))

# --------------
# Ukončení tvorby databáze včetně setřídění dle času
# --------------

nick_list = []
for row in data_base:
    nick = row[0]
    if not nick in nick_list:
        nick_list.append( nick )

# GUI
class Okno(Frame):

    # iniciace rámu
    def __init__(self, master = None ):
        Frame.__init__(self, master )
        self.createWidgets()
        self.grid()
        self.master.title("Nazdar")
        self.master.geometry("600x500")
        # self.config(bg='white')

    # funkce klikacího okna
    def createWidgets(self):
        
        nick_sel = []
        def enter_nick():
            if len(nick_sel) < 5:
                nick = str(nick_.get())
                nick_sel.append(nick)
                text1 = ", ".join(nick_sel)
                label2.config ( text = str( len(nick_sel)) +": " + text1, bg= "SystemButtonFace" )
                nick_obj.delete ( 0, END )
            else:
                label2.config ( text = "Maximum je 5 nicků v grafu!", bg= "SystemButtonFace" )

        # vyprázdnění seznamu nicků
        def clear_nicks():
            nick_sel.clear()
            label2.config ( text = "Seznam nicků je prázdný", bg= "SystemButtonFace" )

        # potvrzení dolního limutu intervalu
        def validate1():
            sel1 = calendar1.selection
            if sel1 is not None:
                text_ = "Vybrané datum: " + sel1.strftime( "%Y-%m-%d" )
                object4.config ( text = text_, bg= "SystemButtonFace")

        # potvrzení horního limitu intervalu
        def validate2():
            sel2 = calendar2.selection
            if sel2 is not None:
                text_ = "Vybrané datum: " + sel2.strftime( "%Y-%m-%d" )
                object6.config ( text = text_, bg= "SystemButtonFace" )

        # výběr funkce pro zpracování dat podle typu grafu
        def vykresli_choice():
            sel1 = calendar1.selection
            sel2 = calendar2.selection
            
            if nick_sel == [] and var_int.get() != 4:
                label2.config( text = "Zadejte alespoň jeden nick", bg = "red")
            elif sel1 is None:
                object4.config( text = "Není zadaný začátek intervalu", bg = "red" )
            elif sel2 is None:
                object6.config( text = "Není zadaný konec intervalu", bg = "red" )
            elif sel1 > sel2:
                object4.config( text = "Začátek intervalu je zadán později než konec", bg = "red" )
                object6.config( text = "Konec intervalu je zadán dříve než začátek", bg = "red" )
            elif var_int.get() == 0:
                label3.config( text = "Není vybraný typ grafu", bg = "red")
            else:
                label3.config( text = "OK. Vykresluji", bg = "green")
                if var_int.get() == 1:
                    vykresli_day( sel1, sel2 )
                elif var_int.get() == 2:
                    vykresli_week( sel1, sel2)
                elif var_int.get() == 3:
                    vykresli_month( sel1, sel2 )
                elif var_int.get() == 4:
                    vykresli_top( sel1, sel2 )
        
        # funkce pro výběr dat pro typ grafu denní
        def vykresli_day( sel1, sel2 ):
            matrix = []
            xlabels = []
            day_sum = int((( sel2 - sel1 ).days ) + 1)
            header = "Hlasování po dnech od " + sel1.strftime( "%Y-%m-%d" ) + " do " + sel2.strftime( "%Y-%m-%d" )

            for i, nck in enumerate(nick_sel):
                matrix.append([nck])
                for d in range( 0, day_sum ):
                    xlabel = "D" + str( d + 1)
                    if xlabel not in xlabels:
                        xlabels.append( xlabel )
                    matrix[i].append(0)
                    set_day = ( sel1 + timedelta( days = d )).strftime( "%Y-%m-%d" )
                    for row in data_base:
                        if ( row[0] == nck ) and ( set_day == (row[1])[:10] ):
                            matrix[i][d+1] = matrix[i][d+1] + 1

            vykresli_graf( matrix, xlabels, header )

        # funkce pro výběr dat pro typ grafu týdenní
        def vykresli_week( sel1, sel2 ):
            matrix = []
            xlabels = []
            monday1 = (sel1 - timedelta(days=sel1.weekday()))
            monday2 = (sel2 - timedelta(days=sel2.weekday()))
            week_sum = int(((monday2 - monday1).days / 7) + 1)
            header = "Hlasování po týdnech od " + monday1.strftime( "%Y-%m-%d" ) + " do " + ( monday2 + timedelta( 6 )).strftime( "%Y-%m-%d" )

            for i, nck in enumerate(nick_sel):
                matrix.append([nck])
                for w in range( 0, week_sum ):
                    xlabel = "T" + str( w + 1)
                    if xlabel not in xlabels:
                        xlabels.append( xlabel )
                    matrix[i].append(0)
                    monday = ( monday1 + timedelta( days = 7*w )).strftime( "%Y-%m-%d" )
                    sunday = ( monday1 + timedelta( days = 7*w + 6 ) ).strftime( "%Y-%m-%d" )
                    for row in data_base:
                        if ( row[0] == nck ) and ( monday <= (row[1])[:10] <= sunday ):
                            matrix[i][w+1] = matrix[i][w+1] + 1

            vykresli_graf( matrix, xlabels, header )

        # funkce pro výběr dat pro typ grafu měsíční
        def vykresli_month( sel1, sel2 ):
            matrix = []
            xlabels = []
            first_day = sel1.replace( day = 1 )
            next_month = sel2.replace( day = 28 ) + timedelta( days=4 )
            last_day = next_month - timedelta( days = next_month.day )
            month_sum = (sel2.year - sel1.year) * 12 + (sel2.month - sel1.month) + 1
            header = "Hlasování po měsících od " + first_day.strftime( "%Y-%m-%d" ) + " do " + last_day.strftime( "%Y-%m-%d" )
            
            for i, nck in enumerate(nick_sel):
                set_first_day = first_day
                matrix.append([nck])
                for m in range( 0, month_sum ):
                    xlabel = "M" + str( m + 1)
                    if xlabel not in xlabels:
                        xlabels.append( xlabel )
                    matrix[i].append(0)
                    set_next_month = set_first_day.replace( day = 28 ) + timedelta( days=4 )
                    set_last_day = set_next_month - timedelta( days = set_next_month.day )
                    day1 = set_first_day.strftime( "%Y-%m-%d" )
                    day2 = set_last_day.strftime( "%Y-%m-%d" )
                    for row in data_base:
                        if ( row[0] == nck ) and ( day1 <= (row[1])[:10] <= day2 ):
                            matrix[i][m+1] = matrix[i][m+1] + 1
                    set_first_day = set_last_day + timedelta( days = 1)

            vykresli_graf( matrix, xlabels, header )

        # funkce pro výběr dat pro typ grafu top 10
        def vykresli_top ( sel1, sel2 ):
            
            xlabels = ["10 nejlepších hlasujících"]
            header = "10 nejvíce hlasujících od " + sel1.strftime( "%Y-%m-%d" ) + " do " + sel2.strftime( "%Y-%m-%d" )

            limited_data_base = []
            for row in data_base:
                if sel1.strftime( "%Y-%m-%d" ) <= (row[1])[:10] <= sel2.strftime( "%Y-%m-%d" ):
                    limited_data_base.append(row)

            nick_list = []
            for row in limited_data_base:
                nick = row[0]
                if not nick in nick_list:
                    nick_list.append( nick )

            top_votes = []
            for nick in nick_list:
                top_votes.append([nick, 0])
                for row in limited_data_base:
                    if nick == row[0]:
                        top_votes[-1][1] = top_votes[-1][1] + 1

            top_votes.sort(key=itemgetter(1), reverse = True)
            matrix = top_votes[:10]

            vykresli_graf( matrix, xlabels, header )

        # společná funkce pro vykreslení grafu
        def vykresli_graf( matrix, xlabels, header ):
            label3.config( text = "Proveď další zadání", bg = "SystemButtonFace")
            seq = len ( matrix )
            ind = numpy.arange( len ( matrix[0]) - 1 )
            width = 0.8

            fig, ax = plt.subplots()

            pp = []
            for i, row in enumerate(matrix):
                pp.append ( ax.bar(ind + ( width * ( 1 - seq + 2 * i)) / ( 2 * seq ), row[1:], width / seq, label= row[0]) )

            ax.axhline(0, color='red', linewidth=2 )
            ax.set_ylabel('Hlasy')
            ax.set_title( header )
            ax.set_xticks(ind)

            ax.set_xticklabels( xlabels )
            ax.legend()

            for i, row in enumerate(pp):
                ax.bar_label(row, label_type='edge', color = "black", rotation = 70, fontsize = 7, padding = 3)

            plt.show()

        # widgety
        label1 = Label( self, text = " " )
        label1.grid( row = 0, column = 0 )

        label1 = Label( self, text = " " )
        label1.grid( row = 0, column = 2 )

        label1 = Label( self, text = " " )
        label1.grid( row = 0, column = 5 )
        
        label1 = Label( self, text = "Cube-craft.cz\nAnalýza a grafické zpracování hlasování ze servru czechcraft.cz", bg = "lightsteelblue1")
        label1.grid( row = 0, column = 1, columnspan = 4, sticky="we" )

        konec = Button( self, text = "Quit", bg = "orange", fg = "black", font="Arial 20 bold" )
        konec['command'] =  self.quit
        konec.grid( row = 0, column = 6, sticky="we" )

        vykresli = Button( self, text = "Draw", bg = "royalblue1", fg = "black", font="Arial 20 bold", command = vykresli_choice )
        vykresli.grid( row = 1, column = 6, rowspan = 2, sticky="we" )

        nick_ = StringVar()
        nick_obj = AutocompleteEntry( self, width=30, completevalues = nick_list, textvariable = nick_ )
        nick_obj.grid( row = 1, column = 1 )

        object1 = Button(self, text = "Enter", command = enter_nick, bg = "royalblue1", border = 2)
        object1.grid( row = 1, column = 3 )

        object2 = Button(self, text = "Clear", command = clear_nicks, bg= "orange" )
        object2.grid( row = 1, column = 4 )

        label2 = Label( self, text = "Seznam nicků je prázdný", bg= "SystemButtonFace" )
        label2.grid( row = 2, column = 1, columnspan = 4 )

        var_int = IntVar()
        frame1 = Frame(self, bg="white", width=300, height=100)
        radio1 = Radiobutton( frame1, text = "Denní", variable = var_int, value = 1)
        radio2 = Radiobutton( frame1, text = "Týdenní", variable = var_int, value = 2)
        radio3 = Radiobutton( frame1, text = "Měsíční", variable = var_int, value = 3)
        radio4 = Radiobutton( frame1, text = "Top 10", variable = var_int, value = 4)
        radio1.grid (row = 0, column = 0)
        radio2.grid (row = 0, column = 1)
        radio3.grid (row = 0, column = 2)
        radio4.grid (row = 0, column = 3)
        frame1.grid( row = 3, column = 1)

        label3 = Label( self, text = "<- Zde vyberte typ grafu", bg= "SystemButtonFace" )
        label3.grid( row = 3, column = 2, columnspan = 4 )

        calendar1 = Calendar( self, year=2021, month=10, selectforeground='white', selectbackground='red' )
        calendar1.grid ( row = 4, column = 1 )

        object3 = Button ( self, text = "Vložit datum", command = validate1, bg = "royalblue1" )
        object3.grid ( row = 5, column = 1 )

        calendar2 = Calendar( self, year=2021, month=11, selectforeground='white', selectbackground='red' )
        calendar2.grid ( row = 4, column = 3, columnspan = 4 )

        object5 = Button ( self, text = "Vložit datum", command = validate2, bg = "royalblue1" )
        object5.grid ( row = 5, column = 3, columnspan = 4 )

        object4 = Label ( self, text='Vybrané datum: žádné', bg= "SystemButtonFace" )
        object4.grid ( row = 6, column = 1 )

        object6 = Label ( self, text='Vybrané datum: žádné', bg= "SystemButtonFace" )
        object6.grid ( row = 6, column = 3, columnspan = 4 )

        tmptxt = "Informace k používání scriptu:\n"
        tmptxt = tmptxt + "Nick: vyberte alespoň jeden nick, maximálně však 5\n"
        tmptxt = tmptxt + "          nick není třeba vybírat v případě volby top 10\n"
        tmptxt = tmptxt + "Datum: zadejte začátek a konec intervalu, ve kterém se mají sčítat hlasy\n"
        tmptxt = tmptxt + "              při výběru měsíčního a týdenního dělení intervalu dojde k zaokrouhlení\n"
        tmptxt = tmptxt + "              na celé kalendářní týdny a měsíce\n"
        tmptxt = tmptxt + "Po vykreslení grafu je možné upravit nastavení a vykreslit nový graf, můžete otevřít více grafů najednou."
        objekt7 = Label (self, text=tmptxt, bg = "lightsteelblue1", justify = "left" )
        objekt7.grid ( row = 7, column = 1, columnspan = 6, pady = 15, sticky="w" )

app = Okno()

app.mainloop()

print ("\nEXIT")