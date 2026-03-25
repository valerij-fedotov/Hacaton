<template>
  <div class="fields-manager">
    <div class="fields-manager__toolbar">
      <button class="fields-manager__add-btn" @click="openAddForm">
        + Добавить поле
      </button>
    </div>

    <!-- Форма создания/редактирования -->
    <div v-if="showForm" class="fields-manager__modal">
      <div class="fields-manager__form">
        <h3 class="fields-manager__form-title">
          {{ editMode ? "Редактировать поле" : "Новое поле" }}
        </h3>
        <div class="fields-manager__form-group">
          <label class="fields-manager__label">Название поля (name):</label>
          <input
            class="fields-manager__input"
            v-model="formData.name"
            placeholder="Например: Дата ДТП"
          />
        </div>
        <div class="fields-manager__form-group">
          <label class="fields-manager__label">Технический ключ (key):</label>
          <input
            class="fields-manager__input"
            v-model="formData.key"
            placeholder="Например: accident_date"
          />
        </div>
        <div class="fields-manager__form-group">
          <label class="fields-manager__label">Тип поля:</label>
          <select class="fields-manager__select" v-model="formData.type">
            <option value="string">Строка</option>
            <option value="text">Длинный текст</option>
            <option value="number">Число</option>
            <option value="date">Дата</option>
            <option value="datetime">Дата и время</option>
            <option value="period">Период</option>
            <option value="radio">Radio</option>
            <option value="checkbox">Checkbox</option>
            <option value="select">Выпадающий список</option>
            <option value="multiselect">Множественный выбор</option>
            <option value="coordinates">Координаты</option>
          </select>
        </div>

        <!-- Для select/multiselect/radio – варианты -->
        <div
          v-if="['select', 'multiselect', 'radio'].includes(formData.type)"
          class="fields-manager__form-group"
        >
          <label class="fields-manager__label">Варианты (через запятую):</label>
          <input
            class="fields-manager__input"
            v-model="optionsString"
            placeholder="Столкновение, Наезд, Опрокидывание"
          />
        </div>

        <!-- Для числа – min/max -->
        <div
          v-if="formData.type === 'number'"
          class="fields-manager__form-group fields-manager__form-row"
        >
          <div>
            <label class="fields-manager__label">Минимум:</label>
            <input
              class="fields-manager__input"
              type="number"
              v-model.number="formData.options.min"
            />
          </div>
          <div>
            <label class="fields-manager__label">Максимум:</label>
            <input
              class="fields-manager__input"
              type="number"
              v-model.number="formData.options.max"
            />
          </div>
        </div>

        <div class="fields-manager__form-actions">
          <button class="fields-manager__save-btn" @click="saveField">
            Сохранить
          </button>
          <button class="fields-manager__cancel-btn" @click="closeForm">
            Отмена
          </button>
        </div>
      </div>
    </div>

    <!-- Сетка карточек -->
    <div class="fields-manager__grid">
      <div v-for="field in fields" :key="field.id" class="fields-manager__card">
        <div class="fields-manager__card-content">
          <div class="fields-manager__card-label">{{ field.name }}</div>
          <div class="fields-manager__card-type">{{ field.type }}</div>
          <div class="fields-manager__card-description">
            {{ getDescription(field) }}
          </div>
          <div class="fields-manager__card-props" v-if="getProps(field)">
            {{ getProps(field) }}
          </div>
        </div>

        <div class="fields-manager__card-menu">
          <button
            class="fields-manager__menu-btn"
            @click.stop="toggleMenu(field.id)"
          >
            ⋮
          </button>
          <div
            v-if="openMenuId === field.id"
            class="fields-manager__dropdown"
            @click.stop
          >
            <button
              class="fields-manager__dropdown-item"
              @click="editField(field)"
            >
              ✏️ Редактировать
            </button>
            <button
              class="fields-manager__dropdown-item fields-manager__dropdown-item--danger"
              @click="deleteFieldById(field.id)"
            >
              🗑️ Удалить
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import {
  fields,
  addField,
  updateField,
  deleteField,
  forms,
} from "../stores/appData";

const showForm = ref(false);
const editMode = ref(false);
const formData = ref({
  id: null,
  name: "",
  key: "",
  type: "string",
  options: {},
});
const optionsString = ref("");
const openMenuId = ref(null);

function openAddForm() {
  editMode.value = false;
  formData.value = { id: null, name: "", key: "", type: "string", options: {} };
  optionsString.value = "";
  showForm.value = true;
}

function editField(field) {
  closeMenu();
  editMode.value = true;
  formData.value = {
    id: field.id,
    name: field.name,
    key: field.key,
    type: field.type,
    options: { ...field.options },
  };
  if (
    ["select", "multiselect", "radio"].includes(field.type) &&
    field.options?.values
  ) {
    optionsString.value = field.options.values.join(", ");
  } else {
    optionsString.value = "";
  }
  showForm.value = true;
}

function closeForm() {
  showForm.value = false;
}

async function saveField() {
  if (!formData.value.name.trim()) {
    alert("Введите название поля");
    return;
  }
  if (!formData.value.key.trim()) {
    alert("Введите технический ключ");
    return;
  }
  const existing = fields.value.find(
    (f) =>
      f.key.toLowerCase() === formData.value.key.toLowerCase() &&
      f.id !== formData.value.id
  );
  if (existing) {
    alert("Поле с таким ключом уже существует");
    return;
  }

  const newOptions = { ...formData.value.options };
  if (["select", "multiselect", "radio"].includes(formData.value.type)) {
    if (optionsString.value.trim()) {
      newOptions.values = optionsString.value.split(",").map((s) => s.trim());
    } else {
      delete newOptions.values;
    }
  }

  const field = {
    name: formData.value.name,
    key: formData.value.key,
    type: formData.value.type,
    options: newOptions,
  };

  try {
    if (editMode.value) {
      await updateField(formData.value.id, field);
    } else {
      await addField(field);
    }
    closeForm();
  } catch (error) {
    console.error(error);
    alert("Ошибка при сохранении поля");
  }
}

async function deleteFieldById(id) {
  closeMenu();
  const usedInForms = forms.value.some((form) => form.field_ids.includes(id));
  if (usedInForms) {
    alert(
      "Поле используется в одной или нескольких формах. Сначала удалите поле из форм."
    );
    return;
  }
  if (confirm("Удалить поле? Это может затронуть формы.")) {
    try {
      await deleteField(id);
    } catch (error) {
      console.error(error);
      alert("Ошибка при удалении поля");
    }
  }
}

function getDescription(field) {
  const descriptions = {
    string: "Однострочное текстовое поле",
    text: "Многострочное поле для больших текстов",
    number: "Числовое поле",
    date: "Выбор даты (календарь)",
    datetime: "Выбор даты и времени",
    period: "Диапазон дат (от — до)",
    radio: "Выбор одного варианта из списка",
    checkbox: "Флажок (да/нет)",
    select: "Одиночный выбор из выпадающего списка",
    multiselect: "Выбор нескольких значений",
    coordinates: "Географические координаты (широта/долгота)",
  };
  return descriptions[field.type] || "Пользовательское поле";
}

function getProps(field) {
  const parts = [];
  if (field.type === "number" && field.options) {
    if (field.options.min !== undefined) parts.push(`min=${field.options.min}`);
    if (field.options.max !== undefined) parts.push(`max=${field.options.max}`);
  }
  if (
    ["select", "multiselect", "radio"].includes(field.type) &&
    field.options?.values?.length
  ) {
    parts.push(`${field.options.values.length} вариантов`);
  }
  return parts.join(", ");
}

function toggleMenu(id) {
  openMenuId.value = openMenuId.value === id ? null : id;
}

function closeMenu() {
  openMenuId.value = null;
}

function handleClickOutside(event) {
  if (openMenuId.value !== null) {
    const menuBtn = event.target.closest(".fields-manager__menu-btn");
    const dropdown = event.target.closest(".fields-manager__dropdown");
    if (!menuBtn && !dropdown) {
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
</script>

<style scoped>
/* Тёмная тема */
.fields-manager {
  width: 100%;
  max-width: 100%;
  padding: 20px;
  background: #121212;
  box-sizing: border-box;
  min-height: 100vh;
}
.fields-manager__toolbar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 24px;
}
.fields-manager__add-btn {
  background: #3ecf8e;
  color: #121212;
  border: none;
  padding: 8px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.2s;
}
.fields-manager__add-btn:hover {
  background: #2eab72;
  color: #ffffff;
}
.fields-manager__modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.fields-manager__form {
  background: #1e1e1e;
  padding: 24px;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
  color: #ffffff;
}
.fields-manager__form-title {
  margin-top: 0;
  margin-bottom: 20px;
  color: #ffffff;
}
.fields-manager__form-group {
  margin-bottom: 16px;
}
.fields-manager__form-row {
  display: flex;
  gap: 12px;
}
.fields-manager__form-row > div {
  flex: 1;
}
.fields-manager__label {
  display: block;
  font-weight: 600;
  margin-bottom: 6px;
  color: #ffffff;
}
.fields-manager__input,
.fields-manager__select,
.fields-manager__textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #afafaf;
  border-radius: 6px;
  font-size: 1rem;
  box-sizing: border-box;
  background: #2a2a2a;
  color: #ffffff;
}
.fields-manager__input::placeholder,
.fields-manager__select::placeholder,
.fields-manager__textarea::placeholder {
  color: #afafaf;
}
.fields-manager__form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
}
.fields-manager__save-btn {
  background: #3ecf8e;
  color: #121212;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
}
.fields-manager__save-btn:hover {
  background: #2eab72;
  color: #ffffff;
}
.fields-manager__cancel-btn {
  background: #afafaf;
  color: #121212;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
}
.fields-manager__cancel-btn:hover {
  background: #8f8f8f;
  color: #ffffff;
}
.fields-manager__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  width: 100%;
}
.fields-manager__card {
  background: #1e1e1e;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  padding: 16px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  transition: transform 0.2s, box-shadow 0.2s;
  position: relative;
}
.fields-manager__card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
}
.fields-manager__card-content {
  flex: 1;
}
.fields-manager__card-label {
  font-weight: 600;
  font-size: 1.1rem;
  margin-bottom: 8px;
  color: #ffffff;
}
.fields-manager__card-type {
  font-size: 0.7rem;
  font-family: monospace;
  background: #2a2a2a;
  display: inline-block;
  padding: 2px 6px;
  border-radius: 20px;
  color: #afafaf;
  margin-bottom: 12px;
}
.fields-manager__card-description {
  font-size: 0.85rem;
  color: #afafaf;
  margin-bottom: 8px;
}
.fields-manager__card-props {
  font-size: 0.75rem;
  color: #afafaf;
  font-style: italic;
  background: #2a2a2a;
  padding: 2px 6px;
  border-radius: 4px;
  display: inline-block;
}
.fields-manager__card-menu {
  position: absolute;
  top: 12px;
  right: 12px;
}
.fields-manager__menu-btn {
  background: none;
  border: none;
  font-size: 1.6rem;
  line-height: 1;
  cursor: pointer;
  padding: 0 4px;
  color: #afafaf;
  transition: color 0.2s;
}
.fields-manager__menu-btn:hover {
  color: #ffffff;
}
.fields-manager__dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background: #2a2a2a;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  min-width: 150px;
  z-index: 10;
  margin-top: 4px;
  overflow: hidden;
}
.fields-manager__dropdown-item {
  display: block;
  width: 100%;
  text-align: left;
  padding: 8px 12px;
  background: none;
  border: none;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.2s;
  color: #ffffff;
}
.fields-manager__dropdown-item:hover {
  background: #3a3a3a;
}
.fields-manager__dropdown-item--danger {
  color: #ff6b6b;
}
.fields-manager__dropdown-item--danger:hover {
  background: #3a2a2a;
}
@media (max-width: 768px) {
  .fields-manager {
    padding: 12px;
  }
  .fields-manager__grid {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 16px;
  }
  .fields-manager__card-label {
    font-size: 1rem;
  }
}
</style>