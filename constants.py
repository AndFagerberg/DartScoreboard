# Färgschema
COLORS = {
    'bg': '#1a1a2e',
    'panel': '#16213e',
    'accent': '#e94560',
    'accent2': '#0f3460',
    'text': '#eaeaea',
    'gold': '#ffd700',
    'green': '#4ecca3',
    'red': '#ff6b6b',
    'button': '#0f3460',
    'button_active': '#e94560',
}

# Spelförklaringar
GAME_HELP = {
    'x01': {
        'title': 'X01 (301/501/701)',
        'text': '''Klassiskt dart där du räknar ner.

• Börja på 301, 501 eller 701
• Varje kast dras från poängen
• Först till exakt 0 vinner

Double Out (valfritt):
Sista pilen måste träffa en
double (yttre smala ringen).

Bust: Om du går under 0 eller
hamnar på 1 med Double Out
räknas rundan inte.'''
    },
    'cricket': {
        'title': 'Cricket',
        'text': '''Stäng nummer och samla poäng!

Mål: 20, 19, 18, 17, 16, 15, Bull

• Träffa ett nummer 3 gånger
  för att "stänga" det
• Single = 1, Double = 2, Triple = 3
• / = 1 träff, X = 2, Ⓧ = stängd

Poäng: När du stängt ett nummer
kan du samla poäng på det - tills
motståndaren också stänger det.

Vinner: Stäng alla + ha flest poäng'''
    },
    'around_the_clock': {
        'title': 'Klockan',
        'text': '''Träffa alla nummer i ordning!

• Börja på 1, sedan 2, 3... till 20
• Sist: träffa Bull för att vinna
• Multiplier spelar ingen roll
  - single, double eller triple
  räknas alla som en träff

Tips: Fokusera på precision,
inte på poäng!

Först runt klockan vinner.'''
    },
    'killer': {
        'title': 'Killer',
        'text': '''Bli Killer och eliminera andra!

• Varje spelare får ett slumpat nummer
• Fas 1: Träffa din egen double
  för att bli Killer (K)
• Fas 2: Träffa andras double
  för att ta deras liv
• 3 liv per spelare
• 0 liv = eliminerad

OBS: Träffar du din egen double
som Killer förlorar DU ett liv!

Sista överlevande vinner.'''
    },
    'hits_killer': {
        'title': 'Hits Killer',
        'text': '''Killer med träffar istället för double!

• Varje spelare får ett slumpat nummer
• Fas 1: Träffa ditt nummer 3 gånger
  för att bli Killer
  (S=1, D=2, T=3 träffar)
• Fas 2: Träffa andras nummer
  för att ta deras liv
  (S=1, D=2, T=3 skada)
• 3 liv per spelare

VARNING: Träffar du en annan
spelares nummer INNAN du är
Killer är du ELIMINERAD!

Sista överlevande vinner.'''
    },
    'triple_killer': {
        'title': 'Triple Killer',
        'text': '''Samma som Killer men med trippel!

• Varje spelare får ett slumpat nummer
• Fas 1: Träffa din egen trippel
  för att bli Killer (K)
• Fas 2: Träffa andras trippel
  för att ta deras liv
• 3 liv per spelare
• 0 liv = eliminerad

Skillnad mot vanlig Killer:
Här gäller trippel istället för
dubbel - svårare men roligare!

Sista överlevande vinner.'''
    },
    'shanghai': {
        'title': 'Shanghai',
        'text': '''20 rundor, runda = mål!

• Runda 1: sikta på 1
• Runda 2: sikta på 2... osv
• Poäng endast på rätt nummer
• Single = värde, D = x2, T = x3

SHANGHAI (direkt vinst):
Träffa single + double + triple
på samma nummer i samma runda!

Högst poäng efter 20 rundor vinner
(om ingen Shanghai).'''
    },
    'halveit': {
        'title': 'Halve It',
        'text': '''Träffa målet eller halvera!

9 rundor med specifika mål:
1. 20  2. 19  3. 18
4. Doubles  5. 17  6. 16
7. 15  8. Triples  9. Bull

• Miss på en runda = din poäng
  halveras!
• Doubles/Triples: alla räknas
• Bull: inner=50, outer=25

Tips: Riskera inte att missa
när du har många poäng!

Högst poäng efter 9 rundor vinner.'''
    },
    'highscore': {
        'title': 'High Score',
        'text': '''Enkel poängjakt!

• 10 rundor per spelare
• Alla träffar räknas normalt
• Single, Double (x2), Triple (x3)
• Ingen speciell regel

Tips:
• Sikta på Triple 20 (60p)
• Triple 19 (57p) är backup
• Bull ger 50p (inner) eller 25p

Högst totalpoäng efter
alla rundor vinner!'''
    },
    'golf': {
        'title': 'Golf',
        'text': '''Lägst poäng vinner!

9 hål - varje hål = ett nummer:
• Hål 1: sikta på 1
• Hål 2: sikta på 2... osv till 9

Poängsättning per pil:
• Triple = 1 (hole in one!)
• Double = 2
• Single = 3
• Miss = 5

Bästa pilen räknas (3 försök).

Lägst totalt efter 9 hål vinner!'''
    },
    'all': {
        'title': 'Spelregler',
        'text': '''X01: Räkna ner till 0.

Cricket: Stäng 20-15 + Bull.

Klockan: Träffa 1-20 + Bull i ordning.

Killer: Bli Killer, eliminera
andra genom deras double.

Triple Killer: Som Killer
men med trippel istället.

Hits Killer: 3 träffar för killer,
träffa annans = du är ute!

Shanghai: 20 rundor, runda=mål.
S+D+T samma runda = direkt vinst!

Halve It: 9 mål, miss = halv poäng.

High Score: 10 rundor, högst vinner.

Golf: 9 hål, lägst poäng vinner.'''
    }
}

# Fördefinierade namn för touch-val
PRESET_NAMES = [
    "Albin", "Andreas", "Linnea", "Evelinn", 
    "Spelare 1", "Spelare 2", "Spelare 3", "Spelare 4",
    "Farfar", "Farmor", "Morfar", "Mormor",
]

# Checkout-kombinationer (vanligaste)
CHECKOUTS = {
    170: "T20 T20 Bull", 167: "T20 T19 Bull", 164: "T20 T18 Bull",
    161: "T20 T17 Bull", 160: "T20 T20 D20", 158: "T20 T20 D19",
    157: "T20 T19 D20", 156: "T20 T20 D18", 155: "T20 T19 D19",
    154: "T20 T18 D20", 153: "T20 T19 D18", 152: "T20 T20 D16",
    151: "T20 T17 D20", 150: "T20 T18 D18", 149: "T20 T19 D16",
    148: "T20 T20 D14", 147: "T20 T17 D18", 146: "T20 T18 D16",
    145: "T20 T19 D14", 144: "T20 T20 D12", 143: "T20 T17 D16",
    142: "T20 T14 D20", 141: "T20 T19 D12", 140: "T20 T20 D10",
    139: "T20 T13 D20", 138: "T20 T18 D12", 137: "T20 T19 D10",
    136: "T20 T20 D8", 135: "T20 T17 D12", 134: "T20 T14 D16",
    133: "T20 T19 D8", 132: "T20 T16 D12", 131: "T20 T13 D16",
    130: "T20 T18 D8", 129: "T19 T16 D12", 128: "T18 T14 D16",
    127: "T20 T17 D8", 126: "T19 T19 D6", 125: "T20 T19 D4",
    124: "T20 T14 D11", 123: "T19 T16 D9", 122: "T18 T18 D7",
    121: "T20 T11 D14", 120: "T20 S20 D20", 119: "T19 T12 D13",
    118: "T20 S18 D20", 117: "T20 S17 D20", 116: "T20 S16 D20",
    115: "T20 S15 D20", 114: "T20 S14 D20", 113: "T20 S13 D20",
    112: "T20 S12 D20", 111: "T20 S11 D20", 110: "T20 S10 D20",
    109: "T20 S9 D20", 108: "T20 S8 D20", 107: "T19 S10 D20",
    106: "T20 S6 D20", 105: "T20 S5 D20", 104: "T18 S10 D20",
    103: "T19 S6 D20", 102: "T20 S10 D16", 101: "T17 S10 D20",
    100: "T20 D20", 99: "T19 S10 D16", 98: "T20 D19",
    97: "T19 D20", 96: "T20 D18", 95: "T19 D19",
    94: "T18 D20", 93: "T19 D18", 92: "T20 D16",
    91: "T17 D20", 90: "T18 D18", 89: "T19 D16",
    88: "T20 D14", 87: "T17 D18", 86: "T18 D16",
    85: "T15 D20", 84: "T20 D12", 83: "T17 D16",
    82: "T14 D20", 81: "T19 D12", 80: "T20 D10",
    79: "T13 D20", 78: "T18 D12", 77: "T19 D10",
    76: "T20 D8", 75: "T17 D12", 74: "T14 D16",
    73: "T19 D8", 72: "T16 D12", 71: "T13 D16",
    70: "T18 D8", 69: "T19 D6", 68: "T20 D4",
    67: "T17 D8", 66: "T10 D18", 65: "T19 D4",
    64: "T16 D8", 63: "T13 D12", 62: "T10 D16",
    61: "T15 D8", 60: "S20 D20", 59: "S19 D20",
    58: "S18 D20", 57: "S17 D20", 56: "T16 D4",
    55: "S15 D20", 54: "S14 D20", 53: "S13 D20",
    52: "S12 D20", 51: "S11 D20", 50: "S10 D20",
    49: "S9 D20", 48: "S8 D20", 47: "S15 D16",
    46: "S6 D20", 45: "S13 D16", 44: "S12 D16",
    43: "S11 D16", 42: "S10 D16", 41: "S9 D16",
    40: "D20", 38: "D19", 36: "D18", 34: "D17",
    32: "D16", 30: "D15", 28: "D14", 26: "D13",
    24: "D12", 22: "D11", 20: "D10", 18: "D9",
    16: "D8", 14: "D7", 12: "D6", 10: "D5",
    8: "D4", 6: "D3", 4: "D2", 2: "D1",
}
