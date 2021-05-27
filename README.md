# OpenCV Kişi Sayma
Opencv ile hareket algılayarak sayma ve flask ile tarayıcıda görüntüleme

**Kurulum**
- Gereksinimler: opencv, matplotlib, flask, sqlite3, datetime

1. Python 3.9 veya daha yeni bir sürümünü kurun.
2. Gereksinimlerde belirtilen kütüphaneleri yükleyin.
3. Veri tabanını oluşturmak için db-create.py çalıştırın.
4. Kurulum tamamlandıktan sonra app.py çalıştırın.
5. Tarayıcınızdan http://localhost:5000/ adresine girin. Bu ekranı açılış ekranı olarak tabir edeceğiz.

**Kullanım**
1. Kurulum tamamlandıktan sonra projeyi çalıştırın.
2. Kamera butonu ile kamerayı görüntüleyebilirsiniz. Kamera çalıştığında veri toplamaya başlayacaktır.
3. Toplanan veriyi kaydetmek için kapat butonuna basılmalıdır. Kapat butonuna basıldığında veri tabanında
   o güne ait kayıt varsa güncelleme yapılacaktır. Eğer o güne ait kayıt yoksa yeni kayır eklenecektir.
4. Kamera açık durumdayken gün değiştiğinde güncelleme ve yeni kayıt ekleme işlemlerini kendiliğinden yapacaktır.
5. Analiz butonuna basıldığında tarih - kişi sayısını gösteren grafik oluşturulacak ve bu grafikle hangi günlerin yoğun olduğu görülebilecektir.
