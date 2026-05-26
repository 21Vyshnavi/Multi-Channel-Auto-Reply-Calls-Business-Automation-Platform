import { randomUUID } from "node:crypto";

export type AutoReplyRule = {
  id: string;
  name: string;
  enabled: boolean;
  channel?: string;
  contains?: string;
  replyText: string;
  createdAt: string;
};

export type RulesStore = {
  list: () => AutoReplyRule[];
  add: (rule: Omit<AutoReplyRule, "id" | "createdAt">) => AutoReplyRule;
  update: (id: string, patch: Partial<Omit<AutoReplyRule, "id" | "createdAt">>) => AutoReplyRule | null;
  remove: (id: string) => boolean;
  match: (input: { channel: string; text?: string }) => AutoReplyRule | null;
};

export function createInMemoryRulesStore(seed?: AutoReplyRule[]): RulesStore {
  const rules: AutoReplyRule[] = seed ? [...seed] : [];

  function list() {
    return [...rules].sort((a, b) => (a.createdAt < b.createdAt ? 1 : -1));
  }

  function add(rule: Omit<AutoReplyRule, "id" | "createdAt">): AutoReplyRule {
    const createdAt = new Date().toISOString();
    const item: AutoReplyRule = { ...rule, id: randomUUID(), createdAt };
    rules.unshift(item);
    return item;
  }

  function update(id: string, patch: Partial<Omit<AutoReplyRule, "id" | "createdAt">>) {
    const idx = rules.findIndex((r) => r.id === id);
    if (idx === -1) return null;
    rules[idx] = { ...rules[idx], ...patch };
    return rules[idx];
  }

  function remove(id: string) {
    const idx = rules.findIndex((r) => r.id === id);
    if (idx === -1) return false;
    rules.splice(idx, 1);
    return true;
  }

  function match(input: { channel: string; text?: string }): AutoReplyRule | null {
    const text = (input.text ?? "").toLowerCase();
    for (const rule of rules) {
      if (!rule.enabled) continue;
      if (rule.channel && rule.channel !== input.channel) continue;
      if (rule.contains && !text.includes(rule.contains.toLowerCase())) continue;
      return rule;
    }
    return null;
  }

  return { list, add, update, remove, match };
}

