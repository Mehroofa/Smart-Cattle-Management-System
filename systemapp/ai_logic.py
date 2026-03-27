def get_ai_suggestion(symptoms):
    symptoms = symptoms.lower()

    if "fever" in symptoms and "no appetite" in symptoms:
        return "Possible infection or fever-related illness"

    elif "cough" in symptoms or "breathing" in symptoms:
        return "Possible respiratory disease"

    elif "diarrhea" in symptoms:
        return "Possible digestive disorder"

    elif "limping" in symptoms or "injury" in symptoms:
        return "Possible injury or leg problem"

    else:
        return "Condition unclear. Veterinary examination recommended."


def _normalize_text(text: str) -> str:
    return (text or "").strip().lower()


def worker_copilot_reply(message: str, language: str = "en") -> str:
    """
    Lightweight, offline "AI copilot" for workers.
    Uses keyword/rule-based guidance + small built-in translations (no external API).
    """
    msg = _normalize_text(message)

    # Detect intent
    vaccination_words = ("vaccin", "vaccine", "fmd", "hs", "bq", "brucell", "rabies", "deworm")
    emergency_words = ("emergency", "breathing", "choking", "bloat", "bloated", "seizure", "unconscious", "bleeding", "can't stand", "cannot stand")
    symptom_words = ("fever", "temperature", "cough", "breathing", "diarrhea", "loose motion", "vomit", "limp", "limping", "injury", "wound", "no appetite", "not eating")

    if any(w in msg for w in emergency_words):
        key = "emergency"
        return _translate_reply(key, language)

    if any(w in msg for w in vaccination_words):
        key = "vaccination"
        return _translate_reply(key, language)

    if any(w in msg for w in symptom_words):
        suggestion = get_ai_suggestion(msg)
        suggestion_key = {
            "Possible infection or fever-related illness": "ai_infection",
            "Possible respiratory disease": "ai_respiratory",
            "Possible digestive disorder": "ai_digestive",
            "Possible injury or leg problem": "ai_injury",
            "Condition unclear. Veterinary examination recommended.": "ai_unclear",
        }.get(suggestion, "ai_unclear")

        parts = [
            _translate_reply(suggestion_key, language),
            _translate_reply("next_steps", language),
        ]
        return "\n\n".join([p for p in parts if p])

    return _translate_reply("ask_more", language)


def _translate_reply(key: str, language: str) -> str:
    language = (language or "en").strip().lower()

    en = {
        "ask_more": (
            "Tell me the symptoms (fever/cough/diarrhea/limping), appetite, and since when.\n"
            "If you can, share temperature and cattle tag id. I’ll suggest the next step."
        ),
        "next_steps": (
            "Next steps:\n"
            "1) Isolate the animal if contagious symptoms.\n"
            "2) Provide clean water; electrolytes if diarrhea.\n"
            "3) Keep the shed clean and observe every 2–4 hours.\n"
            "4) Contact the vet if high fever, breathing trouble, blood in stool, or not eating > 12 hours."
        ),
        "emergency": (
            "This looks urgent.\n"
            "If the cattle has difficulty breathing, severe bloat, heavy bleeding, seizures, or cannot stand — call a veterinarian immediately."
        ),
        "vaccination": (
            "Vaccination help:\n"
            "Tell me the cattle age and last vaccination date.\n"
            "Common vaccines: FMD (Foot & Mouth), HS (Hemorrhagic Septicemia), BQ (Black Quarter), Brucellosis.\n"
            "If you share age + last dose, I’ll tell what may be due and safety steps."
        ),
        "ai_infection": (
            "Possible infection / fever-related illness.\n"
            "Check temperature, hydration, and appetite. Avoid stress and contact the vet for diagnosis/medicine."
        ),
        "ai_respiratory": (
            "Possible respiratory disease.\n"
            "Check breathing rate, nasal discharge, cough. Improve ventilation and contact the vet."
        ),
        "ai_digestive": (
            "Possible digestive disorder.\n"
            "Watch for dehydration. Give clean water/electrolytes and contact the vet if it continues."
        ),
        "ai_injury": (
            "Possible injury / leg problem.\n"
            "Limit movement, check for swelling/wounds, keep the area clean, and contact the vet if severe."
        ),
        "ai_unclear": (
            "Condition unclear.\n"
            "Please share more symptoms and since when. Veterinary examination is recommended."
        ),
    }

    translations = {
        "hi": {
            "ask_more": "लक्षण बताइए (बुखार/खांसी/दस्त/लंगड़ापन), भूख कैसी है, और कब से है।\nअगर हो सके तो तापमान और गाय/भैंस का टैग आईडी भी बताइए।",
            "next_steps": "अगले कदम:\n1) संक्रामक लक्षण हों तो अलग रखें।\n2) साफ पानी दें; दस्त में ORS/इलेक्ट्रोलाइट।\n3) शेड साफ रखें और हर 2–4 घंटे निगरानी करें।\n4) तेज बुखार, सांस में तकलीफ, मल में खून, या 12 घंटे से ज़्यादा न खाना — तुरंत डॉक्टर से संपर्क करें।",
            "emergency": "यह आपातकाल जैसा लग रहा है।\nअगर सांस लेने में बहुत दिक्कत, पेट बहुत फूलना, ज्यादा खून बहना, दौरे, या खड़ा न हो पा रहा हो — तुरंत पशु चिकित्सक को कॉल करें।",
            "vaccination": "टीकाकरण सहायता:\nपशु की उम्र और आखिरी टीका की तारीख बताइए।\nआम टीके: FMD, HS, BQ, Brucellosis.\nउम्र + आखिरी डोज़ बताने पर मैं बताऊँगा/बताऊँगी क्या ड्यू हो सकता है।",
            "ai_infection": "संभावित संक्रमण / बुखार से जुड़ी बीमारी।\nतापमान, पानी की कमी और भूख जांचें। तनाव कम रखें और दवा/जांच के लिए डॉक्टर से संपर्क करें।",
            "ai_respiratory": "संभावित श्वसन रोग।\nसांस की गति, नाक से स्राव, खांसी देखें। वेंटिलेशन सुधारें और डॉक्टर से संपर्क करें।",
            "ai_digestive": "संभावित पाचन समस्या।\nडिहाइड्रेशन देखें। साफ पानी/इलेक्ट्रोलाइट दें और जारी रहे तो डॉक्टर से संपर्क करें।",
            "ai_injury": "संभावित चोट / पैर की समस्या।\nचलना कम कराएं, सूजन/घाव देखें, जगह साफ रखें और ज्यादा हो तो डॉक्टर से संपर्क करें।",
            "ai_unclear": "स्थिति स्पष्ट नहीं है।\nकृपया और लक्षण व कब से है बताइए। पशु चिकित्सक की जांच की सलाह है।",
        },
        "ml": {
            "ask_more": "ലക്ഷണങ്ങൾ പറയൂ (ജ്വരം/ചുമ/ദഹനക്കേട്/കുഴഞ്ഞുനടപ്പ്), ഭക്ഷണം കഴിക്കുന്നുണ്ടോ, എപ്പോൾ മുതൽ എന്ന്.\nകഴിയുമെങ്കിൽ താപനിലയും കാള/പശുവിന്റെ ടാഗ് ഐഡിയും പറയൂ.",
            "next_steps": "അടുത്ത നടപടികൾ:\n1) പകർച്ച ലക്ഷണങ്ങൾ ഉണ്ടെങ്കിൽ മൃഗത്തെ വേർപ്പെടുത്തുക.\n2) ശുദ്ധജലം നൽകുക; ദഹനക്കേടിൽ ORS/ഇലക്ട്രോലൈറ്റ്.\n3) കാളിവളം/ഷെഡ് ശുദ്ധമായി സൂക്ഷിച്ച് 2–4 മണിക്കൂറിൽ ഒരിക്കൽ നിരീക്ഷിക്കുക.\n4) ഉയർന്ന ജ്വരം, ശ്വാസതടസം, മലത്തിൽ രക്തം, അല്ലെങ്കിൽ 12 മണിക്കൂർക്കുമുകളിൽ ഭക്ഷണം കഴിക്കാത്തത് — വെറ്റിനറിയിക്കുക.",
            "emergency": "ഇത് അടിയന്തിരമായതായി തോന്നുന്നു.\nശ്വാസം മുട്ടൽ, കടുത്ത വയർവീര്‌പ്പ്, കൂടുതലായ രക്തസ്രാവം, കുഴഞ്ഞുവീഴൽ/കറക്കം, അല്ലെങ്കിൽ നിൽക്കാൻ കഴിയാത്തത് — ഉടൻ വെറ്റിനെ വിളിക്കുക.",
            "vaccination": "വാക്സിനേഷൻ സഹായം:\nമൃഗത്തിന്റെ പ്രായവും അവസാന വാക്സിനേഷൻ തീയതിയും പറയൂ.\nസാധാരണ വാക്സിനുകൾ: FMD, HS, BQ, Brucellosis.\nപ്രായം + അവസാന ഡോസ് നൽകിയാൽ എന്താണ് due എന്ന് ഞാൻ നിർദ്ദേശിക്കും.",
            "ai_infection": "സാധ്യത: ഇൻഫെക്ഷൻ / ജ്വരവുമായി ബന്ധപ്പെട്ട രോഗം.\nതാപനില, വെള്ളക്കുറവ്, ഭക്ഷണാഭിലാഷം പരിശോധിക്കുക. വെറ്റിന്റെ നിർദ്ദേശം തേടുക.",
            "ai_respiratory": "സാധ്യത: ശ്വാസകോശ രോഗം.\nശ്വാസനിരക്ക്, മൂക്കൊഴുക്ക്, ചുമ എന്നിവ പരിശോധിക്കുക. വാതായനം മെച്ചപ്പെടുത്തി വെറ്റിനെ ബന്ധപ്പെടുക.",
            "ai_digestive": "സാധ്യത: ദഹനക്കേട്.\nവെള്ളക്കുറവ് ശ്രദ്ധിക്കുക. ശുദ്ധജലം/ഇലക്ട്രോലൈറ്റ് നൽകുക; തുടർന്നാൽ വെറ്റിനെ ബന്ധപ്പെടുക.",
            "ai_injury": "സാധ്യത: പരിക്ക് / കാൽ പ്രശ്നം.\nചലനം കുറക്കുക, വീക്കം/മുറിവുകൾ പരിശോധിക്കുക, ശുദ്ധമായി സൂക്ഷിക്കുക; ഗുരുതരമെങ്കിൽ വെറ്റിനെ വിളിക്കുക.",
            "ai_unclear": "സ്ഥിതി വ്യക്തമല്ല.\nകൂടുതൽ ലക്ഷണങ്ങളും എപ്പോൾ മുതൽ എന്നും പറയൂ. വെറ്റിന്റെ പരിശോധന ശുപാർശ ചെയ്യുന്നു.",
        },
        "ta": {
            "ask_more": "அறிகுறிகளை சொல்லுங்கள் (காய்ச்சல்/இருமல்/வயிற்றுப்போக்கு/லங்கடைப்பு), உணவு சாப்பிடுகிறதா, எப்போது முதல்.\nமுடிந்தால் வெப்பநிலை மற்றும் மாட்டின் டேக் ஐடியையும் சொல்லுங்கள்.",
            "next_steps": "அடுத்த படிகள்:\n1) தொற்றுநோய் அறிகுறிகள் இருந்தால் தனிமைப்படுத்துங்கள்.\n2) சுத்தமான தண்ணீர்; வயிற்றுப்போக்கில் ORS/எலெக்ட்ரோலைட்.\n3) களத்தை சுத்தமாக வைத்து 2–4 மணி நேரத்திற்கு ஒருமுறை கண்காணிக்கவும்.\n4) அதிக காய்ச்சல், மூச்சுத்திணறல், மலத்தில் இரத்தம், அல்லது 12 மணி நேரத்துக்கும் மேலாக சாப்பிடாதால் — உடனே மருத்துவரை அணுகவும்.",
            "emergency": "இது அவசர நிலை போல உள்ளது.\nமூச்சுத்திணறல், கடுமையான வீக்கம், அதிக இரத்தம், குலுக்கல்/மயக்கம், அல்லது நிற்க முடியாத நிலை — உடனே விலங்கு மருத்துவரை அழைக்கவும்.",
            "vaccination": "தடுப்பூசி உதவி:\nமாட்டின் வயது மற்றும் கடைசி தடுப்பூசி தேதி சொல்லுங்கள்.\nபொதுவான தடுப்பூசிகள்: FMD, HS, BQ, Brucellosis.\nவயது + கடைசி டோஸ் சொன்னால் என்ன due என்று நான் சொல்வேன்.",
            "ai_infection": "சாத்தியம்: தொற்று / காய்ச்சல் தொடர்பான நோய்.\nவெப்பநிலை, தண்ணீர் குறைவு, உணவு ஆர்வம் பார்க்கவும். மருத்துவரை தொடர்பு கொள்ளவும்.",
            "ai_respiratory": "சாத்தியம்: சுவாச நோய்.\nமூச்சு வேகம், மூக்கு சளி, இருமல் பார்க்கவும். காற்றோட்டத்தை மேம்படுத்தி மருத்துவரை தொடர்பு கொள்ளவும்.",
            "ai_digestive": "சாத்தியம்: ஜீரண கோளாறு.\nநீரிழப்பு கவனிக்கவும். சுத்தமான தண்ணீர்/எலெக்ட்ரோலைட் கொடுக்கவும்; தொடர்ந்தால் மருத்துவரை அணுகவும்.",
            "ai_injury": "சாத்தியம்: காயம் / காலில் பிரச்சனை.\nஇயக்கத்தை குறைத்து, வீக்கம்/காயம் பார்க்கவும், சுத்தமாக வைத்துக் கொள்ளவும்; கடுமையானால் மருத்துவரை அணுகவும்.",
            "ai_unclear": "நிலை தெளிவாக இல்லை.\nமேலும் அறிகுறிகள் மற்றும் எப்போது தொடங்கியது என்பதை சொல்லுங்கள். மருத்துவர் பரிசோதனை பரிந்துரைக்கப்படுகிறது.",
        },
        "ur": {
            "ask_more": "علامات بتائیں (بخار/کھانسی/اسہال/لنگڑاہٹ)، بھوک کیسی ہے، اور کب سے ہے۔\nاگر ممکن ہو تو درجہ حرارت اور جانور کا ٹیگ آئی ڈی بھی بتائیں۔",
            "next_steps": "اگلے اقدامات:\n1) اگر متعدی علامات ہوں تو جانور کو الگ رکھیں۔\n2) صاف پانی دیں؛ اسہال میں ORS/الیکٹرولائٹ۔\n3) شیڈ صاف رکھیں اور ہر 2–4 گھنٹے بعد نگرانی کریں۔\n4) تیز بخار، سانس میں تکلیف، پاخانے میں خون، یا 12 گھنٹے سے زیادہ نہ کھانا — فوراً ڈاکٹر سے رابطہ کریں۔",
            "emergency": "یہ فوری/ایمرجنسی لگ رہی ہے۔\nاگر سانس لینے میں شدید مشکل، بہت زیادہ پیٹ پھولنا، زیادہ خون بہنا، دورے، یا کھڑا نہ ہو سکے — فوراً ویٹرنری ڈاکٹر کو کال کریں۔",
            "vaccination": "ویکسین کی مدد:\nجانور کی عمر اور آخری ویکسین کی تاریخ بتائیں۔\nعام ویکسین: FMD, HS, BQ, Brucellosis.\nعمر + آخری ڈوز بتانے پر میں بتاؤں گا/بتاؤں گی کیا due ہو سکتا ہے۔",
            "ai_infection": "ممکنہ انفیکشن / بخار سے متعلق بیماری۔\nدرجہ حرارت، پانی کی کمی اور بھوک چیک کریں۔ تشخیص/دوائی کے لیے ڈاکٹر سے رابطہ کریں۔",
            "ai_respiratory": "ممکنہ سانس کی بیماری۔\nسانس کی رفتار، ناک سے رطوبت، کھانسی دیکھیں۔ ہوا داری بہتر کریں اور ڈاکٹر سے رابطہ کریں۔",
            "ai_digestive": "ممکنہ ہاضمے کی خرابی۔\nڈی ہائیڈریشن پر نظر رکھیں۔ صاف پانی/الیکٹرولائٹ دیں؛ جاری رہے تو ڈاکٹر سے رابطہ کریں۔",
            "ai_injury": "ممکنہ چوٹ / ٹانگ کا مسئلہ۔\nحرکت کم کریں، سوجن/زخم دیکھیں، جگہ صاف رکھیں، اور شدید ہو تو ڈاکٹر سے رابطہ کریں۔",
            "ai_unclear": "حالت واضح نہیں۔\nمزید علامات اور کب سے ہیں بتائیں۔ ویٹرنری معائنہ تجویز ہے۔",
        },
    }

    if language == "en":
        return en.get(key, en["ask_more"])

    return translations.get(language, {}).get(key) or en.get(key, en["ask_more"])


def normalize_vet_license_number(value: str) -> str:
    value = (value or "").strip().upper()
    return "".join(ch for ch in value if ch.isalnum())


def _luhn_is_valid(digits: str) -> bool:
    if not digits or not digits.isdigit():
        return False
    total = 0
    reverse = digits[::-1]
    for i, ch in enumerate(reverse):
        n = ord(ch) - 48
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


def validate_vet_license_number(value: str) -> dict:
    """
    Non-authoritative validation (offline):
    - Normalizes value (A-Z/0-9 only)
    - Checks length + character rules
    - Optional checksum (Luhn) on digit portion to detect typos (not required)

    Returns: {normalized, format_ok, score, reasons[]}
    """
    reasons = []
    normalized = normalize_vet_license_number(value)

    if not normalized:
        return {"normalized": "", "format_ok": False, "score": 0, "reasons": ["Empty license number"]}

    if len(normalized) < 6:
        reasons.append("Too short (min 6 characters)")
    if len(normalized) > 25:
        reasons.append("Too long (max 25 characters)")

    digit_count = sum(1 for ch in normalized if ch.isdigit())
    if digit_count < 3:
        reasons.append("Should contain at least 3 digits")

    score = 100
    if any("Too short" in r or "Too long" in r for r in reasons):
        score -= 50
    if digit_count < 3:
        score -= 20

    digits = "".join(ch for ch in normalized if ch.isdigit())
    if len(digits) >= 8:
        if _luhn_is_valid(digits):
            score = min(100, score + 5)
        else:
            reasons.append("Checksum looks unusual (possible typo)")
            score -= 10

    format_ok = score >= 50 and not any("Too short" in r or "Too long" in r for r in reasons)
    score = max(0, min(100, score))

    return {"normalized": normalized, "format_ok": format_ok, "score": score, "reasons": reasons}
