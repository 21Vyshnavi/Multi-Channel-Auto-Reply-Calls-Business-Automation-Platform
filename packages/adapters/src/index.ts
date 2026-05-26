import type { Channel, UnifiedMessage } from "@mcabap/core";
import { randomUUID } from "node:crypto";

export type AdapterContext = {
  verifyToken?: string;
  appSecret?: string;
  accessToken?: string;
};

export interface ChannelAdapter {
  channel: Channel;
  normalizeInbound: (payload: unknown) => UnifiedMessage;
}

export class GenericAdapter implements ChannelAdapter {
  channel: Channel = "generic";
  normalizeInbound(payload: unknown): UnifiedMessage {
    const now = new Date().toISOString();
    const p = (payload ?? {}) as any;
    return {
      id: randomUUID(),
      channel: "generic",
      receivedAt: now,
      from: p.from ?? "unknown",
      name: p.name,
      text: p.text,
      metadata: p
    };
  }
}
