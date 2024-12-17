from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from redis import Redis
from database import get_redis_connection
from models import Checkin, User, user_teams, Score
from datetime import datetime, timedelta
import time

# 參數設定
ALPHA = 0.1  # 時間差權重調整因子
BETA = 2    # 新會員數量權重調整因子

redis_conn = get_redis_connection()

def calculate_team_score(team_id: int, db: Session, redis_conn: Redis):
    """
    計算指定團隊的分數
    """
    
    checkin_members = db.query(Checkin.user_id).filter(Checkin.team_id == team_id).all()
    user_ids = [c[0] for c in checkin_members]

    # 計算每個 user_id 的權重 (T)
    user_weights = {}
    for user_id in user_ids:
        # 計算該成員所屬的隊伍數量
        team_count = db.query(func.count(user_teams.c.team_id)).filter(user_teams.c.user_id == user_id).scalar()
        user_weights[user_id] = 1 / team_count

    # 計算總權重 T
    total_weight = sum(user_weights[user_id] for user_id in user_ids)

    # 計算時間差 (S)
    checkins = db.query(Checkin.created_at).filter(Checkin.team_id == team_id).all()
    if len(checkins) < 2:
        time_difference = 0  # 若不足 2 人打卡，時間差設為 0
    else:
        times = [c[0] for c in checkins]
        time_difference = (max(times) - min(times)).seconds

    # 計算新會員數量 (N)
    one_week_ago = datetime.utcnow() - timedelta(weeks=1)
    new_members = db.query(User.id).join(user_teams, User.id == user_teams.c.user_id).filter(
        user_teams.c.team_id == team_id,
        User.created_at >= one_week_ago
    ).count()

    # 從 Redis 獲取當前的分數並計算新的分數
    current_score = redis_conn.get(f"team:{team_id}:score")
    if current_score is None:
        current_score = 0  # 如果 Redis 中沒有分數，則設定為 0
    else:
        current_score = float(current_score)  # 直接轉換為 float，無需 decode

    # 計算新的分數
    score = total_weight / (ALPHA * (time_difference + 1)) + BETA * new_members
    score = round(score, 0)  # 四捨五入到整數
    new_total_score = current_score + score

    # 印出計算公式
    print(f"Team {team_id} score calculation: 人數{total_weight} / ({ALPHA} * ({time_difference} + 1)) + {BETA} * {new_members} = {score}")
    print(f"Previous score: {current_score}, New score: {new_total_score}")

    # 更新 Redis 快取
    redis_conn.set(f"team:{team_id}:score", new_total_score, ex=3600)  # 設置 1 小時過期時間

    # 同步到 PostgreSQL
    sync_scores_to_postgres(team_id, new_total_score, db)
    
    # 返回最終累積的分數
    return round(new_total_score, 0)

def sync_scores_to_postgres(team_id: int, score: float, db: Session):
    """
    將 Redis 中的分數同步回 PostgreSQL
    """
    try:
        # 更新 PostgreSQL
        score_entry = db.query(Score).filter(Score.team_id == team_id).first()
        if score_entry:
            score_entry.score = score
            score_entry.updated_at = time.strftime('%Y-%m-%d %H:%M:%S')
        else:
            new_score = Score(team_id=team_id, score=score)
            db.add(new_score)
        db.commit()
        print(f"Team {team_id} score synchronized to PostgreSQL: {score}")
    except Exception as e:
        print(f"Failed to synchronize score for team {team_id}: {e}")
