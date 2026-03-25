<template>
  <div class="forms-manager">
    <div class="forms-manager__header">
      <h2>Редактор форм</h2>
      <button
        class="forms-manager__btn forms-manager__btn--primary"
        @click="createNewForm"
      >
        + Новая форма
      </button>
    </div>

    <div class="forms-manager__layout">
      <!-- Список форм -->
      <div class="forms-manager__sidebar">
        <div class="forms-manager__sidebar-title">Список форм</div>
        <div class="forms-manager__form-list">
          <div
            v-for="form in forms"
            :key="form.id"
            class="forms-manager__form-card"
            :class="{ active: selectedFormId === form.id }"
            @click="selectForm(form.id)"
          >
            <div class="forms-manager__form-name">{{ form.name }}</div>
            <button
              class="forms-manager__form-delete"
              @click.stop="deleteFormById(form.id)"
              title="Удалить форму"
            >
              🗑️
            </button>
          </div>
          <div v-if="forms.length === 0" class="forms-manager__empty">
            Нет форм. Создайте первую форму.
          </div>
        </div>
      </div>

      <!-- Редактор формы -->
      <div class="forms-manager__editor" v-if="selectedFormId || isNewForm">
        <div class="forms-manager__editor-header">
          <h3>
            {{ isNewForm ? "Создание новой формы" : "Редактирование формы" }}
          </h3>
          <div class="forms-manager__editor-actions">
            <button
              class="forms-manager__btn forms-manager__btn--save"
              @click="saveForm"
            >
              Сохранить
            </button>
          </div>
        </div>

        <div class="forms-manager__form-group">
          <label>Название формы:</label>
          <input
            v-model="editingFormName"
            placeholder="Например: Учет ДТП"
            class="forms-manager__input"
          />
        </div>

        <div class="forms-manager__fields-section">
          <div class="forms-manager__section-title">
            <span>Поля формы (порядок можно менять перетаскиванием)</span>
            <span class="forms-manager__fields-count"
              >{{ selectedFieldIds.length }} полей</span
            >
          </div>

          <div
            v-if="selectedFieldIds.length === 0"
            class="forms-manager__empty-fields"
          >
            Добавьте поля из списка справа
          </div>

          <div
            v-else
            class="forms-manager__selected-fields"
            @dragover.prevent
            @drop="handleDrop"
          >
            <div
              v-for="(fieldId, index) in selectedFieldIds"
              :key="fieldId"
              class="forms-manager__selected-field"
              draggable="true"
              @dragstart="handleDragStart($event, index)"
              @dragend="handleDragEnd"
              :data-index="index"
            >
              <div class="forms-manager__field-info">
                <span class="forms-manager__field-name">{{
                  getFieldById(fieldId)?.name
                }}</span>
                <span class="forms-manager__field-type">{{
                  getTypeLabel(getFieldById(fieldId)?.type)
                }}</span>
              </div>
              <div class="forms-manager__field-actions">
                <button
                  class="forms-manager__remove-btn"
                  @click="removeFieldFromForm(fieldId)"
                  title="Удалить"
                >
                  ✖
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="forms-manager__available-section">
          <div class="forms-manager__section-title">Доступные поля</div>
          <div class="forms-manager__available-fields">
            <button
              v-for="field in availableFields"
              :key="field.id"
              class="forms-manager__add-field"
              @click="addFieldToForm(field.id)"
            >
              + {{ field.name }}
              <span class="forms-manager__field-type-badge">{{
                getTypeLabel(field.type)
              }}</span>
            </button>
            <div
              v-if="availableFields.length === 0"
              class="forms-manager__empty"
            >
              Нет доступных полей. Сначала создайте поля в разделе "Поля".
            </div>
          </div>
        </div>
      </div>

      <div v-else class="forms-manager__placeholder">
        <p>Выберите форму из списка или создайте новую</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import {
  fields,
  forms,
  tables,
  getFieldById,
  addForm,
  updateForm,
  deleteForm,
} from "../stores/appData";

const selectedFormId = ref(null);
const editingFormName = ref("");
const isNewForm = ref(false);
const dragStartIndex = ref(null);
const tempFormFields = ref([]);

const selectedFieldIds = computed(() => {
  if (isNewForm.value) {
    return tempFormFields.value;
  }
  if (!selectedFormId.value) return [];
  const form = forms.value.find((f) => f.id === selectedFormId.value);
  return form ? form.field_ids : [];
});

const availableFields = computed(() => {
  const used = selectedFieldIds.value;
  return fields.value.filter((f) => !used.includes(f.id));
});

function handleDragStart(event, index) {
  dragStartIndex.value = index;
  event.dataTransfer.effectAllowed = "move";
  event.target.classList.add("dragging");
}

function handleDragEnd(event) {
  event.target.classList.remove("dragging");
  dragStartIndex.value = null;
}

function handleDrop(event) {
  event.preventDefault();
  const targetElement = event.target.closest(".forms-manager__selected-field");
  if (!targetElement) return;
  const dropIndex = parseInt(targetElement.dataset.index);
  if (isNaN(dropIndex) || dragStartIndex.value === null) return;

  if (dragStartIndex.value !== dropIndex) {
    let currentFieldIds;
    if (isNewForm.value) {
      currentFieldIds = [...tempFormFields.value];
    } else {
      const form = forms.value.find((f) => f.id === selectedFormId.value);
      if (!form) return;
      currentFieldIds = [...form.field_ids];
    }
    const [movedItem] = currentFieldIds.splice(dragStartIndex.value, 1);
    currentFieldIds.splice(dropIndex, 0, movedItem);
    if (isNewForm.value) {
      tempFormFields.value = currentFieldIds;
    } else {
      const form = forms.value.find((f) => f.id === selectedFormId.value);
      if (form) form.field_ids = currentFieldIds;
    }
  }
  dragStartIndex.value = null;
}

function addFieldToForm(fieldId) {
  if (!selectedFormId.value && !isNewForm.value) {
    alert("Сначала выберите или создайте форму");
    return;
  }
  if (isNewForm.value) {
    if (!tempFormFields.value.includes(fieldId)) {
      tempFormFields.value = [...tempFormFields.value, fieldId];
    }
    return;
  }
  const form = forms.value.find((f) => f.id === selectedFormId.value);
  if (form && !form.field_ids.includes(fieldId)) {
    form.field_ids.push(fieldId);
  }
}

function removeFieldFromForm(fieldId) {
  if (!selectedFormId.value && !isNewForm.value) return;
  if (isNewForm.value) {
    tempFormFields.value = tempFormFields.value.filter((id) => id !== fieldId);
    return;
  }
  const form = forms.value.find((f) => f.id === selectedFormId.value);
  if (form) {
    form.field_ids = form.field_ids.filter((id) => id !== fieldId);
  }
}

function createNewForm() {
  selectedFormId.value = null;
  editingFormName.value = "";
  isNewForm.value = true;
  tempFormFields.value = [];
}

function selectForm(id) {
  selectedFormId.value = id;
  editingFormName.value = forms.value.find((f) => f.id === id)?.name || "";
  isNewForm.value = false;
  tempFormFields.value = [];
}

async function deleteFormById(id) {
  const linkedTables = tables.value.filter((t) => t.form_id === id);
  let confirmMessage = "Вы уверены, что хотите удалить форму?";
  if (linkedTables.length > 0) {
    const tableNames = linkedTables.map((t) => t.name).join(", ");
    confirmMessage = `Форма используется в следующих таблицах: ${tableNames}. Все связанные таблицы и записи будут также удалены. Действие необратимо. Продолжить?`;
  } else {
    confirmMessage =
      "Форма не используется в таблицах. Все связанные данные (таблицы и записи) будут удалены. Действие необратимо. Продолжить?";
  }
  if (confirm(confirmMessage)) {
    try {
      await deleteForm(id);
      if (selectedFormId.value === id) {
        selectedFormId.value = null;
        editingFormName.value = "";
        isNewForm.value = false;
      }
    } catch (error) {
      console.error(error);
      alert("Ошибка при удалении формы");
    }
  }
}

async function saveForm() {
  if (!editingFormName.value.trim()) {
    alert("Введите название формы");
    return;
  }
  if (isNewForm.value) {
    try {
      const newForm = await addForm({
        name: editingFormName.value,
        field_ids: [...tempFormFields.value],
      });
      if (newForm) {
        alert("Форма создана");
        selectForm(newForm.id);
      } else {
        alert("Ошибка при создании формы");
      }
    } catch (error) {
      console.error(error);
      alert("Ошибка при создании формы");
    }
    isNewForm.value = false;
    tempFormFields.value = [];
  } else {
    try {
      await updateForm(selectedFormId.value, {
        name: editingFormName.value,
        field_ids: [...selectedFieldIds.value],
      });
      alert("Форма сохранена");
    } catch (error) {
      console.error(error);
      alert("Ошибка при сохранении формы");
    }
  }
}

function getTypeLabel(type) {
  const types = {
    string: "Строка",
    text: "Текст",
    number: "Число",
    date: "Дата",
    datetime: "Дата+время",
    period: "Период",
    radio: "Radio",
    checkbox: "Checkbox",
    select: "Выпадающий список",
    multiselect: "Множественный выбор",
    coordinates: "Координаты",
  };
  return types[type] || "Поле";
}
</script>

<style scoped>
/* Базовые стили (тёмная тема) */
.forms-manager {
  width: 100%;
  max-width: 100%;
  padding: 20px;
  background: #121212;
  box-sizing: border-box;
  min-height: 100vh;
  font-family: system-ui, -apple-system, sans-serif;
}

.forms-manager__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 12px;
}

.forms-manager__header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #ffffff;
}

.forms-manager__btn {
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.forms-manager__btn--primary {
  background: #3ecf8e;
  color: #121212;
}
.forms-manager__btn--primary:hover {
  background: #2eab72;
  color: #ffffff;
}

.forms-manager__btn--save {
  background: #3ecf8e;
  color: #121212;
}
.forms-manager__btn--save:hover {
  background: #2eab72;
  color: #ffffff;
}

.forms-manager__layout {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.forms-manager__sidebar {
  flex: 0 0 280px;
  background: #1e1e1e;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
  padding: 16px;
  height: fit-content;
}

.forms-manager__sidebar-title {
  font-weight: 600;
  margin-bottom: 12px;
  color: #ffffff;
  font-size: 1.1rem;
  padding-bottom: 8px;
  border-bottom: 1px solid #afafaf;
}

.forms-manager__form-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.forms-manager__form-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: #2a2a2a;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}
.forms-manager__form-card:hover {
  background: #3a3a3a;
}
.forms-manager__form-card.active {
  background: #1e2a1e;
  border-color: #3ecf8e;
}

.forms-manager__form-name {
  font-weight: 500;
  color: #ffffff;
  word-break: break-word;
}

.forms-manager__form-delete {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #afafaf;
  transition: color 0.2s;
}
.forms-manager__form-delete:hover {
  color: #ff6b6b;
}

.forms-manager__editor {
  flex: 1;
  background: #1e1e1e;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
  padding: 20px;
  min-width: 0; /* предотвращает переполнение */
}

.forms-manager__editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}
.forms-manager__editor-header h3 {
  margin: 0;
  font-size: 1.2rem;
  color: #ffffff;
}

.forms-manager__editor-actions {
  display: flex;
  gap: 8px;
}

.forms-manager__form-group {
  margin-bottom: 24px;
}
.forms-manager__form-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
  color: #ffffff;
}

.forms-manager__input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #afafaf;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.2s;
  background: #2a2a2a;
  color: #ffffff;
  box-sizing: border-box;
}
.forms-manager__input:focus {
  outline: none;
  border-color: #3ecf8e;
}

.forms-manager__fields-section,
.forms-manager__available-section {
  margin-bottom: 24px;
}

.forms-manager__section-title {
  font-weight: 600;
  margin-bottom: 12px;
  color: #ffffff;
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  flex-wrap: wrap;
}
.forms-manager__fields-count {
  font-size: 0.8rem;
  font-weight: normal;
  color: #afafaf;
}

.forms-manager__selected-fields {
  border: 1px solid #afafaf;
  border-radius: 8px;
  background: #2a2a2a;
  overflow: hidden;
}

.forms-manager__selected-field {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  border-bottom: 1px solid #3a3a3a;
  cursor: grab;
  user-select: none;
}
.forms-manager__selected-field:last-child {
  border-bottom: none;
}
.forms-manager__selected-field:active {
  cursor: grabbing;
}
.forms-manager__selected-field.dragging {
  opacity: 0.4;
  cursor: grabbing;
}

.forms-manager__field-info {
  display: flex;
  gap: 8px;
  align-items: baseline;
  flex-wrap: wrap;
}
.forms-manager__field-name {
  font-weight: 500;
  color: #ffffff;
}
.forms-manager__field-type {
  font-size: 0.7rem;
  background: #3a3a3a;
  padding: 2px 6px;
  border-radius: 12px;
  color: #afafaf;
}

.forms-manager__field-actions {
  display: flex;
  gap: 6px;
}

.forms-manager__remove-btn {
  background: none;
  border: none;
  font-size: 1rem;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.2s;
  color: #afafaf;
}
.forms-manager__remove-btn:hover {
  background: #3a2a2a;
  color: #ff6b6b;
}

.forms-manager__available-fields {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.forms-manager__add-field {
  background: #2a2a2a;
  border: 1px solid #afafaf;
  padding: 6px 12px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
  color: #ffffff;
}
.forms-manager__add-field:hover {
  background: #3a3a3a;
  border-color: #3ecf8e;
}

.forms-manager__field-type-badge {
  font-size: 0.7rem;
  background: #3a3a3a;
  padding: 2px 6px;
  border-radius: 12px;
  margin-left: 6px;
  color: #afafaf;
}

.forms-manager__empty-fields,
.forms-manager__empty {
  text-align: center;
  color: #afafaf;
  padding: 20px;
  font-size: 0.9rem;
}

.forms-manager__placeholder {
  flex: 1;
  background: #1e1e1e;
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  color: #afafaf;
}

/* Адаптивность */
@media (max-width: 768px) {
  .forms-manager {
    padding: 12px;
  }

  .forms-manager__layout {
    flex-direction: column;
  }

  .forms-manager__sidebar {
    flex: auto;
    width: 100%;
    margin-bottom: 16px;
  }

  .forms-manager__editor {
    padding: 16px;
  }

  .forms-manager__editor-header {
    flex-direction: column;
    align-items: stretch;
  }

  .forms-manager__editor-actions {
    justify-content: stretch;
  }

  .forms-manager__btn--save {
    width: 100%;
    text-align: center;
  }

  .forms-manager__section-title {
    flex-direction: column;
    gap: 4px;
  }

  .forms-manager__selected-field {
    flex-wrap: wrap;
    gap: 8px;
  }

  .forms-manager__field-info {
    flex: 1;
  }
}

@media (max-width: 480px) {
  .forms-manager__form-card {
    padding: 8px 10px;
  }

  .forms-manager__form-name {
    font-size: 0.9rem;
  }

  .forms-manager__add-field {
    font-size: 0.75rem;
    padding: 5px 10px;
  }
}
</style>