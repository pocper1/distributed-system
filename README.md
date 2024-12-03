# distributed-system

## Frontend
```
node -v
v16.20.2
```

```
npm -v
8.19.4
```

```
$ docker --version
Docker version 27.3.1, build ce12230
```

## Backend

## Steps
1. create cloud SQL
    在 GCP 控制台中，創建 PostgreSQL。
    配置網路訪問權限，允許 Cloud Run 或 GKE 訪問。
2. 建立 Pub/Sub 主題
    創建一個名為 score-updates 的 Pub/Sub 主題
    ```bash
    gcloud pubsub topics create score-updates
    ```
