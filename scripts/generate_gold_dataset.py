"""
Script to generate the standardized 150 gold-annotated benchmark dataset.
Ensures authentic GCC dialects, realistic business distributions, and exact CSV formatting.
"""

import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = BASE_DIR / "data" / "gold_dataset_150.csv"
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

# 150 curated items spanning 5 brands across GCC social media channels
ITEMS = [
    # =========================================================================
    # BRAND 1: Al-Noor Telecom (30 Posts)
    # =========================================================================
    ("alnoor_001", "tiktok", "يا جماعة شبكة النور للاتصالات في حي الياسمين شمال الرياض فاصلة تماماً من الصباح! كل ما نكلم الدعم يقولون تحديث برج. 😡📡", "ar", "Al-Noor Telecom", "negative", "Network & Outage", False, "Saudi", "Outage complaint in Riyadh"),
    ("alnoor_002", "instagram", "تجربة قياس سرعة الفايف جي 5G مع @alnoor_telecom في بوليفارد سيتي وصلت 920 Mbps! صراحة تطور جبار في التغطية مقارنة بالعام الماضي. ⚡🏎️", "ar", "Al-Noor Telecom", "positive", "Network & Outage", False, "Saudi", "Praise for 5G speed in Riyadh"),
    ("alnoor_003", "tiktok", "خدمة عملاء النور سريعة جداً ما شاء الله، رادين علي بعد ٤ أيام ويقولون لي أعد تشغيل المودم! قمة الاحترافية 👏🙃", "ar", "Al-Noor Telecom", "negative", "Customer Support", True, "Saudi", "Sarcastic praise for delayed CS response"),
    ("alnoor_004", "instagram", "Al-Noor Telecom just increased their postpaid fiber subscription fee by 15% without prior notice. Disappointing service! #AlNoor", "en", "Al-Noor Telecom", "negative", "Pricing & Billing", False, "English", "Price increase complaint"),
    ("alnoor_005", "tiktok", "عرض باقة التجوال الدولي الجديدة من Al-Noor Telecom لدول الخليج.. 30GB بـ 150 ريال هل تسوى ولا اشتري eSIM محلي؟", "mixed", "Al-Noor Telecom", "neutral", "Promotions & Offers", False, "Mixed", "Roaming package query"),
    ("alnoor_006", "tiktok", "أفضل شبكة ألياف بصرية في الدمام بلا منازع، سرعة وثبات وما قد فصل معي خلال سنة كاملة. شكراً النور للاتصالات 👍", "ar", "Al-Noor Telecom", "positive", "Network & Outage", False, "Saudi", "Praise for fiber reliability in Dammam"),
    ("alnoor_007", "instagram", "قدمت على نقل خط الفايبر لبيتي الجديد من أسبوعين وكل يوم موعد وهمي والفني ما يجي! شركة النور أسوأ خدمة عملاء", "ar", "Al-Noor Telecom", "negative", "Customer Support", False, "Saudi", "Complaint about delayed fiber technician"),
    ("alnoor_008", "tiktok", "هل باقات 5G المسبقة الدفع من النور تدعم التفعيل الفوري عبر النفاذ الوطني؟", "ar", "Al-Noor Telecom", "neutral", "General", False, "Saudi", "General KYC activation inquiry"),
    ("alnoor_009", "instagram", "شباب الـ 5G حق النور صار so slow اليومين ذي في دبي مارينا.. شالسالفة؟", "mixed", "Al-Noor Telecom", "negative", "Network & Outage", False, "Emirati", "Speed drop complaint in Dubai"),
    ("alnoor_010", "tiktok", "يعطيكم العافية على الباقة الشبابية الجديدة، أسعار ممتازة وبيانات سوشال ميديا مفتوحة بدون تقييد 🥳📱", "ar", "Al-Noor Telecom", "positive", "Promotions & Offers", False, "Gulf", "Praise for youth mobile plan"),
    ("alnoor_011", "instagram", "ما قصرتوا يا النور قطعتوا النت وقت اجتماع زووم مصيري للشركة! فعلاً تثبتون كل يوم أنكم الأفضل 👏", "ar", "Al-Noor Telecom", "negative", "Network & Outage", True, "Saudi", "Sarcastic outrage over business outage"),
    ("alnoor_012", "tiktok", "تطبيق النور للاتصالات معلق بعد التحديث ما يخليني ادفع الفاتورة، كل ما اضغط سداد يخرج من البرنامج!", "ar", "Al-Noor Telecom", "negative", "App & UX Experience", False, "Saudi", "App payment screen bug"),
    ("alnoor_013", "instagram", "Great experience upgrading to Al-Noor fiber today. The technician arrived on time and setup took 20 minutes.", "en", "Al-Noor Telecom", "positive", "Customer Support", False, "English", "Technician punctuality praise"),
    ("alnoor_014", "tiktok", "كم رسوم إلغاء العقد السنوي للإنترنت المنزلي مع شركة النور؟", "ar", "Al-Noor Telecom", "neutral", "Pricing & Billing", False, "MSA", "Contract cancellation fee query"),
    ("alnoor_015", "instagram", "والله عروض النور في اليوم الوطني دائماً تفوز، خصم 50% على اشتراكات الفايبر السنوية 🔥🇸🇦", "ar", "Al-Noor Telecom", "positive", "Promotions & Offers", False, "Saudi", "National Day promotion praise"),
    ("alnoor_016", "tiktok", "الفاتورة الشهرية نازلة بـ 450 ريال والباقة حقتي المفروض 250 ريال فقط! راجعوا حساباتكم يا النور للاتصالات", "ar", "Al-Noor Telecom", "negative", "Pricing & Billing", False, "Saudi", "Overbilling complaint"),
    ("alnoor_017", "instagram", "Al-Noor Telecom customer care representative Sarah was super helpful resolving my roaming issues while abroad.", "en", "Al-Noor Telecom", "positive", "Customer Support", False, "English", "Agent praise"),
    ("alnoor_018", "tiktok", "شريحة النور ما فيها شبكة نهائياً في طريق الرياض - القصيم السريع.. يرجى تقوية الأبراج", "ar", "Al-Noor Telecom", "negative", "Network & Outage", False, "Saudi", "Highway network gap complaint"),
    ("alnoor_019", "instagram", "شركة النور تعلن عن توقيع شراكة لتوسيع تغطية شبكات الجيل الخامس في المدن الصناعية.", "ar", "Al-Noor Telecom", "neutral", "Network & Outage", False, "MSA", "Corporate expansion announcement"),
    ("alnoor_020", "tiktok", "يا زين شبكتكم بس، من أمس ما نزل ولا إيميل.. الله يديم هالسرعة الخارقة 🙃", "ar", "Al-Noor Telecom", "negative", "Network & Outage", True, "Gulf", "Sarcastic complaint about dead speed"),
    ("alnoor_021", "instagram", "eSIM activation with Al-Noor Telecom took less than 2 minutes via QR code. Modern and seamless.", "en", "Al-Noor Telecom", "positive", "App & UX Experience", False, "English", "eSIM digital onboarding praise"),
    ("alnoor_022", "tiktok", "الدعم الفني حقكم في الواتساب روبوت غبي يكرر نفس الإجابات بدون أي فائدة ترجى 🤦‍♂️", "ar", "Al-Noor Telecom", "negative", "Customer Support", False, "Saudi", "Chatbot frustration"),
    ("alnoor_023", "instagram", "هل تغطية ألياف النور البصرية وصلت لحي الملقا مربع ٧؟", "ar", "Al-Noor Telecom", "neutral", "Network & Outage", False, "Saudi", "Coverage district query"),
    ("alnoor_024", "tiktok", "انترنت النور لا يعلى عليه في الألعاب والـ Ping ثابت 12ms في سيرفرات الشرق الأوسط 🎮👌", "ar", "Al-Noor Telecom", "positive", "Network & Outage", False, "Saudi", "Gaming latency praise"),
    ("alnoor_025", "instagram", "Why is Al-Noor charging an international roaming activation fee when the website says it's free?", "en", "Al-Noor Telecom", "negative", "Pricing & Billing", False, "English", "Unexpected fee complaint"),
    ("alnoor_026", "tiktok", "تم تدشين مركز بيانات النور الجديد لدعم حلول إنترنت الأشياء والذكاء الاصطناعي.", "ar", "Al-Noor Telecom", "neutral", "General", False, "MSA", "Corporate press release"),
    ("alnoor_027", "instagram", "شكراً النور على تعويضنا بشهر مجاني بعد العطل الفني الأسبوع الماضي، بادرة طيبة تعكس احترامكم للعملاء.", "ar", "Al-Noor Telecom", "positive", "Customer Support", False, "Saudi", "Compensation appreciation"),
    ("alnoor_028", "tiktok", "كل ما اتصل على 900 ينتظرني على الخط نصف ساعة وبعدها ينقفل الخط بوجهي!", "ar", "Al-Noor Telecom", "negative", "Customer Support", False, "Saudi", "Call center drop off"),
    ("alnoor_029", "instagram", "Al-Noor Telecom 5G router setup was totally plug and play. Great speeds in Sharjah.", "en", "Al-Noor Telecom", "positive", "Network & Outage", False, "English", "5G home router praise"),
    ("alnoor_030", "tiktok", "كيف طريقة تفعيل باقة البيانات المفتوحة في شريحة النور مسبقة الدفع؟", "ar", "Al-Noor Telecom", "neutral", "General", False, "Saudi", "How-to inquiry"),

    # =========================================================================
    # BRAND 2: DesertPay (30 Posts)
    # =========================================================================
    ("desertpay_001", "tiktok", "والله محفظة ديزرت باي @DesertPay فكت أزمة! كاش باك 10% فوري على كل مشتريات السوبرماركت طوال رمضان 🌙💳", "ar", "DesertPay", "positive", "Promotions & Offers", False, "Saudi", "Praise for Ramadan cashback"),
    ("desertpay_002", "instagram", "تطبيق نقد الصحراء (DesertPay) معلق عند صفحة التحقق من الهوية بعد التحديث الأخير v3.2. رصيدي معلق ومحد يرد بتويتر!", "ar", "DesertPay", "negative", "App & UX Experience", False, "Saudi", "KYC bug and frozen funds"),
    ("desertpay_003", "tiktok", "Just tested the international remittance feature on DesertPay. Instant transfer from Riyadh to UAE with zero FX fee! Sleek UI 💸", "en", "DesertPay", "positive", "App & UX Experience", False, "English", "Remittance praise"),
    ("desertpay_004", "instagram", "انتبهوا من رسوم التحويل الخفية في تطبيق ديزرت باي، تم خصم 3.5% رسوم معالجة عملة غير معلنة في الإعلان! 📉", "ar", "DesertPay", "negative", "Pricing & Billing", False, "Gulf", "Hidden conversion fee complaint"),
    ("desertpay_005", "tiktok", "هل بطاقة ديزرت باي الائتمانية مقبولة لدخول صالات المطارات في الخليج بدون رسوم إضافية؟", "ar", "DesertPay", "neutral", "Promotions & Offers", False, "MSA", "Airport lounge query"),
    ("desertpay_006", "instagram", "شكراً ديزرت باي على قمة الأمان، جمدتوا حسابي عشان حولت 500 ريال لأخوي وخدمة العملاء نايمة من 3 أيام 👏🔒", "ar", "DesertPay", "negative", "Customer Support", True, "Saudi", "Sarcastic complaint about false fraud lock"),
    ("desertpay_007", "tiktok", "أفضل تطبيق مدفوعات رقمية بالسعودية، تقسيم الفاتورة بين الأصدقاء بضغطة زر وبدون إحراج 👌", "ar", "DesertPay", "positive", "App & UX Experience", False, "Saudi", "Split bill feature praise"),
    ("desertpay_008", "instagram", "DesertPay customer service team refunded my duplicate charge within 15 minutes over WhatsApp. Top tier support!", "en", "DesertPay", "positive", "Customer Support", False, "English", "Quick refund praise"),
    ("desertpay_009", "tiktok", "يا جماعة بطاقة ديزرت باي البلاستيكية كم يوم تأخذ وتوصل للبيت في جدة؟", "ar", "DesertPay", "neutral", "Delivery & Logistics", False, "Saudi", "Physical card delivery inquiry"),
    ("desertpay_010", "instagram", "حولت مبلغ عبر سداد إلى محفظة ديزرت باي والمبلغ انخصم من البنك وما دخل المحفظة من 24 ساعة!", "ar", "DesertPay", "negative", "App & UX Experience", False, "Saudi", "Lost deposit balance issue"),
    ("desertpay_011", "tiktok", "كود خصم ديزرت باي الجديد DESERT50 يخصم 50 ريال على مشترياتك الأولى جربوه شغال 🔥", "ar", "DesertPay", "positive", "Promotions & Offers", False, "Saudi", "Referral code share"),
    ("desertpay_012", "instagram", "DesertPay app keeps crashing whenever I try to add an Apple Pay virtual card. iPhone 15 Pro iOS 18.", "en", "DesertPay", "negative", "App & UX Experience", False, "English", "Apple Pay crash report"),
    ("desertpay_013", "tiktok", "هل يمكن فتح حساب تجاري في ديزرت باي للمتاجر الإلكترونية الصغيرة المسجلة في معروف؟", "ar", "DesertPay", "neutral", "General", False, "Saudi", "Merchant onboarding query"),
    ("desertpay_014", "instagram", "ميزة الادخار التلقائي بحصالة ديزرت باي خلتني أوفر أكثر من 2000 ريال شهرياً بدون ما أحس! فكرة عبقرية 💰", "ar", "DesertPay", "positive", "App & UX Experience", False, "Saudi", "Micro-savings feature praise"),
    ("desertpay_015", "tiktok", "رفعوا رسوم السحب النقدي من الصرافات إلى 10 ريالات للعملية الواحدة! ليش هالجشع يا ديزرت باي؟", "ar", "DesertPay", "negative", "Pricing & Billing", False, "Saudi", "ATM fee hike complaint"),
    ("desertpay_016", "instagram", "DesertPay partners with Visa to introduce GCC-wide virtual card cashback programs.", "en", "DesertPay", "neutral", "Promotions & Offers", False, "English", "Partnership news"),
    ("desertpay_017", "tiktok", "خدمة عملاء ديزرت باي ما في مثلهم، انسرقت بيانات بطاقتي وعوضوني بالمبلغ فوراً بعد التحقيق شكراً لكم 🙏", "ar", "DesertPay", "positive", "Customer Support", False, "Saudi", "Fraud compensation praise"),
    ("desertpay_018", "instagram", "ما شاء الله على السيرفرات القوية، أول يوم نزول الرواتب التطبيق يوقف وما نقدر نحاسب في البقالة! روعة الصراحة 🙃", "ar", "DesertPay", "negative", "App & UX Experience", True, "Saudi", "Sarcastic complaint about payday downtime"),
    ("desertpay_019", "tiktok", "كيف أحول نقاط مكافآت ديزرت باي إلى أميال فرسان؟", "ar", "DesertPay", "neutral", "Promotions & Offers", False, "Saudi", "Points redemption inquiry"),
    ("desertpay_020", "instagram", "Super fast KYC approval on DesertPay! Took literally 30 seconds with Saudi Nafath.", "en", "DesertPay", "positive", "App & UX Experience", False, "English", "Nafath digital onboarding praise"),
    ("desertpay_021", "tiktok", "صاحب محطة الوقود رفض يقبل بطاقة ديزرت باي بحجة أن أجهزة نقاط البيع ترفضها.. وين المشكلة بالضبط؟", "ar", "DesertPay", "negative", "App & UX Experience", False, "Saudi", "POS rejection issue"),
    ("desertpay_022", "instagram", "تحديث تطبيق ديزرت باي الأخير حسن استهلاك البطارية والواجهة صارت أسرع بكثير 👏", "ar", "DesertPay", "positive", "App & UX Experience", False, "Gulf", "UI optimization praise"),
    ("desertpay_023", "tiktok", "مقارنة رسوم التحويل إلى مصر والفلبين بين ديزرت باي والمنافسين.. تفاصيل كاملة في الفيديو.", "ar", "DesertPay", "neutral", "Pricing & Billing", False, "MSA", "Comparison review"),
    ("desertpay_024", "instagram", "I was charged twice for a single order at Starbucks using DesertPay contactless payment.", "en", "DesertPay", "negative", "Pricing & Billing", False, "English", "Double charge issue"),
    ("desertpay_025", "tiktok", "عروض استرجاع الكاش باك مع نقد الصحراء بمناسبة عيد الفطر المبارك تبدأ غداً.", "ar", "DesertPay", "neutral", "Promotions & Offers", False, "MSA", "Promotional alert"),
    ("desertpay_026", "instagram", "ديزرت باي فازت بجائزة أفضل ابتكار مالي في مؤتمر فنتك الشرق الأوسط 2026 يستاهلون 🏆", "ar", "DesertPay", "positive", "General", False, "Emirati", "Award celebration"),
    ("desertpay_027", "tiktok", "طلبت كشف حساب رسمي مختوم من ديزرت باي لتأشيرة الشنغن ولهم 10 أيام يماطلون!", "ar", "DesertPay", "negative", "Customer Support", False, "Saudi", "Bank statement delay"),
    ("desertpay_028", "instagram", "Love the dark mode UI on DesertPay. Makes tracking daily expenses so clean and easy.", "en", "DesertPay", "positive", "App & UX Experience", False, "English", "Dark mode UI praise"),
    ("desertpay_029", "tiktok", "كم الحد الأعلى للتحويل اليومي بين محافظ ديزرت باي بدون توثيق إضافي؟", "ar", "DesertPay", "neutral", "General", False, "Saudi", "Limit inquiry"),
    ("desertpay_030", "instagram", "فريق الدعم الفني في ديزرت باي ما يردون على الإيميلات نهائياً من أسبوع كامل!", "ar", "DesertPay", "negative", "Customer Support", False, "Saudi", "Email support complaint"),

    # =========================================================================
    # BRAND 3: Oasis Retail (30 Posts)
    # =========================================================================
    ("oasis_001", "instagram", "طلبت مقاضي البيت الأسبوعية من تطبيق واحة التجزئة Oasis Retail، وصل الطلب مغلف ومرتب خلال 40 دقيقة بالضبط والفواكه طازجة جداً! 🍎🛒", "ar", "Oasis Retail", "positive", "Delivery & Logistics", False, "Emirati", "Fast fresh delivery praise"),
    ("oasis_002", "tiktok", "أسواق الواحة @oasis_retail للأسف مستوى التوصيل تراجع في جدة.. المندوب تأخر ساعتين والآيس كريم واصل ذايب تماماً! 😡🍦", "ar", "Oasis Retail", "negative", "Delivery & Logistics", False, "Saudi", "Late melted delivery complaint"),
    ("oasis_003", "instagram", "Weekend mega clearance sale at Oasis Retail Festival City! Got premium cookware at 60% off. Clean aisles and fast checkout. 🛍️", "en", "Oasis Retail", "positive", "Promotions & Offers", False, "English", "In-store clearance sale praise"),
    ("oasis_004", "tiktok", "جولة في فرع واحة التجزئة الجديد في الظهران مول.. هل هو أفضل من الفروع القديمة؟", "ar", "Oasis Retail", "neutral", "General", False, "Saudi", "New store walkthrough"),
    ("oasis_005", "instagram", "شكراً واحة التجزئة على التغليف الخرافي، كرتون البيض مكسور والزيت منسكب فوق الخضار! شغل نظيف ما شاء الله 👏📦", "ar", "Oasis Retail", "negative", "Delivery & Logistics", True, "Saudi", "Sarcastic complaint about damaged packaging"),
    ("oasis_006", "tiktok", "عروض الخضار واللحوم الطازجة في واحة التجزئة كل يوم اثنين لا تفوتكم، الأسعار أرخص من حلقة الخضار 🥩🥬", "ar", "Oasis Retail", "positive", "Promotions & Offers", False, "Saudi", "Weekly deals praise"),
    ("oasis_007", "instagram", "اشتريت جهاز من فرع الواحة وطلع عطلان ورفضوا يرجعونه لأن الكرتون مفتوح! وين حقوق المستهلك؟", "ar", "Oasis Retail", "negative", "Customer Support", False, "Saudi", "Return policy dispute"),
    ("oasis_008", "tiktok", "هل تطبيق واحة التجزئة يوفر توصيل لنفس اليوم في مدينة العين؟", "ar", "Oasis Retail", "neutral", "Delivery & Logistics", False, "Emirati", "Delivery coverage query"),
    ("oasis_009", "instagram", "Oasis Retail grocery subscription delivers organic milk and eggs every Sunday without fail. Life saver for busy families! 🥛", "en", "Oasis Retail", "positive", "Delivery & Logistics", False, "English", "Subscription grocery praise"),
    ("oasis_010", "tiktok", "أسعار واحة التجزئة في المواد التموينية ارتفعت فجأة بنسبة 20% مقارنة بالسوبرماركت اللي جنبه!", "ar", "Oasis Retail", "negative", "Pricing & Billing", False, "Saudi", "Price hike complaint"),
    ("oasis_011", "instagram", "برنامج ولاء واحة التجزئة يمنحك نقاط على كل ريال، وفرت 300 ريال بمشتريات مقاضي رمضان 👍", "ar", "Oasis Retail", "positive", "Promotions & Offers", False, "Saudi", "Loyalty program praise"),
    ("oasis_012", "tiktok", "مندوب توصيل الواحة دق الجرس ومشى وحط الأكياس برا في الشمس الحارة بدون ما يتأكد من استلامي!", "ar", "Oasis Retail", "negative", "Delivery & Logistics", False, "Saudi", "Driver dropped in heat complaint"),
    ("oasis_013", "instagram", "Oasis Retail launches autonomous self-checkout kiosks across all major Dubai branches.", "en", "Oasis Retail", "neutral", "App & UX Experience", False, "English", "Kiosk technology news"),
    ("oasis_014", "tiktok", "قسم المخبوزات والحلويات الفرنسية في واحة التجزئة فرع التحلية إدمان لا يوصف خصوصاً الكرواسون 🥐✨", "ar", "Oasis Retail", "positive", "General", False, "Saudi", "Bakery praise"),
    ("oasis_015", "instagram", "تطبيق واحة التجزئة يسحب المبلغ مرتين عند الدفع عن طريق مدى والدعم الفني يقول راجع البنك!", "ar", "Oasis Retail", "negative", "App & UX Experience", False, "Saudi", "Mada double charge"),
    ("oasis_016", "tiktok", "ما مواعيد عمل فرع واحة التجزئة في طريق الملك فهد بالرياض خلال إجازة عيد الأضحى؟", "ar", "Oasis Retail", "neutral", "General", False, "Saudi", "Eid store hours query"),
    ("oasis_017", "instagram", "Great customer service at Oasis Retail Abu Dhabi! Lost my wallet in the trolley and security safely returned it intact.", "en", "Oasis Retail", "positive", "Customer Support", False, "English", "Lost & found praise"),
    ("oasis_018", "tiktok", "يعطيكم العافية يا واحة التجزئة، طالب طلبية بقيمة 800 ريال وتجيبون نصف الأغراض ناقصة بدون تعويض! خدمة فخمة 🙃", "ar", "Oasis Retail", "negative", "Customer Support", True, "Saudi", "Sarcastic missing items complaint"),
    ("oasis_019", "instagram", "هل تتوفر منتجات خالية من الغلوتين في فروع أسواق الواحة بالشارقة؟", "ar", "Oasis Retail", "neutral", "General", False, "Emirati", "Product availability query"),
    ("oasis_020", "tiktok", "تطبيق واحة التجزئة تصميمه يفتح النفس، ميزة إعادة طلب المقاضي بلمسة واحدة سهلت حياتنا كثير 📲🛒", "ar", "Oasis Retail", "positive", "App & UX Experience", False, "Saudi", "Reorder UX feature praise"),
    ("oasis_021", "instagram", "The organic produce section at Oasis Retail was completely empty today at 5 PM. Poor replenishment management.", "en", "Oasis Retail", "negative", "Delivery & Logistics", False, "English", "Out of stock complaint"),
    ("oasis_022", "tiktok", "عروض واحة التجزئة على الأجهزة المنزلية والشاشات بمناسبة العودة للمدارس ممتازة جداً.", "ar", "Oasis Retail", "positive", "Promotions & Offers", False, "Saudi", "Back to school deals praise"),
    ("oasis_023", "instagram", "واحة التجزئة تفتتح مركز التوزيع اللوجستي المؤتمت بالكامل في المنطقة اللوجستية بالرياض.", "ar", "Oasis Retail", "neutral", "Delivery & Logistics", False, "MSA", "Logistics facility announcement"),
    ("oasis_024", "tiktok", "رسوم التوصيل السريع في تطبيق الواحة صارت 25 ريال للطلب الواحد.. سعر مبالغ فيه جداً!", "ar", "Oasis Retail", "negative", "Pricing & Billing", False, "Saudi", "Delivery fee complaint"),
    ("oasis_025", "instagram", "Oasis Retail app is so intuitive. Search filters for vegan and gluten-free items work like a charm.", "en", "Oasis Retail", "positive", "App & UX Experience", False, "English", "App search filter praise"),
    ("oasis_026", "tiktok", "هل كود خصم OASIS20 صالح للاستخدام داخل الفروع أو فقط عبر التطبيق؟", "ar", "Oasis Retail", "neutral", "Promotions & Offers", False, "Saudi", "Coupon terms query"),
    ("oasis_027", "instagram", "وجدت منتجات منتهية الصلاحية معروضة على الرف في فرع واحة التجزئة.. يرجى تشديد الرقابة الصحية!", "ar", "Oasis Retail", "negative", "General", False, "Saudi", "Expired goods complaint"),
    ("oasis_028", "tiktok", "مواقف السيارات في فرع الواحة واسعة ومريحة مع توفر شواحن مجانية للسيارات الكهربائية ⚡🚗", "ar", "Oasis Retail", "positive", "General", False, "Emirati", "EV charger parking praise"),
    ("oasis_029", "instagram", "Delayed delivery by 3 hours from Oasis Retail without any notification or driver call. Ruined our dinner plans.", "en", "Oasis Retail", "negative", "Delivery & Logistics", False, "English", "Dinner delay complaint"),
    ("oasis_030", "tiktok", "أسواق الواحة تعلن عن بدء استقبال طلبات التوظيف الموسمي للمواطنين في فروع مكة والمدينة.", "ar", "Oasis Retail", "neutral", "General", False, "MSA", "Seasonal job opening announcement"),

    # =========================================================================
    # BRAND 4: Falcon Ride (30 Posts)
    # =========================================================================
    ("falcon_001", "tiktok", "يا جماعة مو معقول أسعار صقر رايد Falcon Ride وقت خروج الموظفين في الرياض! المشوار صار بـ 110 ريال والسعر العادي 35.. سلامات؟! 🚗💸", "ar", "Falcon Ride", "negative", "Pricing & Billing", False, "Saudi", "Rush hour surge pricing complaint"),
    ("falcon_002", "instagram", "Falcon Ride driver cancelled after making me wait 20 minutes in 43°C heat outside Dubai Mall, and the app charged ME a cancellation fee! 🚗🔥", "en", "Falcon Ride", "negative", "Customer Support", False, "English", "Unfair cancellation charge complaint"),
    ("falcon_003", "tiktok", "ميزة الحجز المسبق في صقر رايد للمطار ممتازة جداً. السائق وصل قبل الموعد بـ 10 دقائق وسيارة نظيفة وقيادة هادئة 👍✈️", "ar", "Falcon Ride", "positive", "App & UX Experience", False, "Saudi", "Airport pre-booking praise"),
    ("falcon_004", "instagram", "كود خصم صقر رايد FALCON25 شغال حالياً في أبوظبي والشارقة خصم 25% على أول 3 مشاوير.. جربوه وعطوني رايكم 🎟️", "mixed", "Falcon Ride", "neutral", "Promotions & Offers", False, "Emirati", "Promo code share"),
    ("falcon_005", "tiktok", "يا زين كابتن صقر رايد، لافف فيني نص شوارع الرياض عشان يزيد العداد وقال ما أعرف الطريق! قمة الأمانة ما قصرتوا 👏🗺️", "ar", "Falcon Ride", "negative", "Customer Support", True, "Saudi", "Sarcastic complaint about driver route manipulation"),
    ("falcon_006", "instagram", "Falcon Ride EV fleet in Dubai is so clean and quiet. Professional chauffeurs and smooth ride.", "en", "Falcon Ride", "positive", "General", False, "English", "EV fleet praise"),
    ("falcon_007", "tiktok", "تطبيق صقر رايد سحب من بطاقتي مبلغ المشوار مرتين والمشوار تكنسل أصلاً! أرجعوا فلوسي يا صقر", "ar", "Falcon Ride", "negative", "Pricing & Billing", False, "Saudi", "Ghost ride double charge"),
    ("falcon_008", "instagram", "هل يسمح باصطحاب الحيوانات الأليفة الصغيرة في مشاوير صقر رايد داخل السعودية؟", "ar", "Falcon Ride", "neutral", "General", False, "Saudi", "Pet policy query"),
    ("falcon_009", "tiktok", "صقر رايد أسرع تطبيق يلقى لك كابتن في وقت المطر بزحمة طريق الملك فهد، شكراً للخدمة السريعة 🌧️🚗", "ar", "Falcon Ride", "positive", "Delivery & Logistics", False, "Saudi", "Rainy day dispatch praise"),
    ("falcon_010", "instagram", "Customer care on Falcon Ride app refused to investigate driver reckless driving. Very poor safety escalation.", "en", "Falcon Ride", "negative", "Customer Support", False, "English", "Safety response complaint"),
    ("falcon_011", "tiktok", "اشتراك صقر بلس الشهري وفر علي مبالغ كبيرة بالمشاوير اليومية للدوام، ميزة إلغاء رسوم الذروة بطلة 💯", "ar", "Falcon Ride", "positive", "Promotions & Offers", False, "Saudi", "Subscription pass praise"),
    ("falcon_012", "instagram", "السائق طلب مني إلغاء الطلب والدفع كاش بحجة أن نسبة الشركة عالية! وين الرقابة على السائقين؟", "ar", "Falcon Ride", "negative", "Customer Support", False, "Saudi", "Off-platform cash request"),
    ("falcon_013", "tiktok", "كم النسبة المقتطعة من كباتن صقر رايد السعوديين في مشاوير التوصيل داخل المدن؟", "ar", "Falcon Ride", "neutral", "Pricing & Billing", False, "Saudi", "Driver commission query"),
    ("falcon_014", "instagram", "Had a lovely trip with Falcon Ride from Abu Dhabi to Dubai. Comfortable Lexus sedan and polite driver.", "en", "Falcon Ride", "positive", "Delivery & Logistics", False, "English", "Intercity luxury trip praise"),
    ("falcon_015", "tiktok", "تطبيق صقر رايد يهنق وما يحدد الموقع على الـ GPS بدقة، دايم ينزل السائق في الشارع الخلفي!", "ar", "Falcon Ride", "negative", "App & UX Experience", False, "Saudi", "GPS inaccuracy complaint"),
    ("falcon_016", "instagram", "شركة صقر رايد تعلن عن توسيع أسطول المركبات الكهربائية الصديقة للبيئة في موسم الرياض.", "ar", "Falcon Ride", "neutral", "General", False, "MSA", "Green fleet announcement"),
    ("falcon_017", "tiktok", "نسيت شنطتي في سيارة صقر رايد والكابتن تواصل معي ورجعها لباب البيت ورفض يأخذ أي مكافأة! أمانة وأخلاق عالية 👏", "ar", "Falcon Ride", "positive", "Customer Support", False, "Saudi", "Lost item return praise"),
    ("falcon_018", "instagram", "Falcon Ride surge pricing jumped from 1.2x to 3.5x within 3 minutes after the concert ended. Pure price gouging.", "en", "Falcon Ride", "negative", "Pricing & Billing", False, "English", "Extreme event surge pricing"),
    ("falcon_019", "tiktok", "كيف اقدم للعمل كابتن توصيل في تطبيق صقر رايد بسيارتي الخاصة؟", "ar", "Falcon Ride", "neutral", "General", False, "Saudi", "Driver registration query"),
    ("falcon_020", "instagram", "خدمة سريعة جداً ما شاء الله، انتظر السائق 35 دقيقة عشان مشوار مدته 5 دقائق! يعطيكم ألف عافية 🙃", "ar", "Falcon Ride", "negative", "Delivery & Logistics", True, "Saudi", "Sarcastic wait time complaint"),
    ("falcon_021", "tiktok", "أفضل ميزة في صقر رايد هي خيار المشاوير النسائية مع كابتن أنثى، راحة وأمان وخصوصية تامة 🌸🚗", "ar", "Falcon Ride", "positive", "General", False, "Saudi", "Women-only ride feature praise"),
    ("falcon_022", "instagram", "App charged my credit card despite showing 'Payment Failed'. Waiting for customer support since yesterday.", "en", "Falcon Ride", "negative", "App & UX Experience", False, "English", "Payment state bug"),
    ("falcon_023", "tiktok", "هل بطاقات مدى مسبقة الدفع مقبولة في تطبيق صقر رايد؟", "ar", "Falcon Ride", "neutral", "Pricing & Billing", False, "Saudi", "Payment method query"),
    ("falcon_024", "instagram", "سائق صقر رايد كان جداً محترم وشغل تكييف السيارة بدون طلب وكانت رحلة مريحة بعد يوم عمل شاق.", "ar", "Falcon Ride", "positive", "Customer Support", False, "Emirati", "Pleasant ride experience"),
    ("falcon_025", "tiktok", "الكابتن يقبل المشوار ويوقف سيارته بعيد وما يتحرك عشان يخليني أنا ألغي المشوار وأتحمل رسوم الإلغاء!", "ar", "Falcon Ride", "negative", "Customer Support", False, "Saudi", "Driver stalling tactic complaint"),
    ("falcon_026", "instagram", "Falcon Ride introduces pet-friendly rides category in selected Riyadh districts.", "en", "Falcon Ride", "neutral", "General", False, "English", "New category announcement"),
    ("falcon_027", "tiktok", "عرض نهاية الأسبوع من صقر رايد خصم 30% على المشاوير إلى الواجهة البحرية في الخبر بطل جداً.", "ar", "Falcon Ride", "positive", "Promotions & Offers", False, "Saudi", "Promotional discount praise"),
    ("falcon_028", "instagram", "تطبيق صقر رايد كل تحديث يضيع عناوين المنزل المحفوظة وتضطر تدخلها يدوي من جديد!", "ar", "Falcon Ride", "negative", "App & UX Experience", False, "Saudi", "Saved places wipe bug"),
    ("falcon_029", "tiktok", "Great experience booking Falcon Ride executive van for corporate airport delegates. Punctual and clean.", "en", "Falcon Ride", "positive", "Delivery & Logistics", False, "English", "Corporate van booking praise"),
    ("falcon_030", "instagram", "ما هي شروط موديل السيارة المقبولة للعمل في صقر رايد لعام 2026؟", "ar", "Falcon Ride", "neutral", "General", False, "Saudi", "Vehicle model requirement query"),

    # =========================================================================
    # BRAND 5: GulfCloud (30 Posts)
    # =========================================================================
    ("gulfcloud_001", "instagram", "فخورون بإتمام نقل البنية التحتية لشركتنا بالكامل إلى مراكز بيانات سحابة الخليج GulfCloud في الرياض. زمن استجابة أقل من 6ms 🇸🇦☁️", "ar", "GulfCloud", "positive", "App & UX Experience", False, "Saudi", "Low latency enterprise migration praise"),
    ("gulfcloud_002", "tiktok", "GulfCloud me-central-1 region experiencing elevated API latency and partial database replication outages this afternoon. Waiting on post-mortem. ⚠️", "en", "GulfCloud", "negative", "Network & Outage", False, "English", "Database replication incident"),
    ("gulfcloud_003", "instagram", "تعلن جلف كلاود GulfCloud عن برنامج دعم الشركات الناشئة برصيد سحابي يصل إلى 50,000 دولار مع تدريب مجاني للفرق التقنية. 💡🚀", "ar", "GulfCloud", "neutral", "Promotions & Offers", False, "MSA", "Startup credit program announcement"),
    ("gulfcloud_004", "tiktok", "سحابة الخليج ما قصرتوا والله، السيرفرات طاحت بنصف الليل وقاعدة بيانات الإنتاج انضربت والـ SLA عندكم 99.9% على الورق بس! 👏💻", "ar", "GulfCloud", "negative", "Network & Outage", True, "Saudi", "Sarcastic complaint about SLA breach"),
    ("gulfcloud_005", "instagram", "Migrated our Kubernetes workloads to GulfCloud Managed K8s. Deployments are blazing fast and support team is knowledgeable.", "en", "GulfCloud", "positive", "App & UX Experience", False, "English", "Kubernetes migration praise"),
    ("gulfcloud_006", "tiktok", "فاتورة سحابة الخليج هذا الشهر فيها رسوم خيالية غير مفهومة لخدمات نقل البيانات Data Egress بدون تفصيل واضح!", "ar", "GulfCloud", "negative", "Pricing & Billing", False, "Saudi", "Data egress bill shock"),
    ("gulfcloud_007", "instagram", "هل مراكز بيانات GulfCloud معتمدة رسمياً من هيئة الاتصالات والفضاء والتقنية لتخزين البيانات الحكومية الحساسة من الفئة ج؟", "ar", "GulfCloud", "neutral", "General", False, "Saudi", "Regulatory compliance query"),
    ("gulfcloud_008", "tiktok", "الدعم الفني للشركات في GulfCloud سريع الاستجابة جداً، مهندس الدعم اتصل معي هاتفياً وحل مشكلة شهادة SSL خلال 10 دقائق 🔒👍", "ar", "GulfCloud", "positive", "Customer Support", False, "Saudi", "Enterprise support praise"),
    ("gulfcloud_009", "instagram", "GulfCloud web console login session expires every 10 minutes and logs out engineers midway through infrastructure deployments. Annoying UX!", "en", "GulfCloud", "negative", "App & UX Experience", False, "English", "Console session timeout annoyance"),
    ("gulfcloud_010", "tiktok", "ورشة عمل مجانية عبر الإنترنت مقدمة من سحابة الخليج لشرح بنية السحابة السيادية وحلول حماية البيانات.", "ar", "GulfCloud", "neutral", "General", False, "MSA", "Educational webinar announcement"),
    ("gulfcloud_011", "instagram", "أفضل خيار لاستضافة تطبيقات الويب في الشرق الأوسط، سرعة تحميل الصفحات زادت بنسبة 40% مقارنة بالاستضافات الأوروبية ⚡🇸🇦", "ar", "GulfCloud", "positive", "Network & Outage", False, "Saudi", "Local hosting performance praise"),
    ("gulfcloud_012", "tiktok", "خدمة العملاء في سحابة الخليج يرفضون الرد على تذاكر الدعم العاجلة للمستوى المجاني، لهم 4 أيام بدون أي إفادة!", "ar", "GulfCloud", "negative", "Customer Support", False, "Saudi", "Free tier support silence"),
    ("gulfcloud_013", "instagram", "GulfCloud launches Object Storage tier with S3-compatible API and automated multi-zone replication.", "en", "GulfCloud", "neutral", "General", False, "English", "Product launch announcement"),
    ("gulfcloud_014", "tiktok", "تكامل سلس جداً بين سيرفرات GulfCloud وحلول الدفع الإلكتروني المحلية في السعودية، تجربة المطورين عندهم ممتازة 👨‍💻", "ar", "GulfCloud", "positive", "App & UX Experience", False, "Saudi", "Developer experience praise"),
    ("gulfcloud_015", "instagram", "توقف مفاجئ في بوابة السداد الإلكتروني لخدمات GulfCloud تسبب في تعليق ترقية باقة التخزين لموقعنا!", "ar", "GulfCloud", "negative", "App & UX Experience", False, "Saudi", "Billing portal outage"),
    ("gulfcloud_016", "tiktok", "ما هو الحد الأدنى للاشتراك في السيرفرات السحابية المخصصة Dedicated Hosts من سحابة الخليج؟", "ar", "GulfCloud", "neutral", "Pricing & Billing", False, "MSA", "Dedicated host pricing query"),
    ("gulfcloud_017", "instagram", "GulfCloud's IAM role granular permission system made achieving local cybersecurity audit compliance completely stress-free.", "en", "GulfCloud", "positive", "General", False, "English", "Compliance praise"),
    ("gulfcloud_018", "tiktok", "يعطيكم ألف عافية يا جلف كلاود، نزل تحديث فجأة خرب تكوين جدار الحماية وعطل مواقع العملاء ساعتين كاملة! احترافية غير مسبوقة 🙃", "ar", "GulfCloud", "negative", "Network & Outage", True, "Saudi", "Sarcastic outage complaint"),
    ("gulfcloud_019", "instagram", "سحابة الخليج تعلن عن افتتاح ثالث مركز بيانات متقدم في مدينة الجبيل الصناعية.", "ar", "GulfCloud", "neutral", "General", False, "MSA", "Datacenter launch announcement"),
    ("gulfcloud_020", "tiktok", "مقارنة تكاليف البنية التحتية بين GulfCloud والمنصات العالمية.. وفرنا أكثر من 25% من التكاليف التشغيلية السنوية 📊💰", "ar", "GulfCloud", "positive", "Pricing & Billing", False, "Saudi", "Cost saving case study"),
    ("gulfcloud_021", "instagram", "Severe packet loss on GulfCloud UAE interconnect route today between Dubai and Riyadh. DevOps team on high alert.", "en", "GulfCloud", "negative", "Network & Outage", False, "English", "Interconnect packet loss"),
    ("gulfcloud_022", "tiktok", "هل تدعم قواعد بيانات GulfCloud خاصية التشفير في وضع السكون Encryption at Rest بمفاتيح خاصة بالعميل؟", "ar", "GulfCloud", "neutral", "General", False, "Saudi", "Encryption key inquiry"),
    ("gulfcloud_023", "instagram", "خدمة التخزين السحابي البارد Cold Storage في سحابة الخليج ممتازة جداً للأرشفة القانونية وبأسعار رمزية.", "ar", "GulfCloud", "positive", "Promotions & Offers", False, "Saudi", "Cold storage praise"),
    ("gulfcloud_024", "tiktok", "حذفوا خادوم التطوير بالخطأ بدلاً من إعادة تشغيله والدعم الفني يقول لا يمكن استرجاع النسخة الاحتياطية! كارثة بكل المقاييس 🚨", "ar", "GulfCloud", "negative", "Customer Support", False, "Saudi", "Accidental instance deletion complaint"),
    ("gulfcloud_025", "instagram", "GulfCloud SDK for Python and Go is well-documented and easy to integrate into Terraform CI/CD pipelines.", "en", "GulfCloud", "positive", "App & UX Experience", False, "English", "Terraform & SDK praise"),
    ("gulfcloud_026", "tiktok", "جدول دورات التدريب والشهادات الاحترافية المعتمدة لمهندسي سحابة الخليج لشهر نوفمبر 2026.", "ar", "GulfCloud", "neutral", "General", False, "MSA", "Training schedule announcement"),
    ("gulfcloud_027", "instagram", "أسعار قواعد البيانات المدارة Managed PostgreSQL في سحابة الخليج أغلى من المنافسين بـ 30% بدون مبرر مقنع.", "ar", "GulfCloud", "negative", "Pricing & Billing", False, "Saudi", "Database pricing complaint"),
    ("gulfcloud_028", "tiktok", "لوحة تحكم GulfCloud سريعة وخفيفة وتدعم اللغة العربية والإنجليزية بشكل ممتاز ومتقن.", "ar", "GulfCloud", "positive", "App & UX Experience", False, "Saudi", "Bilingual console praise"),
    ("gulfcloud_029", "instagram", "Unexpected network degradation on GulfCloud DNS resolving service causing timeout on our customer portals.", "en", "GulfCloud", "negative", "Network & Outage", False, "English", "DNS timeout incident"),
    ("gulfcloud_030", "tiktok", "كيفية إعداد النسخ الاحتياطي التلقائي لقواعد البيانات في سحابة الخليج بخطوات بسيطة.", "ar", "GulfCloud", "neutral", "General", False, "Saudi", "How-to tutorial guide"),
]


def generate_gold_csv():
    headers = [
        "post_id", "platform", "text", "language", "brand",
        "gold_sentiment", "gold_theme", "is_sarcasm", "dialect", "annotator_notes"
    ]

    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for item in ITEMS:
            writer.writerow(item)

    print(f"Successfully generated {len(ITEMS)} gold records at: {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_gold_csv()
