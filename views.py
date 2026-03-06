import csv
import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI

def index(request):
    return render(request,"index.html")

def analyze(request):
    if request.method=="POST":
        try:
            data=json.loads(request.body)
            player_name=data.get("player", "").lower()
            
            with open("players/data/players.csv", newline='', encoding='utf-8') as f:
                reader = list(csv.DictReader(f))
                
            # sort leaderboard by runs descending
            reader.sort(key=lambda x: int(x["runs"]), reverse=True)
            
            player_data = None
            rank = 1
            for i, row in enumerate(reader):
                if row["player"].lower() == player_name:
                    player_data = row
                    rank = i + 1
                    break
                    
            if player_data:
                return JsonResponse({
                    "player": player_data["player"].title(),
                    "matches": int(player_data["matches"]),
                    "runs": int(player_data["runs"]),
                    "strike_rate": float(player_data["strike_rate"]),
                    "wickets": int(player_data["wickets"]),
                    "rank": rank
                })
        except Exception as e:
            return JsonResponse({"error": str(e)})

    return JsonResponse({"error":"Player not found"})


def calculator(request):
    return render(request,"calculator.html")

def suggestion_view(request):
    return render(request, "suggestion.html")

def leaderboard(request):
    try:
        with open("players/data/players.csv", newline='', encoding='utf-8') as f:
            reader = list(csv.DictReader(f))
            
        # calculate impact for each player
        for player in reader:
            runs = int(player["runs"])
            wickets = int(player["wickets"])
            strike_rate = float(player["strike_rate"])
            # assuming situation = 5 as average
            situation = 5
            player["impact"] = runs * 0.4 + strike_rate * 0.2 + wickets * 15 + situation * 5
        
        # sort by impact descending
        reader.sort(key=lambda x: x["impact"], reverse=True)
        
        # get top 10
        top_players = reader[:10]
        
        leaderboard_data = []
        for i, player in enumerate(top_players, 1):
            leaderboard_data.append({
                "rank": i,
                "player": player["player"],
                "impact": round(player["impact"])
            })
        
        return JsonResponse({"leaderboard": leaderboard_data})
    except Exception as e:
        return JsonResponse({"error": str(e)})

client = OpenAI(api_key="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")


@csrf_exempt
def ai_suggestions(request):

    data = json.loads(request.body)

    prompt = f"""
    Analyze this cricket player performance and give improvement suggestions.

    Name: {data['name']}
    Runs: {data['runs']}
    Strike Rate: {data['strikeRate']}
    Wickets: {data['wickets']}
    Situation: {data['situation']}
    Impact Score: {data['impact']}

    Return JSON array with:
    title
    description
    priority
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are an expert cricket performance analyst."},
            {"role": "user", "content": prompt}
        ]
    )

    content = response.choices[0].message.content

    return JsonResponse({"suggestions": content})