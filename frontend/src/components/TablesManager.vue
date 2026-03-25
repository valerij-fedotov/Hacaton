<template>
  <div class="tables-manager">
    <aside class="tables-manager__sidebar">
      <div class="sidebar__header">
        <h3>Таблицы</h3>
        <button class="btn btn-primary" @click="openCreateTableModal">
          + Создать
        </button>
      </div>
      <div class="sidebar__list">
        <div
          v-for="table in tables"
          :key="table.id"
          class="table-card"
          :class="{ 'table-card--active': currentTableId === table.id }"
          @click="selectTable(table.id)"
        >
          <span class="table-card__name">{{ table.name }}</span>
          <button
            class="table-card__delete"
            @click.stop="deleteTableById(table.id)"
            title="Удалить таблицу"
          >
            🗑️
          </button>
        </div>
        <div v-if="!tables.length" class="sidebar__empty">
          Нет таблиц. Создайте первую!
        </div>
      </div>
    </aside>

    <main class="tables-manager__content">
      <div v-if="currentTable" class="content__wrapper">
        <div class="content__header">
          <h2>{{ currentTable.name }}</h2>
          <button class="btn btn-success" @click="openRecordModal(null)">
            + Новая запись
          </button>
        </div>

        <div class="data-table-container">
          <table class="data-table" v-if="currentRecords.length">
            <thead>
              <tr>
                <th v-for="field in currentFields" :key="field.id">
                  {{ field.name }}
                </th>
                <th style="width: 60px"></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="record in currentRecords" :key="record.id">
                <td v-for="field in currentFields" :key="field.id">
                  {{ formatValue(record[field.key], field) }}
                </td>
                <td class="actions-cell">
                  <div class="menu-wrapper">
                    <button
                      class="menu-trigger"
                      @click.stop="toggleMenu(record.id)"
                    >
                      ⋮
                    </button>
                    <div
                      v-if="openMenuId === record.id"
                      class="dropdown-menu"
                      @click.stop
                    >
                      <button
                        class="dropdown-item"
                        @click="openRecordModal(record)"
                      >
                        ✏️ Редактировать
                      </button>
                      <button
                        class="dropdown-item danger"
                        @click="deleteRecordHandler(record.id)"
                      >
                        🗑️ Удалить
                      </button>
                    </div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-else class="empty-data">
            Нет записей. Нажмите «+ Новая запись», чтобы добавить.
          </div>
        </div>
      </div>
      <div v-else class="content__placeholder">
        Выберите таблицу из списка слева
      </div>
    </main>

    <!-- Модальное окно для создания таблицы -->
    <div
      v-if="showCreateTableModal"
      class="modal"
      @click.self="closeCreateTableModal"
    >
      <div class="modal__content">
        <h3>Создание таблицы</h3>
        <div class="form-group">
          <label>Форма (источник данных)</label>
          <select v-model="newTableFormId">
            <option :value="null">-- Выберите форму --</option>
            <option v-for="form in forms" :key="form.id" :value="form.id">
              {{ form.name }} (ID: {{ form.id }})
            </option>
          </select>
        </div>
        <div class="form-group">
          <label>Название таблицы</label>
          <input
            type="text"
            v-model="newTableName"
            placeholder="Введите название"
          />
        </div>
        <div class="modal__actions">
          <button class="btn btn-secondary" @click="closeCreateTableModal">
            Отмена
          </button>
          <button
            class="btn btn-primary"
            @click="createTable"
            :disabled="!newTableFormId || !newTableName.trim()"
          >
            Создать
          </button>
        </div>
      </div>
    </div>

    <!-- Модальное окно для записи -->
    <div v-if="modalVisible" class="modal" @click.self="closeModal">
      <div class="modal__content record-modal">
        <h3>{{ modalRecord ? "Редактирование записи" : "Новая запись" }}</h3>
        <div v-for="field in modalFields" :key="field.id" class="form-group">
          <label>
            {{ field.name }}
            <span class="field-type-hint">{{
              getFieldTypeHint(field.type)
            }}</span>
          </label>

          <input
            v-if="field.type === 'string'"
            type="text"
            v-model="modalFormData[field.key]"
          />
          <textarea
            v-else-if="field.type === 'text'"
            v-model="modalFormData[field.key]"
            rows="3"
          ></textarea>
          <input
            v-else-if="field.type === 'number'"
            type="number"
            v-model.number="modalFormData[field.key]"
          />
          <input
            v-else-if="field.type === 'date'"
            type="date"
            v-model="modalFormData[field.key]"
          />
          <input
            v-else-if="field.type === 'datetime'"
            type="datetime-local"
            :value="formatDateTimeLocal(modalFormData[field.key])"
            @input="updateDateTime(field.key, $event.target.value)"
          />
          <div v-else-if="field.type === 'period'" class="double-field">
            <input
              type="date"
              :value="periodStart[field.key]"
              @input="updatePeriodStart(field.key, $event.target.value)"
              placeholder="Начало"
            />
            <span>–</span>
            <input
              type="date"
              :value="periodEnd[field.key]"
              @input="updatePeriodEnd(field.key, $event.target.value)"
              placeholder="Конец"
            />
          </div>
          <input
            v-else-if="field.type === 'checkbox'"
            type="checkbox"
            v-model="modalFormData[field.key]"
          />
          <div v-else-if="field.type === 'radio'" class="radio-group">
            <label
              v-for="opt in field.options.values || []"
              :key="opt"
              class="radio-label"
            >
              <input
                type="radio"
                :value="opt"
                v-model="modalFormData[field.key]"
              />
              {{ opt }}
            </label>
          </div>
          <select
            v-else-if="field.type === 'select'"
            v-model="modalFormData[field.key]"
          >
            <option v-for="opt in field.options.values || []" :key="opt">
              {{ opt }}
            </option>
          </select>
          <select
            v-else-if="field.type === 'multiselect'"
            multiple
            v-model="modalFormData[field.key]"
          >
            <option v-for="opt in field.options.values || []" :key="opt">
              {{ opt }}
            </option>
          </select>
          <div v-else-if="field.type === 'coordinates'" class="double-field">
            <input
              type="number"
              step="any"
              :value="coordLat[field.key]"
              @input="updateCoordLat(field.key, $event.target.value)"
              placeholder="Широта"
            />
            <span>,</span>
            <input
              type="number"
              step="any"
              :value="coordLon[field.key]"
              @input="updateCoordLon(field.key, $event.target.value)"
              placeholder="Долгота"
            />
          </div>
          <input v-else type="text" v-model="modalFormData[field.key]" />
        </div>
        <div class="modal__actions">
          <button class="btn btn-secondary" @click="closeModal">Отмена</button>
          <button class="btn btn-primary" @click="saveModalRecord">
            Сохранить
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted, onUnmounted } from "vue";
import {
  fields,
  forms,
  getFormById,
  getFieldsForForm,
  addTable,
  deleteTable,
  tables,
  records,
  deleteRecord,
  updateRecord,
  addRecord,
  addForm,
} from "../stores/appData";

const currentTableId = ref(null);
const modalVisible = ref(false);
const modalRecord = ref(null);
const modalFormData = ref({});
const modalFields = ref([]);
const showCreateTableModal = ref(false);
const newTableFormId = ref(null);
const newTableName = ref("");

const periodStart = reactive({});
const periodEnd = reactive({});
const coordLat = reactive({});
const coordLon = reactive({});

const openMenuId = ref(null);

const currentTable = computed(() => {
  if (!currentTableId.value) return null;
  return tables.value.find((t) => t.id === currentTableId.value);
});

const currentForm = computed(() => {
  if (!currentTable.value) return null;
  return getFormById(currentTable.value.formId);
});

const currentFields = computed(() => {
  if (!currentForm.value) return [];
  return getFieldsForForm(currentForm.value.id);
});

const currentRecords = computed(() => {
  if (!currentForm.value) return [];
  return records[currentForm.value.id] || [];
});

function selectTable(id) {
  currentTableId.value = id;
  closeMenu();
}

async function deleteTableById(id) {
  if (confirm("Удалить таблицу?")) {
    try {
      await deleteTable(id);
      if (currentTableId.value === id) {
        currentTableId.value = null;
      }
    } catch (error) {
      console.error(error);
      alert("Ошибка при удалении таблицы");
    }
  }
  closeMenu();
}

function openCreateTableModal() {
  showCreateTableModal.value = true;
  newTableFormId.value = null;
  newTableName.value = "";
  closeMenu();
}

function closeCreateTableModal() {
  showCreateTableModal.value = false;
}

async function createTable() {
  if (!newTableFormId.value || !newTableName.value.trim()) return;

  const sourceForm = getFormById(newTableFormId.value);
  if (!sourceForm) {
    alert("Форма не найдена");
    return;
  }

  try {
    const copiedForm = await addForm({
      name: `${sourceForm.name} (копия для ${newTableName.value})`,
      field_ids: [...sourceForm.field_ids],
    });
    await addTable({
      name: newTableName.value.trim(),
      formId: copiedForm.id,
      columns: [...copiedForm.field_ids],
    });
    closeCreateTableModal();
    alert("Таблица создана");
  } catch (error) {
    console.error(error);
    alert("Ошибка при создании таблицы");
  }
}

function parsePeriodValue(value) {
  if (!value) return { start: "", end: "" };
  const parts = value.split(" - ");
  if (parts.length === 2) {
    return { start: parts[0], end: parts[1] };
  }
  return { start: value, end: "" };
}

function parseCoordValue(value) {
  if (!value) return { lat: "", lon: "" };
  const parts = value.split(",");
  if (parts.length === 2) {
    return { lat: parts[0].trim(), lon: parts[1].trim() };
  }
  return { lat: value, lon: "" };
}

function updatePeriodStart(key, startValue) {
  periodStart[key] = startValue;
  const end = periodEnd[key] !== undefined ? periodEnd[key] : "";
  modalFormData.value[key] =
    startValue && end ? `${startValue} - ${end}` : startValue || end;
}

function updatePeriodEnd(key, endValue) {
  periodEnd[key] = endValue;
  const start = periodStart[key] !== undefined ? periodStart[key] : "";
  modalFormData.value[key] =
    start && endValue ? `${start} - ${endValue}` : start || endValue;
}

function updateCoordLat(key, latValue) {
  coordLat[key] = latValue;
  const lon = coordLon[key] !== undefined ? coordLon[key] : "";
  modalFormData.value[key] =
    latValue && lon ? `${latValue}, ${lon}` : latValue || lon;
}

function updateCoordLon(key, lonValue) {
  coordLon[key] = lonValue;
  const lat = coordLat[key] !== undefined ? coordLat[key] : "";
  modalFormData.value[key] =
    lat && lonValue ? `${lat}, ${lonValue}` : lat || lon;
}

function formatDateTimeLocal(value) {
  if (!value) return "";
  let formatted = value.replace(" ", "T");
  if (formatted.length === 16) return formatted;
  if (formatted.length >= 19) return formatted.slice(0, 16);
  return formatted;
}

function updateDateTime(key, localValue) {
  modalFormData.value[key] = localValue.replace("T", " ") + ":00";
}

async function deleteRecordHandler(recordId) {
  if (!currentForm.value) return;
  if (confirm("Удалить запись?")) {
    try {
      await deleteRecord(currentForm.value.id, recordId);
      closeMenu();
    } catch (error) {
      console.error(error);
      alert("Ошибка при удалении записи");
    }
  }
}

function openRecordModal(record = null) {
  if (!currentForm.value) {
    alert("Форма не выбрана");
    return;
  }
  closeMenu();

  modalVisible.value = true;
  modalRecord.value = record;
  const formId = currentForm.value.id;
  const fieldsForForm = getFieldsForForm(formId);
  modalFields.value = fieldsForForm;

  if (record) {
    modalFormData.value = { ...record };
    fieldsForForm.forEach((field) => {
      if (field.type === "period") {
        const { start, end } = parsePeriodValue(record[field.key]);
        periodStart[field.key] = start;
        periodEnd[field.key] = end;
      } else if (field.type === "coordinates") {
        const { lat, lon } = parseCoordValue(record[field.key]);
        coordLat[field.key] = lat;
        coordLon[field.key] = lon;
      }
    });
  } else {
    const initial = {};
    fieldsForForm.forEach((field) => {
      if (field.type === "checkbox") initial[field.key] = false;
      else if (field.type === "multiselect") initial[field.key] = [];
      else if (field.type === "radio") initial[field.key] = "";
      else if (field.type === "period") initial[field.key] = "";
      else if (field.type === "coordinates") initial[field.key] = "";
      else initial[field.key] = "";

      if (field.type === "period") {
        periodStart[field.key] = "";
        periodEnd[field.key] = "";
      } else if (field.type === "coordinates") {
        coordLat[field.key] = "";
        coordLon[field.key] = "";
      }
    });
    modalFormData.value = initial;
  }
}

function closeModal() {
  modalVisible.value = false;
  modalRecord.value = null;
  modalFormData.value = {};
  modalFields.value = [];
  Object.keys(periodStart).forEach((k) => delete periodStart[k]);
  Object.keys(periodEnd).forEach((k) => delete periodEnd[k]);
  Object.keys(coordLat).forEach((k) => delete coordLat[k]);
  Object.keys(coordLon).forEach((k) => delete coordLon[k]);
}

async function saveModalRecord() {
  const formId = currentForm.value?.id;
  if (!formId) return;
  try {
    if (modalRecord.value) {
      await updateRecord(formId, modalRecord.value.id, modalFormData.value);
    } else {
      await addRecord(formId, modalFormData.value);
    }
    closeModal();
  } catch (error) {
    console.error(error);
    alert("Ошибка при сохранении записи");
  }
}

function formatValue(value, field) {
  if (value === undefined || value === null) return "";
  if (field.type === "multiselect" && Array.isArray(value)) {
    return value.join(", ");
  }
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

function toggleMenu(recordId) {
  openMenuId.value = openMenuId.value === recordId ? null : recordId;
}

function closeMenu() {
  openMenuId.value = null;
}

function handleClickOutside(event) {
  if (openMenuId.value !== null) {
    const menuTrigger = event.target.closest(".menu-trigger");
    const dropdown = event.target.closest(".dropdown-menu");
    if (!menuTrigger && !dropdown) {
      closeMenu();
    }
  }
}

onMounted(() => {
  document.addEventListener("click", handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener("click", handleClickOutside);
});

function getFieldTypeHint(type) {
  const hints = {
    string: "текст",
    text: "многострочный текст",
    number: "число",
    date: "дата",
    datetime: "дата+время",
    period: "диапазон дат",
    checkbox: "да/нет",
    radio: "выбор варианта",
    select: "выпадающий список",
    multiselect: "множественный выбор",
    coordinates: "координаты",
  };
  return hints[type] ? `(${hints[type]})` : "";
}
</script>

<style scoped>
/* Базовые стили */
.tables-manager {
  display: flex;
  height: 100%;
  min-height: 100vh;
  background-color: #121212;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial,
    sans-serif;
}

.tables-manager__sidebar {
  width: 280px;
  background-color: #1e1e1e;
  border-right: 1px solid #afafaf;
  display: flex;
  flex-direction: column;
  box-shadow: 1px 0 3px rgba(0, 0, 0, 0.3);
  flex-shrink: 0;
}

.sidebar__header {
  padding: 20px 16px;
  border-bottom: 1px solid #afafaf;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.sidebar__header h3 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
  color: #ffffff;
}

.sidebar__list {
  flex: 1;
  padding: 12px;
  overflow-y: auto;
}

.table-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  margin-bottom: 8px;
  background-color: #2a2a2a;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}
.table-card:hover {
  background-color: #3a3a3a;
  border-color: #afafaf;
}
.table-card--active {
  background-color: #1e2a1e;
  border-color: #3ecf8e;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}
.table-card__name {
  font-weight: 500;
  color: #ffffff;
}
.table-card__delete {
  background: none;
  border: none;
  font-size: 1.1rem;
  cursor: pointer;
  opacity: 0.6;
  transition: opacity 0.2s;
  padding: 4px 8px;
  border-radius: 6px;
  color: #afafaf;
}
.table-card__delete:hover {
  opacity: 1;
  background-color: #3a2a2a;
  color: #ff6b6b;
}
.sidebar__empty {
  text-align: center;
  color: #afafaf;
  padding: 24px 16px;
  font-size: 0.9rem;
}

.tables-manager__content {
  flex: 1;
  padding: 24px 32px;
  overflow-y: auto;
  min-width: 0; /* для корректного сжатия */
}

.content__wrapper {
  background-color: #1e1e1e;
  border-radius: 20px;
  box-shadow: 0 4px 6px -2px rgba(0, 0, 0, 0.3), 0 1px 2px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.content__header {
  padding: 20px 24px;
  border-bottom: 1px solid #afafaf;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #1e1e1e;
  flex-wrap: wrap;
  gap: 12px;
}
.content__header h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #ffffff;
}

.data-table-container {
  padding: 0 24px 24px 24px;
  overflow-x: auto;
  width: 100%;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 16px;
  font-size: 0.9rem;
  min-width: 500px; /* принудительная минимальная ширина для скролла */
}
.data-table th,
.data-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #afafaf;
  color: #ffffff;
}
.data-table th {
  background-color: #2a2a2a;
  font-weight: 600;
  color: #ffffff;
}
.data-table tr:hover {
  background-color: #2a2a2a;
}

.actions-cell {
  text-align: right;
  width: 60px;
}
.menu-wrapper {
  position: relative;
  display: inline-block;
}
.menu-trigger {
  background: none;
  border: none;
  font-size: 1.4rem;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 8px;
  color: #afafaf;
  transition: background 0.2s;
}
.menu-trigger:hover {
  background-color: #3a3a3a;
  color: #ffffff;
}
.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background-color: #2a2a2a;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  min-width: 150px;
  z-index: 100;
  overflow: hidden;
  margin-top: 4px;
}
.dropdown-item {
  display: block;
  width: 100%;
  text-align: left;
  padding: 10px 16px;
  background: none;
  border: none;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.2s;
  color: #ffffff;
}
.dropdown-item:hover {
  background-color: #3a3a3a;
}
.dropdown-item.danger {
  color: #ff6b6b;
}
.dropdown-item.danger:hover {
  background-color: #3a2a2a;
}

.empty-data {
  text-align: center;
  padding: 48px 24px;
  color: #afafaf;
  font-size: 0.95rem;
}

.content__placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  background-color: #1e1e1e;
  border-radius: 20px;
  box-shadow: 0 4px 6px -2px rgba(0, 0, 0, 0.3);
  color: #afafaf;
  font-size: 1rem;
  padding: 48px;
}

.btn {
  padding: 8px 16px;
  border-radius: 10px;
  font-weight: 500;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  background: none;
}
.btn-primary {
  background-color: #3ecf8e;
  color: #121212;
}
.btn-primary:hover {
  background-color: #2eab72;
  color: #ffffff;
}
.btn-primary:disabled {
  background-color: #afafaf;
  cursor: not-allowed;
}
.btn-success {
  background-color: #3ecf8e;
  color: #121212;
}
.btn-success:hover {
  background-color: #2eab72;
  color: #ffffff;
}
.btn-secondary {
  background-color: #afafaf;
  color: #121212;
}
.btn-secondary:hover {
  background-color: #8f8f8f;
  color: #ffffff;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(2px);
}
.modal__content {
  background-color: #1e1e1e;
  border-radius: 28px;
  padding: 28px;
  width: 90%;
  max-width: 550px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 35px -8px rgba(0, 0, 0, 0.5);
  color: #ffffff;
}
.record-modal .modal__content {
  max-width: 600px;
}
.modal__content h3 {
  margin-top: 0;
  margin-bottom: 24px;
  font-size: 1.5rem;
  font-weight: 600;
  color: #ffffff;
  letter-spacing: -0.01em;
}
.form-group {
  margin-bottom: 20px;
}
.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #ffffff;
  font-size: 0.9rem;
}
.field-type-hint {
  font-size: 0.7rem;
  color: #afafaf;
  font-style: italic;
  margin-left: 8px;
  font-weight: normal;
}
.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #afafaf;
  border-radius: 14px;
  font-size: 0.9rem;
  transition: border 0.2s, box-shadow 0.2s;
  background-color: #2a2a2a;
  color: #ffffff;
  box-sizing: border-box;
}
.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3ecf8e;
  box-shadow: 0 0 0 3px rgba(62, 207, 142, 0.2);
}
.double-field {
  display: flex;
  gap: 12px;
  align-items: center;
}
.double-field input {
  flex: 1;
}
.double-field span {
  color: #afafaf;
  font-weight: 500;
}
.radio-group {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 8px;
}
.radio-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: normal;
  cursor: pointer;
  color: #ffffff;
}
.modal__actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 28px;
}

/* Адаптивность */
@media (max-width: 768px) {
  .tables-manager {
    flex-direction: column;
  }

  .tables-manager__sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid #afafaf;
    flex-shrink: 1;
  }

  .tables-manager__content {
    padding: 16px;
  }

  .content__header {
    flex-direction: column;
    align-items: stretch;
    text-align: center;
  }

  .content__header h2 {
    font-size: 1.3rem;
  }

  .btn-success {
    width: 100%;
    text-align: center;
  }

  .data-table-container {
    padding: 0 16px 16px 16px;
  }

  .data-table {
    font-size: 0.8rem;
    min-width: 400px;
  }

  .data-table th,
  .data-table td {
    padding: 8px 12px;
  }
}

@media (max-width: 480px) {
  .sidebar__header {
    padding: 12px;
  }
  .sidebar__header h3 {
    font-size: 1rem;
  }
  .table-card {
    padding: 8px 12px;
  }
  .table-card__name {
    font-size: 0.9rem;
  }
  .modal__content {
    padding: 20px;
  }
  .modal__content h3 {
    font-size: 1.2rem;
  }
  .double-field {
    flex-direction: column;
  }
  .double-field span {
    display: none;
  }
  .radio-group {
    gap: 8px;
  }
}
</style>