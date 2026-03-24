<template>
  <div class="forms-manager">
    <div class="forms-manager__toolbar">
      <span>Выберите или создайте форму</span>
      <button class="forms-manager__btn" @click="createNewForm">
        + Новая форма
      </button>
    </div>

    <div class="forms-manager__list">
      <div
        v-for="form in forms"
        :key="form.id"
        class="forms-manager__form-item"
      >
        <button
          class="forms-manager__select-form"
          :class="{ active: selectedFormId === form.id }"
          @click="selectForm(form.id)"
        >
          {{ form.name }}
        </button>
        <button
          class="forms-manager__delete-form"
          @click="deleteFormById(form.id)"
        >
          Удалить форму
        </button>
      </div>
    </div>

    <div class="forms-manager__editor">
      <h3>Редактор формы</h3>
      <div class="forms-manager__form-group">
        <label>Название формы:</label>
        <input v-model="editingFormName" placeholder="Например: Учет ДТП" />
      </div>
      <div class="forms-manager__fields-container">
        <div>
          <strong
            >Выбранные поля (порядок можно менять перетаскиванием):</strong
          >
        </div>
        <div class="forms-manager__selected-fields">
          <div
            v-for="fieldId in selectedFieldIds"
            :key="fieldId"
            class="forms-manager__selected-field"
          >
            {{ getFieldById(fieldId)?.name }} ({{
              getFieldById(fieldId)?.type
            }})
            <button
              class="forms-manager__remove-field"
              @click="removeFieldFromForm(fieldId)"
            >
              ✖️
            </button>
          </div>
        </div>
        <div><strong>Доступные поля:</strong></div>
        <div class="forms-manager__available-fields">
          <button
            v-for="field in availableFields"
            :key="field.id"
            class="forms-manager__add-field"
            @click="addFieldToForm(field.id)"
          >
            + {{ field.name }}
          </button>
        </div>
      </div>
      <button class="forms-manager__save-btn" @click="saveForm">
        Сохранить форму
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import {
  fields,
  forms,
  getFieldById,
  addForm,
  updateForm,
  deleteForm,
} from "../stores/appData";

const selectedFormId = ref(null);
const editingFormName = ref("");

const selectedFieldIds = computed(() => {
  const form = forms.value.find((f) => f.id === selectedFormId.value);
  return form ? form.fieldIds : [];
});

const availableFields = computed(() => {
  const used = selectedFieldIds.value;
  return fields.value.filter((f) => !used.includes(f.id));
});

function createNewForm() {
  selectedFormId.value = null;
  editingFormName.value = "";
}

function selectForm(id) {
  selectedFormId.value = id;
  const form = forms.value.find((f) => f.id === id);
  editingFormName.value = form ? form.name : "";
}

function deleteFormById(id) {
  if (
    confirm(
      "Удалить форму? Все данные по ней останутся, но будут недоступны через интерфейс."
    )
  ) {
    deleteForm(id);
    if (selectedFormId.value === id) {
      selectedFormId.value = null;
      editingFormName.value = "";
    }
  }
}

function addFieldToForm(fieldId) {
  if (!selectedFormId.value) {
    alert("Сначала выберите или создайте форму");
    return;
  }
  const form = forms.value.find((f) => f.id === selectedFormId.value);
  if (form && !form.fieldIds.includes(fieldId)) {
    form.fieldIds.push(fieldId);
  }
}

function removeFieldFromForm(fieldId) {
  if (!selectedFormId.value) return;
  const form = forms.value.find((f) => f.id === selectedFormId.value);
  if (form) {
    form.fieldIds = form.fieldIds.filter((id) => id !== fieldId);
  }
}
function saveForm() {
  if (!editingFormName.value.trim()) {
    alert("Введите название формы");
    return;
  }
  if (!selectedFormId.value) {
    addForm({ name: editingFormName.value, field_ids: [] });  
    alert("Форма создана. Добавьте поля в редакторе.");
  } else {
    updateForm(selectedFormId.value, { name: editingFormName.value });
    alert("Форма сохранена");
  }
}
</script>

<style scoped>
.forms-manager {
  width: 100%;
  max-width: 100%;
  padding: 20px;
  background: #f8f9fa;
  box-sizing: border-box;
  min-height: 100vh;
}
.forms-manager__toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.forms-manager__btn {
  background: #42b983;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
}
.forms-manager__list {
  margin-bottom: 20px;
}
.forms-manager__form-item {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-right: 16px;
  margin-bottom: 8px;
}
.forms-manager__select-form {
  background: #e5e7eb;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
}
.forms-manager__select-form.active {
  background: #3b82f6;
  color: white;
}
.forms-manager__delete-form {
  background: #ef4444;
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.75rem;
}
.forms-manager__editor {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}
.forms-manager__form-group {
  margin-bottom: 16px;
}
.forms-manager__form-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 4px;
  color: #000;
}
.forms-manager__form-group input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 6px;
}
.forms-manager__fields-container {
  margin: 16px 0;
}
.forms-manager__selected-fields,
.forms-manager__available-fields {
  margin: 8px 0;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.forms-manager__selected-field {
  background: #f3f4f6;
  padding: 6px 12px;
  border-radius: 20px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}
.forms-manager__remove-field {
  background: none;
  border: none;
  cursor: pointer;
  color: #ef4444;
}
.forms-manager__add-field {
  background: #3b82f6;
  border: none;
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  cursor: pointer;
}
.forms-manager__save-btn {
  background: #10b981;
  border: none;
  color: white;
  padding: 6px 16px;
  border-radius: 6px;
  cursor: pointer;
}

/*span,
strong,
h3 {
  color: #000;
}*/
</style>