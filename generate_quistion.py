"""
Savollar generatori — TO'G'RI DARAJALAR:
  ⚪ juda_oson  → 1-10 qo'shish/ayirish, x2/x3
  🟢 oson       → jadval ko'paytirish, bo'lish, oddiy ketma-ketlik
  🟡 orta       → kvadrat, geometrik, %, amallar tartibi
  🔴 qiyin      → kub, fibonacci, (a+b)², murakkab masalalar
  🔥 juda_qiyin → 4-daraja, tenglama, log, rekursiv

Topishmoqlar: daraja="topishmoq", kamida 60 ta

Ishlatish: py generate_questions.py
"""
import json, os, random
os.makedirs("questions", exist_ok=True)

# ─── YORDAMCHI ──────────────────────────────────────
def o4(ans, w1, w2, w3):
    seen, res = set(), []
    for v in [str(ans), str(w1), str(w2), str(w3)]:
        if v not in seen:
            seen.add(v); res.append(v)
    extra = 1
    while len(res) < 4:
        v = str(int(str(ans).replace("°","").replace(" minut","")) + extra)
        if v not in seen:
            seen.add(v); res.append(v)
        extra += 1
    random.shuffle(res)
    return res, str(ans)

def dedup(qs, limit=999999):
    seen, u = set(), []
    for q in qs:
        if q["question"] not in seen:
            seen.add(q["question"]); u.append(q)
    random.shuffle(u)
    return u[:limit]

def is_prime(n):
    if n < 2: return False
    for i in range(2, int(n**0.5)+1):
        if n % i == 0: return False
    return True

# ═══════════════════════════════════════════════════════
#   IQ SAVOLLAR
# ═══════════════════════════════════════════════════════

def iq_juda_oson():
    qs = []
    # 1-10 qo'shish
    for a in range(1, 11):
        for b in range(1, 11):
            ans = a + b
            o, a_ = o4(ans, ans+1, ans-1, ans+2)
            qs.append({"question": f"{a} + {b} = ?", "options": o, "answer": a_, "daraja": "juda_oson"})
    # 2-15 ayirish
    for a in range(2, 16):
        for b in range(1, a):
            ans = a - b
            o, a_ = o4(ans, ans+1, ans-1, a)
            qs.append({"question": f"{a} - {b} = ?", "options": o, "answer": a_, "daraja": "juda_oson"})
    # x2, x3 (1-10)
    for a in range(1, 11):
        for m in [2, 3]:
            ans = a * m
            o, a_ = o4(ans, ans+1, ans-1, ans+m)
            qs.append({"question": f"{a} × {m} = ?", "options": o, "answer": a_, "daraja": "juda_oson"})
    # ? + b = c
    for total in range(3, 15):
        for b in range(1, total):
            ans = total - b
            o, a_ = o4(ans, ans+1, ans-1, total)
            qs.append({"question": f"? + {b} = {total}", "options": o, "answer": a_, "daraja": "juda_oson"})
    return dedup(qs, 1000)

def iq_oson():
    qs = []
    # Jadval 2-12
    for a in range(2, 13):
        for b in range(2, 13):
            ans = a * b
            o, a_ = o4(ans, ans+a, ans-b, ans+b)
            qs.append({"question": f"{a} × {b} = ?", "options": o, "answer": a_, "daraja": "oson"})
    # Bo'lish
    for a in range(2, 12):
        for b in range(2, 12):
            o, a_ = o4(a, a+1, a-1, b)
            qs.append({"question": f"{a*b} ÷ {b} = ?", "options": o, "answer": a_, "daraja": "oson"})
    # Arifmetik ketma-ketlik step 2-5
    for start in range(1, 15):
        for step in range(2, 6):
            seq = [start + step*i for i in range(5)]
            ans = seq[-1] + step
            o, a_ = o4(ans, ans+step, ans-step, ans+1)
            qs.append({"question": f"Keyingi son?\n{', '.join(map(str,seq))}, ?", "options": o, "answer": a_, "daraja": "oson"})
    # Oddiy % (10, 25, 50)
    for whole in [10, 20, 40, 50, 100, 200]:
        for pct in [10, 25, 50]:
            ans = whole * pct // 100
            o, a_ = o4(ans, ans+5, ans-2, whole//2)
            qs.append({"question": f"{whole} ning {pct}% = ?", "options": o, "answer": a_, "daraja": "oson"})
    return dedup(qs, 1000)

def iq_orta():
    qs = []
    # Kvadratlar 2-20
    for n in range(2, 21):
        ans = n*n
        o, a_ = o4(ans, (n+1)**2, (n-1)**2, n*n+n)
        qs.append({"question": f"{n}² = ?", "options": o, "answer": a_, "daraja": "orta"})
    # Geometrik r=2,3
    for a in range(1, 8):
        for r in [2, 3]:
            seq = [a*(r**i) for i in range(5)]
            ans = seq[-1]*r
            o, a_ = o4(ans, ans+r, ans-a, seq[-1])
            qs.append({"question": f"Geometrik ketma-ketlik:\n{', '.join(map(str,seq))}, ?", "options": o, "answer": a_, "daraja": "orta"})
    # Amallar tartibi
    for a in range(2, 10):
        for b in range(2, 8):
            for c in range(2, 6):
                ans = a + b*c
                o, a_ = o4(ans, (a+b)*c, a*b+c, ans+1)
                qs.append({"question": f"{a} + {b} × {c} = ?", "options": o, "answer": a_, "daraja": "orta"})
    # Murakkab %
    for whole in [80, 120, 150, 250, 500]:
        for pct in [15, 20, 30, 40, 60]:
            ans = whole*pct//100
            o, a_ = o4(ans, ans+15, ans-10, whole-ans)
            qs.append({"question": f"{whole} ning {pct}% = ?", "options": o, "answer": a_, "daraja": "orta"})
    # Arifmetik step 6-15
    for start in range(1, 15):
        for step in range(6, 16):
            seq = [start + step*i for i in range(5)]
            ans = seq[-1]+step
            o, a_ = o4(ans, ans+step, ans-step, ans+1)
            qs.append({"question": f"Keyingi son:\n{', '.join(map(str,seq))}, ?", "options": o, "answer": a_, "daraja": "orta"})
    return dedup(qs, 1000)

def iq_qiyin():
    qs = []
    # Kublar 2-15
    for n in range(2, 16):
        ans = n**3
        o, a_ = o4(ans, (n+1)**3, (n-1)**3, n*n*2)
        qs.append({"question": f"{n}³ = ?", "options": o, "answer": a_, "daraja": "qiyin"})
    # Fibonacci variatsiya
    for a in range(1, 12):
        for b in range(a, 15):
            c, d, e = a+b, a+2*b, 2*a+3*b
            ans = 3*a+5*b
            o, a_ = o4(ans, ans+a, ans-b, e+b)
            qs.append({"question": f"Qonuniyat:\n{a}, {b}, {c}, {d}, {e}, ?", "options": o, "answer": a_, "daraja": "qiyin"})
    # a² - b²
    for a in range(4, 18):
        for b in range(2, a):
            ans = a**2 - b**2
            if ans > 0:
                o, a_ = o4(ans, ans+b, ans-a, (a-b)**2)
                qs.append({"question": f"{a}² - {b}² = ?", "options": o, "answer": a_, "daraja": "qiyin"})
    # (a+b)²
    for a in range(2, 10):
        for b in range(1, 8):
            ans = (a+b)**2
            o, a_ = o4(ans, a**2+b**2, ans+a, (a-b)**2)
            qs.append({"question": f"({a}+{b})² = ?", "options": o, "answer": a_, "daraja": "qiyin"})
    return dedup(qs, 1000)

def iq_juda_qiyin():
    qs = []
    # n⁴
    for n in range(2, 12):
        ans = n**4
        o, a_ = o4(ans, (n+1)**4, n**3*2, (n-1)**4)
        qs.append({"question": f"{n}⁴ = ?", "options": o, "answer": a_, "daraja": "juda_qiyin"})
    # ax + b = c
    for a in range(2, 10):
        for b in range(1, 8):
            for x in range(1, 8):
                c = a*x + b
                o, a_ = o4(x, x+1, x-1, x+2)
                qs.append({"question": f"{a}x + {b} = {c}. x = ?", "options": o, "answer": a_, "daraja": "juda_qiyin"})
    # x ÷ a = b
    for a in range(2, 8):
        for b in range(2, 12):
            ans = a*b
            o, a_ = o4(ans, ans+a, ans-b, a+b)
            qs.append({"question": f"x ÷ {a} = {b}. x = ?", "options": o, "answer": a_, "daraja": "juda_qiyin"})
    # (a+b)*c
    for a in range(2, 8):
        for b in range(2, 8):
            for c in range(2, 6):
                ans = (a+b)*c
                o, a_ = o4(ans, a*c+b, a+b*c, ans+c)
                qs.append({"question": f"({a} + {b}) × {c} = ?", "options": o, "answer": a_, "daraja": "juda_qiyin"})
    # Daraja
    powers = [(2,4,16),(2,8,256),(2,10,1024),(3,4,81),(3,5,243),(5,3,125),(4,4,256),(2,5,32),(3,3,27),(4,3,64)]
    for base, exp, result in powers:
        o, a_ = o4(result, result+base, result-exp, base**2)
        qs.append({"question": f"{base}^{exp} = ?", "options": o, "answer": a_, "daraja": "juda_qiyin"})
    return dedup(qs, 1000)

# ═══════════════════════════════════════════════════════
#   MANTIQ SAVOLLAR
# ═══════════════════════════════════════════════════════
DAYS = ["Dushanba","Seshanba","Chorshanba","Payshanba","Juma","Shanba","Yakshanba"]
MONTHS = ["Yanvar","Fevral","Mart","Aprel","May","Iyun","Iyul","Avgust","Sentabr","Oktabr","Noyabr","Dekabr"]

def logic_juda_oson():
    qs = []
    # +1,+2,+3 kun
    for i, d in enumerate(DAYS):
        for add in [1, 2, 3]:
            res = DAYS[(i+add)%7]
            w = [x for x in DAYS if x != res][:3]
            opts = [res]+w; random.shuffle(opts)
            qs.append({"question": f"Bugun {d}. {add} kundan keyin?", "options": opts, "answer": res, "daraja": "juda_oson"})
    # Qaysi biri boshqacha — juda sodda
    easy = [
        (["Olma","Nok","Banan","Mashina"], "Mashina"),
        (["It","Mushuk","Qush","Stol"], "Stol"),
        (["Qizil","Ko'k","Yashil","Kitob"], "Kitob"),
        (["Uchburchak","Kvadrat","Doira","Non"], "Non"),
        (["Samolyot","Avtobus","Poyezd","Baliq"], "Baliq"),
        (["Ko'z","Quloq","Burun","Tosh"], "Tosh"),
        (["Kitob","Daftar","Ruchka","Sabzi"], "Sabzi"),
        (["Olcha","Gilos","O'rik","Piyoz"], "Piyoz"),
        (["Mushuk","Sher","Yo'lbars","Daraxt"], "Daraxt"),
        (["Stol","Kursi","Shkaf","Tarvuz"], "Tarvuz"),
        (["Oltin","Kumush","Bronza","Qog'oz"], "Qog'oz"),
        (["Non","Guruch","Un","Asfalt"], "Asfalt"),
        (["Apelsin","Limon","Mandarin","Eshak"], "Eshak"),
        (["Archa","Qayin","Terak","Kaktus"], "Kaktus"),
        (["Mars","Venera","Saturn","Dengiz"], "Dengiz"),
        (["Kapalak","Ari","Chivin","Ilon"], "Ilon"),
        (["Baliq","Kit","Qisqichbaqa","Burgut"], "Burgut"),
        (["Tort","Halva","Pechene","Tuz"], "Tuz"),
        (["Benzin","Neft","Gaz","Suv"], "Suv"),
        (["Qovoq","Bodring","Pomidor","Olma"], "Olma"),
    ]
    for _ in range(50):
        for base, ans in easy:
            o = base[:]; random.shuffle(o)
            qs.append({"question": "Qaysi biri boshqacha?\n"+", ".join(base), "options": o, "answer": ans, "daraja": "juda_oson"})
    # Katta/kichik
    for a in range(1, 12):
        for b in range(a+1, 13):
            o = [str(a), str(b), str(a+b), str(b-a)]; random.shuffle(o)
            qs.append({"question": f"{a} va {b} dan kichigi?", "options": o, "answer": str(a), "daraja": "juda_oson"})
    return dedup(qs, 1000)

def logic_oson():
    qs = []
    # +7,+14,+21
    for i, d in enumerate(DAYS):
        for add in [7, 14, 21, 28]:
            res = DAYS[(i+add)%7]
            w = [x for x in DAYS if x != res][:3]
            opts = [res]+w; random.shuffle(opts)
            qs.append({"question": f"Bugun {d}. {add} kundan keyin?", "options": opts, "answer": res, "daraja": "oson"})
    # Tub/tub emas
    composites = [4,6,8,9,10,12,14,15,16,18,20,21,22,24,25,26,27,28,30,33,35]
    primes_l = [p for p in range(2, 60) if is_prime(p)]
    for comp in composites:
        gp = random.sample(primes_l, 3)
        g = gp+[comp]; random.shuffle(g)
        qs.append({"question": "Tub son EMAS qaysi?\n"+", ".join(map(str,g)), "options": [str(x) for x in g], "answer": str(comp), "daraja": "oson"})
    # Juft/toq
    for _ in range(300):
        evens = random.sample(range(2, 100, 2), 3)
        odd = random.choice(range(1, 100, 2))
        g = evens+[odd]; random.shuffle(g)
        qs.append({"question": "Qaysi biri boshqacha?\n"+", ".join(map(str,g)), "options": [str(x) for x in g], "answer": str(odd), "daraja": "oson"})
    # Mushuk-sichqon
    for cats in range(2, 8):
        for t in range(2, 8):
            ra = f"{t} minut"
            wo = [f"{t*cats} minut", f"{cats} minut", f"{t*2} minut"]
            opts = [ra]+wo; random.shuffle(opts)
            qs.append({"question": f"{cats} mushuk {cats} sichqonni {t} minutda ushlasa,\n1 mushuk 1 sichqonni necha minutda ushlaydi?", "options": opts, "answer": ra, "daraja": "oson"})
    return dedup(qs, 1000)

def logic_orta():
    qs = []
    # Oylar
    for i, oy in enumerate(MONTHS):
        for add in range(1, 12):
            res = MONTHS[(i+add)%12]
            w = [o for o in MONTHS if o != res][:3]
            opts = [res]+w; random.shuffle(opts)
            qs.append({"question": f"Hozir {oy}. {add} oydan keyin?", "options": opts, "answer": res, "daraja": "orta"})
    # Mantiqiy xulosalar
    syll = [
        ("Barcha odamlar o'ladi. Sokrat odam. Demak Sokrat:", ["O'ladi","O'lmaydi","Odam emas","Hech narsa"], "O'ladi"),
        ("Barcha qushlar uchadi. Pingvin qush. Demak pingvin:", ["Uchadi","Uchmaydi","Qush emas","Sut emizuvchi"], "Uchadi"),
        ("Hech bir baliq qush emas. Losos baliq. Demak losos:", ["Qush emas","Qush","Uchadi","Dengiz hayvoni"], "Qush emas"),
        ("Barcha A — B. Barcha B — C. Demak:", ["A — C","A — B emas","C — A","Faqat B — C"], "A — C"),
        ("X > Y va Y > Z. Demak:", ["X > Z","Z > X","X = Z","Y > X"], "X > Z"),
        ("Yomg'ir yog'sa ko'cha ho'l bo'ladi. Ko'cha quruq. Demak:", ["Yomg'ir yog'magan","Yomg'ir yog'gan","Doim quruq","Hech narsa"], "Yomg'ir yog'magan"),
        ("Barcha doktorlar aqlli. Alisher doktor. Demak:", ["Alisher aqlli","Aqlli emas","Doktorlar bema'ni","Hech narsa"], "Alisher aqlli"),
        ("Agar A bo'lsa B bo'ladi. B bo'lmadi. Demak:", ["A bo'lmadi","A bo'ldi","B doim bo'ladi","Hech narsa"], "A bo'lmadi"),
        ("Barcha metallar elektr o'tkazadi. Oltin metall. Demak:", ["Oltin o'tkazadi","O'tkazmaydi","Metallar zaif","Hech narsa"], "Oltin o'tkazadi"),
        ("Hech bir suv yonmaydi. Bu modda suv. Demak:", ["Yonmaydi","Yonadi","Suv emas","Gaz"], "Yonmaydi"),
        ("Barcha planetalar quyosh atrofida aylanadi. Yer planeta. Demak:", ["Yer aylanadi","Yer aylanmaydi","Quyosh aylanadi","Hech narsa"], "Yer aylanadi"),
        ("Hech bir inson baliq emas. Kamol inson. Demak:", ["Kamol baliq emas","Kamol baliq","Inson baliq","Hech narsa"], "Kamol baliq emas"),
    ]
    for _ in range(85):
        for q, o, a in syll:
            oc = o[:]; random.shuffle(oc)
            qs.append({"question": q, "options": oc, "answer": a, "daraja": "orta"})
    # Yosh masalalari
    for yosh in range(5, 25):
        for yil in range(1, 8):
            ans = yosh + yil
            o, a_ = o4(ans, ans+1, ans-1, yosh)
            qs.append({"question": f"Alining hozirgi yoshi {yosh}. {yil} yildan keyin?", "options": o, "answer": a_, "daraja": "orta"})
    # Uchta ketma-ket son
    for n in range(1, 40):
        for step in range(1, 6):
            total = 3*n + 3*step
            mid = n + step
            o, a_ = o4(mid, mid+1, mid-1, mid+step)
            qs.append({"question": f"Uchta ketma-ket sonning yig'indisi {total}. O'rtasi?", "options": o, "answer": a_, "daraja": "orta"})
    return dedup(qs, 1000)

def logic_qiyin():
    qs = []
    hard = [
        ("Ko'l ichida 1 ta nilufar, har kuni ikkilanadi, 30 kunda to'ladi. Yarmi necha kunda to'lgan?", ["29-kunda","15-kunda","20-kunda","25-kunda"], "29-kunda"),
        ("Fermer 17 ta qo'yi bor, bittasidan tashqari hammasi o'ldi. Nechta qoldi?", ["1","0","16","17"], "1"),
        ("1 tuxum 5 daqiqada pishadigan bo'lsa, 5 tuxum bir vaqtda pishirishga necha daqiqa?", ["5","25","10","15"], "5"),
        ("Xonada 4 burchak, har burchakda 1 mushuk, har mushuk 3 mushuk ko'radi. Nechta mushuk?", ["4","12","16","8"], "4"),
        ("5 non 5 bolaga 5 daqiqada yetdi. 100 nonga 100 bolaga necha daqiqa?", ["5","100","50","25"], "5"),
        ("3 tuxumni qaynatish 3 daqiqa. 9 tuxumni qaynatish necha daqiqa?", ["3","9","27","6"], "3"),
        ("2 yil oldin Alining yoshi 10 bo'lsa, 3 yildan keyin necha bo'ladi?", ["15","12","13","10"], "15"),
        ("6 qora, 6 oq, 6 ko'k paypoq. Minimum nechta olsa juft bo'ladi?", ["4","3","6","2"], "4"),
        ("Agar 3=9, 4=16, 5=25 bo'lsa, 6=?", ["36","12","30","18"], "36"),
        ("Agar 1=3, 2=3, 3=5, 4=4 bo'lsa, 5=?", ["4","3","5","6"], "4"),
        ("a+b=10 va a-b=4 bo'lsa, a×b=?", ["21","24","40","14"], "21"),
        ("Ko'paytmasi 48, yig'indisi 14. Kattasi?", ["8","6","10","12"], "8"),
        ("Soat 3:00 da strelkalar orasidagi burchak?", ["90°","0°","180°","45°"], "90°"),
        ("Soat 6:00 da strelkalar orasidagi burchak?", ["180°","90°","0°","270°"], "180°"),
        ("Soat 9:00 da strelkalar orasidagi burchak?", ["270°","90°","180°","360°"], "270°"),
        ("Soat 12:00 da strelkalar orasidagi burchak?", ["0°","180°","90°","360°"], "0°"),
        ("Bir soatda daqiqa mili soat miliga necha marta yetib oladi?", ["11","12","1","60"], "11"),
        ("Bugun chorshanba. 100 kun keyin?", ["Shanba","Juma","Dushanba","Chorshanba"], "Shanba"),
        ("Bugun seshanba. 365 kun keyin?", ["Chorshanba","Seshanba","Dushanba","Payshanba"], "Chorshanba"),
        ("p va q tub son, p+q=10. p×q maksimum? Javob:", ["21","16","25","15"], "21"),
    ]
    for _ in range(55):
        for q, o, a in hard:
            oc = o[:]; random.shuffle(oc)
            qs.append({"question": q, "options": oc, "answer": a, "daraja": "qiyin"})
    # Tub sonlar soni
    for n in range(2, 50):
        cnt = len([p for p in range(n, n+20) if is_prime(p)])
        o, a_ = o4(cnt, cnt+1, cnt-1, cnt+2)
        qs.append({"question": f"{n} dan {n+19} gacha nechta tub son bor?", "options": o, "answer": a_, "daraja": "qiyin"})
    return dedup(qs, 1000)

def logic_juda_qiyin():
    qs = []
    vhard = [
        ("Barcha X—Y, ba'zi Y—Z bo'lsa, ba'zi X haqida:", ["Hech narsa aytib bo'lmaydi","Barcha X—Z","Ba'zi X—Z","Hech bir X—Z emas"], "Hech narsa aytib bo'lmaydi"),
        ("Mantiqiy paradoks o'z-o'zini inkor etsa:", ["Na rost, na yolg'on","Rost","Yolg'on","Ikkisi ham"], "Na rost, na yolg'on"),
        ("Cheksiz mehmonxona to'la, yangi mehmon keldi. Joylashtirish mumkinmi?", ["Ha, mumkin","Yo'q","Faqat pullik","Yo'q"], "Ha, mumkin"),
        ("3 kishi: biri doim rost, biri doim yolg'on, biri goh-goh. Minimal nechta savol?", ["3","2","1","5"], "3"),
        ("A={1,2,3,4}, B={2,4,6,8}. A∩B=?", ["{2,4}","{1,2,3,4,6,8}","{1,3}","{6,8}"], "{2,4}"),
        ("A={1,2,3}, B={2,3,4}. A∪B=?", ["{1,2,3,4}","{2,3}","{1,4}","{1,2,3,4,5}"], "{1,2,3,4}"),
        ("n!/(n-2)!=90. n=?", ["10","9","8","11"], "10"),
        ("f(x)=2x+1, f(f(x))=19. x=?", ["4","5","6","9"], "4"),
        ("2^10=1024. 2^20 taxminan?", ["~1 million","~500 ming","~2 million","~100 ming"], "~1 million"),
        ("ABCD×4=DCBA. A+B+C+D=?", ["18","24","12","27"], "18"),
        ("Soat 3:15 da strelkalar orasidagi aniq burchak?", ["7.5°","0°","15°","22.5°"], "7.5°"),
        ("Soat 6:30 da strelkalar orasidagi aniq burchak?", ["15°","0°","30°","45°"], "15°"),
        ("Soat 12:20 da strelkalar orasidagi aniq burchak?", ["110°","120°","100°","90°"], "110°"),
        ("log₂(256)=?", ["8","4","16","32"], "8"),
        ("log₃(81)=?", ["4","3","9","27"], "4"),
        ("Uchta ketma-ket tub sonning yig'indisi 23. Kichigi?", ["5","3","7","2"], "5"),
        ("Barcha Blobblar Glarb, hech bir Glarb Snorple emas. Blobblar?", ["Hech bir Blobb Snorple emas","Barcha Blobblar Snorple","Ba'zi Blobblar Snorple","Hech narsa"], "Hech bir Blobb Snorple emas"),
        ("p tub son (p>3). p²-1 ni 24 ga bo'linishi?", ["Har doim bo'linadi","Ba'zan bo'linadi","Hech qachon bo'linmaydi","Faqat p=5 da"], "Har doim bo'linadi"),
    ]
    for _ in range(60):
        for q, o, a in vhard:
            oc = o[:]; random.shuffle(oc)
            qs.append({"question": q, "options": oc, "answer": a, "daraja": "juda_qiyin"})
    # Soat burchaklari
    for h in range(1, 13):
        for m in [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]:
            angle = abs(30*h - 5.5*m)
            if angle > 180: angle = 360 - angle
            ans = f"{angle:.1f}°"
            w1 = f"{abs(angle+15):.1f}°"
            w2 = f"{abs(angle-7.5):.1f}°"
            w3 = f"{abs(angle+30):.1f}°"
            opts = [ans, w1, w2, w3]; random.shuffle(opts)
            qs.append({"question": f"Soat {h}:{m:02d} da strelkalar orasidagi aniq burchak?", "options": opts, "answer": ans, "daraja": "juda_qiyin"})
    return dedup(qs, 1000)

# ═══════════════════════════════════════════════════════
#   TOPISHMOQLAR — kamida 60 ta, to'liq savol
# ═══════════════════════════════════════════════════════
def gen_topishmoq():
    topishmoqlar = [
        # ─ JUDA OSON TOPISHMOQLAR ─
        ("Qanday narsa bor: ko'zi bor, ammo ko'rmaydi?", ["Igna","Ko'zgu","Ko'r odam","Devor"], "Igna"),
        ("Erta keladi, kech ketadi, qish kelib yo'qoladi — bu nima?", ["Quyosh","Qor","Kun","Tun"], "Quyosh"),
        ("Qulog'i bor, eshitmaydi — bu nima?", ["Igna","Ko'za","Kashtalar","Stakan"], "Ko'za"),
        ("Tishi bor, tishlamas — bu nima?", ["Taroq","Ko'ra","Arra","Bolg'a"], "Taroq"),
        ("Oqadi, lekin suv emas; yonadi, lekin olov emas — bu nima?", ["Vaqt","Shamol","Qon","Elektr"], "Vaqt"),
        ("Yuradi, lekin oyog'i yo'q — bu nima?", ["Soat","Mashina","Tog'","Daryo"], "Soat"),
        ("Hamma kiradi, hech kim chiqmaydi — bu nima?", ["Qabr","Uy","Hammom","Non"], "Qabr"),
        ("Qancha ko'p olsang, shuncha ko'p qoladi — bu nima?", ["Bilim","Pul","Non","Suv"], "Bilim"),
        ("Kecha keldi, bugun bor, ertaga yo'q — bu nima?", ["Bugun","Tush","Tun","Oy"], "Bugun"),
        ("Ko'tariladi, lekin tushmasdan oldin o'ladi — bu nima?", ["Quyosh","Qor","Tutun","Shamol"], "Tutun"),
        # ─ OSON TOPISHMOQLAR ─
        ("Yuk ko'taradi, lekin qo'li yo'q — bu nima?", ["Ko'prik","Mashina","Ot","Temir"], "Ko'prik"),
        ("Har doim oldinga yuradi, orqaga qaytmas — bu nima?", ["Vaqt","Daryo","Shamol","Quyosh"], "Vaqt"),
        ("Chaqirmasang kelmaydi, chaqirsang keladi — bu nima?", ["Aks-sado","Ko'lak","Shamol","Tosh"], "Aks-sado"),
        ("Oq kiyingan, qo'li uzun — bu nima?", ["Qayin daraxti","Limon","Qor","Bulut"], "Qayin daraxti"),
        ("Suyagi bor, ammo go'shti yo'q — bu nima?", ["Baliq","Skelet","Daryo","Daraxt"], "Skelet"),
        ("Qanchalik yuvsan, shuncha ko'payadigan narsa nima?", ["Ko'piklar","Bulut","Loyqa suv","Ко'l"], "Ko'piklar"),
        ("Qanotli, ammo uchmas — bu nima?", ["Samolyot","Kapalak","Parvoz","Ventilyator"], "Ventilyator"),
        ("Dunyo bo'ylab sayohat qiladi, bir joyda qoladi — bu nima?", ["Pochta markasi","Pasport","Pul","Kitob"], "Pochta markasi"),
        ("Suv ichida yashaydi, lekin ho'l emas — bu nima?", ["Baliqning qorni","Kemaning ichki qismi","Pufakcha","Qayiq"], "Kemaning ichki qismi"),
        ("Ko'z bilan ko'rmaysan, lekin u bilan o'lchayman — bu nima?", ["Vaqt","Havo","Sevgi","Baxt"], "Vaqt"),
        # ─ O'RTA TOPISHMOQLAR ─
        ("Men gapirganda hamma jim bo'ladi, jim bo'lganda hamma gapiradi — bu nima?", ["O'qituvchi","Muazzin","Ovoz","Radio"], "O'qituvchi"),
        ("Katta ko'ra kichik, kichik ko'ra katta bo'ladigan narsa nima?", ["Ko'zgu","Oyna","Ko'z qaroqchisi","Rasm"], "Ko'zgu"),
        ("Uning boshi bor, lekin miyasi yo'q; oyog'i bor, lekin yurmaydi — bu nima?", ["Zardobl","Ko'rpа","Mixcha","Qoziq"], "Mixcha"),
        ("Qanchalik tortib tursa, shuncha yuqori ko'tariladi — bu nima?", ["Uçurtma","Havo shari","Bulut","Tutun"], "Uçurtma"),
        ("Ikki uchi bor: biri tikadi, biri o'chiradi — bu nima?", ["Qalam","Ruchka","Qaychi","Igna"], "Qalam"),
        ("Toqqa chiqasan — kichrayasan, pastga tushasan — kattalasasan — bu nima?", ["Yo'l","Ko'l","Daryo","Temir yo'l"], "Yo'l"),
        ("Kundi keladi, lekin sanasini bilmayman — bu nima?", ["Tug'ilgan kun","Bayram","Oy","Fasl"], "Tug'ilgan kun"),
        ("Suv ichiga tushsa ham ho'l bo'lmaydi — bu nima?", ["Soya","Ko'lanka","Nur","Havo"], "Soya"),
        ("Har kuni o'ladi, har kuni tug'iladi — bu nima?", ["Kun","Oy","Quyosh","Tun"], "Kun"),
        ("Uzun bo'lsa ham, qisqa ham — lekin doira emas — bu nima?", ["Oy","Yil","Kun","Soat"], "Oy"),
        # ─ QIYIN TOPISHMOQLAR ─
        ("Men qanchalik ko'p bo'lsam, shuncha oz ko'rinaman — bu nima?", ["Teshik","Qorongʻilik","Shovqin","Havo"], "Teshik"),
        ("Hech kim sotib ololmaydi, hech kim berib yubormaydi — bu nima?", ["Vaqt","Baxt","Sevgi","Sog'liq"], "Vaqt"),
        ("Boshi bor, ammo miyasi yo'q; orqasi bor, ammo oyog'i yo'q — bu nima?", ["Kitob","Stul","Karavot","Kamon"], "Kitob"),
        ("Katta qopga sig'adi, ammo igna uchiga sig'magan narsa nima?", ["Shovqin","Havo","Yorug'lik","Shamol"], "Shovqin"),
        ("Inson uchun eng qimmat, ammo pulga sotilmaydi — bu nima?", ["Sog'liq","Do'stlik","Umr","Sevgi"], "Umr"),
        ("Qanchalik ishlatilsa, shuncha o'tkir bo'ladi — bu nima?", ["Aql","Qilich","Ko'z","Quloq"], "Aql"),
        ("Har bir odamda bor, ammo hech kim boshqaga bera olmaydi — bu nima?", ["Ism","Soya","Ovoz","Nafas"], "Soya"),
        ("Men bo'lmasam, hech narsa ko'rinmaydi; men bo'lsam, hech narsa yo'qoladi — bu nima?", ["Zulmat","Yorug'lik","Ko'z","Ko'zoynak"], "Yorug'lik"),
        ("O'n barmoq bilan ushlasa bo'lmaydi — bu nima?", ["Suv","Shamol","Havo","Vaqt"], "Shamol"),
        ("Hamma narsani yutadi, lekin och qoladi — bu nima?", ["Dengiz","O'ch","Ko'l","Botqoq"], "Dengiz"),
        # ─ JUDA QIYIN TOPISHMOQLAR ─
        ("O't emas, ammo ko'k; tosh emas, ammo qattiq; suv emas, ammo to'lqinlanadi — bu nima?", ["Osmon","Ko'l","Ko'z","Shisha"], "Osmon"),
        ("Katta-yu kichik barchada bor, ammo hech kim ko'rmaydi, hech kim bermas — bu nima?", ["Nafas","Aql","Kelajak","Soya"], "Nafas"),
        ("Ko'z ko'radi, quloq eshitadi, ammo til aye olmaydi — bu nima?", ["Sir","Hid","Og'riq","Tush"], "Sir"),
        ("Yerga tushsa sinadi, suvga tushsa yo'qoladi — bu nima?", ["Muz","Shisha","Tuxum","Qog'oz"], "Muz"),
        ("Har bir narsani bosib o'tadi, lekin o'zi izlar qoldirmaydi — bu nima?", ["Vaqt","Shamol","Yorug'lik","Nur"], "Vaqt"),
        ("Bir necha bor ishlatsang, har safar yangi bo'ladi — bu nima?", ["Hafiza","Fikr","So'z","Ko'z"], "So'z"),
        ("Uning ichida ko'p narsalar bor, lekin og'irligi yo'q — bu nima?", ["Fikr","Kitob","Xotira","Tush"], "Fikr"),
        ("Ikki inson bir-birini bir vaqtda ushlab tura olmaydi — bu nima?", ["Bir joy","Bir lahza","Bir narsa","Bir nom"], "Bir lahza"),
        ("Hamma narsaga sig'adi, lekin hech narsa unga sig'maydi — bu nima?", ["Fazoviy boʻshliq","Vaqt","Nur","Havo"], "Fazoviy boʻshliq"),
        ("Dunyoda eng yengilroq va eng og'irroq — bu nima?", ["Vijdon","Baxt","Fikr","Orzу"], "Vijdon"),
    ]
    result = []
    for q, opts, ans in topishmoqlar:
        o = opts[:]; random.shuffle(o)
        result.append({"question": q, "options": o, "answer": ans, "daraja": "topishmoq"})
    return result

# ═══════════════════════════════════════════════════════
#  SAQLASH
# ═══════════════════════════════════════════════════════
if __name__ == "__main__":
    print("⚙️  IQ savollar generatsiya qilinmoqda...")
    iq = []
    for fn, lv in [
        (iq_juda_oson, "juda_oson"),
        (iq_oson,      "oson"),
        (iq_orta,      "orta"),
        (iq_qiyin,     "qiyin"),
        (iq_juda_qiyin,"juda_qiyin"),
    ]:
        batch = fn()
        print(f"   {lv}: {len(batch)} ta")
        iq.extend(batch)
    random.shuffle(iq)
    with open("questions/iq.json", "w", encoding="utf-8") as f:
        json.dump(iq, f, ensure_ascii=False, indent=2)
    print(f"✅ iq.json — {len(iq)} ta savol\n")

    print("⚙️  Mantiq savollar generatsiya qilinmoqda...")
    logic = []
    for fn, lv in [
        (logic_juda_oson, "juda_oson"),
        (logic_oson,      "oson"),
        (logic_orta,      "orta"),
        (logic_qiyin,     "qiyin"),
        (logic_juda_qiyin,"juda_qiyin"),
    ]:
        batch = fn()
        print(f"   {lv}: {len(batch)} ta")
        logic.extend(batch)
    random.shuffle(logic)
    with open("questions/logic.json", "w", encoding="utf-8") as f:
        json.dump(logic, f, ensure_ascii=False, indent=2)
    print(f"✅ logic.json — {len(logic)} ta savol\n")

    print("⚙️  Topishmoqlar generatsiya qilinmoqda...")
    top = gen_topishmoq()
    print(f"   topishmoq: {len(top)} ta")
    with open("questions/topishmoq.json", "w", encoding="utf-8") as f:
        json.dump(top, f, ensure_ascii=False, indent=2)
    print(f"✅ topishmoq.json — {len(top)} ta\n")

    print("🎉 Tayyor! Endi: py bot.py")