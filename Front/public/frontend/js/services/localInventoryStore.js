/**
 * FASE 2 — Mini banco temporário em localStorage.
 * Simula CRUD completo para dados logísticos expandidos e configurações
 * que ainda não têm endpoint dedicado no backend.
 *
 * Nenhum dado aqui substitui o backend; apenas enriquece a experiência
 * visual com campos extras até a integração definitiva.
 */

const NS = "antstock:localdb:";

function readTable(name) {
  try {
    return JSON.parse(localStorage.getItem(NS + name) || "{}");
  } catch {
    return {};
  }
}

function writeTable(name, data) {
  localStorage.setItem(NS + name, JSON.stringify(data));
}

function uuid() {
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    return (c === "x" ? r : (r & 0x3) | 0x8).toString(16);
  });
}

function now() {
  return new Date().toISOString();
}

/** Generic CRUD factory */
function makeTable(name) {
  return {
    list() {
      return Object.values(readTable(name));
    },

    get(id) {
      return readTable(name)[id] || null;
    },

    create(data) {
      const table = readTable(name);
      const record = { id: uuid(), criado_em: now(), atualizado_em: now(), ...data };
      table[record.id] = record;
      writeTable(name, table);
      return record;
    },

    update(id, data) {
      const table = readTable(name);
      if (!table[id]) return null;
      table[id] = { ...table[id], ...data, atualizado_em: now() };
      writeTable(name, table);
      return table[id];
    },

    delete(id) {
      const table = readTable(name);
      const existed = !!table[id];
      delete table[id];
      writeTable(name, table);
      return existed;
    },

    clear() {
      writeTable(name, {});
    },

    count() {
      return Object.keys(readTable(name)).length;
    },
  };
}

/**
 * Tabelas disponíveis localmente:
 *
 * locationDetails  — informações logísticas estendidas por produto
 *   { product_id, torre, corredor, prateleira, nivel, posicao, descricao_localizacao, observacoes }
 *
 * appSettings      — preferências locais do usuário
 *   { key, value }
 *
 * barcodeHistory   — histórico de leituras de código de barras
 *   { code, timestamp, found, productName }
 *
 * userProfiles     — perfis e permissões simulados
 *   { id, name, email, role, permissions[] }
 *
 * schoolData       — dados de gestão escolar (placeholder)
 *   { id, titulo, tipo, descricao, data }
 */

export const LocalDB = {
  locationDetails: makeTable("locationDetails"),
  appSettings: makeTable("appSettings"),
  barcodeHistory: makeTable("barcodeHistory"),
  userProfiles: makeTable("userProfiles"),
  schoolData: makeTable("schoolData"),

  /** Get or create location detail for a product */
  getLocationDetail(productId) {
    const all = this.locationDetails.list();
    return all.find((r) => r.product_id === productId) || null;
  },

  /** Save location detail (upsert) */
  saveLocationDetail(productId, data) {
    const existing = this.getLocationDetail(productId);
    if (existing) {
      return this.locationDetails.update(existing.id, { ...data, product_id: productId });
    }
    return this.locationDetails.create({ product_id: productId, ...data });
  },

  /** App settings shorthand */
  getSetting(key, fallback = null) {
    const all = this.appSettings.list();
    const row = all.find((r) => r.key === key);
    return row ? row.value : fallback;
  },

  setSetting(key, value) {
    const all = this.appSettings.list();
    const row = all.find((r) => r.key === key);
    if (row) {
      return this.appSettings.update(row.id, { key, value });
    }
    return this.appSettings.create({ key, value });
  },

  /** Barcode scan log */
  logScan(code, found, productName = "") {
    return this.barcodeHistory.create({
      code,
      timestamp: now(),
      found,
      productName,
    });
  },

  /** Seed demo school data if empty */
  seedSchoolIfEmpty() {
    if (this.schoolData.count() > 0) return;
    const items = [
      { titulo: "Almoxarifado Central", tipo: "deposito", descricao: "Depósito principal da escola.", data: now() },
      { titulo: "Laboratório de Ciências", tipo: "sala", descricao: "Materiais de laboratório.", data: now() },
      { titulo: "Biblioteca", tipo: "sala", descricao: "Livros e recursos didáticos.", data: now() },
      { titulo: "Quadra Esportiva", tipo: "espaco", descricao: "Equipamentos esportivos.", data: now() },
    ];
    items.forEach((i) => this.schoolData.create(i));
  },

  /** Seed demo user profiles if empty */
  seedUsersIfEmpty() {
    if (this.userProfiles.count() > 0) return;
    const profiles = [
      {
        name: "Administrador", email: "admin@antstock.local", role: "administrador",
        permissions: ["create", "read", "update", "delete", "manage_users"],
      },
      {
        name: "Prof. Ana Lima", email: "ana.lima@escola.local", role: "professor",
        permissions: ["create", "read", "update"],
      },
      {
        name: "Carlos Operador", email: "carlos@escola.local", role: "operador",
        permissions: ["read", "update"],
      },
      {
        name: "Gestão Fernanda", email: "fernanda@escola.local", role: "gestor",
        permissions: ["create", "read", "update", "delete"],
      },
    ];
    profiles.forEach((p) => this.userProfiles.create(p));
  },

  /** Full reset */
  resetAll() {
    ["locationDetails", "appSettings", "barcodeHistory", "userProfiles", "schoolData"].forEach(
      (t) => this[t].clear()
    );
  },
};
