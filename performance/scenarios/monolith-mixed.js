import http from "k6/http";
import { check, group, sleep } from "k6";

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";
const HEADERS = { "Content-Type": "application/json" };

export const options = {
  stages: [
    { duration: "20s", target: 10 },
    { duration: "50s", target: 10 },
    { duration: "20s", target: 0 },
  ],
  thresholds: {
    http_req_duration: ["p(95)<1400"],
    checks: ["rate>0.93"],
  },
  summaryTrendStats: ["avg", "min", "med", "p(90)", "p(95)", "p(99)"],
  setupTimeout: "120s",
};

function employeePayload() {
  const suffix = Math.random().toString(16).slice(2, 8);
  return {
    name: `Name-${suffix}`,
    lastname: `Lastname-${suffix}`,
    salary: 52000 + Math.floor(Math.random() * 18000),
    address: `Block ${Math.floor(Math.random() * 400)}`,
    in_vacation: Math.random() > 0.75,
  };
}

export function setup() {
  const employees = [];
  for (let i = 0; i < 10; i += 1) {
    const res = http.post(
      `${BASE_URL}/employees`,
      JSON.stringify(employeePayload()),
      { headers: HEADERS }
    );
    if (res.status === 201) {
      employees.push(res.json().id);
    }
  }
  return { employees };
}

export default function (data) {
  const listRes = http.get(`${BASE_URL}/employees`);
  check(listRes, {
    "list employees 200": (r) => r.status === 200,
    "list payload array": (r) => Array.isArray(r.json()),
  });

  const employees = listRes.json();
  const fallbackIds = data.employees || [];
  const pool = employees.length ? employees.map((e) => e.id) : fallbackIds;
  const targetId = pool.length
    ? pool[Math.floor(Math.random() * pool.length)]
    : null;

  if (targetId) {
    group("read employee detail", () => {
      const res = http.get(`${BASE_URL}/employees/${targetId}`);
      check(res, { "employee detail 200": (r) => r.status === 200 });
    });
  }

  group("create then update employee", () => {
    const createPayload = employeePayload();
    const createRes = http.post(
      `${BASE_URL}/employees`,
      JSON.stringify(createPayload),
      { headers: HEADERS }
    );
    check(createRes, { "employee created": (r) => r.status === 201 });

    if (createRes.status === 201) {
      const createdId = createRes.json("id");
      const updatePayload = {
        ...createPayload,
        salary: createPayload.salary + 1000,
        in_vacation: true,
      };
      const updateRes = http.put(
        `${BASE_URL}/employees/${createdId}`,
        JSON.stringify(updatePayload),
        { headers: HEADERS }
      );
      check(updateRes, { "employee updated": (r) => r.status === 200 });
    }
  });

  if (targetId) {
    group("refresh existing employee", () => {
      const payload = { ...employeePayload(), in_vacation: false };
      const updateRes = http.put(
        `${BASE_URL}/employees/${targetId}`,
        JSON.stringify(payload),
        { headers: HEADERS }
      );
      check(updateRes, {
        "existing updated": (r) => r.status === 200 || r.status === 404,
      });
    });
  }

  sleep(1);
}
