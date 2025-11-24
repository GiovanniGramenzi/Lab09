from copy import deepcopy

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
        # TODO
        relazioni=TourDAO.get_tour_attrazioni()
        for relazione in relazioni:
            self.tour_map[relazione['id_tour']].attrazioni.add(self.attrazioni_map[relazione['id_attrazione']])
            self.attrazioni_map[relazione['id_attrazione']].tour.add(self.tour_map[relazione['id_tour']])
        #print(self.tour_map)
        #print(self.attrazioni_map)
        return self.tour_map, self.attrazioni_map
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
        self._pacchetto_ottimo = []
        self._costo = 0
        self._valore_ottimo = -1
        tour_regione=[]
        for t in self.tour_map.values():
            if t.id_regione == id_regione:
                tour_regione.append(t)
        self._ricorsione(start_index=0,lista_tour=tour_regione,pacchetto_parziale=[],durata_corrente=0,costo_corrente=0,valore_corrente=0,attrazioni_usate=set(),max_giorni=max_giorni,max_budget=max_budget)
        return self._pacchetto_ottimo, self._costo, self._valore_ottimo
        # TODO


    def _ricorsione(self, start_index: int,lista_tour, pacchetto_parziale: list, durata_corrente: int, costo_corrente: float, valore_corrente: int, attrazioni_usate: set,max_giorni, max_budget):
        """ Algoritmo di ricorsione che deve trovare il pacchetto che massimizza il valore culturale"""

        # TODO: è possibile cambiare i parametri formali della funzione se ritenuto opportuno
        if start_index==len(lista_tour):
            if valore_corrente>self._valore_ottimo:
                self._valore_ottimo = valore_corrente
                self._costo = costo_corrente
                self._pacchetto_ottimo=pacchetto_parziale.copy()
            return
        else:
            tour = lista_tour[start_index]
            self._ricorsione(start_index+1,lista_tour,pacchetto_parziale,durata_corrente,costo_corrente,valore_corrente,attrazioni_usate,max_giorni,max_budget)
            if max_budget is not None and costo_corrente+tour.costo>max_budget:
                return
            if max_giorni is not None and durata_corrente+tour.durata_giorni>max_giorni:
                return
            if tour.attrazioni.intersection(attrazioni_usate):
                return
            pacchetto_parziale.append(tour)
            costo_corrente += tour.costo

            nuovo_valore=valore_corrente+sum(a.valore_culturale for a in tour.attrazioni)

            durata_corrente += tour.durata_giorni
            nuove_attr=tour.attrazioni.union(attrazioni_usate)
            self._ricorsione(start_index+1,lista_tour,pacchetto_parziale,durata_corrente,costo_corrente,nuovo_valore,nuove_attr,max_giorni,max_budget)
            pacchetto_parziale.pop()

