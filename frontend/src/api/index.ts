import axios from 'axios';

const API_BASE = 'http://localhost:8000'; // если бэкенд на этом порту

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Типы для данных
export interface Field {
  id: number;
  name: string;
  key: string;
  type: string;
  options: any;
}

export interface Form {
  id: number;
  name: string;
  field_ids: number[];
}

export interface Table {
  id: number;
  name: string;
  form_id: number;
  columns: number[];
}

export interface FormRecord {
  id: number;
  form_id: number;
  data: Record<string, any>;
  created_at?: string;
}

// Fields
export const getFields = async (): Promise<Field[]> => {
  const res = await api.get('/fields');
  return res.data;
};

export const createField = async (field: Omit<Field, 'id'>): Promise<Field> => {
  const res = await api.post('/fields', field);
  return res.data;
};

export const updateField = async (id: number, field: Partial<Field>): Promise<Field> => {
  const res = await api.put(`/fields/${id}`, field);
  return res.data;
};

export const deleteField = async (id: number): Promise<void> => {
  await api.delete(`/fields/${id}`);
};

// Forms
export const getForms = async (): Promise<Form[]> => {
  const res = await api.get('/forms');
  return res.data;
};

export const createForm = async (form: Omit<Form, 'id'>): Promise<Form> => {
  const res = await api.post('/forms', form);
  return res.data;
};

export const updateForm = async (id: number, form: Partial<Form>): Promise<Form> => {
  const res = await api.put(`/forms/${id}`, form);
  return res.data;
};

export const deleteForm = async (id: number): Promise<void> => {
  await api.delete(`/forms/${id}`);
};

// Tables
export const getTables = async (): Promise<Table[]> => {
  const res = await api.get('/tables');
  return res.data;
};

export const createTable = async (table: Omit<Table, 'id'>): Promise<Table> => {
  const res = await api.post('/tables', table);
  return res.data;
};

export const deleteTable = async (id: number): Promise<void> => {
  await api.delete(`/tables/${id}`);
};

// Records
export const getRecords = async (formId?: number): Promise<FormRecord[]> => {
  const params = formId ? { form_id: formId } : {};
  const res = await api.get('/records', { params });
  return res.data;
};

export const createRecord = async (record: Omit<FormRecord, 'id'>): Promise<FormRecord> => {
  const res = await api.post('/records', record);
  return res.data;
};

export const updateRecord = async (id: number, record: Partial<FormRecord>): Promise<FormRecord> => {
  const res = await api.put(`/records/${id}`, record);
  return res.data;
};

export const deleteRecord = async (id: number): Promise<void> => {
  await api.delete(`/records/${id}`);
};