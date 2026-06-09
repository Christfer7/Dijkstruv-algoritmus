import tkinter as tk
from tkinter import messagebox
import heapq

VELKOST_STVORCA = 50
RIADKY = 10
STLPCE = 10

TERENY = {
    "volne": {"cena": 1, "farba": "white"},
    "les": {"cena": 5, "farba": "#228B22"},
    "voda": {"cena": 10, "farba": "#1E90FF"},
    "ohen": {"cena": 20, "farba": "#FF4500"},
    "stena": {"cena": float('inf'), "farba": "#404040"},
}

class Aplikacia:
    def __init__(self, root):
        self.root = root
        self.root.title("Najrýchlejšia cesta")

        self.mapa = [[1 for stlpec in range(STLPCE)]for riadok in range(RIADKY)]
        self.start_bod = None  # Na zaciatku este nie je vybraty bod A.
        self.ciel_bod = None  # Na zaciatku este nie je vybraty bod B.
        self.text_a = None  # Premenna bude drzat text A na mape.
        self.text_b = None  # Premenna bude drzat text B na mape.
        self.text_ceny = []  # Zoznam bude drzat texty s cenami na najdenej ceste.
        self.vybrany_nastroj = "les"  # Ako prvy nastroj je vybraty les.
# Tento riadok oddeluje pociatocne hodnoty od vytvarania rozhrania.
        self.vytvor_menu()  # Vytvori horne menu s tlacidlami.
        self.canvas = tk.Canvas(root, width=STLPCE*VELKOST_STVORCA, height=RIADKY*VELKOST_STVORCA)  # Vytvori plochu na kreslenie mapy.
        self.canvas.pack(padx=10, pady=10)  # Zobrazi kresliacu plochu v okne s okrajmi.
# Tento riadok oddeluje canvas od zoznamu stvorcov.
        self.stvorce = [[None for stlpec in range(STLPCE)] for riadok in range(RIADKY)]  # Vytvori 2D zoznam pre graficke stvorce.
        self.vykresli_mriezku()  # Vykresli celu mriezku na canvas.
# Tento riadok oddeluje kreslenie mapy od ovladania mysou.
        self.canvas.bind("<B1-Motion>", self.klik_mysou)  # Pri tahaní lavym tlacidlom mysi sa vola metoda klik_mysou.
        self.canvas.bind("<Button-1>", self.klik_mysou)  # Pri jednom kliknuti lavym tlacidlom mysi sa vola metoda klik_mysou.
# Tento riadok oddeluje konstruktor od metody na menu.
    def vytvor_menu(self):  # Metoda vytvori menu s tlacidlami.
        frame = tk.Frame(self.root)  # Vytvori ramik, do ktoreho sa daju tlacidla.
        frame.pack(pady=10)  # Zobrazi ramik v okne s medzerou zhora a zdola.
# Tento riadok oddeluje ramik od samotnych tlacidiel.
        tk.Button(frame, text="Štart (A)", fg="red", font='bold', command=self.nastroj_a).pack(side=tk.LEFT, padx=2)  # Vytvori tlacidlo na vyber bodu A.
        tk.Button(frame, text="Cieľ (B)", fg="blue", font='bold', command=self.nastroj_b).pack(side=tk.LEFT, padx=2)  # Vytvori tlacidlo na vyber bodu B.
        tk.Button(frame, text="Les (5)", bg=TERENY["les"]["farba"], command=self.nastroj_les).pack(side=tk.LEFT, padx=2)  # Vytvori tlacidlo na kreslenie lesa.
        tk.Button(frame, text="Voda (10)", bg=TERENY["voda"]["farba"], command=self.nastroj_voda).pack(side=tk.LEFT, padx=2)  # Vytvori tlacidlo na kreslenie vody.
        tk.Button(frame, text="Oheň (20)", bg=TERENY["ohen"]["farba"], command=self.nastroj_ohen).pack(side=tk.LEFT, padx=2)  # Vytvori tlacidlo na kreslenie ohna.
        tk.Button(frame, text="Stena", bg=TERENY["stena"]["farba"], command=self.nastroj_stena).pack(side=tk.LEFT, padx=2)  # Vytvori tlacidlo na kreslenie steny.
        tk.Button(frame, text="Guma", command=self.nastroj_volne).pack(side=tk.LEFT, padx=2)  # Vytvori tlacidlo na mazanie terenu na volne policko.
# Tento riadok oddeluje nastroje od ovladacich tlacidiel.
        tk.Button(frame, text="VYMAZAŤ MAPU", bg="#FF9999", command=self.vymaz_mapu).pack(side=tk.LEFT, padx=10)  # Vytvori tlacidlo na vymazanie celej mapy.
        tk.Button(frame, text="ŠTART", bg="yellow", width=10, font='bold', command=self.spusti_vypocet).pack(side=tk.LEFT, padx=10)  # Vytvori tlacidlo na spustenie vypoctu cesty.
# Tento riadok oddeluje menu od kreslenia mriezky.
    def vykresli_mriezku(self):  # Metoda vykresli stvorce mapy.
        for r in range(RIADKY):  # Prechadza vsetky riadky mapy.
            for s in range(STLPCE):  # Prechadza vsetky stlpce mapy.
                x1, y1 = s * VELKOST_STVORCA, r * VELKOST_STVORCA  # Vypocita lavy horny roh stvorca.
                x2, y2 = x1 + VELKOST_STVORCA, y1 + VELKOST_STVORCA  # Vypocita pravy dolny roh stvorca.
                id_stvorca = self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="lightgray")  # Nakresli jedno biele policko.
                self.stvorce[r][s] = id_stvorca  # Ulozi identifikator stvorca do 2D zoznamu.
# Tento riadok oddeluje kreslenie mriezky od zmeny nastroja.
    def zmen_nastroj(self, nastroj):  # Metoda zmeni aktualne vybraty nastroj.
        self.vybrany_nastroj = nastroj  # Ulozi nazov zvoleneho nastroja.
# Tento riadok oddeluje univerzalnu zmenu nastroja od konkretnych tlacidiel.
    def nastroj_a(self):  # Metoda sa spusti po kliknuti na tlacidlo Start A.
        self.zmen_nastroj("A")  # Nastavi nastroj na umiestnovanie bodu A.
# Tento riadok oddeluje jednu metodu tlacidla od druhej.
    def nastroj_b(self):  # Metoda sa spusti po kliknuti na tlacidlo Ciel B.
        self.zmen_nastroj("B")  # Nastavi nastroj na umiestnovanie bodu B.
# Tento riadok oddeluje jednu metodu tlacidla od druhej.
    def nastroj_les(self):  # Metoda sa spusti po kliknuti na tlacidlo Les.
        self.zmen_nastroj("les")  # Nastavi nastroj na kreslenie lesa.
# Tento riadok oddeluje jednu metodu tlacidla od druhej.
    def nastroj_voda(self):  # Metoda sa spusti po kliknuti na tlacidlo Voda.
        self.zmen_nastroj("voda")  # Nastavi nastroj na kreslenie vody.
# Tento riadok oddeluje jednu metodu tlacidla od druhej.
    def nastroj_ohen(self):  # Metoda sa spusti po kliknuti na tlacidlo Ohen.
        self.zmen_nastroj("ohen")  # Nastavi nastroj na kreslenie ohna.
# Tento riadok oddeluje jednu metodu tlacidla od druhej.
    def nastroj_stena(self):  # Metoda sa spusti po kliknuti na tlacidlo Stena.
        self.zmen_nastroj("stena")  # Nastavi nastroj na kreslenie steny.
# Tento riadok oddeluje jednu metodu tlacidla od druhej.
    def nastroj_volne(self):  # Metoda sa spusti po kliknuti na tlacidlo Guma.
        self.zmen_nastroj("volne")  # Nastavi nastroj na mazanie terenu.
# Tento riadok oddeluje metody tlacidiel od ovladania mysou.
    def klik_mysou(self, event):  # Metoda spracuje kliknutie alebo tahanie mysou.
        s = event.x // VELKOST_STVORCA  # Vypocita stlpec, do ktoreho pouzivatel klikol.
        r = event.y // VELKOST_STVORCA  # Vypocita riadok, do ktoreho pouzivatel klikol.
# Tento riadok oddeluje vypocet suradnic od kontroly mapy.
        if 0 <= r < RIADKY and 0 <= s < STLPCE:  # Skontroluje, ci kliknutie bolo vo vnutri mapy.
            stred_x = s * VELKOST_STVORCA + VELKOST_STVORCA // 2  # Vypocita x-suradnicu stredu policka.
            stred_y = r * VELKOST_STVORCA + VELKOST_STVORCA // 2  # Vypocita y-suradnicu stredu policka.
# Tento riadok oddeluje stred policka od vyberu akcie.
            if self.vybrany_nastroj == "A":  # Ak je vybraty nastroj A, nastavuje sa start.
                if self.text_a: self.canvas.delete(self.text_a)  # Ak uz existuje text A, vymaze ho.
                if self.start_bod: self.prefarbi_stvorec(self.start_bod[0], self.start_bod[1])  # Ak uz existoval start, vrati mu povodnu farbu.
                self.start_bod = (r, s)  # Ulozi novu poziciu startu.
                self.canvas.itemconfig(self.stvorce[r][s], fill="#FFCCCC")  # Zafarbi startovacie policko svetlocervenou farbou.
                self.text_a = self.canvas.create_text(stred_x, stred_y, text="A", font=("Arial", 20, "bold"), fill="red")  # Napise pismeno A do policka.
# Tento riadok oddeluje vetvu pre A od vetvy pre B.
            elif self.vybrany_nastroj == "B":  # Ak je vybraty nastroj B, nastavuje sa ciel.
                if self.text_b: self.canvas.delete(self.text_b)  # Ak uz existuje text B, vymaze ho.
                if self.ciel_bod: self.prefarbi_stvorec(self.ciel_bod[0], self.ciel_bod[1])  # Ak uz existoval ciel, vrati mu povodnu farbu.
                self.ciel_bod = (r, s)  # Ulozi novu poziciu ciela.
                self.canvas.itemconfig(self.stvorce[r][s], fill="#CCCCFF")  # Zafarbi cielove policko svetlomodrou farbou.
                self.text_b = self.canvas.create_text(stred_x, stred_y, text="B", font=("Arial", 20, "bold"), fill="blue")  # Napise pismeno B do policka.
            else:  # Ak nie je vybraty bod A ani B, kresli sa teren.
                if (r, s) == self.start_bod: self.start_bod = None; self.canvas.delete(self.text_a); self.text_a = None  # Ak kreslis na start, start sa odstrani.
                if (r, s) == self.ciel_bod: self.ciel_bod = None; self.canvas.delete(self.text_b); self.text_b = None  # Ak kreslis na ciel, ciel sa odstrani.
# Tento riadok oddeluje odstranenie bodov od nastavenia terenu.
                self.mapa[r][s] = TERENY[self.vybrany_nastroj]["cena"]  # Do mapy ulozi cenu vybrateho terenu.
                self.canvas.itemconfig(self.stvorce[r][s], fill=TERENY[self.vybrany_nastroj]["farba"])  # Zafarbi policko podla vybrateho terenu.
# Tento riadok oddeluje ovladanie mysou od prefarbovania stvorca.
    def prefarbi_stvorec(self, r, s):  # Metoda vrati policku farbu podla jeho ceny v mape.
        cena = self.mapa[r][s]  # Nacita cenu daneho policka.
        for t in TERENY.values():  # Prechadza vsetky typy terenu.
            if t["cena"] == cena:  # Hlada teren s rovnakou cenou.
                self.canvas.itemconfig(self.stvorce[r][s], fill=t["farba"])  # Nastavi policku farbu najdeneho terenu.
                break  # Ukonci cyklus, lebo teren uz bol najdeny.
# Tento riadok oddeluje prefarbovanie od mazania mapy.
    def vymaz_mapu(self):  # Metoda vymaze celu mapu.
        self.mapa = [[1 for stlpec in range(STLPCE)] for riadok in range(RIADKY)]  # Obnovi mapu tak, aby boli vsetky policka volne.
        self.start_bod = None  # Zrusi bod A.
        self.ciel_bod = None  # Zrusi bod B.
# Tento riadok oddeluje resetovanie dat od mazania textov.
        if self.text_a: self.canvas.delete(self.text_a); self.text_a = None  # Ak je na mape text A, vymaze ho.
        if self.text_b: self.canvas.delete(self.text_b); self.text_b = None  # Ak je na mape text B, vymaze ho.
        for text in self.text_ceny:  # Prechadza vsetky texty cien na ceste.
            self.canvas.delete(text)  # Vymaze jeden text ceny z canvasu.
        self.text_ceny = []  # Vyprazdni zoznam textov cien.
# Tento riadok oddeluje mazanie textov od obnovy stvorcov.
        for r in range(RIADKY):  # Prechadza vsetky riadky mapy.
            for s in range(STLPCE):  # Prechadza vsetky stlpce mapy.
                self.canvas.itemconfig(self.stvorce[r][s], fill="white", outline="lightgray", width=1)  # Nastavi policko spat na biele s normalnym obrysom.
# Tento riadok oddeluje mazanie mapy od Dijkstrovho algoritmu.
    def dijkstra(self, start, ciel):  # Metoda vypocita najlacnejsiu cestu z bodu start do bodu ciel.
        fronta = [(0, start)]  # Vytvori prioritny rad, kde start ma cenu 0.
        vzdialenosti = {start: 0}  # Ulozi najnizsiu znamu cenu do startu.
        prisiel_z = {start: None}  # Ulozi predchodcu startu, ktory neexistuje.
# Tento riadok oddeluje pripravu Dijkstru od hlavneho cyklu.
        while fronta:  # Cyklus bezi, kym su vo fronte policka na preskumanie.
            aktualna_vzdialenost, (r, s) = heapq.heappop(fronta)  # Vyberie policko s najmensou doterajsou cenou.
            if (r, s) == ciel:  # Ak je aktualne policko ciel, cesta bola najdena.
                return prisiel_z, aktualna_vzdialenost  # Vrati mapu predchodcov a celkovu cenu.
# Tento riadok oddeluje kontrolu ciela od skumania susedov.
            for dr, ds in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Prechadza styroch susedov: hore, dole, vlavo, vpravo.
                nr, ns = r + dr, s + ds  # Vypocita suradnice susedneho policka.
                if 0 <= nr < RIADKY and 0 <= ns < STLPCE:  # Skontroluje, ci sused lezi v mape.
                    cena_prechodu = 0 if (nr, ns) == ciel else self.mapa[nr][ns]  # Zisti cenu vstupu na susedne policko.
                    if cena_prechodu == float('inf'): continue  # Ak je sused stena, preskoci ho.
# Tento riadok oddeluje kontrolu steny od vypoctu novej ceny.
                    nova_vzdialenost = aktualna_vzdialenost + cena_prechodu  # Vypocita cenu cesty cez aktualne policko do suseda.
                    if (nr, ns) not in vzdialenosti or nova_vzdialenost < vzdialenosti[(nr, ns)]:  # Ak je tato cesta do suseda lepsia, ulozi sa.
                        vzdialenosti[(nr, ns)] = nova_vzdialenost  # Ulozi novu najnizsiu cenu do suseda.
                        prisiel_z[(nr, ns)] = (r, s)  # Ulozi, odkial sme do suseda prisli.
                        heapq.heappush(fronta, (nova_vzdialenost, (nr, ns)))  # Prida suseda do prioritneho radu.
        return None, None  # Ak sa cesta nenasla, vrati prazdny vysledok.
# Tento riadok oddeluje Dijkstrov algoritmus od spustenia vypoctu.
    def spusti_vypocet(self):  # Metoda sa spusti po kliknuti na tlacidlo START.
        if not self.start_bod or not self.ciel_bod:  # Skontroluje, ci su nastavene body A aj B.
            messagebox.showwarning("Pozor", "Najprv umiestni A a B!")  # Zobrazi upozornenie, ak chyba A alebo B.
            return  # Ukonci metodu, lebo nie je co pocitat.
# Tento riadok oddeluje kontrolu bodov od cistenia starej cesty.
        for r in range(RIADKY):  # Prechadza vsetky riadky mapy.
            for s in range(STLPCE):  # Prechadza vsetky stlpce mapy.
                self.canvas.itemconfig(self.stvorce[r][s], outline="lightgray", width=1)  # Vrati obrysy policok na povodny stav.
        for text in self.text_ceny:  # Prechadza texty cien zo starej cesty.
            self.canvas.delete(text)  # Vymaze jeden text ceny.
        self.text_ceny = []  # Vyprazdni zoznam textov cien.
# Tento riadok oddeluje cistenie starej cesty od spustenia Dijkstru.
        cesta_mapa, celkova_cena = self.dijkstra(self.start_bod, self.ciel_bod)  # Spusti Dijkstrov algoritmus.
# Tento riadok oddeluje vypocet od vykreslenia vysledku.
        if cesta_mapa:  # Ak sa nasla cesta, zacne sa vykreslovat.
            aktualny = self.ciel_bod  # Zacne od cieloveho bodu.
            cesta = []  # Vytvori prazdny zoznam policok cesty.
            while aktualny in cesta_mapa and aktualny != self.start_bod:  # Ide spatne od ciela ku startu.
                predchadzajuci = cesta_mapa[aktualny]  # Zisti predchadzajuce policko na ceste.
                if predchadzajuci and predchadzajuci != self.start_bod:  # Ak predchodca existuje a nie je start, prida sa do cesty.
                    cesta.append(predchadzajuci)  # Prida policko do zoznamu cesty.
                aktualny = predchadzajuci  # Posunie sa o jedno policko spat.
# Tento riadok oddeluje zostavenie cesty od vykreslenia cien.
            priebezna_cena = 0  # Nastavi priebeznu cenu cesty na 0.
            for r, s in reversed(cesta):  # Prechadza cestu od startu smerom k cielu.
                priebezna_cena += self.mapa[r][s]  # Pripocita cenu aktualneho policka.
                self.canvas.itemconfig(self.stvorce[r][s], outline="yellow", width=4)  # Zvýrazni policko zltým obrysom.
                stred_x = s * VELKOST_STVORCA + VELKOST_STVORCA // 2  # Vypocita x-suradnicu stredu policka.
                stred_y = r * VELKOST_STVORCA + VELKOST_STVORCA // 2  # Vypocita y-suradnicu stredu policka.
                text = self.canvas.create_text(  # Zacne vytvarat text s priebeznou cenou.
                    stred_x,  # Nastavi x-suradnicu textu.
                    stred_y,  # Nastavi y-suradnicu textu.
                    text=str(priebezna_cena),  # Nastavi obsah textu na priebeznu cenu.
                    font=("Arial", 12, "bold"),  # Nastavi pismo textu.
                    fill="black"  # Nastavi ciernu farbu textu.
                )  # Dokonci vytvorenie textu.
                self.text_ceny.append(text)  # Ulozi text ceny, aby sa dal neskor vymazat.
            messagebox.showinfo("Hotovo", f"Celková cena cesty: {celkova_cena}")  # Zobrazi okno s celkovou cenou.
        else:  # Ak sa cesta nenasla, vykona sa tato vetva.
            messagebox.showerror("Chyba", "Cesta neexistuje!")  # Zobrazi chybove okno.
# Tento riadok oddeluje triedu od spustenia programu.
root = tk.Tk()  # Vytvori hlavne okno tkinteru.
app = Aplikacia(root)  # Vytvori objekt aplikacie.
root.mainloop()  # Spusti hlavny cyklus programu, aby okno reagovalo na kliknutia.
