export type Channel =
  | "whatsapp"
  | "instagram"
  | "facebook"
  | "linkedin"
  | "webchat"
  | "voice"
  | "generic";

export type UnifiedMessage = {
  id: string;
  channel: Channel;
  receivedAt: string;
  from: string;
  name?: string;
  text?: string;
  metadata?: unknown;
};

