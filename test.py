import os, sqlite3, random
from datetime import date
from flask import Flask, request, render_template_string, redirect, url_for, session, flash

app=Flask(__name__)
app.secret_key=os.environ.get("SECRET_KEY","change-this-secret-before-deploy")
DB=os.environ.get("DB_PATH","site.db")
ADSENSE_CLIENT=os.environ.get("ADSENSE_CLIENT","")
ADSENSE_SLOT=os.environ.get("ADSENSE_SLOT","")

Q=[
("ما عاصمة اليابان؟",["بكين","طوكيو","سيول","بانكوك"],1,"جغرافيا","طوكيو عاصمة اليابان."),
("كم ضلعاً للشكل السداسي؟",["5","6","7","8"],1,"علوم","الشكل السداسي له ستة أضلاع."),
("ما الكوكب الأحمر؟",["الزهرة","المريخ","زحل","عطارد"],1,"علوم","المريخ يبدو أحمر بسبب أكاسيد الحديد."),
("ما أكبر محيط؟",["الأطلسي","الهندي","الهادئ","المتجمد"],2,"جغرافيا","المحيط الهادئ هو الأكبر."),
("كم دقيقة في ساعتين ونصف؟",["120","130","150","180"],2,"رياضيات","ساعتان ونصف تساوي 150 دقيقة."),
("ما لغة تنسيق صفحات الويب؟",["HTML","CSS","SQL","Python"],1,"تقنية","CSS مسؤولة عن تنسيق صفحات الويب."),
("ما الغاز الذي تمتصه النباتات؟",["الأكسجين","النيتروجين","ثاني أكسيد الكربون","الهيدروجين"],2,"علوم","تمتص النباتات ثاني أكسيد الكربون."),
("كم يوماً في السنة الكبيسة؟",["364","365","366","367"],2,"معلومات عامة","السنة الكبيسة 366 يوماً."),
("من مؤلف البؤساء؟",["فيكتور هوغو","تولستوي","نجيب محفوظ","شكسبير"],0,"ثقافة","مؤلفها فيكتور هوغو."),
("ما أسرع حيوان بري؟",["الأسد","الفهد الصياد","الحصان","الغزال"],1,"طبيعة","الفهد الصياد أسرع حيوان بري."),
("ما ناتج 9 × 8؟",["64","70","72","81"],2,"رياضيات","الناتج 72."),
("في أي قارة تقع البرازيل؟",["أفريقيا","آسيا","أمريكا الجنوبية","أوروبا"],2,"جغرافيا","تقع البرازيل في أمريكا الجنوبية."),
("ما وحدة قياس التيار الكهربائي؟",["الفولت","الأمبير","الواط","الأوم"],1,"علوم","تقاس شدة التيار بالأمبير."),
("ما العملية التي تصنع بها النباتات غذاءها؟",["التبخر","البناء الضوئي","التكاثف","التجمد"],1,"علوم","تصنع النباتات غذاءها بالبناء الضوئي."),
("كم عدد ألوان قوس قزح التقليدية؟",["5","6","7","8"],2,"معلومات عامة","الألوان التقليدية سبعة.")
]

STYLE="""
*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 80% 0,#1c3153,transparent 38%),#091020;color:#f5f7ff;font-family:Tahoma,Arial;line-height:1.8}
.wrap{width:min(1000px,92%);margin:auto}header{border-bottom:1px solid #293a58;padding:18px 0}.nav{display:flex;justify-content:space-between;gap:15px;flex-wrap:wrap;align-items:center}.brand{font-size:24px;font-weight:bold;color:#75f0bd}a{color:inherit;text-decoration:none}nav{display:flex;gap:16px;color:#aab8d1;font-size:14px}
.hero{text-align:center;padding:55px 10px 25px}.tag{color:#75f0bd;border:1px solid #39765f;border-radius:30px;padding:5px 13px}.hero h1{font-size:clamp(30px,5vw,48px);line-height:1.3}.muted{color:#aab8d1}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;margin:25px 0 40px}.card,.box{background:#14213a;border:1px solid #2b3c5b;border-radius:18px;padding:22px;box-shadow:0 12px 35px #0003}.card:hover{border-color:#75b7ff;transform:translateY(-3px)}.emoji{font-size:36px}.btn,button{display:inline-block;border:0;border-radius:11px;padding:11px 18px;background:linear-gradient(90deg,#75f0bd,#75b7ff);color:#071321;font-weight:bold;cursor:pointer;margin-top:8px}
.box{max-width:760px;margin:35px auto}.question{font-size:22px;font-weight:bold}.option{display:block;background:#0b1528;border:1px solid #304363;border-radius:11px;padding:10px 14px;margin:9px 0;cursor:pointer}.option:hover{border-color:#75b7ff}.ad{min-height:90px;border:1px dashed #405574;border-radius:13px;margin:25px auto;display:flex;justify-content:center;align-items:center;text-align:center;color:#8193b1;padding:12px}.result{background:#0b1528;border:1px solid #304363;border-radius:12px;padding:14px;margin:12px 0}.flash{background:#285344;padding:10px;border-radius:10px}footer{border-top:1px solid #293a58;color:#aab8d1;padding:25px 0;margin-top:40px;font-size:13px}
"""
BASE="""<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="تحديات وأسئلة وألعاب ذهنية مجانية"><title>{{title}} | تحدي اليوم</title><style>"""+STYLE+"""</style>{% if client %}<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={{client}}" crossorigin="anonymous"></script>{% endif %}</head><body><header><div class="wrap nav"><a class="brand" href="/">⚡ تحدي اليوم</a><nav><a href="/">الرئيسية</a><a href="/about">عن الموقع</a><a href="/privacy">الخصوصية</a></nav></div></header><main class="wrap">{% with m=get_flashed_messages() %}{% for x in m %}<p class="flash">{{x}}</p>{% endfor %}{% endwith %}{{content|safe}}<div class="ad">{% if client and slot %}<ins class="adsbygoogle" style="display:block" data-ad-client="{{client}}" data-ad-slot="{{slot}}" data-ad-format="auto" data-full-width-responsive="true"></ins><script>(adsbygoogle=window.adsbygoogle||[]).push({});</script>{% else %}مساحة إعلانية تجريبية — فعّلها ببيانات حساب إعلاني معتمد بعد القبول.{% endif %}</div></main><footer><div class="wrap">© {{year}} تحدي اليوم — العب وتعلّم وشارك نتيجتك.</div></footer></body></html>"""

def page(title,content):
    return render_template_string(BASE,title=title,content=content,year=date.today().year,client=ADSENSE_CLIENT,slot=ADSENSE_SLOT)
def init():
    with sqlite3.connect(DB) as c:
        c.execute("CREATE TABLE IF NOT EXISTS scores(id INTEGER PRIMARY KEY, player TEXT, score INTEGER, total INTEGER, created TEXT)")
init()

@app.route("/")
def home():
    c="""<section class='hero'><span class='tag'>مجاني • ممتع • تحديات قصيرة</span><h1>اختبر ذكاءك في <span style='color:#75f0bd'>تحدي اليوم</span></h1><p class='muted'>جاوب على أسئلة متنوعة، اختبر سرعتك، ونافس أصحابك.</p></section><section class='grid'><a class='card' href='/quiz'><div class='emoji'>🧠</div><h2>اختبار معلومات عامة</h2><p class='muted'>10 أسئلة متنوعة واعرف نتيجتك.</p><span class='btn'>ابدأ التحدي</span></a><a class='card' href='/math'><div class='emoji'>➗</div><h2>الحساب السريع</h2><p class='muted'>حل عمليات حسابية عشوائية.</p><span class='btn'>العب الآن</span></a><a class='card' href='/scores'><div class='emoji'>🏆</div><h2>لوحة المتصدرين</h2><p class='muted'>شاهد أفضل النتائج.</p><span class='btn'>عرض النتائج</span></a></section><div class='box'><h2>✨ تحدَّ أصدقاءك</h2><p>شارك رابط الموقع مع أصدقائك واعرفوا من يحقق أعلى نتيجة.</p></div>"""
    return page("الرئيسية",c)

@app.route("/quiz",methods=["GET","POST"])
def quiz():
    if request.method=="POST":
        ids=session.get("ids")
        if not ids: return redirect(url_for("quiz"))
        score=0; review=[]
        for n,i in enumerate(ids):
            q=Q[i]
            try: chosen=int(request.form.get("q"+str(n),"-1"))
            except ValueError: chosen=-1
            good=chosen==q[2]; score+=good
            review.append((q[0],q[1][q[2]],good,q[4]))
        name=(request.form.get("name") or "زائر").strip()[:24] or "زائر"
        with sqlite3.connect(DB) as c: c.execute("INSERT INTO scores(player,score,total,created) VALUES(?,?,?,?)",(name,score,len(ids),date.today().isoformat()))
        session.pop("ids",None)
        html=f"<div class='box'><h1>نتيجتك {score} من {len(ids)} 🎉</h1><p>{'ممتاز! أداء رائع.' if score>=8 else 'أحسنت، حاول مرة أخرى لتحسن نتيجتك.'}</p><h3>مراجعة الإجابات</h3>"
        for question,answer,good,why in review: html+=f"<div class='result'><b>{'✅' if good else '❌'} {question}</b><p>الإجابة: {answer}</p><small>{why}</small></div>"
        html+="<a class='btn' href='/quiz'>اختبار جديد</a> <a class='btn' href='/scores'>المتصدرون</a></div>"
        return page("نتيجتك",html)
    ids=random.sample(range(len(Q)),10); session["ids"]=ids
    html="<div class='box'><h1>🧠 اختبار المعلومات العامة</h1><p class='muted'>10 أسئلة — اختر إجابة واحدة لكل سؤال.</p><form method='post'><label>اسمك (اختياري)</label><input name='name' maxlength='24' placeholder='اسم أو لقب' style='padding:12px;width:100%;border-radius:9px'>"
    for n,i in enumerate(ids):
        q=Q[i]; html+=f"<div class='result'><small>السؤال {n+1} • {q[3]}</small><p class='question'>{q[0]}</p>"
        for k,opt in enumerate(q[1]): html+=f"<label class='option'><input type='radio' name='q{n}' value='{k}' required> {opt}</label>"
        html+="</div>"
    html+="<button>اعرض نتيجتي</button></form></div>"
    return page("اختبار المعلومات",html)

@app.route("/math",methods=["GET","POST"])
def math():
    if request.method=="POST":
        try:
            a,b,op,ans=int(request.form["a"]),int(request.form["b"]),request.form["op"],int(request.form["ans"])
            val=a+b if op=="+" else a-b if op=="-" else a*b
            msg="إجابة صحيحة! 🎉" if ans==val else f"ليست صحيحة. الإجابة هي {val}."
            return page("النتيجة",f"<div class='box'><h1>{msg}</h1><a class='btn' href='/math'>سؤال جديد</a></div>")
        except (ValueError,KeyError): flash("اكتب إجابة رقمية."); return redirect(url_for("math"))
    a,b=random.randint(2,20),random.randint(2,20); op=random.choice(["+","-","*"]); sym="×" if op=="*" else op
    return page("الحساب السريع",f"<div class='box'><h1>➗ تحدي الحساب السريع</h1><p class='question' style='font-size:40px;text-align:center'>{a} {sym} {b} = ؟</p><form method='post'><input type='hidden' name='a' value='{a}'><input type='hidden' name='b' value='{b}'><input type='hidden' name='op' value='{op}'><label>إجابتك</label><input type='number' name='ans' required style='padding:12px;width:100%'><button>تحقق</button></form></div>")

@app.route("/scores")
def scores():
    with sqlite3.connect(DB) as c: rows=c.execute("SELECT player,score,total,created FROM scores ORDER BY score DESC,id DESC LIMIT 20").fetchall()
    html="<div class='box'><h1>🏆 لوحة المتصدرين</h1>"
    if rows:
        html+="<table style='width:100%;text-align:right'><tr><th>الاسم</th><th>النتيجة</th><th>التاريخ</th></tr>"
        for r in rows: html+=f"<tr><td>{r[0]}</td><td>{r[1]}/{r[2]}</td><td>{r[3]}</td></tr>"
        html+="</table>"
    else: html+="<p class='muted'>لا توجد نتائج حتى الآن. كن أول المتصدرين!</p>"
    html+="<p><a class='btn' href='/quiz'>ابدأ الاختبار</a></p></div>"
    return page("المتصدرون",html)

@app.route("/about")
def about(): return page("عن الموقع","<div class='box'><h1>عن تحدي اليوم</h1><p>منصة ترفيهية تعليمية مجانية تقدم اختبارات معلومات عامة وألعاباً ذهنية بسيطة.</p><p>أضف بريد تواصل حقيقياً قبل نشر الموقع.</p></div>")
@app.route("/privacy")
def privacy(): return page("الخصوصية","<div class='box'><h1>سياسة الخصوصية</h1><p>قد نحفظ الاسم الذي تدخله ونتيجة الاختبار وتاريخها لعرض لوحة المتصدرين. لا تكتب معلومات شخصية حساسة.</p><p>قد تستخدم خدمات الإعلانات الخارجية ملفات تعريف الارتباط أو تقنيات مشابهة عند تفعيلها. حدّث هذه السياسة حسب الخدمات الفعلية، وأضف آلية موافقة على ملفات الارتباط حيث يلزم.</p></div>")
if __name__=="__main__": app.run(host="0.0.0.0",port=int(os.environ.get("PORT",5000)),debug=False)