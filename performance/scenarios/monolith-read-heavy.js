import http from "k6/http";
import { check, group, sleep } from "k6";

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";
const HEADERS = { "Content-Type": "application/json" };

export const options = {
  stages: [
    { duration: "20s", target: 8 },
    { duration: "50s", target: 8 },
    { duration: "20s", target: 0 },
  ],
  thresholds: {
    http_req_duration: ["p(95)<1200"],
    checks: ["rate>0.95"],
  },
  summaryTrendStats: ["avg", "min", "med", "p(90)", "p(95)", "p(99)"],
  setupTimeout: "120s",
};

function employeePayload() {
  const suffix = Math.random().toString(16).slice(2, 8);
  return {
    name: `Name-${suffix}`,
    lastname: `Lastname-${suffix}`,
    salary: 50000 + Math.floor(Math.random() * 15000),
    address: `Avenue ${Math.floor(Math.random() * 300)}`,
    in_vacation: Math.random() > 0.85,
  };
}

export function setup() {
  const employees = [];
  for (let i = 0; i < 12; i += 1) {
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
  group("list employees", () => {
    const res = http.get(`${BASE_URL}/employees`);
    check(res, {
      "list employees 200": (r) => r.status === 200,
      "list payload array": (r) => Array.isArray(r.json()),
    });
  });

  if (data.employees.length) {
    const randomId =
      data.employees[Math.floor(Math.random() * data.employees.length)];
    group("get employee detail", () => {
      const res = http.get(`${BASE_URL}/employees/${randomId}`);
      check(res, {
        "get employee 200": (r) => r.status === 200,
        "has id": (r) => r.json("id") === randomId,
      });
    });
  }

  // light think-time to mimic user pacing
  sleep(1);
}
