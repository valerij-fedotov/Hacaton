import { ref, reactive } from 'vue';
import {
	getFields as apiGetFields,
	createField as apiCreateField,
	updateField as apiUpdateField,
	deleteField as apiDeleteField,
	getForms as apiGetForms,
	createForm as apiCreateForm,
	updateForm as apiUpdateForm,
	deleteForm as apiDeleteForm,
	getTables as apiGetTables,
	createTable as apiCreateTable,
	deleteTable as apiDeleteTable,
	getRecords as apiGetRecords,
	createRecord as apiCreateRecord,
	updateRecord as apiUpdateRecord,
	deleteRecord as apiDeleteRecord,
	type Field,
	type Form,
	type Table,
	type FormRecord,
} from '../api';

export type { Field, Form, Table };

export interface LocalRecord extends Record<string, any> {
	id: number;
	created_at?: string;
}

export const fields = ref<Field[]>([]);
export const forms = ref<Form[]>([]);
export const tables = ref<Table[]>([]);
export const records = reactive<Record<number, LocalRecord[]>>({});

function mapApiRecordToLocal(apiRecord: FormRecord, formFields: Field[]): LocalRecord {
	const localRecord: LocalRecord = { id: apiRecord.id };
	for (const [key, value] of Object.entries(apiRecord.data)) {
		localRecord[key] = value;
	}
	if (apiRecord.created_at) localRecord.created_at = apiRecord.created_at;
	return localRecord;
}

function mapLocalRecordToApi(
	formId: number,
	localRecord: LocalRecord,
	formFields: Field[]
): Omit<FormRecord, 'id'> {
	const data: Record<string, any> = {};
	for (const field of formFields) {
		if (localRecord[field.key] !== undefined) {
			data[field.key] = localRecord[field.key];
		}
	}
	return {
		form_id: formId,
		data,
	};
}

export async function loadAllData(): Promise<void> {
	try {
		fields.value = await apiGetFields();
		forms.value = await apiGetForms();
		tables.value = await apiGetTables();
		const allRecords = await apiGetRecords();

		// Очистка локального хранилища записей
		for (const key in records) delete records[key];

		for (const apiRec of allRecords) {
			const formId = apiRec.form_id;
			if (!records[formId]) records[formId] = [];

			const form = forms.value.find(f => f.id === formId);
			if (form) {
				const formFields = form.field_ids
					.map(id => fields.value.find(f => f.id === id))
					.filter((f): f is Field => f !== undefined);
				const localRec = mapApiRecordToLocal(apiRec, formFields);
				records[formId].push(localRec);
			} else {
				// Если форма не найдена, сохраняем только id и данные как есть
				records[formId].push({ id: apiRec.id, ...apiRec.data });
			}
		}
	} catch (error) {
		console.error('Failed to load data from API', error);
		// Здесь можно добавить уведомление пользователя
		throw error;
	}
}

// --- Fields ---
export async function addField(field: Omit<Field, 'id'>): Promise<Field> {
	const newField = await apiCreateField(field);
	fields.value.push(newField);
	return newField;
}

export async function updateField(id: number, updated: Partial<Field>): Promise<Field> {
	const updatedField = await apiUpdateField(id, updated);
	const idx = fields.value.findIndex(f => f.id === id);
	if (idx !== -1) fields.value[idx] = updatedField;
	return updatedField;
}

export async function deleteField(id: number): Promise<void> {
	await apiDeleteField(id);
	fields.value = fields.value.filter(f => f.id !== id);
}

// --- Forms ---
export async function addForm(form: any) {
	const apiForm = {
		name: form.name,
		field_ids: form.field_ids || form.fieldIds || []
	};
	const newForm = await apiCreateForm(apiForm);
	forms.value.push(newForm);
	return newForm;
}

export async function updateForm(id: number, updated: any) {
	const apiUpdate = {
		name: updated.name,
		field_ids: updated.field_ids || updated.fieldIds
	};
	const updatedForm = await apiUpdateForm(id, apiUpdate);
	const idx = forms.value.findIndex(f => f.id === id);
	if (idx !== -1) forms.value[idx] = updatedForm;
	return updatedForm;
}

export async function deleteForm(id: number): Promise<void> {
	// Находим все таблицы, использующие эту форму
	const linkedTables = tables.value.filter(t => t.form_id === id);

	// Удаляем каждую таблицу (каскадно удаляются и записи)
	for (const table of linkedTables) {
		await deleteTable(table.id); // deleteTable уже удаляет записи и таблицу
	}

	// Удаляем саму форму
	await apiDeleteForm(id);

	// Обновляем локальные данные
	forms.value = forms.value.filter(f => f.id !== id);
	tables.value = tables.value.filter(t => t.form_id !== id);
	delete records[id];
}

// --- Tables ---
export async function addTable(table: Omit<Table, 'id'>): Promise<Table> {
	const newTable = await apiCreateTable(table);
	tables.value.push(newTable);
	return newTable;
}

export async function deleteTable(id: number): Promise<void> {
	const table = tables.value.find(t => t.id === id);
	if (!table) return;

	const formId = table.form_id;

	// Проверяем, есть ли другие таблицы, использующие ту же форму
	const otherTables = tables.value.filter(t => t.form_id === formId && t.id !== id);
	const isLastTable = otherTables.length === 0;

	// Если это последняя таблица для формы, удаляем все записи формы
	if (isLastTable && records[formId]) {
		for (const record of records[formId]) {
			await apiDeleteRecord(record.id);
		}
		delete records[formId];
	}

	// Удаляем саму таблицу
	await apiDeleteTable(id);
	tables.value = tables.value.filter(t => t.id !== id);
}

// --- Records ---
export async function addRecord(formId: number, record: Partial<LocalRecord>): Promise<LocalRecord> {
	const form = forms.value.find(f => f.id === formId);
	if (!form) throw new Error(`Form ${formId} not found`);
	const formFields = form.field_ids
		.map(id => fields.value.find(f => f.id === id))
		.filter((f): f is Field => f !== undefined);
	const apiRecord = mapLocalRecordToApi(formId, record as LocalRecord, formFields);
	const newApiRecord = await apiCreateRecord(apiRecord);
	const localRec = mapApiRecordToLocal(newApiRecord, formFields);
	if (!records[formId]) records[formId] = [];
	records[formId].push(localRec);
	return localRec;
}

export async function updateRecord(formId: number, recordId: number, data: Partial<LocalRecord>): Promise<void> {
	const form = forms.value.find(f => f.id === formId);
	if (!form) throw new Error(`Form ${formId} not found`);
	const formFields = form.field_ids
		.map(id => fields.value.find(f => f.id === id))
		.filter((f): f is Field => f !== undefined);
	const localRecords = records[formId] || [];
	const localRec = localRecords.find(r => r.id === recordId);
	if (!localRec) throw new Error(`Record ${recordId} not found`);
	const updatedLocal = { ...localRec, ...data };
	const apiRecord = mapLocalRecordToApi(formId, updatedLocal, formFields);
	const updatedApiRecord = await apiUpdateRecord(recordId, apiRecord);
	const idx = localRecords.findIndex(r => r.id === recordId);
	if (idx !== -1) {
		localRecords[idx] = mapApiRecordToLocal(updatedApiRecord, formFields);
	}
}

export async function deleteRecord(formId: number, recordId: number): Promise<void> {
	await apiDeleteRecord(recordId);
	if (records[formId]) {
		records[formId] = records[formId].filter(r => r.id !== recordId);
	}
}

// --- Sync helpers ---
export function getFieldById(id: number): Field | undefined {
	return fields.value.find(f => f.id === id);
}

export function getFormById(id: number): Form | undefined {
	return forms.value.find(f => f.id === id);
}

export function getFieldsForForm(formId: number): Field[] {
	const form = getFormById(formId);
	if (!form) return [];
	return form.field_ids
		.map(id => getFieldById(id))
		.filter((f): f is Field => f !== undefined);
}

export function getRecords(formId: number): LocalRecord[] {
	return records[formId] || [];
}