import http from "k6/http";
import { check, sleep } from "k6";

// 配置選項
export let options = {
    setupTimeout: "10m",
    scenarios: {
        create_entities: {
            executor: "ramping-arrival-rate",
            startRate: 1,
            timeUnit: "1s",
            preAllocatedVUs: 50,
            maxVUs: 200,
            stages: [
                { target: 50, duration: "1m" },
                { target: 100, duration: "2m" },
                { target: 200, duration: "3m" },
            ],
        },
    },
};

const BASE_URL = "http://localhost/api";
const USERS_COUNT = 1000;
const TEAMS_COUNT = 2000;

// 創建用戶
function createUsers() {
    let userIds = [];
    for (let i = 0; i < USERS_COUNT; i++) {
        let res = http.post(
            `${BASE_URL}/user/register`,
            JSON.stringify({
                username: `user_${i}`,
                password: "password123",
                email: `user_${i}@example.com`,
            }),
            { headers: { "Content-Type": "application/json" } }
        );

        check(res, {
            "User created successfully": r => r.status === 200,
        });

        let userId = res.json().user_id;
        if (userId) {
            userIds.push(userId);
        } else {
            console.error(`Failed to create user: ${res.body}`);
        }

        sleep(0.1); // 模擬延遲
    }
    return userIds;
}

// 創建隊伍並讓用戶加入
function createTeamsAndJoinUsers(eventId, userIds) {
    let teamIds = [];
    for (let i = 0; i < TEAMS_COUNT; i++) {
        // 創建隊伍
        let res = http.post(
            `${BASE_URL}/event/${eventId}/team/create`,
            JSON.stringify({
                name: `team_${i}`,
                description: `Team number ${i}`,
            }),
            { headers: { "Content-Type": "application/json" } }
        );

        check(res, {
            "Team created successfully": r => r.status === 200,
        });

        let teamId = res.json().team_id;
        if (teamId) {
            teamIds.push(teamId);

            // 隨機用戶加入隊伍
            const randomUserId = userIds[Math.floor(Math.random() * userIds.length)];
            let joinRes = http.post(`${BASE_URL}/event/${eventId}/team/${teamId}/join`, JSON.stringify({ user_id: randomUserId }), { headers: { "Content-Type": "application/json" } });

            check(joinRes, {
                "User joined team successfully": r => r.status === 200,
                "User already a member": r => r.status === 400,
            });

            console.log(`User ${randomUserId} joined Team ${teamId}`);
        } else {
            console.error(`Failed to create team: ${res.body}`);
        }

        sleep(0.1); // 模擬延遲
    }
    return teamIds;
}

// 初始化階段
export function setup() {
    // 創建活動
    let eventRes = http.post(
        `${BASE_URL}/event/create`,
        JSON.stringify({
            name: `Event_${Date.now()}`,
            description: "Test Event",
            start_time: new Date().toISOString(),
            end_time: new Date(Date.now() + 3600000).toISOString(),
        }),
        { headers: { "Content-Type": "application/json" } }
    );

    check(eventRes, {
        "Event created successfully": r => r.status === 200,
    });

    let eventId = eventRes.json().event_id;
    if (!eventId) {
        throw new Error("Failed to create event.");
    }

    console.log(`Event created with ID: ${eventId}`);

    // 創建用戶和隊伍
    const userIds = createUsers();
    const teamIds = createTeamsAndJoinUsers(eventId, userIds);

    return { eventId, userIds, teamIds };
}

// 主函數：模擬執行任務
export default function (data) {
    const { eventId, userIds, teamIds } = data;

    // 隨機選擇一個用戶和隊伍進行操作（例如提交數據或其他測試場景）
    const randomUserId = userIds[Math.floor(Math.random() * userIds.length)];
    const randomTeamId = teamIds[Math.floor(Math.random() * teamIds.length)];

    // 模擬操作，例如用戶提交文件到隊伍
    let res = http.post(
        `${BASE_URL}/event/${eventId}/teams/join`,
        JSON.stringify({
            user_id: randomUserId,
            team_id: randomTeamId,
        }),
        { headers: { "Content-Type": "application/json" } }
    );

    check(res, {
        "Submission successful": r => r.status === 200,
    });

    sleep(1); // 模擬延遲
}
