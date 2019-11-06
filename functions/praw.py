from datetime import datetime

def extract_data(submission):
    return {
        "id": submission.id,
        "title": submission.title,
        "author": str(submission.author),
        "timestamp": submission.created_utc,
        "datetime": datetime.fromtimestamp(submission.created_utc).isoformat(),
        "year": datetime.fromtimestamp(submission.created_utc).year,
        "month": datetime.fromtimestamp(submission.created_utc).month,
        "day": datetime.fromtimestamp(submission.created_utc).day,
        "hour": datetime.fromtimestamp(submission.created_utc).hour,
        "minute": datetime.fromtimestamp(submission.created_utc).minute,
        "media": submission.url,
        "upvote_ratio": submission.upvote_ratio,
        "upvotes": submission.score,
        "downvotes": round(submission.score / submission.upvote_ratio) - submission.score,
        "nsfw": submission.over_18,
        "num_comments": submission.num_comments
    }