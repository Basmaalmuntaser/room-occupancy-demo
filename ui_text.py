"""All user-facing text (English / Arabic). Both languages have exactly the same keys."""

TXT = {
    "en": dict(
        brand="Is Anyone There?",
        ai_on="AI online", ai_off="AI offline",
        tab_play="The Room", tab_lab="Sensor lab", tab_about="About",
        you="YOU", ai="AI", round="ROUND", streak="Streak",
        # play - headline per phase
        h_guess="Can you read the room?",
        s_guess="Read the sensor clues, guess how many people are inside, then see if you can beat the AI.",
        h_locked="Your guess is locked.",
        s_locked="Open the door to see who was really inside and what the AI predicted.",
        h_you="You outsmarted the AI!", h_both="A great call from both!",
        h_ai="This round goes to the AI.", h_none="The room fooled you both!",
        s_you="You matched the recorded count and the AI did not.",
        s_both="You and the AI both matched the recorded count.",
        s_ai="Good try. The next round could be yours.",
        s_none="Neither of you matched it. The recorded count was {c}.",
        scene_note="Illustration only. The AI reads the sensor values, not this picture.",
        evidence="Evidence", evidence_note="Teal tick = typical empty room",
        c_temp="Temperature", c_light="Light", c_sound="Sound level", c_co2="CO₂", c_motion="Motion",
        h_avg4="Average of 4 sensors", h_avg4v="Average of 4 sensors (volts)",
        h_motion="{n} of 2 ceiling sensors triggered",
        trend=("Rising", "Steady", "Falling"),
        motion_val=("No motion", "Motion detected"),
        details="Compare with typical rooms",
        cmp_now="This room",
        cmp_note="Each box shows the typical value (median) in the project data for that number of people. "
                 "The highlighted box is the closest to this room. These are approximate patterns, not rules.",
        d_rows=("Temperature (°C)", "Light (lux)", "Sound (V)", "CO₂ (ppm)", "CO₂ slope", "Motion (S6 / S7)"),
        d_cols=("Reading", "Sensor 1", "Sensor 2", "Sensor 3", "Sensor 4"),
        pick_q="How many people are inside?",
        lock="Lock my guess", lock_hint="Pick a number, then lock it in.",
        locked_as="Locked guess", open="Open the door", next="Next round",
        cmp_you="Your guess", cmp_ai="AI estimate", cmp_truth="Recorded count",
        prob_title="AI output: probability for each count",
        prob_note="Raw probabilities returned by the model. They are not a guarantee that the estimate is correct.",
        foot="Research/demo prototype trained on recorded data. Not a reliable system for deciding automatically "
             "whether a room is available.",
        people=lambda n: "Empty room" if n == 0 else ("1 person" if n == 1 else f"{n} people"),
        card=lambda n: "nobody" if n == 0 else ("person" if n == 1 else "people"),
        # connection / errors
        off_title="The AI could not be reached",
        off_msg="Predictions are unavailable right now. If the service was idle it can take about a minute to wake up.",
        retry="Try again", tech="Technical details", api_label="Service address",
        how_to_start="To run it locally, start the API in a separate terminal:",
        e_conn="Could not reach the prediction service. No points were given for this round.",
        e_slow="The prediction service took too long to answer. If it was idle it may still be waking up.",
        e_bad="The service rejected these readings: {d}",
        e_http="The prediction service returned an error.",
        # lab
        lab_intro_t="Try sensor readings",
        lab_intro="Pick a recorded example or adjust the readings, then see how the model estimates the number of "
                  "people. This is an experiment on recorded data, not a connection to live sensors.",
        s1="Choose a recorded example", s2="Review the readings", s3="Estimate", s4="Result",
        filt="Show examples with", filt_any="Any count", another="Try another example",
        ex_label="Example {n}", ex_rec="Recorded count for this example",
        ex_note="This is the number of people written down when the data was recorded. It is not a model prediction.",
        h_temp="Average of 4 sensors", h_light="Average of 4 sensors", h_sound="Average of 4 sensors (volts)",
        h_co2="CO₂ trend", h_motion2="of 2 ceiling sensors triggered",
        ref_empty="Empty room ≈ {v}", ref_motion="No motion ≠ empty room",
        custom="Customize sensor readings", custom_hint="Optional. Change any value to see how the estimate reacts.",
        reset="Reset to original example",
        g_temp="Temperature (°C)", g_light="Light (lux)", g_sound="Sound level (volts)", g_co2="CO₂ and motion",
        l_temp="Temperature — Sensor {i} (°C)", l_light="Light — Sensor {i} (lux)", l_sound="Sound — Sensor {i} (V)",
        l_co2="CO₂ (ppm)", l_slope="CO₂ slope", l_motion="Motion — Sensor {i}",
        help_slope="How fast CO₂ is changing. Positive means rising, negative means falling, close to 0 means steady. "
                   "It has no unit.",
        help_sound="The sensor's output voltage. It shows how loud it is, never the audio itself.",
        help_motion="Ceiling motion sensor: on means it detected motion.",
        estimate="Estimate occupancy", est_title="Estimated occupancy",
        est_edit_note="You changed the readings, so the recorded count above belongs to the original example only. "
                      "It is not the correct answer for these values.",
        est_match="Matches the recorded count of the original example.",
        est_diff="Differs from the recorded count of the original example.",
        est_rec="Recorded count (original example)",
        stale="Readings changed since the last estimate. Press “Estimate occupancy” to update the result.",
        # help / about
        help_title="Understanding sensor readings",
        help_intro="Approximate patterns (median values) from the project data. They are not fixed rules: the same CO₂ "
                   "reading can appear with different numbers of people, and this is not an explanation of any "
                   "single model estimate.",
        help_cols=("People", "CO₂ (ppm)", "Light (lux)", "Temperature (°C)", "Sound (V)"),
        help_rules=["**CO₂** tends to be higher with more people. It rises while people are present and falls slowly "
                    "after they leave.",
                    "**Light** is usually higher when people are present, but a dark room is not necessarily empty.",
                    "**Sound** is close to silent in an empty room. Two and three people sound alike.",
                    "**Motion** suggests someone is present, but no motion does not mean the room is empty."],
        about=("### What is this?\n"
               "A team project that estimates **how many people (0-3) are in a room** using sensor readings only: "
               "temperature, light, sound level, CO₂ and motion. **No cameras, no audio recordings.** "
               "The room picture in the game is an illustration; the AI never sees it.\n\n"
               "### Why?\n"
               "Meeting, study and co-working rooms are often booked but nobody shows up, or people leave early. "
               "Knowing whether a room is really used helps. This prototype only estimates the number of people; "
               "connecting it to a booking system is a possible future extension.\n\n"
               "### The model\n"
               "A tuned Logistic Regression (StandardScaler + LogisticRegression in one saved pipeline) using all 16 "
               "sensor features, trained on December 2017 data only. Data: UCI *Room Occupancy Estimation* "
               "(10,129 samples; December = training period, January = test period).\n\n"
               "### How the game is scored\n"
               "You and the AI are each compared with the **recorded count** (the number written down when the data "
               "was collected), never with each other. The AI's answer comes from the real model through the API.\n\n"
               "### Good to know\n"
               "- About 81% of the readings in the data are an empty room.\n"
               "- The model can be wrong, which is part of the game.\n"
               "- It is a research/demo prototype, not a system to decide room availability automatically."),
        splash_sub="You vs AI",
    ),
    "ar": dict(
        brand="فيها أحد؟",
        ai_on="الـ AI متصل", ai_off="الـ AI غير متصل",
        tab_play="الغرفة", tab_lab="مختبر الحساسات", tab_about="عن المشروع",
        you="أنت", ai="الـ AI", round="الجولة", streak="إصابات متتالية",
        h_guess="هل تستطيع قراءة الغرفة؟",
        s_guess="اقرأ أدلة الحساسات، وخمّن عدد من في الغرفة، ثم تحدَّ الـ AI.",
        h_locked="تم تثبيت توقّعك.",
        s_locked="افتح الباب لترى من كان في الداخل فعلًا، وبماذا توقّع الـ AI.",
        h_you="تفوّقت على الـ AI!", h_both="توقّع موفّق من الطرفين!",
        h_ai="هذه الجولة للـ AI.", h_none="الغرفة خدعتكما!",
        s_you="طابقتَ العدد المسجّل، ولم يطابقه الـ AI.",
        s_both="أنت والـ AI طابقتما العدد المسجّل.",
        s_ai="محاولة جيدة. قد تكون الجولة القادمة لك.",
        s_none="لم يطابقه أيٌّ منكما. العدد المسجّل: {c}.",
        scene_note="الرسم توضيحي فقط. يعتمد الـ AI على قراءات الحساسات، لا على هذه الصورة.",
        evidence="الأدلة", evidence_note="العلامة الفيروزية = غرفة فارغة نموذجية",
        c_temp="الحرارة", c_light="الإضاءة", c_sound="مستوى الصوت", c_co2="CO₂", c_motion="الحركة",
        h_avg4="متوسط 4 حساسات", h_avg4v="متوسط 4 حساسات (فولت)",
        h_motion="{n} من حساسَي السقف رصدا حركة",
        trend=("يرتفع", "شبه ثابت", "ينخفض"),
        motion_val=("لا توجد حركة", "تم رصد حركة"),
        details="قارن بالغرف النموذجية",
        cmp_now="هذه الغرفة",
        cmp_note="كل مربع يعرض القيمة النموذجية (الوسيط) في بيانات المشروع لهذا العدد من الأشخاص. "
                 "المربع المميَّز هو الأقرب لهذه الغرفة. هذه أنماط تقريبية وليست قواعد.",
        d_rows=("الحرارة (°C)", "الإضاءة (lux)", "الصوت (V)", "CO₂ (ppm)", "ميل CO₂", "الحركة (S6 / S7)"),
        d_cols=("القراءة", "حساس 1", "حساس 2", "حساس 3", "حساس 4"),
        pick_q="كم شخصًا في الغرفة؟",
        lock="ثبّت توقّعي", lock_hint="اختر رقمًا ثم ثبّته.",
        locked_as="التوقّع المثبَّت", open="افتح الباب", next="الجولة التالية",
        cmp_you="توقّعك", cmp_ai="توقّع الـ AI", cmp_truth="العدد المسجّل",
        prob_title="مخرجات الـ AI: احتمال كل عدد",
        prob_note="احتمالات خام يعيدها النموذج، وليست ضمانًا بأن التقدير صحيح.",
        foot="نموذج بحثي تجريبي مدرَّب على بيانات مسجّلة. ليس نظامًا موثوقًا لتحديد إتاحة الغرف تلقائيًا.",
        people=lambda n: {0: "غرفة فارغة", 1: "شخص واحد", 2: "شخصان"}.get(n, f"{n} أشخاص"),
        card=lambda n: {0: "لا أحد", 1: "شخص", 2: "شخصان"}.get(n, "أشخاص"),
        off_title="تعذّر الوصول إلى الـ AI",
        off_msg="التوقعات غير متاحة حاليًا. إذا كانت الخدمة خاملة فقد تحتاج إلى نحو دقيقة لتستيقظ.",
        retry="إعادة المحاولة", tech="تفاصيل تقنية", api_label="عنوان الخدمة",
        how_to_start="للتشغيل محليًا، شغّل الـ API في نافذة طرفية منفصلة:",
        e_conn="تعذّر الاتصال بخدمة التوقع. لم تُحتسب نقاط لهذه الجولة.",
        e_slow="استغرقت خدمة التوقع وقتًا طويلًا في الرد. إذا كانت خاملة فقد تكون ما زالت تستيقظ.",
        e_bad="رفضت الخدمة هذه القراءات: {d}",
        e_http="أعادت خدمة التوقع خطأً.",
        lab_intro_t="جرّب قراءات الحساسات",
        lab_intro="اختر مثالًا مسجّلًا أو عدّل القراءات، ثم شاهد كيف يقدّر النموذج عدد الأشخاص. هذه تجربة على بيانات "
                  "مسجّلة وليست اتصالًا بحساسات حية.",
        s1="اختيار مثال مسجّل", s2="مراجعة القراءات", s3="التقدير", s4="النتيجة",
        filt="عرض الأمثلة بعدد", filt_any="أي عدد", another="جرّب مثالًا آخر",
        ex_label="مثال {n}", ex_rec="العدد المسجّل لهذا المثال",
        ex_note="هذا هو عدد الأشخاص المدوَّن وقت تسجيل البيانات، وليس توقعًا من النموذج.",
        h_temp="متوسط 4 حساسات", h_light="متوسط 4 حساسات", h_sound="متوسط 4 حساسات (فولت)",
        h_co2="اتجاه CO₂", h_motion2="من حساسَي السقف رصدا حركة",
        ref_empty="الغرفة الفارغة ≈ {v}", ref_motion="غياب الحركة لا يعني غرفة فارغة",
        custom="تخصيص قراءات الحساسات", custom_hint="اختياري. غيّر أي قيمة لترى كيف يتغير التقدير.",
        reset="العودة إلى المثال الأصلي",
        g_temp="الحرارة (°C)", g_light="الإضاءة (lux)", g_sound="مستوى الصوت (فولت)", g_co2="CO₂ والحركة",
        l_temp="الحرارة — حساس {i} (°C)", l_light="الإضاءة — حساس {i} (lux)", l_sound="الصوت — حساس {i} (V)",
        l_co2="CO₂ (ppm)", l_slope="ميل CO₂", l_motion="الحركة — حساس {i}",
        help_slope="سرعة تغيّر CO₂. القيمة الموجبة تعني ارتفاعًا، والسالبة انخفاضًا، والقريبة من 0 ثباتًا. بلا وحدة.",
        help_sound="جهد خرج الحساس. يعبّر عن شدة الصوت وليس عن الصوت نفسه.",
        help_motion="حساس حركة في السقف: التفعيل يعني أنه رصد حركة.",
        estimate="تقدير عدد الأشخاص", est_title="العدد المقدَّر",
        est_edit_note="عدّلت القراءات، لذلك فالعدد المسجّل أعلاه يخص المثال الأصلي فقط، وليس الإجابة الصحيحة لهذه القيم.",
        est_match="يطابق العدد المسجّل في المثال الأصلي.",
        est_diff="يختلف عن العدد المسجّل في المثال الأصلي.",
        est_rec="العدد المسجّل (المثال الأصلي)",
        stale="تغيّرت القراءات منذ آخر تقدير. اضغط «تقدير عدد الأشخاص» لتحديث النتيجة.",
        help_title="فهم قراءات الحساسات",
        help_intro="أنماط تقريبية (قيم وسيطة) من بيانات المشروع. ليست قواعد ثابتة: قد تظهر نفس قراءة CO₂ مع أعداد مختلفة "
                   "من الأشخاص، وهذا ليس تفسيرًا لتقدير النموذج في حالة بعينها.",
        help_cols=("الأشخاص", "CO₂ (ppm)", "الإضاءة (lux)", "الحرارة (°C)", "الصوت (V)"),
        help_rules=["**CO₂** يميل إلى الارتفاع مع زيادة عدد الأشخاص. يرتفع أثناء وجودهم وينخفض ببطء بعد مغادرتهم.",
                    "**الإضاءة** تكون عادةً أعلى مع وجود الأشخاص، لكن الغرفة المظلمة ليست بالضرورة فارغة.",
                    "**الصوت** شبه صامت في الغرفة الفارغة. صوت شخصين وثلاثة أشخاص متقارب.",
                    "**الحركة** تدل على وجود شخص، لكن غيابها لا يعني أن الغرفة فارغة."],
        about=("### ما هذا المشروع؟\n"
               "مشروع فريق يقدّر **عدد الأشخاص (0-3) داخل الغرفة** باستخدام قراءات الحساسات فقط: "
               "الحرارة والإضاءة ومستوى الصوت وCO₂ والحركة. **بدون كاميرات وبدون تسجيل صوتي.** "
               "صورة الغرفة في اللعبة رسم توضيحي، ولا يراها الـ AI.\n\n"
               "### لماذا؟\n"
               "غرف الاجتماعات والمذاكرة والعمل المشترك كثيرًا ما تكون محجوزة دون حضور، أو يغادرها أصحابها مبكرًا. "
               "ومعرفة ما إذا كانت الغرفة مستخدمة فعلًا مفيدة. يقدّر هذا النموذج عدد الأشخاص فقط، "
               "وربطه بنظام حجوزات توسّع مستقبلي محتمل.\n\n"
               "### النموذج\n"
               "Logistic Regression مضبوط (StandardScaler + LogisticRegression داخل Pipeline واحد محفوظ) يستخدم كل الـ 16 "
               "Feature، ومدرَّب على بيانات ديسمبر 2017 فقط. البيانات: UCI *Room Occupancy Estimation* "
               "(10,129 عينة؛ ديسمبر = فترة التدريب، يناير = فترة الاختبار).\n\n"
               "### كيف تُحسب النقاط؟\n"
               "يُقارَن توقّعك وتوقّع الـ AI كلٌّ على حدة مع **العدد المسجّل** (المدوَّن وقت جمع البيانات)، لا مع بعضهما. "
               "وإجابة الـ AI تأتي من النموذج الحقيقي عبر الـ API.\n\n"
               "### للعلم\n"
               "- نحو 81% من القراءات في البيانات تمثل غرفة فارغة.\n"
               "- قد يخطئ النموذج، وهذا جزء من اللعبة.\n"
               "- نموذج بحثي تجريبي، وليس نظامًا لتحديد إتاحة الغرف تلقائيًا."),
        splash_sub="أنت ضد الذكاء الاصطناعي",
    ),
}
