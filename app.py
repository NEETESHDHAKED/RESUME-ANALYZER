from flask import Flask, render_template, request, redirect
import json, os
import urllib.parse

app = Flask(__name__)
FILE = "blood.json"

def load():
    if os.path.exists(FILE):
        try:
            with open(FILE) as f:
                data = json.load(f)
                for i, p in enumerate(data):
                    p["id"] = i
                return data
        except: return []
    return []

def save(d):
    for p in d:
        if "id" in p: del p["id"]
    with open(FILE,"w") as f:
        json.dump(d,f)

@app.route("/")
def home():
    donors = load()
    q = request.args.get("q","")
    # q = blood group like O+, B+
    search_result = []
    if q:
        search_result = [p for p in donors if q.lower() in p['blood'].lower() or q.lower() in p['name'].lower() or q.lower() in p['village'].lower()]
    total = len(donors)
    # count groups
    groups = {}
    for d in donors:
        groups[d['blood']] = groups.get(d['blood'],0)+1
    return render_template("blood.html", donors=donors, search_result=search_result, q=q, total=total, groups=groups)

@app.route("/add", methods=["POST"])
def add():
    d = load()
    d.append({
        "name": request.form["name"],
        "blood": request.form["blood"],
        "phone": request.form["phone"],
        "village": request.form["village"],
        "age": request.form["age"],
        "last_donate": request.form.get("last_donate","Kabhi nahi")
    })
    save(d)
    return redirect("/")

@app.route("/delete/<int:id>")
def delete(id):
    d = load()
    if id < len(d): d.pop(id); save(d)
    return redirect("/")

@app.route("/donor/<int:id>")
def donor(id):
    all_d = load()
    if id >= len(all_d): return redirect("/")
    p = all_d[id]
    msg = f"Namaste {p['name']} ji 🙏 Aapka Blood Group {p['blood']} hai. Gaon me ek patient ko urgently khoon chahiye. Kya aap de sakte ho? - Ramgarh Blood Bank"
    wa_link = "https://wa.me/91" + p['phone'] + "?text=" + urllib.parse.quote(msg) if p['phone'] else "#"
    return render_template("donor.html", p=p, id=id, wa_link=wa_link)

@app.route("/emergency/<group>")
def emergency(group):
    donors = load()
    same = [p for p in donors if p['blood']==group]
    return render_template("emergency.html", group=group, same=same)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)