from flask import Flask, render_template, request, redirect, url_for, flash
from weather import get_weather, WeatherError
from storage import load_data, save_data
from weather import describe_code, activity_tip

app.jinja_env.globals['weather_code'] = describe_code
app.jinja_env.globals['activity_tip'] = activity_tip

app = Flask(__name__)
app.secret_key = "change-this-secret-key-before-deployment"


@app.route("/", methods=["GET", "POST"])
def index():
    data = load_data()
    city = request.args.get("city", "").strip()
    weather = None
    error = None

    if request.method == "POST":
        action = request.form.get("action", "")
        if action == "save_city":
            new_city = request.form.get("city", "").strip()
            if not new_city or len(new_city) > 100:
                flash("Enter a valid city name (1–100 characters).", "error")
            elif new_city.casefold() not in [c.casefold() for c in data["saved_cities"]]:
                data["saved_cities"].append(new_city)
                save_data(data)
                flash(f"{new_city} saved.", "success")
            return redirect(url_for("index", city=new_city))
        elif action == "delete_city":
            target = request.form.get("city", "")
            data["saved_cities"] = [c for c in data["saved_cities"] if c != target]
            save_data(data)
            flash(f"{target} removed from saved locations.", "success")
            return redirect(url_for("index"))
        elif action == "save_note":
            note_city = request.form.get("city", "").strip()
            note = request.form.get("note", "").strip()
            if not note_city or not note or len(note) > 1000:
                flash("Choose a city and enter a note up to 1000 characters.", "error")
            else:
                data["notes"].insert(0, {"city": note_city, "note": note})
                data["notes"] = data["notes"][:100]
                save_data(data)
                flash("Activity note saved.", "success")
            return redirect(url_for("index", city=note_city))
        elif action == "delete_note":
            try:
                idx = int(request.form.get("index", "-1"))
                if 0 <= idx < len(data["notes"]):
                    data["notes"].pop(idx)
                    save_data(data)
                    flash("Note deleted.", "success")
            except ValueError:
                flash("Invalid note selection.", "error")
            return redirect(url_for("index"))

    if city:
        if len(city) > 100:
            error = "City name is too long."
        else:
            try:
                weather = get_weather(city)
            except WeatherError as exc:
                error = str(exc)

    return render_template("index.html", city=city, weather=weather, error=error, data=data)


if __name__ == "__main__":
    app.run(debug=True)
