<template>
  <div class="tables-manager">
    <div class="tables-manager__toolbar">
      <span>Доступные таблицы</span>
      <button class="tables-manager__btn" @click="createTableViewPrompt">+ Создать представление (таблицу)</button>
    </div>
    <div class="tables-manager__list">
      <div v-for="table in tables" :key="table.id" class="tables-manager__table-item">
        <button class="tables-manager__show-table" @click="showTableData(table.id)">
          {{ table.name }}
        </button>
        <button class="tables-manager__delete-table" @click="deleteTableById(table.id)">🗑️</button>
      </div>
    </div>
    <div class="tables-manager__data" v-html="activeTableHtml"></div>

    <!-- Модальное окно для записи -->
    <div v-if="modalVisible" class="tables-manager__modal" @click.self="closeModal">
      <div class="tables-manager__modal-content">
        <h3>{{ modalRecord ? "Редактирование" : "Новая запись" }}</h3>
        <div v-for="field in modalFields" :key="field.id" class="tables-manager__form-group">
          <label>{{ field.name }}</label>
          <input
            v-if="field.type === 'text' || field.type === 'date'"
            :type="field.type === 'date' ? 'date' : 'text'"
            v-model="modalFormData[field.key]"
          />
          <input
            v-else-if="field.type === 'number'"
            type="number"
            v-model.number="modalFormData[field.key]"
          />
          <input
            v-else-if="field.type === 'checkbox'"
            type="checkbox"
            v-model="modalFormData[field.key]"
          />
          <select
            v-else-if="field.type === 'select'"
            v-model="modalFormData[field.key]"
          >
            <option v-for="opt in field.options.values || []" :key="opt">{{ opt }}</option>
          </select>
          <select
            v-else-if="field.type === 'multiselect'"
            multiple
            v-model="modalFormData[field.key]"
          >
            <option v-for="opt in field.options.values || []" :key="opt">{{ opt }}</option>
          </select>
          <input
            v-else-if="field.type === 'coordinates'"
            v-model="modalFormData[field.key]"
            placeholder="широта, долгота"
          />
        </div>
        <button @click="saveModalRecord">Сохранить</button>
        <button @click="closeModal">Отмена</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import {
  fields,
  forms,          // добавлен импорт
  getFieldById,
  getFormById,
  getFieldsForForm,
  addTable,
  deleteTable,
  tables,
  records,
  getRecords,
  deleteRecord,
  updateRecord,
  addRecord,
} from "../stores/appData";

const activeTableHtml = ref("");
const modalVisible = ref(false);
const modalRecord = ref(null);
const modalFormId = ref(null);
const modalFormData = ref({});
const modalFields = ref([]);

function deleteTableById(id) {
  if (confirm("Удалить таблицу?")) {
    deleteTable(id);
    activeTableHtml.value = "";
  }
}

async function showTableData(tableId) {
  const table = tables.value.find(t => t.id === tableId);
  if (!table) return;
  const form = getFormById(table.formId);
  if (!form) return;
  const formFields = getFieldsForForm(form.id);
  const recordsForForm = records[form.id] || [];
  let html = '<table class="tables-manager__data-table"><thead><tr>';
  for (const colId of table.columns) {
    const field = formFields.find(f => f.id === colId);
    if (field) {
      html += `<th>${field.name}</th>`;
    }
  }
  html += '<th>Действия</th></tr></thead><tbody>';
  for (const rec of recordsForForm) {
    html += '<tr>';
    for (const colId of table.columns) {
      const field = formFields.find(f => f.id === colId);
      if (field) {
        let val = rec[field.key];
        if (val === undefined) val = "";
        if (typeof val === "object") val = JSON.stringify(val);
        html += `<td>${escapeHtml(String(val))}</td>`;
      }
    }
    html += `<td>
      <button class="edit-record" data-id="${rec.id}">✏️</button>
      <button class="delete-record" data-id="${rec.id}">🗑️</button>
    </td></tr>`;
  }
  html += '</tbody></table><button class="tables-manager__add-record-btn" data-form-id="' + form.id + '">+ Новая запись</button>';
  activeTableHtml.value = html;
  setTimeout(() => {
    document.querySelectorAll(".edit-record").forEach(btn => {
      btn.addEventListener("click", e => {
        const recId = parseInt(btn.dataset.id);
        const record = recordsForForm.find(r => r.id === recId);
        if (record) openRecordModal(record, form.id);
      });
    });
    document.querySelectorAll(".delete-record").forEach(btn => {
      btn.addEventListener("click", async e => {
        const recId = parseInt(btn.dataset.id);
        if (confirm("Удалить запись?")) {
          await deleteRecord(form.id, recId);
          showTableData(tableId);
        }
      });
    });
    const addBtn = document.querySelector(".tables-manager__add-record-btn");
    if (addBtn) {
      addBtn.addEventListener("click", () => openRecordModal(null, form.id));
    }
  }, 0);
}

function createTableViewPrompt() {
  const formId = prompt(
    "Выберите ID формы, на основе которой создать таблицу (доступные формы: " +
      forms.value.map(f => `${f.id}:${f.name}`).join(", ")
  );
  if (!formId) return;
  const fid = parseInt(formId);
  if (!getFormById(fid)) {
    alert("Форма не найдена");
    return;
  }
  const tableName = prompt("Название таблицы");
  if (!tableName) return;
  const formFields = getFieldsForForm(fid);
  const columnsPrompt =
    "Введите ID полей через запятую (доступны: " +
    formFields.map(f => `${f.id}:${f.name}`).join(", ") + ")";
  let colIds = prompt(columnsPrompt);
  if (!colIds) return;
  let colArray = colIds
    .split(",")
    .map(s => parseInt(s.trim()))
    .filter(id => formFields.find(f => f.id === id));
  if (colArray.length === 0) {
    alert("Нет валидных полей");
    return;
  }
  addTable({ name: tableName, formId: fid, columns: colArray });
  alert("Таблица создана");
}

function openRecordModal(record, formId) {
  modalVisible.value = true;
  modalRecord.value = record;
  modalFormId.value = formId;
  const form = getFormById(formId);
  if (!form) return;
  const fieldsForForm = getFieldsForForm(formId);
  modalFields.value = fieldsForForm;
  if (record) {
    modalFormData.value = { ...record };
  } else {
    const initial = {};
    for (const field of fieldsForForm) {
      if (field.type === "checkbox") initial[field.key] = false;
      else if (field.type === "multiselect") initial[field.key] = [];
      else initial[field.key] = "";
    }
    modalFormData.value = initial;
  }
}

function closeModal() {
  modalVisible.value = false;
  modalRecord.value = null;
  modalFormId.value = null;
  modalFormData.value = {};
  modalFields.value = [];
}

async function saveModalRecord() {
  const formId = modalFormId.value;
  if (!formId) return;
  if (modalRecord.value) {
    await updateRecord(formId, modalRecord.value.id, modalFormData.value);
  } else {
    await addRecord(formId, modalFormData.value);
  }
  closeModal();
  const tableToRefresh = tables.value.find(t => t.formId === formId);
  if (tableToRefresh) showTableData(tableToRefresh.id);
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str).replace(/[&<>]/g, function (m) {
    if (m === "&") return "&amp;";
    if (m === "<") return "&lt;";
    if (m === ">") return "&gt;";
    return m;
  });
}
</script>

<style scoped>
.tables-manager {
  width: 100%;
  max-width: 100%;
  padding: 20px;
  background: #f8f9fa;
  box-sizing: border-box;
  min-height: 100vh;
}
.tables-manager__toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.tables-manager__btn {
  background: #42b983;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
}
.tables-manager__list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 20px;
}
.tables-manager__table-item {
  display: flex;
  align-items: center;
  gap: 8px;
}
.tables-manager__show-table {
  background: #e5e7eb;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
}
.tables-manager__delete-table {
  background: #ef4444;
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.75rem;
}
.tables-manager__data {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-top: 20px;
  overflow-x: auto;
}
.tables-manager__data-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 16px;
}
.tables-manager__data-table th,
.tables-manager__data-table td {
  border: 1px solid #e5e7eb;
  padding: 8px 12px;
  text-align: left;
}
.tables-manager__data-table th {
  background: #f3f4f6;
}
.tables-manager__add-record-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  margin-bottom: 12px;
}
.tables-manager__modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.tables-manager__modal-content {
  background: white;
  border-radius: 12px;
  padding: 24px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}
.tables-manager__form-group {
  margin-bottom: 16px;
}
.tables-manager__form-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 4px;
  color: #000;
}
.tables-manager__form-group input,
.tables-manager__form-group select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 6px;
}
.tables-manager__modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
}
.tables-manager__save-btn {
  background: #42b983;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
}
.tables-manager__cancel-btn {
  background: #6c757d;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
}
</style>