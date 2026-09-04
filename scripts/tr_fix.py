"""ASCII Turkce -> dogru Turkce.

Yontem: en uzun kok eslesmesi + Turkce unlu uyumuyla ek duzeltmesi.
Sadece AST ile Turkce oldugu bilinen string'lerde calisir.
"""
import re

# ---- ASCII kok -> dogru kok (en uzun eslesme onceligiyle uygulanir)
ROOTS = {
# a
"henuz":"henüz","uste":"üste","ustu":"üstü","yontem":"yöntem","aktor":"aktör","gomul":"gömül","govde":"gövde","uyus":"uyuş","gezin":"gezin","dokunul":"dokunul","tanimli":"tanımlı","yonlu":"yönlü","haric":"hariç","kapsa":"kapsa","kapsi":"kapsı","uzanti":"uzantı","barindir":"barındır","cubuk":"çubuk","cubug":"çubuğ","ugra":"uğra","segment":"segment","iletim":"iletim","toparlan":"toparlan","reddet":"reddet","redded":"redded","odak":"odak","klavye":"klavye","okuyucu":"okuyucu","limit":"limit","iler":"iler","damga":"damga","nihai":"nihai","sade":"sade","bekleme":"bekleme","mektup":"mektup","parti":"parti","rakam":"rakam","tetikleyici":"tetikleyici","idempotent":"idempotent","referans":"referans","kurtarma":"kurtarma","yol":"yol",
"abone":"abone","acik":"açık","ac":"aç","ad":"ad","adet":"adet","adim":"adım",
"adres":"adres","agirlik":"ağırlık","ag":"ağ","aile":"aile","ait":"ait","akis":"akış",
"aksam":"akşam","aksan":"aksan","aksesuar":"aksesuar","aksiyon":"aksiyon","aktar":"aktar",
"aktif":"aktif","aktivasyon":"aktivasyon","aktivite":"aktivite","alan":"alan","alarm":"alarm",
"alici":"alıcı","alim":"alım","alisveris":"alışveriş","al":"al","alt":"alt","altyazi":"altyazı",
"ama":"ama","ana":"ana","anahtar":"anahtar","analist":"analist","analitik":"analitik","analiz":"analiz",
"analizor":"analizör","anket":"anket","anla":"anla","anlasma":"anlaşma","aninda":"anında",
"animasyon":"animasyon","ara":"ara","aralik":"aralık","arac":"araç","arayuz":"arayüz",
"ard":"ard","arka":"arka","arkadas":"arkadaş","art":"art","asagi":"aşağı","asama":"aşama",
"asim":"aşım","as":"aş","ata":"ata","at":"at","ay":"ay","ayar":"ayar","ayik":"ayık",
"ayir":"ayır","ayni":"aynı","ayril":"ayrıl","ayristir":"ayrıştır","az":"az",
# b
"backend":"backend","bagimli":"bağımlı","bagimsiz":"bağımsız","bagla":"bağla","baglanti":"bağlantı",
"bagli":"bağlı","bak":"bak","bakiye":"bakiye","banka":"banka","bankacilik":"bankacılık",
"barkod":"barkod","bas":"baş","basari":"başarı","basarisiz":"başarısız","basi":"başı",
"baska":"başka","basla":"başla","baslangic":"başlangıç","baslat":"başlat","baslik":"başlık",
"basil":"basıl","basim":"basım","bastan":"baştan","basvuru":"başvuru","bazi":"bazı","bazli":"bazlı",
"beceri":"beceri","bekle":"bekle","belge":"belge","belirle":"belirle","belirli":"belirli",
"bellek":"bellek","benzer":"benzer","bes":"beş","bicim":"biçim","bildirim":"bildirim","bil":"bil",
"bile":"bile","bilet":"bilet","bilgi":"bilgi","bin":"bin","bir":"bir","birak":"bırak",
"birebir":"birebir","bireysel":"bireysel","birik":"birik","birim":"birim","birkac":"birkaç",
"birlestir":"birleştir","birlikte":"birlikte","bit":"bit","bitir":"bitir","biyometrik":"biyometrik",
"bloke":"bloke","bodrum":"bodrum","bol":"böl","bolge":"bölge","bolum":"bölüm","bos":"boş",
"bosal":"boşal","bosalt":"boşalt","boyunca":"boyunca","bozuk":"bozuk","boz":"boz","bu":"bu",
"bul":"bul","bulut":"bulut","butce":"bütçe","butun":"bütün","buyuk":"büyük",
# c
"cagri":"çağrı","cagir":"çağır","calis":"çalış","calistir":"çalıştır","canli":"canlı",
"canlilik":"canlılık","cek":"çek","cevrimdisi":"çevrimdışı","cevrimici":"çevrimiçi",
"ceyrek":"çeyrek","cihaz":"cihaz","cikar":"çıkar","cikis":"çıkış","cik":"çık","cinsi":"cinsi",
"cip":"çip","cizelge":"çizelge","cocuk":"çocuk","cocug":"çocuğ","cogu":"çoğu","cok":"çok","coz":"çöz",
# d
"da":"da","dagitim":"dağıtım","daha":"daha","dahil":"dahil","dakika":"dakika","dal":"dal",
"davet":"davet","defter":"defter","de":"de","deger":"değer","degerlendirme":"değerlendirme",
"degil":"değil","degisiklik":"değişiklik","degis":"değiş","degistir":"değiştir","demek":"demek",
"deneme":"deneme","dene":"dene","denetci":"denetçi","denetim":"denetim","departman":"departman",
"depo":"depo","dereceli":"dereceli","derleme":"derleme","ders":"ders","destek":"destek",
"detay":"detay","devam":"devam","devre":"devre","dijital":"dijital","dil":"dil","dilim":"dilim",
"disari":"dışarı","disi":"dışı","disinda":"dışında","dis":"dış","dizi":"dizi","dizustu":"dizüstü",
"dogru":"doğru","dogrula":"doğrula","dogrulama":"doğrulama","dogrulanabilir":"doğrulanabilir",
"dogruluk":"doğruluk","dogum":"doğum","doktor":"doktor","dokum":"döküm","dokumante":"dokümante",
"dokunus":"dokunuş","dolandiricilik":"dolandırıcılık","dol":"dol","doldur":"doldur","dolu":"dolu",
"dondur":"dondur","don":"dön","donem":"dönem","dongu":"döngü","donustur":"dönüştür",
"donusum":"dönüşüm","dordunc":"dördünc","dort":"dört","dosya":"dosya","doviz":"döviz","doz":"doz",
"dozla":"dozla","dugme":"düğme","durak":"durak","duraklat":"duraklat","durdur":"durdur",
"dur":"dur","durt":"dürt","durum":"durum","dus":"düş","dusuk":"düşük","dusur":"düşür",
"duz":"düz","duzelt":"düzelt","duzenle":"düzenle","duzenli":"düzenli",
# e
"ebeveyn":"ebeveyn","eczane":"eczane","ed":"ed","egitim":"eğitim","egitmen":"eğitmen",
"ekibim":"ekibim","ekip":"ekip","ekle":"ekle","ekran":"ekran","eksik":"eksik","ekstre":"ekstre",
"elle":"elle","en":"en","engel":"engel","engelle":"engelle","entegrasyon":"entegrasyon",
"erisim":"erişim","eris":"eriş","erken":"erken","ertele":"ertele","es":"eş","esit":"eşit",
"eski":"eski","esleme":"eşleme","esles":"eşleş","eslestir":"eşleştir","et":"et","etiket":"etiket",
"etkilen":"etkilen","evde":"evde","evrak":"evrak",
# f
"fark":"fark","farkli":"farklı","fatura":"fatura","faturalandir":"faturalandır","fazla":"fazla",
"filo":"filo","filtre":"filtre","filtrele":"filtrele","finans":"finans","firlat":"fırlat",
"fiyat":"fiyat","form":"form","format":"format","fotograf":"fotoğraf","fragman":"fragman",
# g
"gec":"geç","gecikme":"gecikme","gecerli":"geçerli","gecerlilik":"geçerlilik","gece":"gece",
"gecelik":"gecelik","gecis":"geçiş","gecmis":"geçmiş","gel":"gel","gelir":"gelir",
"gelistirici":"geliştirici","genel":"genel","genisle":"genişle","gercek":"gerçek",
"gerceklesme":"gerçekleşme","gerceklestir":"gerçekleştir","geri":"geri","gerilimsiz":"gerilimsiz",
"getir":"getir","gibi":"gibi","gir":"gir","giris":"giriş","git":"git","gizli":"gizli",
"gonder":"gönder","gore":"göre","gorev":"görev","gorme":"görme","gor":"gör","gorun":"görün",
"gorunt":"görünt","goruntu":"görüntü","goruntule":"görüntüle","gorunum":"görünüm",
"goster":"göster","gosterge":"gösterge","govdeleme":"gövdeleme",
"gozlemlenebilirlik":"gözlemlenebilirlik","grup":"grup","grupla":"grupla","gucl":"güçl",
"gun":"gün","gunluk":"günlük","guncelle":"güncelle","guvenilirlik":"güvenilirlik","guvenilirlig":"güvenilirliğ",
"guvenli":"güvenli","guvenlik":"güvenlik",
# h
"hafta":"hafta","haftalik":"haftalık","hakedis":"hakediş","hakki":"hakkı","hale":"hale",
"halinde":"halinde","hangi":"hangi","harcama":"harcama","hareket":"hareket","hareketsiz":"hareketsiz",
"harita":"harita","hasta":"hasta","hata":"hata","hatali":"hatalı","hatirlat":"hatırlat",
"havale":"havale","hazir":"hazır","hazirla":"hazırla","hedef":"hedef","hediye":"hediye",
"hekim":"hekim","hemen":"hemen","hep":"hep","her":"her","herhangi":"herhangi","herkes":"herkes",
"hesap":"hesap","hesab":"hesab","hesapla":"hesapla","hic":"hiç","hicbir":"hiçbir","hisset":"hisset",
"hizali":"hizalı","hiz":"hız","hizlica":"hızlıca",
# i
"iade":"iade","icer":"içer","icerik":"içerik","ici":"içi","icin":"için","icinde":"içinde",
"ihlal":"ihlal","ihtiyac":"ihtiyaç","iki":"iki","ikinci":"ikinci","ilac":"ilaç","ile":"ile",
"ilerleme":"ilerleme","ilet":"ilet","iletisim":"iletişim","ilgili":"ilgili","ilk":"ilk",
"imzala":"imzala","imza":"imza","inceleme":"inceleme","incele":"incele","indir":"indir",
"indirim":"indirim","indirimli":"indirimli","indirme":"indirme","internet":"internet",
"iptal":"iptal","isaret":"işaret","isaretle":"işaretle","ise":"ise","isi":"işi",
"iskelet":"iskelet","isle":"işle","islem":"işlem","isley":"işley","istanbul":"İstanbul",
"iste":"iste","isti":"isti","istek":"istek","isveren":"işveren","isyeri":"işyeri",
"itiraf":"itiraf","itiraz":"itiraz","iyi":"iyi","iz":"iz","izle":"izle","izleme":"izleme",
"izleyici":"izleyici","izole":"izole","is":"iş",
# k
"kabul":"kabul","android":"Android","bogaz":"Boğaz","kac":"kaç","kacir":"kaçır","kadar":"kadar","kademeli":"kademeli","kalan":"kalan",
"kal":"kal","kaldig":"kaldığ","kalici":"kalıcı","kalicilik":"kalıcılık","kalmak":"kalmak",
"kamera":"kamera","kampanya":"kampanya","kanal":"kanal","kanit":"kanıt","kapasite":"kapasite",
"kapat":"kapat","kapsam":"kapsam","kapsamli":"kapsamlı","kapi":"kapı","karakter":"karakter",
"karar":"karar","kare":"kare","kargo":"kargo","karsilastir":"karşılaştır","kart":"kart",
"kartlarim":"Kartlarım","kasa":"kasa","kaseli":"kaşeli","katalog":"katalog","katil":"katıl",
"kat":"kat","katman":"katman","katmanli":"katmanlı","kaybet":"kaybet","kaybed":"kaybed",
"kayb":"kayb","kaybol":"kaybol","kayip":"kayıp","kayit":"kayıt","kayitli":"kayıtlı",
"kayd":"kayd","kaydet":"kaydet","kaydir":"kaydır","kay":"kay","kayg":"kayğ","kaynak":"kaynak","kazanilabilir":"kazanılabilir",
"kazanim":"kazanım","kazan":"kazan","kdv":"KDV","kelime":"kelime","kendi":"kendi","kes":"kes",
"kez":"kez","kilif":"kılıf","kil":"kıl","kilometre":"kilometre","kimlik":"kimlik","kimlig":"kimliğ","jenerig":"jeneriğ","jenerik":"jenerik","kimse":"kimse",
"kira":"kira","kisa":"kısa","kisalt":"kısalt","kisi":"kişi","kisit":"kısıt","kisitli":"kısıtlı",
"klinik":"klinik","klinig":"kliniğ","kod":"kod","koltuk":"koltuk","komisyon":"komisyon",
"komsu":"komşu","konsol":"konsol","kontrol":"kontrol","konum":"konum","kop":"kop","kopya":"kopya",
"kopyala":"kopyala","korlemesine":"körlemesine","koru":"koru","koruma":"koruma","korumali":"korumalı",
"kota":"kota","kritik":"kritik","kullanici":"kullanıcı","kullan":"kullan","kullanim":"kullanım",
"kupon":"kupon","kucuk":"küçük","kural":"kural","kurma":"kurma","kur":"kur","kurulum":"kurulum","kurum":"kurum",
"kurumsal":"kurumsal","kurus":"kuruş","kurye":"kurye","kutucuk":"kutucuk","kuyruk":"kuyruk",
"kuyrug":"kuyruğ","kuyruga":"kuyruğa","kvkk":"KVKK",
# l
"lider":"lider","link":"link","lisans":"lisans","liste":"liste","log":"log",
"logla":"logla","loglan":"loglan",
# m
"maas":"maaş","maasli":"maaşlı","mac":"maç","makbuz":"makbuz","maliyet":"maliyet",
"manifest":"manifest","marka":"marka","mart":"Mart","maskele":"maskele","medyan":"medyan",
"merkez":"merkez","mesafe":"mesafe","mesaj":"mesaj","metin":"metin","metre":"metre",
"metrik":"metrik","metro":"metro","mevcut":"mevcut","mezun":"mezun","misafir":"misafir",
"mobil":"mobil","model":"model","mod":"mod","motor":"motor","muayene":"muayene",
"muhasebe":"muhasebe","muhendis":"mühendis","muhendislik":"mühendislik","mukerrer":"mükerrer",
"musait":"müsait","musteri":"müşteri","mutlak":"mutlak",
# n
"ne":"ne","neden":"neden","negatif":"negatif","net":"net","nobetci":"nöbetçi","numara":"numara",
# o
"odasi":"odası","oda":"oda","odeme":"ödeme","ode":"öde","odul":"ödül","ogrenci":"öğrenci",
"okut":"okut","okuyup":"okuyup","oku":"oku","olan":"olan","olarak":"olarak","olay":"olay",
"oldug":"olduğ","ol":"ol","olma":"olma","olustur":"oluştur","olus":"oluş","onam":"onam",
"onay":"onay","onayla":"onayla","onbellek":"önbellek","onbelleg":"önbelleğ","once":"önce",
"onceden":"önceden","onceki":"önceki","oncesi":"öncesi","one":"öne","oneri":"öneri",
"oner":"öner","onizleme":"önizleme","operasyon":"operasyon","operator":"operatör",
"optimize":"optimize","oran":"oran","oranli":"oranlı","orijinal":"orijinal","ortak":"ortak",
"ortalama":"ortalama","ortam":"ortam","ortasinda":"ortasında","otomasyon":"otomasyon",
"otomatik":"otomatik","oturum":"oturum","oynat":"oynat","oyna":"oyna","oyun":"oyun",
"oyuncu":"oyuncu","ozel":"özel","ozellik":"özellik","ozet":"özet",
# p
"paylas":"paylaş","paket":"paket","palet":"palet","panel":"panel","pano":"pano","para":"para","paralel":"paralel",
"parca":"parça","pasiflestir":"pasifleştir","pazarlik":"pazarlık","pazarlig":"pazarlığ","pazaryeri":"pazaryeri",
"plan":"plan","planla":"planla","platform":"platform","politika":"politika","portal":"portal",
"posta":"posta","profil":"profil","program":"program","proje":"proje","puan":"puan",
# r
"randevu":"randevu","rapor":"rapor","raporla":"raporla","recete":"reçete","reddedil":"reddedil",
"rehberli":"rehberli","rekabetci":"rekabetçi","renk":"renk","replika":"replika",
"resepsiyon":"resepsiyon","resmi":"resmi","rezervasyon":"rezervasyon","risk":"risk",
"rol":"rol","rota":"rota","rotasyon":"rotasyon","rozet":"rozet","rutin":"rutin",
# s
"saat":"saat","sabah":"sabah","sabit":"sabit","sablon":"şablon","sag":"sağ","sagla":"sağla",
"sahibi":"sahibi","sahip":"sahip","sahte":"sahte","sakla":"sakla","sanal":"sanal",
"saniye":"saniye","satici":"satıcı","satil":"satıl","satin":"satın","satir":"satır",
"savas":"savaş","sayfa":"sayfa","sayil":"sayıl","sayi":"sayı","sebep":"sebep","secenek":"seçenek",
"sec":"seç","secim":"seçim","secici":"seçici","sefer":"sefer",
"sekilde":"şekilde","sekme":"sekme","selfie":"selfie","senkron":"senkron","senkronize":"senkronize",
"sepet":"sepet","serbest":"serbest","seri":"seri","sertifika":"sertifika","servis":"servis",
"ses":"ses","sessizce":"sessizce","sevkiyat":"sevkiyat","sey":"şey","seyahat":"seyahat",
"seyrel":"seyrel","sezon":"sezon","sicra":"sıçra","sicri":"sıçrı","sifir":"sıfır","sifirla":"sıfırla",
"sifre":"şifre","sik":"sık","siki":"sıkı","silin":"silin","siler":"siler","sil":"sil",
"sinav":"sınav","sinir":"sınır","sinirsiz":"sınırsız","sinyal":"sinyal","siparis":"sipariş",
"sira":"sıra","siradaki":"sıradaki","sirala":"sırala","sirasinda":"sırasında","sirket":"şirket",
"sistem":"sistem","siyah":"siyah","siz":"sız","skor":"skor","skorla":"skorla","sokak":"sokak",
"sok":"sok","soluk":"soluk","son":"son","sonlandir":"sonlandır","sonra":"sonra",
"sonraki":"sonraki","sonrasi":"sonrası","sonsuz":"sonsuz","sonuc":"sonuç","sorgu":"sorgu",
"soru":"soru","sorumlu":"sorumlu","spamla":"spamla","sprint":"sprint","stok":"stok",
"stog":"stoğ","su":"şu","sube":"şube","sun":"sun","sunucu":"sunucu","supheli":"şüpheli",
"sure":"süre","sureli":"süreli","surpriz":"sürpriz","surum":"sürüm","surume":"sürüme",
"sutun":"sütun","sutyen":"sutyen",
# t
"tabanli":"tabanlı","tahlil":"tahlil","tahmin":"tahmin","tahsil":"tahsil","tahsilat":"tahsilat",
"takibi":"takibi","takim":"takım","takip":"takip","talep":"talep","talimat":"talimat",
"tam":"tam","tamam":"tamam","tamamla":"tamamla","tane":"tane","taraf":"taraf","tarayici":"tarayıcı",
"tarih":"tarih","tasarla":"tasarla","tasi":"taşı","tasima":"taşıma","tedavi":"tedavi",
"tek":"tek","teklif":"teklif","tekrar":"tekrar","tekrarlan":"tekrarlan","tele":"tele",
"telefon":"telefon","televizyon":"televizyon","temas":"temas","temassiz":"temassız","tepki":"tepki",
"terk":"terk","termin":"termin","teslim":"teslim","teslimat":"teslimat","tespit":"tespit",
"test":"test","tetikle":"tetikle","teyit":"teyit","ticaret":"ticaret","tikla":"tıkla",
"tiklama":"tıklama","tip":"tip","toplam":"toplam","topla":"topla","toplu":"toplu",
"transfer":"transfer","tuken":"tüken","tukenmis":"tükenmiş","tuketim":"tüketim","tum":"tüm",
"tunel":"tünel","tur":"tür","turkce":"Türkçe","tus":"tuş","tut":"tut","tutar":"tutar",
"tutarli":"tutarlı",
# u
"uc":"üç","ucak":"uçak","ucret":"ücret","ucretsiz":"ücretsiz","ucunc":"üçünc","ucus":"uçuş",
"ulas":"ulaş","ulastir":"ulaştır","ulusal":"ulusal","umutsuz":"umutsuz","unut":"unut",
"uretim":"üretim","uret":"üret","urun":"ürün","ustel":"üstel","uyan":"uyan","uyari":"uyarı",
"uye":"üye","uyeliksiz":"üyeliksiz","uygula":"uygula","uygulama":"uygulama","uygulan":"uygulan",
"uyku":"uyku","uy":"uy","uyum":"uyum","uyumlu":"uyumlu","uzere":"üzere","uzerinde":"üzerinde",
"uzerinden":"üzerinden","uzerine":"üzerine","uzman":"uzman","uzun":"uzun",
# v
"vaat":"vaat","vadesiz":"vadesiz","vaka":"vaka","var":"var","vardiya":"vardiya","varis":"varış",
"varsayilan":"varsayılan","ve":"ve","ver":"ver","veritabani":"veritabanı","veri":"veri",
"veya":"veya","video":"video","vize":"vize",
# y
"ya":"ya","yaklas":"yaklaş","yaklasik":"yaklaşık","yalnizca":"yalnızca","yanit":"yanıt",
"yanlis":"yanlış","yansit":"yansıt","yap":"yap","yapil":"yapıl","yapilandir":"yapılandır",
"yara":"yara","yaram":"yaram","yarim":"yarım","yarisi":"yarısı","yas":"yaş","yasan":"yaşan",
"yayin":"yayın","yayinla":"yayınla","yaz":"yaz","yazdir":"yazdır","yazil":"yazıl","yazim":"yazım",
"yazis":"yazış","yeni":"yeni","yeniden":"yeniden","yenile":"yenile","yer":"yer","yerel":"yerel",
"yerine":"yerine","yetersiz":"yetersiz","yetiskin":"yetişkin","yetki":"yetki",
"yetkilendir":"yetkilendir","yil":"yıl","yitir":"yitir","yok":"yok","yoksa":"yoksa",
"yonelik":"yönelik","yonetici":"yönetici","yonetim":"yönetim","yonlendir":"yönlendir",
"yukle":"yükle","yukleme":"yükleme","yuklen":"yüklen","yuksek":"yüksek","yukselt":"yükselt",
"yurut":"yürüt","yuz":"yüz","yuzde":"yüzde","yuzlerce":"yüzlerce","yuzunden":"yüzünden",
# z
"zaman":"zaman","zamanla":"zamanla","zamanli":"zamanlı","zaten":"zaten","zayif":"zayıf",
"zincir":"zincir","ziyaret":"ziyaret","ziyaretci":"ziyaretçi","zorla":"zorla","zorunda":"zorunda",
"zorunlu":"zorunlu",
}

# ekleri duzeltmeyecegimiz, oldugu gibi birakilacak kelimeler (kisaltma/marka/kod)
KEEP = set(["API", "CSV", "SDK", "URL", "REST", "JSON", "HTTP", "HTTPS", "SSO", "SCIM", "SAML", "SLO", "SMS", "OTP", "PIN", "PDF", "POS", "PAN", "KDV", "TL", "EUR", "USD", "IBAN", "MFA", "PCI", "DSS", "SOC", "WAF", "DRM", "HDR", "SDR", "TV", "CI", "CD", "GB", "MB", "ms", "mg", "ml", "SKU", "ID", "IdP", "OK", "Slack", "Google", "Apple", "Face", "iPhone", "iOS", "Android", "Excel", "Kafka", "Wi", "Fi", "ICE", "ML", "AI", "QA", "UX", "UI", "IoT", "OOMKilled", "PATCH", "POST", "GET", "Type", "Live", "Pull", "SaaS", "B2B", "Q1", "Q2", "Q3", "Q4", "H1", "H2", "KVKK", "GDPR", "asciifolding", "analyzer", "stemming", "tokenizer", "webhook", "endpoint", "payload", "timeout", "rollback", "rollout", "backlog", "sprint", "grooming", "staging"])

# ince ek alan (Arapca/Bati kokenli) istisna kokler: saat -> saatleri, rol -> rolu
FRONT_EXC = {"saat", "rol", "kontrol", "kabul", "kimlig", "jenerig", "ihlal", "iptal", "istikbal", "dikkat", "harf", "kalp", "alkol", "ideal",
             "usul", "hukuk", "petrol", "protokol", "sembol", "sinyal", "mesul",
             "sual", "hal", "gol"}

VOWELS = "aeıioöuüAEIİOÖUÜ"
BACK = "aıouAIOU"          # kalin unluler
ROUND = "oöuüOÖUÜ"         # yuvarlak unluler
HARD = "pçtkfhsşPÇTKFHSŞ"  # sert unsuzler


def last_vowel(s):
    for ch in reversed(s):
        if ch in VOWELS:
            return ch.lower()
    return None


def harmonize(suffix, stem, front=False):
    """Kok'e gore ekteki a/e ve i/i/u/u unlulerini duzeltir."""
    out = []
    ctx = (stem + "e") if front else stem
    for ch in suffix:
        lv = last_vowel(ctx)
        if ch in "ae":
            ch = "a" if (lv in "aıou") else "e"
        elif ch in "iıuü":
            if lv in "aı":
                ch = "ı" if ch in "iı" else "u"
            elif lv in "ei":
                ch = "i" if ch in "iı" else "ü"
            elif lv in "ou":
                ch = "u" if ch in "uü" else ("u" if ch in "iı" else ch)
                if ch in "iı":
                    ch = "u"
            elif lv in "öü":
                ch = "ü"
            # unlu yoksa oldugu gibi birak
        out.append(ch)
        ctx += ch
    sfx = "".join(out)
    # ek icindeki unsuz kurallari: iki unlu arasi g -> g yumusak, unluden sonra
    # ek sonunda/unsuz onunde s -> s sapkali (gorusme, yapilmistir)
    sfx = re.sub(r"(?<=[aeiou\u0131\u00f6\u00fc])g(?=[aeiou\u0131\u00f6\u00fc])", "\u011f", sfx)
    # kok unluyle bitiyorsa ek basindaki g de yumusar: guvenli + gi -> guvenligi
    if sfx[:1] == "g" and ctx[:1] and stem[-1:] in "aeıioöuü" and sfx[1:2] in "aeıioöuü":
        sfx = "\u011f" + sfx[1:]
    sfx = re.sub(r"(?<=[aeiou\u0131\u00f6\u00fc])s(?=$|[bcdfgjklmnprstvyz\u00e7\u011f\u015f])", "\u015f", sfx)
    sfx = re.sub(r"(?<=[kpt\u00e7\u015f])c(?=[a\u0131e i])", "\u00e7", sfx)
    if sfx[:1] == "c" and stem[-1:] in HARD:      # acik + ca -> acikca
        sfx = "\u00e7" + sfx[1:]
    return sfx


# tam kelime onceligi: kok eslesmesinin yanlis calistigi formlar
EXACT = {
 "gecen": "geçen", "gecerken": "geçerken", "gecerek": "geçerek",
 "gecince": "geçince", "gecip": "geçip", "gecerse": "geçerse",
 "uredilir": "üretilir", "uredilen": "üretilen",
 "uretilir": "üretilir", "iletilir": "iletilir", "gecik": "gecik", "gecikti": "gecikti", "ihtiyaci": "ihtiyacı",
 "ihtiyacim": "ihtiyacım", "ihtiyacima": "ihtiyacıma", "ihtiyacini": "ihtiyacını", "ihtiyaca": "ihtiyaca", "analiz": "analiz", "sonucu": "sonucu", "bastiginda": "bastığında", "basildiginda": "basıldığında",
 "basar": "basar", "basma": "basma", "basmak": "basmak", "limidi": "limiti", "limidini": "limitini",
 "limidin": "limitin", "segmendi": "segmenti", "tamaman": "tamamen",
 "iledim": "iletim", "iledimden": "iletimden", "hala": "hâlâ", "gecersiz": "geçersiz", "isten": "işten", "istenir": "istenir",
 "istenen": "istenen", "istendi": "istendi", "gecti": "geçti", "gectikten": "geçtikten", "gece": "gece",
 "ise": "ise", "isin": "işin", "on": "ön", "one": "öne", "sonu": "sonu",
 "sonuc": "sonuç", "kar": "kâr", "yaz": "yaz", "yazi": "yazı", "tur": "tür",
 "tum": "tüm", "olcum": "ölçüm", "olcut": "ölçüt",
}

# ceviri sirasinda unlu uyumunu SIFIRLAYAN sabit ek parcalari
# ornek: yap+abil+ir -> yapabilir (bil koku ince oldugu icin sonrasi ince devam eder)
FIXED_CHUNKS = ("abil", "ebil", "yor", "ken", "imsi")

_roots_sorted = sorted(ROOTS, key=len, reverse=True)


# unluyle baslayan ek alinca yumusayan son unsuzler (ilac -> ilaci)
SOFTEN = {"ç": "c", "p": "b", "t": "d", "k": "ğ"}


def harmonize_suffix(suffix, stem, front=False):
    """Eki uyumlar, ama -abil-/-ebil- gibi sabit parcalarda baglami sifirlar."""
    for chunk in ("abil", "ebil"):
        i = suffix.find(chunk)
        if i != -1:
            head = harmonize(suffix[:i], stem, front=front)
            # a/e secimi koke gore, sonrasi "bil" (ince, duz) baglaminda devam eder
            lv = last_vowel(stem + ("e" if front else "") + head)
            link = ("a" if lv in "aıou" else "e") + "bil"
            tail = harmonize(suffix[i + 4:], "bil")
            return head + link + tail
    # "et-/ed-" yardimci fiili uyuma girmez: kaydedip, teyit edildi
    for chunk in ("edi", "edip", "ede", "eder", "edil", "ett"):
        if suffix.startswith(chunk):
            return chunk + harmonize(suffix[len(chunk):], "edi")
    # "-ken" eki sabittir: yaparken, bakarken (uyuma girmez)
    if suffix.endswith("kan") or suffix.endswith("ken"):
        head = harmonize(suffix[:-3], stem, front=front)
        return head + "ken"
    return harmonize(suffix, stem, front=front)


def fix_word(w):
    if w in KEEP or (w.upper() == w and len(w) > 1):
        return w
    low = w.lower()
    if low in EXACT:
        out = EXACT[low]
        return out[0].upper() + out[1:] if w[0].isupper() else out
    for r in _roots_sorted:
        if low.startswith(r):
            fixed_root = ROOTS[r]
            suffix = low[len(r):]
            if suffix and not all(c.isalpha() or c == "'" for c in suffix):
                # kesme isaretli ek: 'nda gibi -> uyum uygula ama ' korunur
                pass
            sfx = harmonize_suffix(suffix, fixed_root, front=(r in FRONT_EXC))
            fixed = fixed_root + sfx
            # buyuk harf bicimini koru
            if w[0].isupper():
                head = "\u0130" if fixed[0] == "i" else fixed[0].upper()
                fixed = head + fixed[1:]
            return fixed
    return w


TOKEN = re.compile(r"[A-Za-zçğıöşüÇĞİÖŞÜ]+(?:'[A-Za-zçğıöşüÇĞİÖŞÜ]+)?")


PLACEHOLDER = re.compile(r"\{[a-zA-Z_][a-zA-Z0-9_]*\}")


def fix_text(t):
    """Metni duzeltir; {placeholder} ve <etiket> icerigine dokunmaz."""
    holes = []

    def stash(m):
        holes.append(m.group(0))
        return f"\x00{len(holes) - 1}\x00"

    t = PLACEHOLDER.sub(stash, t)
    t = TOKEN.sub(lambda m: fix_word(m.group(0)), t)
    return re.sub(r"\x00(\d+)\x00", lambda m: holes[int(m.group(1))], t)


if __name__ == "__main__":
    tests = [
        "bireysel bankacilik musterisi banka kartimi uygulamadan aninda dondurup acmak",
        "kullanicilarin islemlerini goruntulemesi icin yetkilendirme gerekiyor",
        "musteri sepetindeki urunler kayboluyor ve destek talebi aciliyor",
        "Kartlarim ekraninda harcama limiti belirlemek istiyorum",
        "odeme adiminda dogrulama kodu gonderilmeli",
    ]
    for t in tests:
        print(fix_text(t))
