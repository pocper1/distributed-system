from database import get_postgresql_connection
from .score_service import calculate_team_score, sync_scores_to_postgres
from redis import Redis
import logging
from sqlalchemy.orm import Session
from models import Team

# 設置日誌
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# def subscribe_and_sync_scores():
#     """
#     監聽 Redis 訊息，更新 Redis 並同步到 PostgreSQL
#     """
#     try:
#         pubsub = redis_conn.pubsub()
#         pubsub.subscribe("team_checkin_channel")
#         logger.info("Subscribed to Redis channel: team_checkin_channel")

#         # 持久化的 PostgreSQL 連接
#         db: Session = next(get_postgresql_connection())  # 保持一個資料庫連接

#         for message in pubsub.listen():
#             if message["type"] == "message":
#                 try:
#                     team_id = int(message["data"])
#                     logger.info(f"Received update for team {team_id}")

#                     # 計算分數
#                     score = calculate_team_score(team_id, db, redis_conn)
#                     logger.info(f"Calculated score for team {team_id}: {score}")

#                     # 更新 Redis 快取
#                     redis_conn.set(f"team:{team_id}:score", score, ex=3600)  # 設置 1 小時過期時間
#                     logger.info("Updated Redis cache for team {} with score {}".format(team_id, str(score)))

#                     # 同步到 PostgreSQL
#                     sync_scores_to_postgres(team_id, score, db)
#                     logger.info(f"Synced score for team {team_id} to PostgreSQL")

#                 except Exception as e:
#                     logger.error(f"Error processing team {team_id}: {str(e)}")

#     except Exception as e:
#         logger.error(f"Error in Redis subscription: {str(e)}")
        
# def startup_sync_scores():
#     """
#     初始化時同步所有團隊的分數
#     """
#     db = next(get_postgresql_connection())
#     initialize_team_scores(db)

# def initialize_team_scores(db: Session):
#     """
#     初始化所有團隊的分數並同步到 Redis
#     """
#     teams = db.query(Team).all()  # 獲取所有團隊
#     for team in teams:
#         initial_score = 0.0  # 初始分數設為 0
#         # 更新 Redis 快取
#         redis_conn.set(f"team:{team.id}:score", initial_score, ex=3600)  # 設置 1 小時過期時間
#         # 同步到 PostgreSQL
#         sync_scores_to_postgres(team.id, initial_score, db)
#         logger.info("Initialized score for team {} to {}".format(team.id, str(initial_score)))
