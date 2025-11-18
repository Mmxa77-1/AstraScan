def prioritize(scores, top_n=20):
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
