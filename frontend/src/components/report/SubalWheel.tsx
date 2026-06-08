"use client";

import {
  ArrowLeft,
  ArrowRight,
  Bandage,
  Compass,
  Drama,
  Flame,
  Megaphone,
  Puzzle,
  Shield,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import type { ComponentType } from "react";

type IconProps = {
  size?: number | string;
  color?: string;
  strokeWidth?: number | string;
};

type WheelIconComponent = LucideIcon | ComponentType<IconProps>;

function ContradictionArrows({ size = 32, color = "#FFFFFF", strokeWidth = 2.25 }: IconProps) {
  const dimension = typeof size === "number" ? size : 32;
  const arrowSize = dimension * 0.46;
  return (
    <svg
      width={dimension}
      height={dimension}
      viewBox={`0 0 ${dimension} ${dimension}`}
      aria-hidden
    >
      <g transform={`translate(${dimension / 2 - arrowSize / 2}, ${dimension * 0.18})`}>
        <ArrowLeft size={arrowSize} color={color} strokeWidth={strokeWidth} />
      </g>
      <g transform={`translate(${dimension / 2 - arrowSize / 2}, ${dimension * 0.52})`}>
        <ArrowRight size={arrowSize} color={color} strokeWidth={strokeWidth} />
      </g>
    </svg>
  );
}

const DIMENSIONS = [
  { slug: "burnout_risk", label: "Burnout Risk", number: 1, color: "#0B4F71", Icon: Flame },
  { slug: "authenticity_strain", label: "Authenticity Strain", number: 2, color: "#31B8C6", Icon: Drama },
  { slug: "suppressed_influence", label: "Suppressed Influence", number: 3, color: "#6F3FA0", Icon: Megaphone },
  {
    slug: "internal_contradiction",
    label: "Internal Contradiction",
    number: 4,
    color: "#D83A4B",
    Icon: ContradictionArrows,
  },
  { slug: "structural_misfit", label: "Structural Misfit", number: 5, color: "#F47C20", Icon: Puzzle },
  { slug: "old_wounds_new_systems", label: "Old Wounds, New Systems", number: 6, color: "#F2A51A", Icon: Bandage },
  { slug: "emotional_containment", label: "Emotional Containment", number: 7, color: "#68B84E", Icon: Shield },
  { slug: "values_misalignment", label: "Values Misalignment", number: 8, color: "#28A98B", Icon: Compass },
] as const satisfies ReadonlyArray<{
  slug: string;
  label: string;
  number: number;
  color: string;
  Icon: WheelIconComponent;
}>;

const LEVEL_COLORS = {
  Low: "#68B84E",
  Moderate: "#F2A51A",
  High: "#D83A4B",
} as const;

type WheelData = {
  scores: Record<string, number>;
  levels: Record<string, string>;
  top_pressure_zones: Array<{
    domain: string;
    slug: string;
    score: number;
    level: string;
  }>;
};

type Props = {
  wheel: WheelData;
};

const SIZE = 1000;
const CENTER = SIZE / 2;
const INNER_RADIUS = 70;
const OUTER_RADIUS = 360;
const LABEL_INNER = 372;
const LABEL_OUTER = 470;
const START_ANGLE = 90;
const ANGLE_PER_SEGMENT = 360 / 8;
const ICON_SIZE = 56;
const NUMBER_FONT_SIZE = 36;
const NAME_FONT_SIZE = 17;
const NAME_LINE_HEIGHT = 19;
const GAP_AFTER_NUMBER = 10;

function polar(angleDeg: number, radius: number) {
  const rad = (angleDeg * Math.PI) / 180;
  return {
    x: CENTER + radius * Math.cos(rad),
    y: CENTER - radius * Math.sin(rad),
  };
}

function scoreRadius(score: number) {
  return INNER_RADIUS + (score / 100) * (OUTER_RADIUS - INNER_RADIUS);
}

function segmentPath(index: number, inner: number, outer: number) {
  const start = START_ANGLE - index * ANGLE_PER_SEGMENT;
  const end = start - ANGLE_PER_SEGMENT;
  const p1 = polar(start, inner);
  const p2 = polar(end, inner);
  const p3 = polar(end, outer);
  const p4 = polar(start, outer);
  return `M ${p1.x} ${p1.y} A ${inner} ${inner} 0 0 1 ${p2.x} ${p2.y} L ${p3.x} ${p3.y} A ${outer} ${outer} 0 0 0 ${p4.x} ${p4.y} Z`;
}

function segmentMidAngle(index: number) {
  return START_ANGLE - index * ANGLE_PER_SEGMENT - ANGLE_PER_SEGMENT / 2;
}

/** Clockwise (right-hand) edge of each pizza slice */
function segmentRightAngle(index: number) {
  return START_ANGLE - (index + 1) * ANGLE_PER_SEGMENT;
}

/** Icon sits on the outer-right of the slice, inset from the edge */
function segmentIconPoint(index: number) {
  const rightAngle = segmentRightAngle(index);
  return polar(rightAngle + ANGLE_PER_SEGMENT * 0.24, LABEL_OUTER - 44);
}

function WheelIcon({
  icon: Icon,
  x,
  y,
  size,
}: {
  icon: WheelIconComponent;
  x: number;
  y: number;
  size: number;
}) {
  return (
    <g transform={`translate(${x - size / 2}, ${y - size / 2})`} aria-hidden>
      <Icon size={size} color="#FFFFFF" strokeWidth={2.5} />
    </g>
  );
}

function wrapDomainName(label: string): string[] {
  if (label === "Old Wounds, New Systems") return ["Old Wounds,", "New Systems"];
  if (label === "Authenticity Strain") return ["Authenticity", "Strain"];
  if (label === "Suppressed Influence") return ["Suppressed", "Influence"];
  if (label === "Internal Contradiction") return ["Internal", "Contradiction"];
  if (label === "Structural Misfit") return ["Structural", "Misfit"];
  if (label === "Emotional Containment") return ["Emotional", "Containment"];
  if (label === "Values Misalignment") return ["Values", "Misalignment"];
  return [label];
}

function SegmentLabel({
  index,
  number,
  nameLines,
}: {
  index: number;
  number: number;
  nameLines: string[];
}) {
  const anchor = polar(segmentMidAngle(index), LABEL_INNER + (LABEL_OUTER - LABEL_INNER) * 0.36);
  const nameBlockHeight = nameLines.length * NAME_LINE_HEIGHT;
  const blockHeight = NUMBER_FONT_SIZE + GAP_AFTER_NUMBER + nameBlockHeight;
  const blockTop = anchor.y - blockHeight / 2;

  return (
    <g>
      <text
        x={anchor.x}
        y={blockTop + NUMBER_FONT_SIZE / 2}
        textAnchor="middle"
        dominantBaseline="middle"
        fontSize={NUMBER_FONT_SIZE}
        fontWeight="700"
        fill="#FFFFFF"
        fontFamily="var(--font-heading), system-ui, sans-serif"
      >
        {number}
      </text>
      {nameLines.map((line, lineIndex) => (
        <text
          key={line}
          x={anchor.x}
          y={
            blockTop +
            NUMBER_FONT_SIZE +
            GAP_AFTER_NUMBER +
            NAME_LINE_HEIGHT * lineIndex +
            NAME_LINE_HEIGHT / 2
          }
          textAnchor="middle"
          dominantBaseline="middle"
          fontSize={NAME_FONT_SIZE}
          fontWeight="700"
          fill="#FFFFFF"
          fontFamily="var(--font-heading), system-ui, sans-serif"
        >
          {line}
        </text>
      ))}
    </g>
  );
}

export function SubalWheel({ wheel }: Props) {
  const polygonPoints = DIMENSIONS.map((dim, index) => {
    const score = wheel.scores[dim.slug] ?? 0;
    const angle = START_ANGLE - index * ANGLE_PER_SEGMENT;
    const point = polar(angle, scoreRadius(score));
    return `${point.x},${point.y}`;
  }).join(" ");

  const summary = wheel.top_pressure_zones.map((zone) => zone.domain).join(", ");

  return (
    <div className="grid gap-6">
      <div className="overflow-x-auto rounded-xl bg-[#F7F8FA] p-4 sm:p-6">
        <svg
          viewBox={`0 0 ${SIZE} ${SIZE}`}
          role="img"
          aria-label={`SUBAL Wheel summary: highest strain areas are ${summary}.`}
          className="mx-auto h-auto min-w-[320px] w-full max-w-[720px]"
        >
          <rect width={SIZE} height={SIZE} fill="#F7F8FA" rx="24" />
          <circle cx={CENTER} cy={CENTER} r={INNER_RADIUS - 4} fill="#FFFFFF" stroke="#D8DDE3" strokeWidth={2} />
          <text
            x={CENTER}
            y={CENTER}
            textAnchor="middle"
            dominantBaseline="middle"
            fontSize="26"
            fontWeight="700"
            fill="#102A43"
            letterSpacing="0.14em"
            fontFamily="var(--font-heading), system-ui, sans-serif"
          >
            SUBAL
          </text>

          {DIMENSIONS.map((dim, index) => (
            <path
              key={`label-band-${dim.slug}`}
              d={segmentPath(index, LABEL_INNER, LABEL_OUTER)}
              fill={dim.color}
            />
          ))}

          {DIMENSIONS.map((dim, index) => (
            <path
              key={`score-band-${dim.slug}`}
              d={segmentPath(index, INNER_RADIUS, OUTER_RADIUS)}
              fill={dim.color}
              opacity={0.12}
            />
          ))}

          {[20, 40, 60, 80, 100].map((ring) => {
            const radius = scoreRadius(ring);
            return (
              <g key={ring}>
                <circle cx={CENTER} cy={CENTER} r={radius} fill="none" stroke="#D8DDE3" strokeWidth={1.5} />
                <text
                  x={CENTER + 10}
                  y={CENTER - radius - 8}
                  fontSize="16"
                  fill="#64748b"
                  fontFamily="var(--font-body), system-ui, sans-serif"
                >
                  {ring}
                </text>
              </g>
            );
          })}

          <polygon
            points={polygonPoints}
            fill="#DCEBFA"
            fillOpacity={0.45}
            stroke="#0B2D4D"
            strokeWidth={3}
          />

          {DIMENSIONS.map((dim, index) => {
            const score = wheel.scores[dim.slug] ?? 0;
            const angle = START_ANGLE - index * ANGLE_PER_SEGMENT;
            const point = polar(angle, scoreRadius(score));
            const scoreLabel = polar(angle, scoreRadius(score) + 24);

            return (
              <g key={`score-${dim.slug}`}>
                <circle cx={point.x} cy={point.y} r={8} fill="#0B2D4D" />
                <text
                  x={scoreLabel.x}
                  y={scoreLabel.y}
                  fontSize="18"
                  fontWeight="700"
                  fill="#102A43"
                  textAnchor="middle"
                  dominantBaseline="middle"
                  fontFamily="var(--font-body), system-ui, sans-serif"
                >
                  {Math.round(score)}
                </text>
              </g>
            );
          })}

          {DIMENSIONS.map((dim, index) => (
            <SegmentLabel
              key={`label-${dim.slug}`}
              index={index}
              number={dim.number}
              nameLines={wrapDomainName(dim.label)}
            />
          ))}

          {DIMENSIONS.map((dim, index) => {
            const iconPoint = segmentIconPoint(index);
            return (
              <WheelIcon
                key={`icon-${dim.slug}`}
                icon={dim.Icon}
                x={iconPoint.x}
                y={iconPoint.y}
                size={ICON_SIZE}
              />
            );
          })}
        </svg>
      </div>

      <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
        {DIMENSIONS.map((dim) => {
          const score = wheel.scores[dim.slug] ?? 0;
          const level = wheel.levels[dim.slug] ?? "Low";
          return (
            <div
              key={dim.slug}
              className="flex items-center gap-3 rounded-lg border bg-card p-3"
              style={{ borderLeft: `4px solid ${dim.color}` }}
            >
              <div
                className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-white"
                style={{ backgroundColor: dim.color }}
              >
                <dim.Icon size={18} strokeWidth={2.25} aria-hidden />
              </div>
              <div className="min-w-0">
                <div className="truncate text-sm font-medium text-[#102A43]">{dim.label}</div>
                <div className="text-xs text-muted-foreground">
                  {Math.round(score)} — {level}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="flex flex-wrap items-center gap-4 text-sm text-[#102A43]">
        <span className="inline-flex items-center gap-2">
          <span className="h-2.5 w-2.5 rounded-full" style={{ background: LEVEL_COLORS.Low }} />
          0–39 Low
        </span>
        <span className="inline-flex items-center gap-2">
          <span className="h-2.5 w-2.5 rounded-full" style={{ background: LEVEL_COLORS.Moderate }} />
          40–69 Moderate
        </span>
        <span className="inline-flex items-center gap-2">
          <span className="h-2.5 w-2.5 rounded-full" style={{ background: LEVEL_COLORS.High }} />
          70–100 High
        </span>
        <span className="text-muted-foreground">
          Higher scores indicate greater strain or misalignment.
        </span>
      </div>

      <div className="grid gap-3 sm:grid-cols-3">
        {wheel.top_pressure_zones.map((zone, index) => {
          const dim = DIMENSIONS.find((item) => item.slug === zone.slug);
          const color = dim?.color ?? "#0B4F71";
          const Icon = dim?.Icon;
          return (
            <div
              key={zone.slug}
              className="rounded-lg border bg-card p-3"
              style={{ borderLeft: `4px solid ${color}` }}
            >
              <div className="flex items-center gap-2">
                {Icon ? (
                  <div
                    className="flex h-8 w-8 items-center justify-center rounded-full text-white"
                    style={{ backgroundColor: color }}
                  >
                    <Icon size={16} strokeWidth={2.25} aria-hidden />
                  </div>
                ) : null}
                <div>
                  <div className="text-xs text-muted-foreground">Top pressure zone {index + 1}</div>
                  <div className="font-medium text-[#102A43]">{zone.domain}</div>
                </div>
              </div>
              <div className="mt-2 text-sm text-muted-foreground">
                {Math.round(zone.score)} — {zone.level}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
