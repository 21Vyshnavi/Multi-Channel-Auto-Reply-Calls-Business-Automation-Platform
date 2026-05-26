import Fastify from "fastify";
import cors from "@fastify/cors";
import { z } from "zod";
import { createInMemoryInboxStore } from "./stores/inbox.js";
import { createInMemoryRulesStore } from "./stores/rules.js";
import { createInMemoryLeadsStore } from "./stores/leads.js";
import { createInMemoryAppointmentsStore } from "./stores/appointments.js";
import { normalizeInbound } from "./normalize.js";

const envSchema = z.object({
  PORT: z.coerce.number().default(8080)
});

const env = envSchema.parse(process.env);

const app = Fastify({ logger: true });
await app.register(cors, { origin: true });

const inbox = createInMemoryInboxStore();
const rules = createInMemoryRulesStore([
  {
    id: "seed-1",
    name: "Pricing keyword",
    enabled: true,
    channel: undefined,
    contains: "price",
    replyText: "Thanks! Please share your business name and preferred time for a quick call.",
    createdAt: new Date().toISOString()
  }
]);
const leads = createInMemoryLeadsStore();
const appointments = createInMemoryAppointmentsStore();

app.get("/health", async () => ({ ok: true }));

app.post("/v1/webhooks/:channel/inbound", async (req, reply) => {
  const channel = (req.params as { channel: string }).channel;
  const item = normalizeInbound(channel, req.body);
  inbox.add(item);
  const matched = rules.match({ channel, text: item.text });
  reply.code(202).send({ accepted: true, id: item.id, autoReply: matched?.replyText ?? null });
});

app.get("/v1/inbox", async () => {
  return { items: inbox.list() };
});

app.get("/v1/rules", async () => ({ rules: rules.list() }));

app.post("/v1/rules", async (req) => {
  const schema = z.object({
    name: z.string().min(1),
    enabled: z.boolean().default(true),
    channel: z.string().optional(),
    contains: z.string().min(1).optional(),
    replyText: z.string().min(1)
  });
  const input = schema.parse(req.body ?? {});
  return { rule: rules.add(input) };
});

app.patch("/v1/rules/:id", async (req, reply) => {
  const id = (req.params as { id: string }).id;
  const schema = z
    .object({
      name: z.string().min(1).optional(),
      enabled: z.boolean().optional(),
      channel: z.string().optional().nullable(),
      contains: z.string().min(1).optional().nullable(),
      replyText: z.string().min(1).optional()
    })
    .partial();
  const patch = schema.parse(req.body ?? {});
  const updated = rules.update(id, patch as any);
  if (!updated) return reply.code(404).send({ error: "not_found" });
  return { rule: updated };
});

app.delete("/v1/rules/:id", async (req, reply) => {
  const id = (req.params as { id: string }).id;
  const ok = rules.remove(id);
  if (!ok) return reply.code(404).send({ error: "not_found" });
  return { deleted: true };
});

app.get("/v1/leads", async () => ({ leads: leads.list() }));

app.post("/v1/leads", async (req) => {
  const schema = z.object({
    name: z.string().optional(),
    phone: z.string().optional(),
    email: z.string().optional(),
    sourceChannel: z.string().optional(),
    notes: z.string().optional()
  });
  const input = schema.parse(req.body ?? {});
  return { lead: leads.add(input) };
});

app.get("/v1/appointments", async () => ({ appointments: appointments.list() }));

app.post("/v1/appointments", async (req) => {
  const schema = z.object({
    name: z.string().optional(),
    phone: z.string().optional(),
    email: z.string().optional(),
    startAt: z.string().min(1),
    reason: z.string().optional()
  });
  const input = schema.parse(req.body ?? {});
  return { appointment: appointments.add(input) };
});

app.post("/v1/appointments/:id/cancel", async (req, reply) => {
  const id = (req.params as { id: string }).id;
  const updated = appointments.cancel(id);
  if (!updated) return reply.code(404).send({ error: "not_found" });
  return { appointment: updated };
});

await app.listen({ port: env.PORT, host: "0.0.0.0" });
