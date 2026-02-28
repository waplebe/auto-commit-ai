"use client";

import { useEffect, useState } from "react";

const PATTERNS: Record<string, number[]> = {
  box: [4, 4, 4, 4],
  "4-7-8": [4, 7, 8, 0],
  calm: [5, 2, 5, 2],
};

type PatternKey = keyof typeof PATTERNS;

export default function Breath() {
  const [phaseIdx, setPhaseIdx] = useState(0);
  const [phaseSec, setPhaseSec] = useState(0);
  const [cycle, setCycle] = useState(0);
  const [pattern, setPattern] = useState<PatternKey>("box");
  const [lang, setLang] = useState<"ru" | "en">("ru");

  const durations = PATTERNS[pattern];
  const phases = ["inhale", "hold", "exhale", "hold"] as const;
  const currentPhase = phases[phaseIdx % 4];
  const phaseDuration = durations[phaseIdx] ?? 4;
  const countdown = Math.max(0, phaseDuration - phaseSec);

  useEffect(() => {
    const id = setInterval(() => {
      setPhaseSec((s) => {
        const next = s + 1;
        if (next >= phaseDuration) {
          if (phaseIdx + 1 >= durations.length || durations[phaseIdx + 1] === 0) {
            setPhaseIdx(0);
            setCycle((c) => c + 1);
          } else {
            setPhaseIdx((i) => i + 1);
          }
          return 0;
        }
        return next;
      });
    }, 1000);
    return () => clearInterval(id);
  }, [phaseIdx, phaseDuration, durations]);

  useEffect(() => {
    setPhaseIdx(0);
    setPhaseSec(0);
    setCycle(0);
  }, [pattern]);

  const scale = (() => {
    if (currentPhase === "inhale") {
      return 0.55 + (phaseSec / phaseDuration) * 0.45;
    }
    if (currentPhase === "exhale") {
      return 1 - (phaseSec / phaseDuration) * 0.45;
    }
    return 1;
  })();

  const i18n = {
    ru: {
      title: "Дыхание",
      tagline: "Следуй за кругом",
      inhale: "Вдох",
      hold: "Задержка",
      exhale: "Выдох",
      cycles: "циклов",
      box: "Квадрат",
      "4-7-8": "4-7-8",
      calm: "Спокойное",
    },
    en: {
      title: "Breathe",
      tagline: "Follow the circle",
      inhale: "Inhale",
      hold: "Hold",
      exhale: "Exhale",
      cycles: "cycles",
      box: "Box",
      "4-7-8": "4-7-8",
      calm: "Calm",
    },
  };

  const t = i18n[lang];

  return (
    <div className="fixed inset-0 overflow-hidden bg-[#07070a] flex flex-col items-center justify-center">
      <div
        className="absolute inset-0 opacity-30"
        style={{
          background:
            currentPhase === "inhale"
              ? "radial-gradient(ellipse 80% 80% at 50% 50%, rgba(34,197,94,0.25) 0%, transparent 70%)"
              : currentPhase === "exhale"
              ? "radial-gradient(ellipse 80% 80% at 50% 50%, rgba(59,130,246,0.2) 0%, transparent 70%)"
              : "radial-gradient(ellipse 80% 80% at 50% 50%, rgba(168,85,247,0.12) 0%, transparent 70%)",
        }}
      />

      <div className="relative z-10 flex flex-col items-center">
        <h1 className="text-lg font-light text-zinc-500 mb-1 tracking-[0.3em] uppercase">
          {t.title}
        </h1>
        <p className="text-[11px] text-zinc-600 mb-10">{t.tagline}</p>

        <div
          className="rounded-full transition-all duration-700 ease-in-out"
          style={{
            width: 260,
            height: 260,
            transform: `scale(${scale})`,
            background:
              currentPhase === "inhale"
                ? "radial-gradient(circle at 35% 35%, rgba(34,197,94,0.5), rgba(22,163,74,0.25))"
                : currentPhase === "exhale"
                ? "radial-gradient(circle at 35% 35%, rgba(59,130,246,0.45), rgba(37,99,235,0.2))"
                : "radial-gradient(circle at 35% 35%, rgba(168,85,247,0.4), rgba(126,34,206,0.18))",
            boxShadow:
              currentPhase === "inhale"
                ? "0 0 100px rgba(34,197,94,0.35), inset 0 0 80px rgba(34,197,94,0.12)"
                : currentPhase === "exhale"
                ? "0 0 100px rgba(59,130,246,0.3), inset 0 0 80px rgba(59,130,246,0.1)"
                : "0 0 80px rgba(168,85,247,0.25), inset 0 0 60px rgba(168,85,247,0.08)",
            border: "1px solid rgba(255,255,255,0.04)",
          }}
        />

        <p className="mt-10 text-xl font-light text-white/80">
          {t[currentPhase]}
        </p>
        <p className="text-5xl font-extralight text-zinc-400 mt-3 tabular-nums">
          {countdown}
        </p>
        <p className="text-sm text-zinc-600 mt-8">
          {cycle} {t.cycles}
        </p>
      </div>

      <div className="absolute bottom-12 left-0 right-0 flex justify-center gap-2">
        {(Object.keys(PATTERNS) as PatternKey[]).map((p) => (
          <button
            key={p}
            onClick={() => setPattern(p)}
            className={`px-5 py-2.5 rounded-2xl text-sm font-medium transition-all ${
              pattern === p
                ? "bg-white/10 text-white border border-white/15"
                : "text-zinc-500 hover:text-zinc-400 border border-transparent"
            }`}
          >
            {(t as Record<string, string>)[p]}
          </button>
        ))}
      </div>

      <div className="absolute top-6 right-6 flex gap-1">
        {(["ru", "en"] as const).map((l) => (
          <button
            key={l}
            onClick={() => setLang(l)}
            className={`px-3 py-1.5 rounded-xl text-xs ${
              lang === l ? "text-white bg-white/10" : "text-zinc-500"
            }`}
          >
            {l.toUpperCase()}
          </button>
        ))}
      </div>
    </div>
  );
}
