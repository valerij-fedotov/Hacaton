export type FieldType =
	| 'string'
	| 'text'
	| 'number'
	| 'date'
	| 'datetime'
	| 'period'
	| 'radio'
	| 'checkbox'
	| 'select'
	| 'multiselect'
	| 'coordinates';

export interface FieldOption {
	value: string;
	label: string;
}

export interface FieldConfig {
	required?: boolean;
	min?: number;
	max?: number;
	options?: FieldOption[] | string; // для select/multiselect/radio
	coordinateFormat?: 'latlng' | 'lnglat'; // для координат
}

export interface Field {
	id: string;          // уникальный временный id для v-for key
	key: string;         // техническое имя
	label: string;       // отображаемое имя
	type: FieldType;
	config: FieldConfig;
}