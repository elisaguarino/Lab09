from database.regione_DAO import RegioneDAO
from database.tour_DAO import TourDAO
from database.attrazione_DAO import AttrazioneDAO

class Model:
    def __init__(self):
        self.tour_map = {} # Mappa ID tour -> oggetti Tour
        self.attrazioni_map = {} # Mappa ID attrazione -> oggetti Attrazione

        self._pacchetto_ottimo = []
        self._valore_ottimo: int = -1
        self._costo = 0
        self._relazioniT_A=[]
        self._Tour_ha_attrazioni={}
        self._Attrazione_del_tour = {}
        # TODO: Aggiungere eventuali altri attributi

        # Caricamento
        self.load_tour()
        self.load_attrazioni()
        self.load_relazioni()

    @staticmethod
    def load_regioni():
        """ Restituisce tutte le regioni disponibili """
        return RegioneDAO.get_regioni()

    def load_tour(self):
        """ Carica tutti i tour in un dizionario [id, Tour]"""
        self.tour_map = TourDAO.get_tour()


    def load_attrazioni(self):
        """ Carica tutte le attrazioni in un dizionario [id, Attrazione]"""
        self.attrazioni_map = AttrazioneDAO.get_attrazioni()


    def load_relazioni(self):
        """
            Interroga il database per ottenere tutte le relazioni fra tour e attrazioni e salvarle nelle strutture dati
            Collega tour <-> attrazioni.
            --> Ogni Tour ha un set di Attrazione.
            --> Ogni Attrazione ha un set di Tour.
        """
        self._relazioniT_A = TourDAO.get_tour_attrazioni()
        for id in self.tour_map:
            attr=set()
            for rel in self._relazioniT_A:
                if id == rel["id_tour"]:
                    attr.add(rel["id_attrazione"])
            self.tour_map[id].attrazioni = attr
        for id in self.attrazioni_map:
            t=set()
            for rel in self._relazioniT_A:
                if id == rel["id_attrazione"]:
                    t.add(rel["id_tour"])
            self.attrazioni_map[id].tour = t

        print(self.tour_map)
        # TODO

    def genera_pacchetto(self, id_regione: str, max_giorni: int = None, max_budget: float = None):
        """
        Calcola il pacchetto turistico ottimale per una regione rispettando i vincoli di durata, budget e attrazioni uniche.
        :param id_regione: id della regione
        :param max_giorni: numero massimo di giorni (può essere None --> nessun limite)
        :param max_budget: costo massimo del pacchetto (può essere None --> nessun limite)

        :return: self._pacchetto_ottimo (una lista di oggetti Tour)
        :return: self._costo (il costo del pacchetto)
        :return: self._valore_ottimo (il valore culturale del pacchetto)
        """

        # Filtra i tour della regione selezionata
        lista_tour_regione = []
        for tour in self.tour_map.values():
            if tour.id_regione == id_regione:
                lista_tour_regione.append(tour)

        self._pacchetto_ottimo = []
        self._costo = 0
        self._valore_ottimo = -1

        # Avvia la ricorsione solo con i tour della regione specificata
        self._ricorsione(
            lista_tour_regione,
            0,
            [],
            0,
            0.0,
            0,
            set(),
            max_giorni,
            max_budget
        )

        return self._pacchetto_ottimo, self._costo, self._valore_ottimo

    def _ricorsione(self, lista_tour, posizione_corrente, pacchetto_parziale, durata_corrente, costo_corrente, valore_corrente, attrazioni_usate, max_giorni, max_budget):
        """ Algoritmo di ricorsione che deve trovare il pacchetto che massimizza il valore culturale"""
        #sempre eseguite
        #verifico che il valore corrente non sia migmiore di quello ottimo
        if valore_corrente > self._valore_ottimo:
            self._valore_ottimo = valore_corrente
            self._pacchetto_ottimo = pacchetto_parziale.copy()
            self._costo = costo_corrente
        #condizioni terminali
        if posizione_corrente>=len(lista_tour):
            return False

    #suddivido in due rami cosi posso controllare piu di uno alla volta
        #non aggiungo il tour lo ignoro
        self._ricorsione(lista_tour, posizione_corrente + 1, pacchetto_parziale,durata_corrente, costo_corrente, valore_corrente,attrazioni_usate, max_giorni, max_budget)

        #provo ad aggiungerlo se rispetta i vincoli
        tour = lista_tour[posizione_corrente]
        nuova_durata = durata_corrente + tour.durata_giorni
        nuovo_costo = float(costo_corrente) + float(tour.costo)
        nuove_attrazioni = tour.attrazioni - attrazioni_usate

        #vincoli
        nuova_durata = durata_corrente + tour.durata_giorni
        nuovo_costo = float(costo_corrente) + float(tour.costo)
        nuove_attrazioni = self.tour_map[tour.id].attrazioni - attrazioni_usate
        if (max_giorni is None) or( nuova_durata<= max_giorni):
            if  (max_budget is None) or (nuovo_costo <= max_budget):
                 if len(nuove_attrazioni) > 0:
                    somma_valore = 0
                    for attr_id in nuove_attrazioni:
                         somma_valore += self.attrazioni_map[attr_id].valore_culturale
                    nuovo_valore = valore_corrente + somma_valore
                    pacchetto_parziale.append(tour)
                    attrazioni_usate.update(nuove_attrazioni)

                    #ricorsione
                    self._ricorsione(lista_tour, posizione_corrente + 1, pacchetto_parziale,nuova_durata, nuovo_costo, nuovo_valore,attrazioni_usate, max_giorni, max_budget)
                    # backtracking
                    pacchetto_parziale.pop()
                    attrazioni_usate.difference_update(nuove_attrazioni)

        # TODO: è possibile cambiare i parametri formali della funzione se ritenuto opportuno
