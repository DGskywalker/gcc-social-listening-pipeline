# GCC Social Listening Data Labelling & Annotation Guide

## 1. Purpose & Scope

This guide defines the standardized methodology for annotating social listening data originating from the GCC region (Saudi Arabia, UAE, Qatar, Kuwait, Bahrain, and Oman). It provides explicit rules for classifying sentiment, dialectal nuances, sarcasm, and business themes across Arabic (dialects + MSA), English, and bilingual code-switching.

---

## 2. Sentiment Annotation Taxonomy

Annotators must classify each post into exactly one of three sentiment categories:

### A. Positive (`positive`)
- **Definition**: The author expresses satisfaction, gratitude, excitement, praise, recommendation, or happiness with a brand, service, or feature.
- **GCC Examples**:
  - *"والله محفظة ديزرت باي فكت أزمة كاش باك فوري وخدمة ممتازة شكرا لكم"* (Saudi praise for cashback)
  - *"Al-Noor Telecom 5G in Business Bay is blistering fast! Over 900 Mbps."* (Praise for 5G speed)
  - *"توصيل واحة التجزئة في دبي وصل في أقل من نص ساعة وفواكه طازجة"* (Satisfaction with delivery)

### B. Negative (`negative`)
- **Definition**: The author expresses frustration, disappointment, anger, criticism, financial grievance, or operational complaints.
- **Includes Dialectal Sarcasm & Polite Complaints**: (See Section 3 below).
- **GCC Examples**:
  - *"تطبيق صقر رايد رافع الأسعار ثلاث أضعاف وقت الذروة حرام عليكم"* (Complaint about surge pricing)
  - *"سحابة الخليج طايحة من الصباح وسيرفرات الشركة متعطلة ومحد يرد"* (Critical cloud outage)
  - *"Waiting 40 minutes on Al-Noor support line and got disconnected. Worst telco ever."* (CS complaint)

### C. Neutral (`neutral`)
- **Definition**: Factual questions, operational announcements, neutral comparisons without sentiment valence, feature inquiries, or balanced statements where positive and negative aspects cancel out.
- **GCC Examples**:
  - *"هل فرع واحة التجزئة في دبي مول يفتح بعد صلاة الجمعة؟"* (Factual store hours query)
  - *"عرض باقة التجوال لدول الخليج بـ 150 ريال، هل تشمل بيانات غير محدودة؟"* (Inquiry on terms)
  - *"Falcon Ride launched operations in Abu Dhabi this week."* (Factual announcement)

---

## 3. Special Case: Sarcasm & Irony Detection (`is_sarcasm`)

Sarcasm is prevalent on GCC social media (especially Twitter/X and TikTok). Surface positive words are deliberately used to ridicule operational failures.

### Sarcasm Rules:
1. **Rule 1 - The Praise-Complaint Juxtaposition**: If a post pairs praise terms (*"ما قصرتوا"*, *"خدمة روعة"*, *"يعطيكم العافية"*, *"يا زين خدمتكم"*, *"قمة الاحترافية"*) with an obvious failure (*"النت فاصل"*, *"الطلب تأخر ٣ ساعات"*, *"الآيس كريم واصل ذايب"*), mark as **`negative`** and set `is_sarcasm = TRUE`.
2. **Rule 2 - Mocking Emojis**: Posts celebrating failures with claps (*"👏"*) or upside-down faces (*"🙃"*) are sarcastic.
   - Example: *"خدمة عملاء النور سريعة جداً ما شاء الله، رادين علي بعد ٤ أيام 👏"* -> **`negative`**, `is_sarcasm = TRUE`.

---

## 4. Theme & Topic Taxonomy (`gold_theme`)

Select the single most prominent primary theme:
1. **`Network & Outage`**: Fiber disconnections, 5G signal gaps, latency, server downtime, packet loss, tower maintenance.
2. **`Customer Support`**: Unresponsive support, long wait times, bot complaints, agent interactions, unresolved tickets.
3. **`Pricing & Billing`**: High tariffs, surge pricing, unexpected fees, international transfer charges, billing disputes.
4. **`Delivery & Logistics`**: Courier turnaround time, damaged/melted orders, driver cancellations, delivery fees.
5. **`Promotions & Offers`**: Cashback promotions, discount codes, National Day/Ramadan campaigns, referral incentives.
6. **`App & UX Experience`**: App crashes, frozen screens, OTP failures, biometric login bugs, UI navigation issues.
7. **`General`**: Corporate announcements, generic queries, store location requests.

---

## 5. Dialect & Language Annotation

- **Language (`language`)**: `ar` (Arabic dominant), `en` (English dominant), `mixed` (Bilingual code-switching).
- **Dialect (`dialect`)**:
  - `Saudi`: Distinct markers (*"شالسالفة"*, *"ودي"*, *"بالرياض"*, *"سلامات"*, *"فكت أزمة"*).
  - `Emirati`: Distinct markers (*"وايد"*, *"شو سالفة"*, *"حبيت"*, *"بدبي"*).
  - `Gulf`: Generalized Khaleeji vocabulary.
  - `MSA`: Modern Standard Arabic (*"نعلن عن إطلاق"*, *"تحديث البنية التحتية"*).
  - `English`: Standard GCC expat or technical English.
  - `Mixed`: Code-switching (*"الـ 5G حق النور صار so slow اليومين ذي"*).

---

## 6. Annotator Agreement & Arbitration
- All posts must be audited by at least one secondary reviewer.
- Discrepancies between annotators are resolved using majority vote or arbitration by a GCC native domain specialist.
- All finalized items become part of the immutable Gold Benchmark dataset.
