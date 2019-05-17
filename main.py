'''
	Yapay Zeka - Dönem Ödevi
	Genetik Besteci

	Öğrenci: Osman Araz
	Numara: 16011020

	Teslim Tarihi: 17.05.2019
'''

'''
	NOT: Programın çalışması için bilgisayarınızda Python 3 yüklü olması gerekmektedir.
    Python indirmek için:
    https://www.python.org/downloads/

    Gerekli kütüphane kurulumu için terminal üzerinden aşağıdaki komutu çalıştırın:
    pip install music21
'''

import os
import platform
from music21 import note, stream, midi, interval, chord
from random import randint

#########################################

# notalar:
noteNames = ["C", "D", "E", "F", "G", "A", "B"]
# nota değerleri için olasılık değerlerine göre bir hash tablosu:
noteOctaves = {0: "2", 1: "2", 2: "2", 3: "3", 4: "3", 5: "3", 6: "4", 7: "4", 8: "4", 9: "5", 10: "5",
			   11: "5", 12: "6", 13: "6", 14: "7", 15: "1"}

#########################################

class Composition: # müzik eseri için oluşturulan sınıf
	def __init__(self):
		self.notes = [] # müzik notaları
		self.fitness = 0 # müziğin uygunluk değeri (ne kadar az, o kadar iyi)

	def initializeNotes(self, base): # notaları ilklendiren fonksiyon
		for i in range(len(base.notes)):
			self.notes.append(randomNote(base.notes[i].duration))

	def assignRestsAndChords(self, base): # akortları ve boşlukları ilklendiren fonksiyon
		for i in range(len(base.notes)):
			if (type(base.notes[i]) != note.Note):
				self.notes[i] = base.notes[i]

	def assignDurations(self, base): # nota sürelerini ilklendiren fonksiyon
		for i in range(len(base.notes)):
			self.notes[i].duration = base.notes[i].duration

	def calculateFitness(self, base): # uygunluk değerini ölçen fonksiyon
		self.fitness = 0  # less is better

		for i in range(len(self.notes)):
			if type(base.notes[i]) == note.Note:
				self.fitness += noteDiff(base.notes[i], self.notes[i])

#########################################
'''
	Verilen bir notanın sayısal değerini ölçen fonksiyon.
	@param note1: nota
	@return: ölçülen sayısal değer
'''

def noteValue(note1):
	nameVal = (ord(note1.name[0].upper()) - ord('A') + 5) % 7
	octaveVal = note1.octave

	if len(note1.name) > 1:
		if note1.name[1] == '#': # diyez, sesi yarım ses inceltir
			octaveVal += 0.05
		else:				     # bemol, sesi yarım ses kalınlaştırır
			octaveVal -= 0.05

	return 10*octaveVal + nameVal

#########################################
'''
	İki nota arasındaki sayısal farkı ölçen fonksiyon.
	@param notes1: birinci müzik parçası
	@param notes2: ikinci müzik parçası
	@return: ölçülen sayısal fark
'''

def noteDiff(note1, note2):
	return abs(noteValue(note1) - noteValue(note2))

#########################################
'''
	Dosya konumu verilen müziği okuyan fonksiyon.
	@param path: müziğin dosya konumu
	@return: okunan müzik parçası
'''

def readStream(path):
	mfIn = midi.MidiFile()
	mfIn.open(path)
	mfIn.read()
	mfIn.close()
	return midi.translate.midiFileToStream(mfIn).flat

#########################################
'''
	Oluşturulan müziği bir dosyaya yazdıran fonksiyon.
	@param notes: müzik notaları
	@param path: yazdırılacak dosya konumu
'''

def writeStream(notes, path):
	strm = stream.Stream()
	strm.append(notes)
	mfOut = midi.translate.streamToMidiFile(strm)
	mfOut.open(path, 'wb')
	mfOut.write()
	mfOut.close()

#########################################
'''
	Rastegele bir nota oluşturan fonksiyon.
	@param dur: mevcut notanın çalınma süresi
	@return: oluşturulan nota
'''

def randomNote(dur):
	# nota A-G arasından rastgele seçilir:
	noteName = noteNames[randint(0, 6)]
	# nota değeri 1-7 arasından rastgele seçilir:
	noteOctave = noteOctaves[randint(0, 15)]
	newNote = note.Note(noteName + str(noteOctave))
	# notanın süresi atanır:
	newNote.duration = dur
	return newNote

#########################################
'''
	İlk oluşturulan nesil için ilklendirmeleri yapan fonksiyon.
	@param baseComposition: taklit edilecek müzik parçası
	@return iklendirilmiş nesil
'''

def initializeCompositions(baseComposition):
	compositions = []

	for _ in range(100):
		composition = Composition()
		# notalar iklendirilir:
		composition.initializeNotes(baseComposition)
		# akortlar ve boşluklar ilklendirilir:
		composition.assignRestsAndChords(baseComposition)
		# nota süreleri ilklendirilir:
		composition.assignDurations(baseComposition)
		# fitness değeri ölçülür:
		composition.calculateFitness(baseComposition)
		compositions.append(composition)

	return compositions

#########################################
'''
	Yeni birey için iki tane ebeveyn seçen fonksiyon.
	@return: ebeveynlerin indisleri
'''

def selectParents():
	# %70 ihtimalle en iyi 5 ebeveynden seçim yapılır
	if randint(1, 10) <= 7:
		return randint(0, 5), randint(0, 5)
	# %21 ihtimalle en iyi 10 ebeveynden seçim yapılır
	elif randint(1, 10) <= 7:
		return randint(0, 10), randint(0, 10)

	# %9 ihtimalle en iyi 25 ebeveynden seçim yapılır
	return randint(0, 25), randint(0, 25)

#########################################
'''
	Seçilen iki ebeveyni çarprazlayan fonksiyon.
	@param notes1: birinci müzik parçası
	@param notes2: ikinci müzik parçası
	@return: çarprazlama sonucu oluşan müzik parçası
'''

def crossover(notes1, notes2):
	newNotes = []
	threshold = randint(0, len(notes1)-1) # çarpazlamanın yapılacağı konum

	for i in range(threshold):
		# mevcut nota %99 ihtimalle yeni müziğe eklenir
		if type(notes1[i]) != note.Note or randint(1, 100) <= 99:
			newNotes.append(notes1[i])
		else:	# mutasyon
			newNotes.append(randomNote(notes1[i].duration))

	for i in range(threshold, len(notes1)):
		# mevcut nota %99 ihtimalle yeni müziğe eklenir
		if type(notes2[i]) != note.Note or randint(1, 100) <= 99:
			newNotes.append(notes2[i])
		else:  # mutasyon
			newNotes.append(randomNote(notes2[i].duration))

	return newNotes

#########################################
'''
	Nesillerin evrim geçirmesini sağlayan fonksiyon.
	@param compositions: mevcut nesildeki müzik parçaları
	@param baseComposition: taklit edilen müzik parçası
	@return: evrim geçiren müzik parçaları
'''

def evolution(compositions, baseComposition):
	newCompositions = []

	for i in range(len(compositions)):
		# müzik parçasının ebeveynleri seçilir:
		x, y = selectParents()
		composition = Composition()
		# seçilen ebeveynlerin çarprazlanmasıyla yeni birey oluşturulur:
		composition.notes = crossover(compositions[x].notes, compositions[y].notes)
		# yeni bireyin fitness değeri ölçülür:
		composition.calculateFitness(baseComposition)
		# birey, yeni nesle eklenir:
		newCompositions.append(composition)

	return newCompositions

#########################################
'''
	Terminal ekranını temizleyen fonksiyon.
'''

def clearScreen():
    if platform.system() == "Windows":
        os.system("cls")
    else:                  # Linux & Mac OS
        os.system("clear")

#########################################

'''
	Program logosunu bastıran fonksiyon.
'''
def printBanner():
	clearScreen()
	print("\n\t#####################################")
	print("\t########## GENETİK BESTECİ ##########")
	print("\t#####################################\n")

#########################################

'''
	Program menüsünü bastıran fonksiyon.
'''
def printMenu():
	print("\t1. Gesi Bağları")
	print("\t2. Lüküs Hayat")
	print("\t3. Bir Masal Anlat Bana")
	print("\t4. Bak Postacı Geliyor")
	print("\t5. Küçük Kurbağa")
	print("\t6. Tren Geliyor")
	print("\t7. Yağmur Yağıyor")
	print("\t8. Yağ Satarım")
	print("\t9. Uç Uç Böceğim")
	print("\t10. Şimdi Okullu Olduk")
	print("\t11. Kendi '.mid' Dosyanız")
	print("\t12. Çıkış")

#########################################

def main():
	# şarkıların konumları için bir dizi:
	songs = ["gesi.mid", "lukus.mid", "masal.mid", "postaci.mid", "kurbaga.mid",
			 "tren.mid", "yagmur.mid", "yag.mid", "bocek.mid", "okul.mid"]

	# program menüsü yazdırılır:
	printBanner()
	printMenu()
	print("\n\tŞarkı seçiminizi girin: ", end="")
	choice = int(input()) # kullanıcıdan şarkı seçimi alınır
	filePath = ""

	if choice == 12: # çıkış:
		exit()
	elif choice == 11: # kullanıcı kendi ".mid" dosyasını girer:
		print("\tDosyanın konumunu girin: ", end=""),
		filePath = input()
	else: # bir şarkı seçildi:
		filePath = "dataset/" + songs[choice-1]

	fileExists = os.path.exists(filePath)

	if (fileExists == False): # dosyanın mevcut olup olmadığı kontrol edilir
		print("\n\tDosya okunamadı.\n")
		exit()

	# kullanıcıdan nesil (generation) sayısı alınır
	print("\tNesil sayısını girin (tavsiye edilen: 100): ", end="")
	gen = int(input())

	print("\n\tVaryasyon oluşturuluyor...")

	baseComposition = Composition()
	baseComposition.notes = readStream(filePath) # .mid dosyası okunuyor

	# ilk nesil ilklendiriliyor:
	compositions = initializeCompositions(baseComposition)
	# oluşan parçalar, fitness değerlerine göre sıralanıyor:
	compositions.sort(key=lambda composition: composition.fitness)

	print("\tBaşlangıç fitness değeri: ", compositions[0].fitness)

	for _ in range(gen):
		# nesiller evrim geçiriyor:
		compositions = evolution(compositions, baseComposition)
		# oluşan parçalar, fitness değerlerine göre sıralanıyor:
		compositions.sort(key=lambda composition: composition.fitness)

	print("\t" + str(gen) + " nesil sonucu oluşan fitness değeri: ", compositions[0].fitness)

	filePath = filePath.replace(".mid", "_variation.mid")
	writeStream(compositions[0].notes, filePath) # varyasyon müzik yazdırılıyor

	print("\n\tVaryasyon oluşturuldu:", filePath)

if __name__ == '__main__':
	main()