"use client";

import { useEffect, useRef } from "react";

/**
 * Scroll-reveal wrapper. Uses IntersectionObserver; adds .is-visible once.
 * Content is fully visible without JS or under prefers-reduced-motion
 * (see .reveal rules in globals.css).
 */
export function Reveal({
  children,
  delay = 0,
  className = "",
  as: Tag = "div",
}: {
  children: React.ReactNode;
  delay?: number;
  className?: string;
  as?: "div" | "section" | "li" | "span";
}) {
  const ref = useRef<HTMLElement | null>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (typeof IntersectionObserver === "undefined") {
      el.classList.add("is-visible");
      return;
    }
    const reveal = () => el.classList.add("is-visible");
    const io = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            reveal();
            io.disconnect();
          }
        }
      },
      { threshold: 0.12, rootMargin: "0px 0px -40px 0px" },
    );
    io.observe(el);
    // fail-safe: content must never stay hidden (no IO support, printing,
    // full-page captures, exotic browsers). Reveal after a short grace period.
    const timer = window.setTimeout(reveal, 1100 + delay);
    return () => {
      io.disconnect();
      window.clearTimeout(timer);
    };
  }, []);

  return (
    <Tag
      // @ts-expect-error polymorphic ref across the allowed tags
      ref={ref}
      className={`reveal ${className}`}
      style={delay ? { transitionDelay: `${delay}ms` } : undefined}
    >
      {children}
    </Tag>
  );
}

/** Section header: editorial index + kicker + display title, ruled. */
export function SectionHeader({
  index,
  kicker,
  title,
  meta,
}: {
  index: string;
  kicker: string;
  title?: React.ReactNode;
  meta?: string;
}) {
  return (
    <Reveal className="mb-10 sm:mb-14">
      <div className="rule-t pt-4">
        <div className="flex items-baseline justify-between gap-4">
          <div className="flex items-baseline gap-4">
            <span className="section-index">{index}</span>
            <span className="microlabel">{kicker}</span>
          </div>
          {meta ? <span className="microlabel hidden sm:block">{meta}</span> : null}
        </div>
        {title ? <h2 className="display-md mt-6 max-w-3xl text-balance">{title}</h2> : null}
      </div>
    </Reveal>
  );
}
