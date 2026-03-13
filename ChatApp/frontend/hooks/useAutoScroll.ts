import { useRef, useEffect, useCallback } from "react";

export function useAutoScroll(deps: unknown[]) {
  const ref = useRef<HTMLDivElement>(null);

  const scrollToBottom = useCallback(() => {
    ref.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  return ref;
}
