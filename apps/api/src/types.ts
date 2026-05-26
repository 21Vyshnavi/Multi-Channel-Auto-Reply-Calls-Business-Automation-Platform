export type InboxItem = {
  id: string;
  channel: string;
  receivedAt: string;
  from: string;
  name?: string;
  text?: string;
  metadata?: unknown;
};

