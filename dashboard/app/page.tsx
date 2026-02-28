"use client";

import { useEffect, useState } from "react";

const HOURS_MONTH = 160;

export default function Dashboard() {
  const [now, setNow] = useState(new Date());
  const [lang, setLang] = useState<"ru" | "en">(() => {
    if (typeof window !== "undefined") {
      return (localStorage.getItem("dashboard-lang") as "ru" | "en") || "ru";
    }
    return "ru";
  });
  const [salary, setSalary] = useState(120000);

  useEffect(() => {
    const t = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    if (typeof window !== "undefined") {
      localStorage.setItem("dashboard-lang", lang);
    }
  }, [lang]);

  const start = new Date(now);
  start.setHours(0, 0, 0, 0);
  const end = new Date(now);
  end.setHours(23, 59, 59, 999);
  const dayProgress = (now.getTime() - start.getTime()) / (end.getTime() - start.getTime());
  const percent = Math.round(dayProgress * 100);

  const endOfDay = new Date(now);
  endOfDay.setHours(23, 59, 0, 0);
  const minsLeft = Math.max(0, Math.round((endOfDay.getTime() - now.getTime()) / 60000));
  const hoursLeft = Math.floor(minsLeft / 60);
  const minsLeftOnly = minsLeft % 60;

  const phase = now.getHours() >= 0 && now.getHours() < 6 ? 0
    : now.getHours() < 12 ? 1
    : now.getHours() < 18 ? 2 : 3;

  const perSec = salary > 0 ? (salary / HOURS_MONTH) / 3600 : 0;
  const [burnStart, setBurnStart] = useState(() => Date.now());
  const burnAmount = perSec * ((Date.now() - burnStart) / 1000);

  useEffect(() => {
    setBurnStart(Date.now());
  }, [salary]);

  const i18n = {
    ru: {
      title: "Прогресс дня",
      dayPassed: "дня прошло",
      left: "Осталось",
      phase: "Сейчас",
      burn: "Пока смотришь",
      night: "Ночь",
      morning: "Утро",
      afternoon: "День",
      evening: "Вечер",
      salary: "Зарплата/мес",
      hrs: "ч",
      min: "мин",
    },
    en: {
      title: "Day Progress",
      dayPassed: "of day passed",
      left: "Left today",
      phase: "Now",
      burn: "While viewing",
      night: "Night",
      morning: "Morning",
      afternoon: "Afternoon",
      evening: "Evening",
      salary: "Salary/mo",
      hrs: "h",
      min: "min",
    },
  };

  const t = i18n[lang];
  const phaseNames = [t.night, t.morning, t.afternoon, t.evening];
  const currency = lang === "ru" ? "₽" : "$";

  const format = (n: number) => {
    if (n >= 1000) return Math.round(n).toLocaleString(lang === "ru" ? "ru-RU" : "en-US");
    if (n >= 1) return n.toFixed(1);
    if (n >= 0.01) return n.toFixed(2);
    return n.toFixed(3);
  };

  const circumference = 2 * Math.PI * 90;
  const strokeOffset = circumference - dayProgress * circumference;

  return (
    <div className="relative min-h-screen overflow-x-hidden">
      {/* Background */}
      <div
        className="fixed inset-0 -z-10"
        style={{
          background: `
            radial-gradient(ellipse 120% 80% at 50% 20%, rgba(249, 115, 22, 0.18) 0%, transparent 50%),
            radial-gradient(ellipse 100% 100% at 70% 80%, rgba(236, 72, 153, 0.1) 0%, transparent 45%),
            linear-gradient(180deg, #1a1d2e 0%, #141620 40%, #0d0e14 100%)
          `,
        }}
      />

      {/* Mountain silhouettes */}
      <div
        className="fixed bottom-0 left-0 right-0 h-[45%] -z-[1] opacity-20"
        style={{
          background: `
            linear-gradient(165deg, transparent 50%, #1a1c28 50.5%) 0% 100% / 33% 60% no-repeat,
            linear-gradient(150deg, transparent 45%, #22242f 45.5%) 20% 100% / 40% 75% no-repeat,
            linear-gradient(160deg, transparent 55%, #1a1c28 55.5%) 60% 100% / 35% 55% no-repeat,
            linear-gradient(155deg, transparent 50%, #22242f 50.5%) 85% 100% / 30% 65% no-repeat
          `,
        }}
      />

      <div className="relative z-10 max-w-2xl mx-auto px-4 py-6 pb-12">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-xl font-bold bg-gradient-to-r from-orange-400 to-pink-500 bg-clip-text text-transparent">
            {t.title}
          </h1>
          <div
            className="flex gap-1 rounded-xl p-1"
            style={{
              background: "var(--surface)",
              boxShadow: "var(--shadow-soft)",
            }}
          >
            {(["ru", "en"] as const).map((l) => (
              <button
                key={l}
                onClick={() => setLang(l)}
                className={`px-3 py-1.5 rounded-lg text-sm font-semibold transition-all ${
                  lang === l
                    ? "bg-gradient-to-r from-orange-500 to-pink-500 text-white shadow-lg shadow-orange-500/20"
                    : "text-zinc-500 hover:text-zinc-300"
                }`}
              >
                {l.toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        {/* Main grid */}
        <div className="grid gap-4 grid-cols-1 md:grid-cols-2">
          {/* Circular progress + time */}
          <div
            className="rounded-2xl p-6 flex flex-col items-center"
            style={{
              background: "var(--surface)",
              boxShadow: "var(--shadow-soft)",
              border: "1px solid rgba(255,255,255,0.03)",
            }}
          >
            <div className="relative w-44 h-44 mb-4">
              <svg className="w-full h-full -rotate-90" viewBox="0 0 200 200">
                <circle
                  cx="100"
                  cy="100"
                  r="90"
                  fill="none"
                  stroke="var(--border)"
                  strokeWidth="10"
                />
                <circle
                  cx="100"
                  cy="100"
                  r="90"
                  fill="none"
                  stroke="url(#grad)"
                  strokeWidth="10"
                  strokeLinecap="round"
                  strokeDasharray={circumference}
                  strokeDashoffset={strokeOffset}
                  className="transition-all duration-500"
                />
                <defs>
                  <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#f97316" />
                    <stop offset="100%" stopColor="#ec4899" />
                  </linearGradient>
                </defs>
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-3xl font-bold bg-gradient-to-r from-orange-400 to-pink-500 bg-clip-text text-transparent">
                  {percent}%
                </span>
                <span className="text-xs text-zinc-500 uppercase tracking-widest mt-0.5">
                  {t.dayPassed}
                </span>
              </div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold tracking-tight text-white">
                {String(now.getHours()).padStart(2, "0")}:
                {String(now.getMinutes()).padStart(2, "0")}
              </div>
              <div className="text-sm text-zinc-500 mt-1">
                {now.toLocaleDateString(lang === "ru" ? "ru-RU" : "en-US", {
                  weekday: "short",
                  day: "numeric",
                  month: "short",
                })}
              </div>
            </div>
          </div>

          {/* Phase + Hours left */}
          <div className="flex flex-col gap-4">
            <div
              className="rounded-2xl p-5 flex-1"
              style={{
                background: "linear-gradient(145deg, rgba(249,115,22,0.12) 0%, rgba(236,72,153,0.06) 100%)",
                border: "1px solid rgba(249,115,22,0.25)",
                boxShadow: "var(--shadow-soft)",
              }}
            >
              <div className="text-xs text-zinc-500 uppercase tracking-wider mb-1">
                {t.phase}
              </div>
              <div className="text-2xl font-bold bg-gradient-to-r from-orange-400 to-pink-500 bg-clip-text text-transparent">
                {phaseNames[phase]}
              </div>
              <div className="flex gap-1 mt-4">
                {[0, 1, 2, 3].map((i) => (
                  <div
                    key={i}
                    className="h-1.5 flex-1 rounded-full transition-all duration-300"
                    style={{
                      background: i === phase ? "linear-gradient(90deg, #f97316, #ec4899)" : "var(--border)",
                      boxShadow: i === phase ? "0 0 12px var(--glow)" : "none",
                    }}
                  />
                ))}
              </div>
              <div className="flex justify-between text-[10px] text-zinc-600 mt-1">
                <span>0:00</span>
                <span>6:00</span>
                <span>12:00</span>
                <span>18:00</span>
                <span>24:00</span>
              </div>
            </div>

            <div
              className="rounded-2xl p-5"
              style={{
                background: "var(--surface)",
                boxShadow: "var(--shadow-soft)",
                border: "1px solid rgba(255,255,255,0.03)",
              }}
            >
              <div className="text-xs text-zinc-500 uppercase tracking-wider mb-1">
                {t.left}
              </div>
              <div className="text-2xl font-bold text-white">
                {hoursLeft > 0
                  ? `${hoursLeft} ${t.hrs} ${minsLeftOnly} ${t.min}`
                  : `${minsLeftOnly} ${t.min}`}
              </div>
            </div>
          </div>
        </div>

        {/* Burn rate + Salary */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          <div
            className="rounded-2xl p-5"
            style={{
              background: "var(--surface)",
              boxShadow: "var(--shadow-soft)",
              border: "1px solid rgba(255,255,255,0.03)",
            }}
          >
            <div className="text-xs text-zinc-500 uppercase tracking-wider mb-1">
              {t.burn}
            </div>
            <div className="text-2xl font-bold text-white">
              {format(burnAmount)} {currency}
            </div>
          </div>

          <div
            className="rounded-2xl p-5"
            style={{
              background: "var(--surface)",
              boxShadow: "var(--shadow-soft)",
              border: "1px solid rgba(255,255,255,0.03)",
            }}
          >
            <div className="text-xs text-zinc-500 uppercase tracking-wider mb-2">
              {t.salary}
            </div>
            <input
              type="number"
              value={salary}
              onChange={(e) => setSalary(Number(e.target.value) || 0)}
              className="w-full text-2xl font-bold bg-transparent border-none outline-none text-white [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
              placeholder={lang === "ru" ? "120000" : "5000"}
              min={1000}
              step={5000}
            />
            <span className="text-zinc-500 ml-1">{currency}</span>
          </div>
        </div>

        {/* Waveform bar */}
        <div
          className="rounded-2xl p-4 mt-4"
          style={{
            background: "var(--surface)",
            boxShadow: "var(--shadow-soft)",
            border: "1px solid rgba(255,255,255,0.03)",
          }}
        >
          <div className="flex items-end justify-between gap-2 h-12">
            {Array.from({ length: 24 }).map((_, i) => {
              const seed = (i * 7 + now.getMinutes() * 11) % 100;
              const h = 25 + (seed / 100) * 50;
              return (
              <div
                key={i}
                className="flex-1 rounded-sm min-w-[4px] transition-all duration-500"
                style={{
                  height: `${h}%`,
                  background: i < (now.getHours() % 24)
                    ? "linear-gradient(180deg, #f97316, #ec4899)"
                    : "var(--border)",
                  opacity: i < (now.getHours() % 24) ? 0.9 : 0.3,
                }}
              />
            );
            })}
          </div>
          <div className="flex justify-between text-[10px] text-zinc-600 mt-2">
            <span>0</span>
            <span>12</span>
            <span>24</span>
          </div>
        </div>

        <p className="text-center text-sm text-zinc-500 mt-8">
          <a
            href="https://github.com/waplebe/auto-commit-ai"
            className="text-orange-400 hover:text-orange-300"
          >
            Source
          </a>
        </p>
      </div>
    </div>
  );
}
