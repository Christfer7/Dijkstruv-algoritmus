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
        self.root.title("Projekt - Najrýchlejšia cesta")

        self.mapa = [[1 for stlpec in range(STLPCE)]for riadok in range(RIADKY)]
        self.start_bod = None
        self.ciel_bod = None
        self.text_a = None 
        self.text_b = None 
        self.text_ceny = []
        self.vybrany_nastroj = "les"
        
        self.vytvor_menu()
        self.canvas = tk.Canvas(root, width=STLPCE*VELKOST_STVORCA, height=RIADKY*VELKOST_STVORCA)
        self.canvas.pack(padx=10, pady=10)
        
        self.stvorce = [[None for stlpec in range(STLPCE)] for riadok in range(RIADKY)] 
        self.vykresli_mriezku()

        self.canvas.bind("<B1-Motion>", self.klik_mysou)
        self.canvas.bind("<Button-1>", self.klik_mysou)

    def vytvor_menu(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        tk.Button(frame, text="Štart (A)", fg="red", font='bold', command=lambda: self.zmen_nastroj("A")).pack(side=tk.LEFT, padx=2)
        tk.Button(frame, text="Cieľ (B)", fg="blue", font='bold', command=lambda: self.zmen_nastroj("B")).pack(side=tk.LEFT, padx=2)
        tk.Button(frame, text="Les (5)", bg=TERENY["les"]["farba"], command=lambda: self.zmen_nastroj("les")).pack(side=tk.LEFT, padx=2)
        tk.Button(frame, text="Voda (10)", bg=TERENY["voda"]["farba"], command=lambda: self.zmen_nastroj("voda")).pack(side=tk.LEFT, padx=2)
        tk.Button(frame, text="Oheň (20)", bg=TERENY["ohen"]["farba"], command=lambda: self.zmen_nastroj("ohen")).pack(side=tk.LEFT, padx=2)
        tk.Button(frame, text="Stena", bg=TERENY["stena"]["farba"], fg="black", command=lambda: self.zmen_nastroj("stena")).pack(side=tk.LEFT, padx=2)
        tk.Button(frame, text="Guma", command=lambda: self.zmen_nastroj("volne")).pack(side=tk.LEFT, padx=2)
        
        tk.Button(frame, text="VYMAZAŤ MAPU", bg="#FF9999", command=self.vymaz_mapu).pack(side=tk.LEFT, padx=10)
        tk.Button(frame, text="ŠTART", bg="yellow", width=10, font='bold', command=self.spusti_vypocet).pack(side=tk.LEFT, padx=10)

    def vykresli_mriezku(self):
        for r in range(RIADKY):
            for s in range(STLPCE):
                x1, y1 = s * VELKOST_STVORCA, r * VELKOST_STVORCA
                x2, y2 = x1 + VELKOST_STVORCA, y1 + VELKOST_STVORCA
                id_stvorca = self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="lightgray")
                self.stvorce[r][s] = id_stvorca

    def zmen_nastroj(self, nastroj):
        self.vybrany_nastroj = nastroj

    def klik_mysou(self, event):
        s = event.x // VELKOST_STVORCA
        r = event.y // VELKOST_STVORCA

        if 0 <= r < RIADKY and 0 <= s < STLPCE:
            stred_x = s * VELKOST_STVORCA + VELKOST_STVORCA // 2
            stred_y = r * VELKOST_STVORCA + VELKOST_STVORCA // 2

            if self.vybrany_nastroj == "A":
                if self.text_a: self.canvas.delete(self.text_a)
                if self.start_bod: self.prefarbi_stvorec(self.start_bod[0], self.start_bod[1])
                self.start_bod = (r, s)
                self.canvas.itemconfig(self.stvorce[r][s], fill="#FFCCCC") 
                self.text_a = self.canvas.create_text(stred_x, stred_y, text="A", font=("Arial", 20, "bold"), fill="red")
                
            elif self.vybrany_nastroj == "B":
                if self.text_b: self.canvas.delete(self.text_b)
                if self.ciel_bod: self.prefarbi_stvorec(self.ciel_bod[0], self.ciel_bod[1])
                self.ciel_bod = (r, s)
                self.canvas.itemconfig(self.stvorce[r][s], fill="#CCCCFF") 
                self.text_b = self.canvas.create_text(stred_x, stred_y, text="B", font=("Arial", 20, "bold"), fill="blue")
            else:
                if (r, s) == self.start_bod: self.start_bod = None; self.canvas.delete(self.text_a); self.text_a = None
                if (r, s) == self.ciel_bod: self.ciel_bod = None; self.canvas.delete(self.text_b); self.text_b = None
                
                self.mapa[r][s] = TERENY[self.vybrany_nastroj]["cena"]
                self.canvas.itemconfig(self.stvorce[r][s], fill=TERENY[self.vybrany_nastroj]["farba"])

    def prefarbi_stvorec(self, r, s):
        cena = self.mapa[r][s]
        for t in TERENY.values():
            if t["cena"] == cena:
                self.canvas.itemconfig(self.stvorce[r][s], fill=t["farba"])
                break

    def vymaz_mapu(self):
        self.mapa = [[1 for stlpec in range(STLPCE)] for riadok in range(RIADKY)]
        self.start_bod = None
        self.ciel_bod = None
        
        if self.text_a: self.canvas.delete(self.text_a); self.text_a = None
        if self.text_b: self.canvas.delete(self.text_b); self.text_b = None
        for text in self.text_ceny:
            self.canvas.delete(text)
        self.text_ceny = []
        
        for r in range(RIADKY):
            for s in range(STLPCE):
                self.canvas.itemconfig(self.stvorce[r][s], fill="white", outline="lightgray", width=1)

    def dijkstra(self, start, ciel):
        fronta = [(0, start)]
        vzdialenosti = {start: 0}
        prisiel_z = {start: None}

        while fronta:
            aktualna_vzdialenost, (r, s) = heapq.heappop(fronta)
            if (r, s) == ciel:
                return prisiel_z, aktualna_vzdialenost

            for dr, ds in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, ns = r + dr, s + ds
                if 0 <= nr < RIADKY and 0 <= ns < STLPCE:
                    cena_prechodu = 0 if (nr, ns) == ciel else self.mapa[nr][ns]
                    if cena_prechodu == float('inf'): continue 

                    nova_vzdialenost = aktualna_vzdialenost + cena_prechodu
                    if (nr, ns) not in vzdialenosti or nova_vzdialenost < vzdialenosti[(nr, ns)]:
                        vzdialenosti[(nr, ns)] = nova_vzdialenost
                        prisiel_z[(nr, ns)] = (r, s)
                        heapq.heappush(fronta, (nova_vzdialenost, (nr, ns)))
        return None, None

    def spusti_vypocet(self):
        if not self.start_bod or not self.ciel_bod:
            messagebox.showwarning("Pozor", "Najprv umiestni A a B!")
            return

        for r in range(RIADKY):
            for s in range(STLPCE):
                self.canvas.itemconfig(self.stvorce[r][s], outline="lightgray", width=1)
        for text in self.text_ceny:
            self.canvas.delete(text)
        self.text_ceny = []

        cesta_mapa, celkova_cena = self.dijkstra(self.start_bod, self.ciel_bod)

        if cesta_mapa:
            aktualny = self.ciel_bod
            cesta = []
            while aktualny in cesta_mapa and aktualny != self.start_bod:
                predchadzajuci = cesta_mapa[aktualny]
                if predchadzajuci and predchadzajuci != self.start_bod:
                    cesta.append(predchadzajuci)
                aktualny = predchadzajuci

            priebezna_cena = 0
            for r, s in reversed(cesta):
                priebezna_cena += self.mapa[r][s]
                self.canvas.itemconfig(self.stvorce[r][s], outline="yellow", width=4)
                stred_x = s * VELKOST_STVORCA + VELKOST_STVORCA // 2
                stred_y = r * VELKOST_STVORCA + VELKOST_STVORCA // 2
                text = self.canvas.create_text(
                    stred_x,
                    stred_y,
                    text=str(priebezna_cena),
                    font=("Arial", 12, "bold"),
                    fill="black"
                )
                self.text_ceny.append(text)
            messagebox.showinfo("Hotovo", f"Celková cena cesty: {celkova_cena}")
        else:
            messagebox.showerror("Chyba", "Cesta neexistuje!")

root = tk.Tk()
app = Aplikacia(root)
root.mainloop()
