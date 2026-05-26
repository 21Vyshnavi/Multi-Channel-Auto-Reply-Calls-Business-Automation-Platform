import { randomUUID } from "node:crypto";
import { z } from "zod";
import type { InboxItem } from "./types.js";

const genericInboundSchema = z
  .object({
    from: z.string().optional(),
    text: z.string().optional(),
    name: z.string().optional(),
    phone: z.string().optional(),
    email: z.string().optional(),
    metadata: z.record(z.any()).optional()
  })
  .passthrough();

export function normalizeInbound(channel: string, body: unknown): InboxItem {
  const parsed = genericInboundSchema.parse(body ?? {});
  const now = new Date().toISOString();
  return {
    id: randomUUID(),
    channel,
    receivedAt: now,
    from: parsed.from ?? parsed.phone ?? parsed.email ?? "unknown",
    name: parsed.name,
    text: parsed.text,
    metadata: parsed.metadata ?? parsed
  };
}

