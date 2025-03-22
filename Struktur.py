
class Matakuliah:
    def __init__(self, kode, sks, semester, model, keilmuan, prodi, nama):
        self.kode = kode
        self.sks = sks
        self.semester = semester
        self.model = model
        self.keilmuan = keilmuan
        self.prodi = prodi
        self.nama = nama


class Prodi:
    def __init__(self, kode, prodi, fakultas):
        self.kode = kode
        self.prodi = prodi
        self.fakultas = fakultas
        

class Dosen:
    def __init__(self, nip, keilmuan, prodi, fakultas, nama):
        self.nip = nip
        self.keilmuan = keilmuan
        self.prodi = prodi
        self.fakultas = fakultas
        self.nama = nama

class Ruang:
    def __init__(self, kode, model, prodi, fakultas):
        self.kode = kode
        self.model = model
        self.prodi = prodi
        self.fakultas = fakultas

class Waktu:
    def __init__(self, hari, menit):
        self.hari = hari
        self.menit = int(menit)

class Kelas:
    def __init__(self, kelas, semester):
        self.kelas = kelas
        self.semester = semester
